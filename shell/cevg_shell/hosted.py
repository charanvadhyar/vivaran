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
    CEVG_WATERMARK      text in the corner of every video (default "Vivaran")
    CEVG_DAILY_VOICE_MINUTES   voiced minutes one user may render per day (default 10)
    CEVG_MAX_MINUTES    longest single video, in minutes (default 12)
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

from . import providers
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
"""


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
        self._users: dict[str, tuple[float, dict[str, Any] | None]] = {}
        # A render that was cut off by a restart can never finish; say so.
        self._execute("update videos set status = 'failed', error = 'the server restarted during this render; "
                      "render it again', finished_at = now() where status in ('queued', 'running')")

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
        user = self._one("select id::text as id, name, handle from users where connector_token = %s", (token,))
        if len(self._users) > 10_000:
            self._users.clear()
        self._users[token] = (time.time(), user)
        return user

    # -- limits ----------------------------------------------------------

    def _check_limits(self, user_id: str, seconds: float, voiced: bool) -> None:
        if seconds > self.max_seconds:
            raise Limit(f"this video would be about {seconds / 60:.1f} minutes; the longest allowed is "
                        f"{self.max_seconds / 60:.0f} minutes. Shorten the script or split the topic in two.")
        busy = self._one("select count(*) as n from videos where user_id = %s and status in ('queued', 'running')",
                         (user_id,))
        if busy and busy["n"] >= 1:
            raise Limit("this account already has a video rendering; wait for it to finish (call `status`)")
        if voiced:
            used = self._one(
                "select coalesce(sum(seconds), 0) as s from videos where user_id = %s and voiced "
                "and status = 'done' and created_at > now() - interval '24 hours'", (user_id,))
            left = self.daily_voice_seconds - float(used["s"] if used else 0)
            if seconds > left:
                raise Limit(f"this account has {max(left, 0) / 60:.1f} voiced minutes left today and this video "
                            f"needs about {seconds / 60:.1f}. Render it with voice=false (silent, with captions), "
                            "make it shorter, or try again tomorrow.")

    # -- rendering -------------------------------------------------------

    def start(self, user: dict[str, Any], script: dict[str, Any], language: str, voice: bool, captions: bool,
              speaker: str, pace: float, subject: str | None = None) -> dict[str, Any]:
        if subject is not None and subject not in SUBJECTS:
            raise ValueError(f"unknown subject `{subject}`; choose one of: {', '.join(SUBJECTS)}")
        estimate = self.estimate(script, language)  # validates too
        if "problem" in estimate:
            raise ValueError(estimate["problem"])
        if voice:
            provider = providers.current()
            if not provider.available():
                raise ValueError("voice is not available on this server right now; render with voice=false")
            provider.check(speaker or None, language, pace)
            speaker = speaker or provider.default_speaker(language)
        self._check_limits(user["id"], estimate["seconds"], voice)

        video_id = uuid.uuid4().hex[:12]
        self._execute(
            "insert into videos (id, user_id, title, language, speaker, voiced, captions, status, progress, script, "
            "outline, steps, subject) values (%s, %s, %s, %s, %s, %s, %s, 'queued', %s, %s, %s, %s, %s)",
            (video_id, user["id"], str(script.get("title") or "Untitled")[:200], language, speaker if voice else None,
             voice, captions, "waiting for an earlier render to finish", Jsonb(script), Jsonb(estimate["outline"]),
             estimate["steps"], subject))
        folder = Path(tempfile.mkdtemp(prefix="cevg-job-"))
        path = self._write(script, folder)
        threading.Thread(target=self._render, args=(video_id, user, path, language, voice, captions, speaker, pace),
                         daemon=True).start()
        return {"job": video_id, "state": "queued", "estimated_minutes": estimate["minutes"],
                "advice": "call `status` with this job id in about 20 seconds"}

    def _render(self, video_id: str, user: dict[str, Any], script: Path, language: str, voice: bool, captions: bool,
                speaker: str, pace: float) -> None:
        def progress(message: str) -> None:
            self._execute("update videos set progress = %s where id = %s", (message, video_id))

        with self._one_at_a_time:
            self._execute("update videos set status = 'running', progress = 'starting' where id = %s", (video_id,))
            out = self.out_dir / f"{video_id}.mp4"
            mark = f"{self.watermark} · {user['handle']}" if self.watermark else None
            try:
                characters = 0
                note = "finished"
                if voice:
                    voice_obj = self._voice(speaker, pace)
                    result = narrate(script, out, voice_obj, language=language,
                                     cache_dir=self.cache_dir, cevg=self.cevg, burn_captions=captions, watermark=mark,
                                     listen=hasattr(voice_obj, "listen"), progress=progress)
                    seconds, characters = result.seconds, result.characters
                    doubtful = result.doubtful()
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
            except providers.VoiceError as e:
                self._fail(video_id, f"{e}\n{e.advice()}")
            except Exception as e:  # a job must always end in a state the assistant can read
                self._fail(video_id, str(e))

    def _fail(self, video_id: str, error: str) -> None:
        self._execute("update videos set status = 'failed', error = %s, finished_at = now() where id = %s",
                      (error[:2000], video_id))

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
        user = platform._one("select id::text as id, name, handle from users where id::text = %s", (user_id,)) \
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

    @server.tool(title="Estimate length and contents", annotations=READ_ONLY)
    def estimate(script: dict[str, Any], language: str = "en") -> dict[str, Any]:
        """How long the video will be, in minutes, and an outline of its scenes with the time each takes,
        without rendering. Use it to bring the script to the length the user chose, and to tell the user
        what the video will contain before `render`."""
        return guarded(lambda: platform.estimate(script, language))

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

    @server.tool(title="Start rendering the video", annotations=MAKES_FILES)
    def render(ctx: Context, script: dict[str, Any], language: str = "en", voice: bool = True,
               captions: bool = False, speaker: str = "", pace: float = 1.0,
               subject: str | None = None) -> dict[str, Any]:
        """Start making the video and return a job id at once; then call `status` until it is done.
        `subject` files the video on the site: dsa (data structures and algorithms), ml, dbms, os, coa
        (computer architecture), networks, maths or other.
        The video is saved, private, in the user's account. `language` picks which narration in each
        step's `say` is spoken; every step must have it. `voice=false` makes a silent video timed from the
        text. `captions=true` shows the narration under the picture. Each account has a daily allowance of
        voiced minutes, so validate, preview and estimate first."""
        user = who(ctx)
        return guarded(lambda: platform.start(user, script, language, voice, captions, speaker, pace, subject))

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
        if len(parts) != 3 or parts[0] != "u" or parts[2] != "mcp":
            return await refuse(send, 404, "not found")
        import anyio
        user = await anyio.to_thread.run_sync(platform.user_for_token, parts[1])
        if user is None:
            return await refuse(send, 401, "this connector address is not valid; copy a fresh one from the site")
        headers = [(k, v) for k, v in scope["headers"] if k.lower() != USER_HEADER.encode()]
        headers.append((USER_HEADER.encode(), user["id"].encode()))
        return await app({**scope, "path": "/mcp", "raw_path": b"/mcp", "headers": headers}, receive, send)

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
        max_minutes=float(os.environ.get("CEVG_MAX_MINUTES", "12")),
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
