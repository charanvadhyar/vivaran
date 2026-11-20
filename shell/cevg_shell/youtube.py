"""The Vivaran YouTube channel: SEO written by the Claude API, uploads, and view milestones.

The website owns the channel's OAuth: it keeps the refresh token (encrypted) and
hands this server a short-lived access token with each request, so the Google
client secret never needs to live here. This server owns the video files, so
it does the uploading.

Rewards follow the plans in the `settings` table: a creator's first video on the
channel, the friend who referred them, and each video passing 1,000 and 10,000
views on YouTube.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import credits, figures

API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
SUBJECT_NAMES = {"dsa": "Data structures and algorithms", "ml": "Machine learning", "dbms": "Databases",
                 "os": "Operating systems", "coa": "Computer architecture", "networks": "Computer networks",
                 "maths": "Mathematics", "other": "Computer science"}
LANGUAGES = {"en": "English", "te": "Telugu (code-mixed with English)", "hi": "Hindi (code-mixed with English)"}

SEO_SYSTEM = """\
You write YouTube metadata for Vivaran, a channel of step-by-step animated explanations of computer
science and mathematics for Indian university and GATE students. Be accurate to the video: never
promise anything the narration does not cover. Reply with one JSON object and nothing else:
{"title": "...", "description": "...", "tags": ["...", ...]}

- title: at most 95 characters. The topic first, the way students search it ("Banker's Algorithm: Safe
  Sequence Step by Step"), plus one concrete hook from the video. No clickbait, no ALL CAPS, no emoji.
- description: 900-1800 characters. First two lines: what the student will be able to do after
  watching. Then a short list of what is covered, in order. Then the chapters exactly as given, one per
  line ("0:00 Title"). Then the credit line exactly as given. Then 3-5 hashtags on the last line.
- tags: 10-20 search phrases, together under 450 characters: the topic, its synonyms, the course
  (e.g. COA, DBMS), GATE and university exam terms, and the language if it is not English.
"""


class YouTubeError(Exception):
    pass


def _google(method: str, url: str, token: str, body: dict | None = None, data: bytes | None = None,
            headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    h = {"Authorization": f"Bearer {token}", **(headers or {})}
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json; charset=UTF-8"
    request = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(request, timeout=600) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise YouTubeError(f"YouTube said {e.code}: {detail}") from None


def _chapters(video: dict[str, Any]) -> list[str]:
    """Chapters from the estimated outline, scaled to the real length."""
    outline = video.get("outline") or []
    if isinstance(outline, str):
        outline = json.loads(outline)
    total_est = sum(float(o.get("seconds") or 0) for o in outline) or 1.0
    scale = float(video.get("seconds") or total_est) / total_est
    out, at = [], 0.0
    for o in outline:
        title = (o.get("opens_with") or o.get("scene") or "").strip()
        title = re.split(r"(?<=[.?!])\s", title)[0][:60].rstrip(".") or str(o.get("scene"))
        out.append(f"{int(at // 60)}:{int(at % 60):02d} {title}")
        at += float(o.get("seconds") or 0) * scale
    # YouTube shows chapters only with at least three, each at least ten seconds long.
    return out if len(out) >= 3 else []


def seo(db, video_id: str, model: str | None = None) -> dict[str, Any]:
    """Title, description and tags for a video, written by the Claude API."""
    v = db.execute("select v.id, v.title, v.language, v.subject, v.seconds, v.outline, v.script, u.name, u.handle "
                   "from videos v join users u on u.id = v.user_id where v.id = %s", (video_id,)).fetchone()
    if v is None:
        raise YouTubeError("no such video")
    script = v["script"] if isinstance(v["script"], dict) else json.loads(v["script"])
    lang = v["language"] or "en"
    lines = [str(step.get("say", {}).get(lang) or step.get("say", {}).get("en") or "")
             for scene in script.get("scenes", []) for step in scene.get("steps", [])]
    narration = " ".join(lines)[:12000]
    site = os.environ.get("SITE_URL", "https://vivaran.tech").rstrip("/")
    credit = f"Made by {v['name']} (@{v['handle']}) with Vivaran: {site}/v/{v['id']}"
    prompt = (f"Video title from the creator: {v['title']}\nSubject: {SUBJECT_NAMES.get(v['subject'] or '', 'Computer science')}\n"
              f"Narration language: {LANGUAGES.get(lang, lang)}\nLength: {round((v['seconds'] or 0) / 60, 1)} minutes\n"
              f"Chapters:\n" + "\n".join(_chapters(v)) + f"\nCredit line: {credit}\n\nFull narration:\n{narration}")
    key = figures._api_key()
    reply = figures._call([{"role": "user", "content": prompt}],
                          model or os.environ.get("CEVG_SEO_MODEL", os.environ.get("CEVG_FIGURE_MODEL", figures.DEFAULT_MODEL)),
                          key, max_tokens=3000, system=SEO_SYSTEM)
    m = re.search(r"\{.*\}", reply, flags=re.S)
    if not m:
        raise YouTubeError("the Claude API did not return the metadata")
    data = json.loads(m.group(0))
    title = str(data.get("title", v["title"]))[:100]
    description = str(data.get("description", ""))[:4900]
    if credit not in description:
        description = f"{description}\n\n{credit}"
    tags, used = [], 0
    for t in data.get("tags", []):
        t = str(t).strip()[:60]
        if t and used + len(t) + 1 <= 480:
            tags.append(t)
            used += len(t) + 1
    credits.event(db, "seo_ai", None, video_id)
    return {"title": title, "description": description, "tags": tags}


def _with_watermark(src: Path, text: str, font: str | None) -> Path:
    """The YouTube copy always carries the Vivaran mark; Pro renders are made without it."""
    out = Path(tempfile.mkdtemp(prefix="cevg-yt-")) / src.name
    safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
    draw = f"drawtext=text='{safe}':x=w-tw-28:y=h-th-24:fontsize=h/40:fontcolor=white@0.55"
    if font:
        draw += f":fontfile={font}"
    done = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", draw, "-c:a", "copy",
                           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", str(out)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise YouTubeError(f"could not add the watermark: {done.stderr.strip()[:300]}")
    return out


def upload(db, upload_id: int, token: str, out_dir: Path, watermark: str | None = "Vivaran") -> dict[str, Any]:
    """Upload one approved video to the channel, then give the rewards it earns."""
    row = db.execute("select y.*, v.subject, v.language, u.handle, vivaran_tier(v.user_id) as tier "
                     "from youtube_uploads y join videos v on v.id = y.video_id join users u on u.id = y.user_id "
                     "where y.id = %s", (upload_id,)).fetchone()
    if row is None:
        raise YouTubeError("no such upload")
    if row["status"] not in ("approved", "failed"):
        raise YouTubeError(f"upload is {row['status']}, not approved")
    db.execute("update youtube_uploads set status = 'uploading', error = null where id = %s", (upload_id,))
    try:
        src = out_dir / f"{row['video_id']}.mp4"
        if not src.is_file():
            raise YouTubeError("the video file is missing on the render server")
        path = src
        if row["tier"] == "pro" and watermark:  # Pro renders carry no mark; the channel copy does
            font = os.environ.get("CEVG_FONT_FILE") or next(
                (str(p) for p in (Path("/app/fonts/NotoSans-SemiBold.ttf"),) if p.is_file()), None)
            path = _with_watermark(src, f"{watermark} · {row['handle']}", font)
        lang = row["language"] or "en"
        meta = {"snippet": {"title": row["title"], "description": row["description"], "tags": list(row["tags"] or []),
                            "categoryId": "27", "defaultLanguage": lang, "defaultAudioLanguage": lang},
                "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                           "containsSyntheticMedia": True}}
        size = path.stat().st_size
        _, headers, _ = _google("POST", UPLOAD, token, body=meta,
                                headers={"X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"})
        location = headers.get("Location") or headers.get("location")
        if not location:
            raise YouTubeError("YouTube did not start the upload")
        _, _, body = _google("PUT", location, token, data=path.read_bytes(), headers={"Content-Type": "video/mp4"})
        video = json.loads(body)
        yt_id = video["id"]
        thumb = out_dir / f"{row['video_id']}.png"
        notes = []
        if thumb.is_file():
            try:
                _google("POST", f"{API}/thumbnails/set?videoId={yt_id}", token, data=thumb.read_bytes(),
                        headers={"Content-Type": "image/png"})
            except YouTubeError as e:
                notes.append(f"thumbnail not set ({e})")
        playlists = (db.execute("select value from settings where key = 'youtube_playlists'").fetchone() or {}).get("value") or {}
        if isinstance(playlists, str):
            playlists = json.loads(playlists)
        if row["subject"] in playlists:
            try:
                _google("POST", f"{API}/playlistItems?part=snippet", token, body={"snippet": {
                    "playlistId": playlists[row["subject"]], "resourceId": {"kind": "youtube#video", "videoId": yt_id}}})
            except YouTubeError as e:
                notes.append(f"not added to the playlist ({e})")
        privacy = video.get("status", {}).get("privacyStatus")
        db.execute("update youtube_uploads set status = 'published', youtube_id = %s, published_at = now(), "
                   "error = %s where id = %s", (yt_id, "; ".join(notes) or None, upload_id))
        credits.event(db, "youtube_published", row["user_id"], row["video_id"], youtube_id=yt_id, privacy=privacy)
        reward_first_publish(db, row["user_id"])
        return {"youtube_id": yt_id, "privacy": privacy, "notes": notes}
    except Exception as e:
        db.execute("update youtube_uploads set status = 'failed', error = %s where id = %s", (str(e)[:1000], upload_id))
        credits.event(db, "youtube_failed", row["user_id"], row["video_id"], error=str(e)[:300])
        raise


def _grant(db, user_id, kind: str, amount: float, video_id: str | None = None, note: str | None = None) -> bool:
    if amount <= 0:
        return False
    done = db.execute("insert into credit_ledger (user_id, bucket, delta, kind, video_id, note) "
                      "values (%s, 'bonus', %s, %s, %s, %s) on conflict do nothing returning id",
                      (user_id, amount, kind, video_id, note)).fetchone()
    if done:
        credits.event(db, f"reward_{kind}", str(user_id), video_id, credits=amount)
    return bool(done)


def reward_first_publish(db, user_id) -> None:
    """A creator's first video on the channel: a credit for them, and one for the friend who invited them."""
    r = credits.plans(db)["rewards"]
    if _grant(db, user_id, "first_publish", float(r.get("first_publish", 0))):
        ref = db.execute("select referred_by from users where id = %s", (user_id,)).fetchone()
        if ref and ref["referred_by"]:
            _grant(db, ref["referred_by"], "referral", float(r.get("referral", 0)), note=str(user_id))


def sync_stats(db, token: str) -> dict[str, Any]:
    """Fetch views for every published video and give the view-milestone rewards."""
    rows = db.execute("select id, user_id, video_id, youtube_id from youtube_uploads "
                      "where status = 'published' and youtube_id is not null").fetchall()
    r = credits.plans(db)["rewards"]
    updated, rewarded = 0, 0
    for i in range(0, len(rows), 50):
        chunk = rows[i:i + 50]
        ids = ",".join(x["youtube_id"] for x in chunk)
        _, _, body = _google("GET", f"{API}/videos?part=statistics&id={urllib.parse.quote(ids)}", token)
        stats = {item["id"]: item.get("statistics", {}) for item in json.loads(body).get("items", [])}
        for x in chunk:
            s = stats.get(x["youtube_id"])
            if not s:
                continue
            views, likes = int(s.get("viewCount", 0)), int(s.get("likeCount", 0))
            db.execute("update youtube_uploads set yt_views = %s, yt_likes = %s, stats_at = now() where id = %s",
                       (views, likes, x["id"]))
            updated += 1
            if views >= 1000:
                rewarded += _grant(db, x["user_id"], "views_1k", float(r.get("views_1k", 0)), x["video_id"])
            if views >= 10000:
                rewarded += _grant(db, x["user_id"], "views_10k", float(r.get("views_10k", 0)), x["video_id"])
    channel = {}
    try:
        _, _, body = _google("GET", f"{API}/channels?part=statistics,snippet&mine=true", token)
        items = json.loads(body).get("items", [])
        if items:
            st = items[0].get("statistics", {})
            channel = {"title": items[0]["snippet"]["title"], "subscribers": int(st.get("subscriberCount", 0)),
                       "views": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0))}
            db.execute("insert into settings (key, value, updated_at) values ('youtube_channel', %s::jsonb, now()) "
                       "on conflict (key) do update set value = excluded.value, updated_at = now()", (json.dumps(channel),))
    except YouTubeError:
        pass
    return {"videos_updated": updated, "rewards_given": rewarded, "channel": channel}
