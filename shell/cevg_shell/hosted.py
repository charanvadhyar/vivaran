"""The CEVG MCP server for the platform: many users, one machine.

Each user has their own connector address, `/u/<token>/mcp`. The token says
who is calling. A video rendered through that address is saved to that
user's account in the database the website reads, and stays private until
the creator makes it public on the site.

This runs beside the website and shares its Postgres database and its
storage folder. It needs `pip install "mcp>=2.3" "psycopg[binary]"`.

Settings come from the environment:

    DATABASE_URL        postgres://user:password@host:port/dbname   (required)
    SITE_URL            where the website is reached, e.g. https://cevg.example
    CEVG_STORAGE        folder for videos and thumbnails (default ./storage)
    CEVG_TTS            voice service: gnani (default) or sarvam
    GNANI_API_KEY       the platform's Gnani key (or SARVAM_API_KEY for Sarvam);
                        without it videos are silent
    CEVG_KEY_SECRET     passphrase that pgcrypto uses to encrypt each user's own
                        Gnani key in the database (shared with the website); a
                        user who has set their own key renders on their own Gnani
                        credits, and the platform key is only the free-taste default
    CEVG_WATERMARK      text in the corner of every video (default "Vivaran")
    CEVG_MAX_MINUTES    longest single video for anyone, in minutes (default 20); each
                        tier's own limit is in the `settings` table
    ANTHROPIC_API_KEY   for figures and YouTube SEO drawn by the Claude API

Credits, tiers and rewards: see credits.py and platform/schema.sql. The schema is
applied when the server starts, so the database is always up to date.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import psycopg
from mcp.server import MCPServer
from mcp.server.mcpserver import Context, Image
from mcp.server.mcpserver.exceptions import ToolError
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from . import credits, providers
from .narrate import NarrateError, narrate
from .server import INSTRUCTIONS, MAKES_FILES, READ_ONLY, Studio, _voice_line

USER_HEADER = "x-cevg-user-id"

# The subjects the site groups videos under. Keep in step with platform/web/lib/brand.ts.
SUBJECTS = ("dsa", "ml", "dbms", "os", "coa", "networks", "maths", "other")

HOSTED_INSTRUCTIONS = INSTRUCTIONS + """
This is Vivaran, the hosted platform. Every video you render is saved to the user's
account and is private. When `status` says it is done, give the user the
`watch_url`. Tell them to watch it and check it against your explanation;
if it is right they can make it public from that page. `my_videos` lists
what they have made.

The user decides how long the video is. Always pass the length they chose as
`target_minutes` to `estimate`. In hosts that show Vivaran's panel, `estimate`
shows the plan (each scene's length, the total against their length, the cost),
`render` shows live progress and then the video, and `account` shows their
credits. Buttons in the panel send the user's words into the chat, such as
"Change the script to about 8 minutes" or "Render it": act on them as if typed.
If the plan is more than about 15% off the chosen length, say so and offer to
add or remove steps; render only when the user agrees.
"""

# The panel shown inside hosts that support MCP Apps (Claude, ChatGPT and others).
PANEL_URI = "ui://vivaran/panel.html"
PANEL_MIME = "text/html;profile=mcp-app"


def panel_meta(*, app_only: bool = False) -> dict[str, Any]:
    """Tool metadata that shows the panel with this tool's result. Both spellings, for older hosts."""
    ui: dict[str, Any] = {"resourceUri": PANEL_URI}
    if app_only:
        ui["visibility"] = ["app"]
    return {"ui": ui, "ui/resourceUri": PANEL_URI}


def signed(site_url: str, path: str, video_id: str, hours: float = 6) -> str:
    """A link to a video file or thumbnail that works for a few hours without signing in, for the panel's
    player (the host shows the panel in a sandbox without the site's cookies). The site checks it with the
    same CEVG_INTERNAL_TOKEN."""
    import hashlib
    import hmac
    key = os.environ.get("CEVG_INTERNAL_TOKEN", "")
    if not key:
        return ""
    expires = int(time.time() + hours * 3600)
    sig = hmac.new(key.encode(), f"{video_id}.{expires}".encode(), hashlib.sha256).hexdigest()[:32]
    return f"{site_url}/api/videos/{video_id}/{path}?exp={expires}&sig={sig}"


class Limit(ValueError):
    """A render refused because of a per-user limit."""


class Platform(Studio):
    """The studio, with accounts: who is rendering, where it is stored, what they may spend."""

    def __init__(self, database_url: str, storage: Path, site_url: str, cevg: str | None = None,
                 watermark: str = "Vivaran", daily_voice_minutes: float = 10, max_minutes: float = 12,
                 requests_per_minute: float = 30):
        storage = Path(storage).expanduser().resolve()
        super().__init__(storage / "videos", storage / "voice-cache", cevg, requests_per_minute=requests_per_minute)
        self.database_url = database_url
        self.site_url = site_url.rstrip("/")
        self.samples = storage / "samples"
        self.samples.mkdir(parents=True, exist_ok=True)
        self.watermark = watermark
        self.daily_voice_seconds = daily_voice_minutes * 60
        self.max_seconds = max_minutes * 60
        try:
            credits.apply_schema(database_url, os.environ.get("CEVG_PLATFORM_DIR"))
        except Exception as e:  # the site can apply it too; never stop the server for this
            print(f"could not apply the schema: {e}", flush=True)
        self._users: dict[str, tuple[float, dict[str, Any] | None]] = {}
        self.draw_missing_figures = False
        # A render that was cut off by a restart can never finish; say so.
        cut_off = self._all("update videos set status = 'failed', error = 'the server restarted during this render; "
                            "render it again', finished_at = now() where status in ('queued', 'running') returning id")
        for row in cut_off:
            try:
                with self._connect() as db:
                    credits.refund(db, row["id"])
            except Exception as e:
                print(f"could not refund {row['id']}: {e}", flush=True)

    # -- database --------------------------------------------------------

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, row_factory=dict_row, autocommit=True)

    def _execute(self, sql: str, params: tuple = ()) -> None:
        with self._connect() as db:
            db.execute(sql, params)

    def _one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        with self._connect() as db:
            return db.execute(sql, params).fetchone()

    def _all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self._connect() as db:
            return db.execute(sql, params).fetchall()

    def user_for_token(self, token: str) -> dict[str, Any] | None:
        """The account a connector token belongs to. Answers are kept for a minute."""
        kept = self._users.get(token)
        if kept and time.time() - kept[0] < 60:
            return kept[1]
        user = self._one("update users set last_seen_at = now(), connector_used_at = now() where connector_token = %s "
                         "returning id::text as id, name, handle, is_admin", (token,))
        if len(self._users) > 10_000:
            self._users.clear()
        self._users[token] = (time.time(), user)
        return user

    def gnani_key_for(self, user_id: str) -> str | None:
        """A user's own Gnani key, decrypted, or None if they have not set one.

        Bring-your-own-key: when set, the render runs on the user's own Gnani
        credits instead of the platform's. Needs CEVG_KEY_SECRET (the same
        passphrase the website encrypts with); without it, BYOK is off and
        everyone falls back to the platform key.
        """
        secret = os.environ.get("CEVG_KEY_SECRET", "").strip()
        if not secret:
            return None
        row = self._one(
            "select pgp_sym_decrypt(gnani_key_enc, %s) as key from users "
            "where id = %s and gnani_key_enc is not null", (secret, user_id))
        key = (row or {}).get("key")
        if isinstance(key, (bytes, bytearray, memoryview)):
            key = bytes(key).decode("utf-8", "replace")
        key = (key or "").strip()
        return key or None

    # -- limits ----------------------------------------------------------

    def account(self, user: dict[str, Any]) -> dict[str, Any]:
        """Tier, credits and what things cost, for the assistant to tell the user."""
        with self._connect() as db:
            p = credits.plans(db)
            t = credits.tier(db, user["id"])
            b = credits.balance(db, user["id"])
        own = bool(self.gnani_key_for(user["id"]))
        c = p["cost"]
        return {
            "tier": t, "credits": b["total"], "monthly_credits_left": b["monthly"], "bonus_credits": b["bonus"],
            "longest_video_minutes": min(float(p[t]["max_minutes"]), self.max_seconds / 60), "own_gnani_key": own,
            "cost": (f"{c['voiced']:g} credit per started {c['minutes_per_credit']:g} minutes voiced with Vivaran's "
                     f"voice; {c['silent_or_own_key']:g} per started {c['minutes_per_credit']:g} minutes silent or "
                     f"voiced on the user's own Gnani key"),
            "more_credits": f"{self.site_url}/dashboard",
            "limits_url": self._limit_link("other"),
            "held": bool((self._one("select free_held and vivaran_tier(id) = 'free' as held from users where id = %s",
                                    (user["id"],)) or {}).get("held")),
            **({"admin": "this is an admin account: renders are not charged"} if user.get("is_admin") else {}),
        }

    def _limit_link(self, limit: str) -> str:
        """Where a user asks for a limit to be raised (the site's contact page)."""
        return f"{self.site_url.rstrip('/')}/contact?kind=support&topic=limit&limit={limit}"

    def _check_limits(self, user_id: str, seconds: float, voiced: bool, has_own_key: bool = False,
                      is_admin: bool = False) -> float:
        """Refuse what this account may not render; otherwise return the credits it will cost (admins: none)."""
        with self._connect() as db:
            p = credits.plans(db)
            t = credits.tier(db, user_id)
            b = credits.balance(db, user_id)
        longest = min(float(p[t]["max_minutes"]) * 60, self.max_seconds)
        if seconds > longest:
            more = (" Pro allows longer videos." if t == "free" else
                    f" To ask for longer videos: {self._limit_link('length')}")
            raise Limit(f"this video would be about {seconds / 60:.1f} minutes; the longest allowed on this plan is "
                        f"{longest / 60:.0f} minutes. Shorten the script or split the topic in two.{more}")
        busy = self._one("select count(*) as n from videos where user_id = %s and status in ('queued', 'running')",
                         (user_id,))
        if busy and busy["n"] >= 1:
            raise Limit("this account already has a video rendering; wait for it to finish (call `status`)")
        if is_admin:
            return 0.0
        price = credits.cost(p, seconds, voiced and not has_own_key)
        if price > b["total"] + 1e-9:
            raise Limit(f"this video costs {price:g} credit(s) and the account has {b['total']:g}. Credits refill each "
                        f"month, and more can be earned or bought at {self.site_url}/dashboard. A silent video "
                        f"(voice=false), or one voiced on the user's own Gnani key, costs a quarter as much. If the "
                        f"account's free credits are on hold, or the user needs more, they can ask at "
                        f"{self._limit_link('credits')}")
        return price

    def start(self, user: dict[str, Any], script: dict[str, Any], language: str, voice: bool, captions: bool,
              speaker: str, pace: float, subject: str | None = None) -> dict[str, Any]:
        if subject is not None and subject not in SUBJECTS:
            raise ValueError(f"unknown subject `{subject}`; choose one of: {', '.join(SUBJECTS)}")
        estimate = self.estimate(script, language)  # validates too
        if "problem" in estimate:
            raise ValueError(estimate["problem"])
        # Bring-your-own-key: if this user has set their own Gnani key, the render
        # uses it (their credits, no daily cap); otherwise the platform key is the
        # free-taste default, bounded by the daily voiced-minute limit.
        own_key = self.gnani_key_for(user["id"]) if voice else None
        if voice:
            provider = providers.current(api_key=own_key)
            if not provider.available():
                raise ValueError(
                    f"voice needs a Gnani key: this server has none and your account has none. Add your own key in "
                    f"Settings on {self.site_url}, or render with voice=false (silent, with captions).")
            provider.check(speaker or None, language, pace)
            speaker = speaker or provider.default_speaker(language)
        price = self._check_limits(user["id"], estimate["seconds"], voice, has_own_key=bool(own_key),
                                   is_admin=bool(user.get("is_admin")))
        with self._connect() as db:
            watermark_on = bool(credits.plans(db)[credits.tier(db, user["id"])]["watermark"]) and bool(self.watermark)

        video_id = uuid.uuid4().hex[:12]
        self._execute(
            "insert into videos (id, user_id, title, language, speaker, voiced, captions, status, progress, script, "
            "outline, steps, subject, watermarked) values (%s, %s, %s, %s, %s, %s, %s, 'queued', %s, %s, %s, %s, %s, %s)",
            (video_id, user["id"], str(script.get("title") or "Untitled")[:200], language, speaker if voice else None,
             voice, captions, "waiting for an earlier render to finish", Jsonb(script), Jsonb(estimate["outline"]),
             estimate["steps"], subject, watermark_on))
        with self._connect() as db:
            if price > 0 and not credits.spend(db, user["id"], price, video_id):
                db.execute("delete from videos where id = %s", (video_id,))
                raise Limit("not enough credits for this video; the dashboard on the site shows the balance")
            credits.event(db, "render_started", user["id"], video_id, credits=price, voiced=voice,
                          own_key=bool(own_key), language=language)
        folder = Path(tempfile.mkdtemp(prefix="cevg-job-"))
        path = self._write(script, folder)
        threading.Thread(target=self._render,
                         args=(video_id, user, path, language, voice, captions, speaker, pace, own_key, watermark_on),
                         daemon=True).start()
        return {"job": video_id, "state": "queued", "estimated_minutes": estimate["minutes"], "credits": price,
                "advice": "call `status` with this job id in about 20 seconds"}

    def _render(self, video_id: str, user: dict[str, Any], script: Path, language: str, voice: bool, captions: bool,
                speaker: str, pace: float, own_key: str | None = None, watermark_on: bool = True) -> None:
        def progress(message: str) -> None:
            self._execute("update videos set progress = %s where id = %s", (message, video_id))

        with self._one_at_a_time:
            self._execute("update videos set status = 'running', progress = 'starting' where id = %s", (video_id,))
            out = self.out_dir / f"{video_id}.mp4"
            mark = f"{self.watermark} · {user['handle']}" if self.watermark and watermark_on else None
            try:
                characters = 0
                note = "finished"
                self._draw_figures_in(script, progress)
                if voice:
                    voice_obj = self._voice(speaker, pace, api_key=own_key)
                    result = narrate(script, out, voice_obj, language=language,
                                     cache_dir=self.cache_dir, cevg=self.cevg, burn_captions=captions, watermark=mark,
                                     listen=hasattr(voice_obj, "listen"), progress=progress)
                    seconds, characters = result.seconds, result.characters
                    doubtful = result.doubtful()
                    unchecked = result.unchecked()
                    if unchecked:
                        note = ("finished; the narration could not be listened back (the transcription service "
                                "failed), so watch it through before publishing")
                    if doubtful:
                        steps = ", ".join(str(h["step"]) for h in doubtful)
                        note = (f"finished; listening back, the voice may have skipped or garbled words in "
                                f"step(s) {steps}: watch those before publishing")
                else:
                    progress("rendering video")
                    command = ["render", str(script), "--json", "-o", str(out)]
                    if captions:
                        command += ["--captions", language]
                    if mark:
                        command += ["--watermark", mark]
                    done = self._run(*command)
                    if done.returncode != 0:
                        raise NarrateError((done.stdout + "\n" + done.stderr).strip())
                    seconds = json.loads(done.stdout)["seconds"]
                # A still from the last step is the thumbnail on the site.
                self._run("frame", str(script), "-o", str(self.out_dir / f"{video_id}.png"))
                self._execute("update videos set status = 'done', progress = %s, seconds = %s, "
                              "characters = %s, finished_at = now() where id = %s", (note, seconds, characters, video_id))
                with self._connect() as db:
                    credits.event(db, "render_done", user["id"], video_id, seconds=seconds, characters=characters,
                                  voiced=voice, own_key=bool(own_key), language=language)
            except providers.VoiceError as e:
                self._fail(video_id, f"{e}\n{e.advice()}")
            except Exception as e:  # a job must always end in a state the assistant can read
                self._fail(video_id, str(e))

    def figure_for(self, user: dict[str, Any], prompt: str) -> dict[str, Any]:
        """Draw a figure on the platform's Claude API key, within the plan's monthly allowance."""
        from . import figures
        if not figures.cache_path(prompt, self.cache_dir).exists():
            with self._connect() as db:
                p = credits.plans(db)
                t = credits.tier(db, user["id"])
                used = db.execute("select count(*) as n from events where type = 'figure' and user_id = %s::uuid "
                                  "and created_at > date_trunc('month', now())", (user["id"],)).fetchone()["n"]
            allowed = int(p[t].get("figures_per_month", 5))
            if used >= allowed:
                raise ValueError(f"this account has drawn {used} new figures this month, the {t} plan's allowance; "
                                 "reuse a figure already drawn, or give a figure's `svg` yourself. The user can ask "
                                 f"for more at {self._limit_link('figures')}")
            result = self.draw_figure(prompt)
            with self._connect() as db:
                credits.event(db, "figure", user["id"], prompt=prompt[:300])
            return result
        return self.draw_figure(prompt)

    def _fail(self, video_id: str, error: str) -> None:
        """A render failed: say why, and give back the credits it took."""
        with self._connect() as db:
            row = db.execute("update videos set status = 'failed', error = %s, finished_at = now() where id = %s "
                             "returning user_id::text as uid", (error[:2000], video_id)).fetchone()
            back = credits.refund(db, video_id)
            credits.event(db, "render_failed", row["uid"] if row else None, video_id, error=error[:300], refunded=back)

    def job(self, user: dict[str, Any], video_id: str) -> dict[str, Any]:
        row = self._one("select id, title, status, progress, error, seconds, steps, is_public, "
                        "extract(epoch from coalesce(finished_at, now()) - created_at)::int as elapsed "
                        "from videos where id = %s and user_id = %s", (video_id, user["id"]))
        if row is None:
            return {"state": "unknown", "error": f"this account has no video `{video_id}`"}
        report: dict[str, Any] = {"job": row["id"], "title": row["title"], "state": row["status"],
                                  "progress": row["progress"], "elapsed_seconds": row["elapsed"]}
        if row["status"] == "done":
            report.update(seconds=round(row["seconds"], 1), steps=row["steps"],
                          watch_url=f"{self.site_url}/v/{row['id']}", public=row["is_public"],
                          next="the video is private; the creator watches it at watch_url and can make it public there")
        elif row["status"] == "failed":
            report["error"] = row["error"]
        else:
            report["advice"] = "still working; ask again in about 20 seconds"
        return report

    def progress_for_panel(self, user: dict[str, Any], video_id: str) -> dict[str, Any]:
        """`job`, plus what the panel needs: the video's note, and signed links to play it once done."""
        report = self.job(user, video_id)
        if report.get("state") == "done":
            row = self._one("select progress from videos where id = %s", (video_id,))
            report["note"] = (row or {}).get("progress", "")
            report["player"] = {"video": signed(self.site_url, "file", video_id),
                                "poster": signed(self.site_url, "thumb", video_id)}
        return report

    def plan(self, user: dict[str, Any], script: dict[str, Any], language: str, target_minutes: float | None,
             voice: bool) -> dict[str, Any]:
        """`estimate`, with the length the user chose, what rendering it costs and what the account has."""
        result = self.estimate(script, language)
        with self._connect() as db:
            p = credits.plans(db)
        own = bool(self.gnani_key_for(user["id"])) if voice else False
        acc = self.account(user)
        result.update(view="plan", voice=voice, target_minutes=target_minutes,
                      cost=0.0 if user.get("is_admin") else credits.cost(p, result["seconds"], voice and not own),
                      account={k: acc[k] for k in ("tier", "credits", "longest_video_minutes")})
        if target_minutes:
            off = result["minutes"] / target_minutes - 1
            result["length_check"] = ("on target" if abs(off) <= 0.15 else
                                      f"{abs(off) * 100:.0f}% {'longer' if off > 0 else 'shorter'} than the "
                                      f"{target_minutes:g} minutes the user chose: offer to "
                                      f"{'remove' if off > 0 else 'add'} steps before rendering")
        return result

    def library(self, user: dict[str, Any]) -> list[dict[str, Any]]:
        rows = self._all("select id, title, language, status, seconds, is_public, created_at from videos "
                         "where user_id = %s order by created_at desc limit 30", (user["id"],))
        return [{"id": r["id"], "title": r["title"], "language": r["language"], "state": r["status"],
                 "minutes": round(r["seconds"] / 60, 1) if r["seconds"] else None, "public": r["is_public"],
                 "made": r["created_at"].date().isoformat(), "watch_url": f"{self.site_url}/v/{r['id']}"}
                for r in rows]

    def sample(self, speaker: str, language: str, pace: float) -> dict[str, Any]:
        result = self.voice_sample(speaker, language, pace)  # writes into out_dir
        made = Path(result.pop("file"))
        made.replace(self.samples / made.name)
        result["url"] = f"{self.site_url}/api/samples/{made.name}"
        return result


def build(platform: Platform) -> MCPServer:
    server = MCPServer("cevg", title="Vivaran: explanation videos for CS and maths", instructions=HOSTED_INSTRUCTIONS)

    def who(ctx: Context) -> dict[str, Any]:
        """The account this call belongs to, set by the gate in front of the server."""
        user_id = (ctx.headers or {}).get(USER_HEADER)
        user = platform._one("select id::text as id, name, handle, is_admin from users where id::text = %s", (user_id,)) \
            if user_id else None
        if user is None:
            raise ToolError("this connector address is not linked to an account; copy a fresh address from the site")
        return user

    def guarded(call):
        try:
            return call()
        except providers.VoiceError as e:
            raise ToolError(f"{e}\n{e.advice()}") from None
        except (ValueError, NarrateError) as e:
            raise ToolError(str(e)) from None

    @server.tool(title="Read the authoring guide", annotations=READ_ONLY)
    def guide() -> str:
        """The reference for writing a CEVG scene script: what can be drawn, how parts are named, every
        action, how to plan scenes, the teaching standard, and how to write narration (including the
        code-mixed style for Hindi and Telugu). Call this once before writing a script."""
        return platform.guide()

    @server.tool(title="Check a scene script", annotations=READ_ONLY)
    def validate(script: dict[str, Any]) -> dict[str, Any]:
        """Check a scene script without drawing it. Returns `ok`, and `diagnostics` with the exact path of
        every problem and how to fix it. Costs nothing; call it after every change."""
        return platform.validate(script)

    @server.tool(title="Look at one frame", annotations=READ_ONLY)
    def preview(script: dict[str, Any], scene: str | None = None, step: int | None = None, at: float = 1.0,
                captions: str | None = None) -> Image:
        """Draw one moment of the video as a picture, to check the layout by eye before rendering.
        `scene` is a scene id (default: the last scene); `step` counts from 0 within the scene (default: its
        last step); `at` is how far through the step, 0 to 1; `captions` is a language code to show that
        narration under the picture."""
        return Image(data=guarded(lambda: platform.preview(script, scene, step, at, captions)), format="png")

    @server.tool(title="Draw a figure")
    def figure(ctx: Context, prompt: str) -> dict[str, Any]:
        """Have a textbook-style figure drawn as SVG from a description, for a `figure` object: for example
        "the ANSI/SPARC three-schema architecture: end users, external views, conceptual schema, internal
        schema, stored database, with both mappings labelled". Say what the parts are and the order to build
        them in. Returns the SVG and its part names; the drawing is checked and corrected before it comes back.
        Takes up to a minute or two; the same prompt is drawn only once."""
        user = who(ctx)
        return guarded(lambda: platform.figure_for(user, prompt))

    @server.resource(PANEL_URI, name="vivaran-panel", title="Vivaran", mime_type=PANEL_MIME,
                     description="Vivaran's panel: the video plan, render progress and the account.",
                     meta={"ui": {"prefersBorder": True,
                                  "csp": {"resourceDomains": [platform.site_url], "connectDomains": []}}})
    def panel() -> str:
        return (Path(__file__).with_name("panel.html")).read_text(encoding="utf-8")

    @server.tool(title="Estimate length and contents", annotations=READ_ONLY, meta=panel_meta())
    def estimate(ctx: Context, script: dict[str, Any], language: str = "en", target_minutes: float | None = None,
                 voice: bool = True) -> dict[str, Any]:
        """How long the video will be, in minutes, and an outline of its scenes with the time each takes,
        without rendering, with what rendering it costs. Pass `target_minutes`, the length the user chose,
        and `voice` as you will render. Use it to bring the script to the user's length, and to show the
        user what the video will contain before `render`; `length_check` says how far off it is."""
        user = who(ctx)
        return guarded(lambda: platform.plan(user, script, language, target_minutes, voice))

    @server.tool(title="List the narration voices", annotations=READ_ONLY)
    def voices() -> dict[str, Any]:
        """The voices a video can be narrated in and the languages they speak. Show this to the user and
        let them choose; use `voice_sample` if they want to hear one first."""
        return platform.voices()

    @server.tool(title="Hear a voice", annotations=MAKES_FILES)
    def voice_sample(ctx: Context, speaker: str = "", language: str = "en", pace: float = 1.0) -> dict[str, Any]:
        """Make a short audio sample of one voice in one language so the user can hear it before choosing.
        Returns a `url` to play."""
        who(ctx)
        return guarded(lambda: platform.sample(speaker, language, pace))

    @server.tool(title="Start rendering the video", annotations=MAKES_FILES, meta=panel_meta())
    def render(ctx: Context, script: dict[str, Any], language: str = "en", voice: bool = True,
               captions: bool = False, speaker: str = "", pace: float = 1.0,
               subject: str | None = None) -> dict[str, Any]:
        """Start making the video and return a job id at once; then call `status` until it is done.
        `subject` files the video on the site: dsa (data structures and algorithms), ml, dbms, os, coa
        (computer architecture), networks, maths or other.
        The video is saved, private, in the user's account. `language` picks which narration in each
        step's `say` is spoken; every step must have it. `voice=false` makes a silent video timed from the
        text. `captions=true` shows the narration under the picture. A render costs credits (see `account`):
        one credit per started 10 minutes with Vivaran's voice, a quarter of that silent or on the user's own
        Gnani key. A failed render gives its credits back. Validate, preview and estimate first."""
        user = who(ctx)
        started = guarded(lambda: platform.start(user, script, language, voice, captions, speaker, pace, subject))
        return {**started, "view": "render", "title": str(script.get("title") or "Untitled")[:200]}

    @server.tool(title="Credits and plan", annotations=READ_ONLY, meta=panel_meta())
    def account(ctx: Context) -> dict[str, Any]:
        """The user's plan, credits left and what a video costs. Check it before `render` and tell the user
        what the video will cost."""
        return {**platform.account(who(ctx)), "view": "account"}

    @server.tool(title="Render progress for the panel", annotations=READ_ONLY, meta=panel_meta(app_only=True))
    def video_progress(ctx: Context, job: str) -> dict[str, Any]:
        """For Vivaran's panel: how a render is going, and links to play it once done. Use `status` instead."""
        return platform.progress_for_panel(who(ctx), job)

    @server.tool(title="Ask how a render is going", annotations=READ_ONLY)
    def status(ctx: Context, job: str) -> dict[str, Any]:
        """The state of a render: `queued`, `running`, `done` or `failed`. When done it gives `watch_url`,
        the page where the creator watches the video and can make it public."""
        return platform.job(who(ctx), job)

    @server.tool(title="List my videos", annotations=READ_ONLY)
    def my_videos(ctx: Context) -> list[dict[str, Any]]:
        """The user's most recent videos on the platform, with their state and watch links."""
        return platform.library(who(ctx))

    return server


def gate(app, platform: Platform):
    """Let only `/u/<token>/mcp` through, as `/mcp`, with the account attached.

    The account header is taken off anything arriving from outside, so a
    caller cannot name an account they do not hold the token for.
    """
    async def refuse(send, status: int, text: str) -> None:
        body = text.encode()
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"text/plain; charset=utf-8"),
                                (b"content-length", str(len(body)).encode())]})
        await send({"type": "http.response.body", "body": body})

    async def gated(scope, receive, send):
        if scope["type"] != "http":
            return await app(scope, receive, send)
        parts = scope["path"].strip("/").split("/")
        if len(parts) == 1 and parts[0] == "health":
            return await refuse(send, 200, "ok")
        if len(parts) == 3 and parts[0] == "files":
            return await files(scope, receive, send, parts[1], parts[2])
        if len(parts) == 2 and parts[0] == "internal" and scope["method"] == "POST":
            return await internal(scope, receive, send, parts[1])
        if len(parts) != 3 or parts[0] != "u" or parts[2] != "mcp":
            return await refuse(send, 404, "not found")
        import anyio
        user = await anyio.to_thread.run_sync(platform.user_for_token, parts[1])
        if user is None:
            return await refuse(send, 401, "this connector address is not valid; copy a fresh one from the site")
        headers = [(k, v) for k, v in scope["headers"] if k.lower() != USER_HEADER.encode()]
        headers.append((USER_HEADER.encode(), user["id"].encode()))
        return await app({**scope, "path": "/mcp", "raw_path": b"/mcp", "headers": headers}, receive, send)

    async def files(scope, receive, send, kind: str, name: str):
        """Videos, thumbnails and voice samples, for the website only: it checks who
        may watch, then asks for the file with the shared internal token."""
        import hmac
        from starlette.responses import FileResponse
        token = os.environ.get("CEVG_INTERNAL_TOKEN", "")
        given = dict(scope["headers"]).get(b"x-cevg-internal", b"").decode("latin-1")
        if not token or not hmac.compare_digest(token, given):
            return await refuse(send, 404, "not found")
        folders = {"videos": platform.out_dir, "samples": platform.samples}
        types = {".mp4": "video/mp4", ".png": "image/png", ".wav": "audio/wav"}
        path = folders.get(kind, Path("/nonexistent")) / name
        if Path(name).name != name or path.suffix not in types or not path.is_file():
            return await refuse(send, 404, "not found")
        return await FileResponse(path, media_type=types[path.suffix])(scope, receive, send)

    async def internal(scope, receive, send, name: str):
        """Calls from the website only: YouTube SEO, uploads and statistics."""
        import hmac
        import anyio
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from . import youtube
        token = os.environ.get("CEVG_INTERNAL_TOKEN", "")
        given = dict(scope["headers"]).get(b"x-cevg-internal", b"").decode("latin-1")
        if not token or not hmac.compare_digest(token, given):
            return await refuse(send, 404, "not found")
        try:
            body = await Request(scope, receive).json()
        except Exception:
            return await JSONResponse({"error": "the body must be JSON"}, status_code=400)(scope, receive, send)

        def run():
            with platform._connect() as db:
                if name == "seo":
                    return youtube.seo(db, str(body["video_id"]))
                if name == "youtube-sync":
                    return youtube.sync_stats(db, str(body["access_token"]))
                if name == "youtube-upload":
                    upload_id, access = int(body["upload_id"]), str(body["access_token"])

                    def work():
                        try:
                            with platform._connect() as conn:
                                youtube.upload(conn, upload_id, access, platform.out_dir, platform.watermark or None)
                        except Exception as e:
                            print(f"youtube upload {upload_id} failed: {e}", flush=True)
                    threading.Thread(target=work, daemon=True).start()
                    return {"started": True}
            raise KeyError(name)

        try:
            result = await anyio.to_thread.run_sync(run)
        except KeyError:
            return await refuse(send, 404, "not found")
        except Exception as e:
            return await JSONResponse({"error": str(e)[:500]}, status_code=502)(scope, receive, send)
        return await JSONResponse(result)(scope, receive, send)

    return gated


def load_env(path: Path) -> None:
    """Read KEY=value lines into the environment. Values already set win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value:
            os.environ.setdefault(key.strip(), value)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings

    # The site and this server share one settings file, platform/.env.
    home = Path(os.environ.get("CEVG_PLATFORM_DIR") or Path(__file__).resolve().parents[2] / "platform")
    load_env(home / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set; see platform/README.md")
    platform = Platform(
        database_url,
        home / os.environ.get("CEVG_STORAGE", "storage"),  # a relative path is taken from the platform folder
        os.environ.get("SITE_URL", "http://localhost:3000"),
        cevg=os.environ.get("CEVG_BIN"),
        watermark=os.environ.get("CEVG_WATERMARK", "Vivaran"),
        daily_voice_minutes=float(os.environ.get("CEVG_DAILY_VOICE_MINUTES", "10")),
        max_minutes=float(os.environ.get("CEVG_MAX_MINUTES", "20")),
    )
    # The gate checks the token on every request, and the server sits behind the
    # site's proxy or a tunnel, so any host name is accepted here.
    security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    app = build(platform).streamable_http_app(streamable_http_path="/mcp", stateless_http=True, json_response=True,
                                               transport_security=security, host=host)
    print(f"CEVG platform MCP server on http://{host}:{port}\n"
          f"  connector addresses look like: <public address>/u/<token>/mcp\n"
          f"  storage: {platform.out_dir.parent}\n"
          f"  voice: {_voice_line()}",
          flush=True)
    uvicorn.run(gate(app, platform), host=host, port=port, log_level="warning")
