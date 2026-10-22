"""The CEVG MCP server: lets an assistant write a scene script and get a video.

One server, two ways to reach it:

- stdio, for an app on the same computer (Claude Desktop, Claude Code);
- streamable HTTP, for apps that only reach servers over the internet
  (ChatGPT, claude.ai). The address then carries a secret, because whoever
  has it can spend the Sarvam credits of the key this server runs with.

The tools follow the order an assistant should work in: read the guide,
write a script, validate it, look at a few frames, then render. Rendering
takes minutes, so it runs as a job that is started and then asked about.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver import Image
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import sarvam
from .narrate import NarrateError, find_cevg, narrate
from .voice import Cache, SarvamVoice

CHARS_PER_SECOND = 16.0  # Bulbul v3 at pace 1, measured on the binary search example
HOLD = 0.35  # the rest after each step, as in the renderer

INSTRUCTIONS = """\
CEVG turns an explanation of a computer science or mathematics topic into an
animated, narrated video. You write a scene script (JSON); CEVG draws it.

Before writing anything, agree the video with the user:
- Ask how long the video should be, in minutes, and in which language
  (English, or code-mixed Hindi or Telugu), unless they already said.
  Length is what the user pays for, so it is their choice.
- Ask which voice they want, unless they already said or the video is
  silent. Call `voices` and offer the list; offer `voice_sample` if they
  want to hear one first. If they have no preference, use the default.
  Use the same voice for the whole video.
- Show a short outline: the scenes you plan, one line each, with roughly
  how long each takes. Ask whether to go ahead. Change it if they ask.

Then work in this order:
1. Call `guide` once and read it. It is the only description of what can be
   drawn and how narration must be written. Do not guess the format.
2. Write the whole script. Follow the teaching standard in the guide: a
   student must be able to redo the working in an exam.
3. Call `validate`. Fix every error it reports and validate again.
4. Call `preview` on a few steps to see the picture. Fix what looks wrong.
5. Call `estimate`. If the length is not close to what the user chose, add
   or remove steps. Tell the user the estimated length and what the video
   contains, and wait for a yes before rendering with voice.
6. Call `render`, then call `status` with the job id until it is done. Give
   the user the video link or file path from `status`.
"""


@dataclass
class Job:
    id: str
    title: str
    state: str = "queued"  # queued, running, done, failed
    progress: str = "waiting for an earlier render to finish"
    started: float = field(default_factory=time.time)
    finished: float | None = None
    error: str | None = None
    result: dict[str, Any] = field(default_factory=dict)


class Studio:
    """Everything the tools need: the renderer, the output folder, the jobs."""

    def __init__(self, out_dir: Path, cache_dir: Path, cevg: str | None = None, public_base: str | None = None,
                 requests_per_minute: float = 30):
        self.cevg = find_cevg(cevg)
        self.out_dir = Path(out_dir).expanduser().resolve()
        self.cache_dir = Path(cache_dir).expanduser().resolve()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.public_base = public_base.rstrip("/") if public_base else None
        self.requests_per_minute = requests_per_minute
        self.jobs: dict[str, Job] = {}
        self._one_at_a_time = threading.Lock()

    # -- helpers ---------------------------------------------------------

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([self.cevg, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")

    @staticmethod
    def _write(script: dict[str, Any] | str, folder: Path) -> Path:
        """Put the script in a file. A script given as text must be JSON."""
        if isinstance(script, str):
            try:
                script = json.loads(script)
            except json.JSONDecodeError as e:
                raise ValueError(f"the script is not valid JSON: {e}") from None
        path = folder / "script.json"
        path.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
        return path

    def link(self, name: str) -> str | None:
        return f"{self.public_base}/videos/{name}" if self.public_base else None

    # -- the tools -------------------------------------------------------

    def guide(self) -> str:
        return self._run("guide").stdout

    def validate(self, script: dict[str, Any] | str) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="cevg-") as tmp:
            done = self._run("validate", str(self._write(script, Path(tmp))), "--json")
        try:
            return json.loads(done.stdout)
        except json.JSONDecodeError:
            return {"ok": False, "errors": 1, "diagnostics": [
                {"severity": "error", "path": "", "message": (done.stderr or done.stdout).strip()}]}

    def estimate(self, script: dict[str, Any] | str, language: str) -> dict[str, Any]:
        """How long the video will be and what is in it, without rendering."""
        if isinstance(script, str):
            script = json.loads(script)
        report = self.validate(script)
        if not report.get("ok"):
            raise ValueError("the script has errors; call `validate` and fix them first")
        outline, total, characters, missing = [], 0.0, 0, 0
        for scene in script.get("scenes", []):
            seconds = 0.0
            for step in scene.get("steps", []):
                line = str(step.get("say", {}).get(language, "")).strip()
                missing += not line
                characters += len(line)
                # Measured on Bulbul v3 at pace 1: about 16 characters a second, and never
                # shorter than the renderer's minimum; each step then rests for a moment.
                seconds += max(1.5, len(line) / CHARS_PER_SECOND) + HOLD
            first = next((str(st.get("say", {}).get(language, "")) for st in scene.get("steps", [])), "")
            outline.append({"scene": scene.get("id"), "steps": len(scene.get("steps", [])),
                            "seconds": round(seconds), "opens_with": first[:120]})
            total += seconds
        result: dict[str, Any] = {
            "title": script.get("title"), "language": language, "minutes": round(total / 60, 1),
            "seconds": round(total), "steps": sum(o["steps"] for o in outline),
            "characters_to_speak": characters, "outline": outline,
            "note": "an estimate from the length of the narration, usually within a fifth of the real length",
        }
        if missing:
            result["problem"] = f"{missing} steps have no `{language}` narration; add it before rendering"
        return result

    def preview(self, script: dict[str, Any] | str, scene: str | None, step: int | None, at: float,
                captions: str | None) -> bytes:
        with tempfile.TemporaryDirectory(prefix="cevg-") as tmp:
            tmp = Path(tmp)
            command = ["frame", str(self._write(script, tmp)), "--at", str(at), "-o", str(tmp / "frame.png")]
            if scene:
                command += ["--scene", scene]
            if step is not None:
                command += ["--step", str(step)]
            if captions:
                command += ["--captions", captions]
            done = self._run(*command)
            if done.returncode != 0:
                raise ValueError((done.stdout + "\n" + done.stderr).strip())
            return (tmp / "frame.png").read_bytes()

    def render(self, script: dict[str, Any] | str, language: str, voice: bool, captions: bool, speaker: str,
               pace: float) -> Job:
        report = self.validate(script)
        if not report.get("ok"):
            raise ValueError("the script has errors; call `validate`, fix them, then render:\n"
                             + json.dumps(report.get("diagnostics", []), ensure_ascii=False, indent=1))
        if voice:
            if not os.environ.get("SARVAM_API_KEY"):
                raise ValueError("this server has no SARVAM_API_KEY, so it cannot speak. Render with voice=false "
                                 "(a silent video with captions), or ask the owner to set the key and restart.")
            if speaker not in sarvam.SPEAKERS:
                raise ValueError(f"unknown speaker `{speaker}`; choose one of: {', '.join(sarvam.SPEAKERS)}")
            sarvam.language_code(language)  # raises with the list of languages

        job = Job(id=uuid.uuid4().hex[:12], title=str(report.get("summary", {}).get("title", "video")))
        self.jobs[job.id] = job
        folder = Path(tempfile.mkdtemp(prefix="cevg-job-"))
        path = self._write(script, folder)
        threading.Thread(target=self._work, args=(job, path, language, voice, captions, speaker, pace),
                         daemon=True).start()
        return job

    def _work(self, job: Job, script: Path, language: str, voice: bool, captions: bool, speaker: str,
              pace: float) -> None:
        with self._one_at_a_time:
            job.state, job.progress = "running", "starting"
            name = f"{job.id}.mp4"
            out = self.out_dir / name

            def progress(message: str) -> None:
                job.progress = message

            try:
                if voice:
                    client = sarvam.Sarvam(os.environ["SARVAM_API_KEY"], requests_per_minute=self.requests_per_minute)
                    result = narrate(script, out, SarvamVoice(client, speaker=speaker, pace=pace), language=language,
                                     cache_dir=self.cache_dir, cevg=self.cevg, burn_captions=captions,
                                     progress=progress)
                    job.result = {"seconds": round(result.seconds, 1), "steps": result.steps,
                                  "characters_spoken": result.characters if result.spoken else 0,
                                  "lines_from_cache": result.reused}
                else:
                    job.progress = "rendering video"
                    command = ["render", str(script), "--json", "-o", str(out)]
                    if captions:
                        command += ["--captions", language]
                    done = self._run(*command)
                    if done.returncode != 0:
                        raise NarrateError((done.stdout + "\n" + done.stderr).strip())
                    info = json.loads(done.stdout)
                    job.result = {"seconds": round(info["seconds"], 1), "steps": len(info["step_starts"])}
                job.result["file"] = str(out)
                if self.link(name):
                    job.result["url"] = self.link(name)
                job.state, job.progress = "done", "finished"
            except sarvam.SarvamError as e:
                job.state, job.error = "failed", f"{e}\n{e.advice()}"
            except Exception as e:  # a job must always end in a state the assistant can read
                job.state, job.error = "failed", str(e)
            finally:
                job.finished = time.time()

    def voices(self) -> dict[str, Any]:
        female = [v for v in sarvam.SPEAKERS if v in FEMALE_NAMES]
        male = [v for v in sarvam.SPEAKERS if v not in FEMALE_NAMES]
        return {
            "default": sarvam.DEFAULT_SPEAKER,
            "female_sounding_names": female,
            "male_sounding_names": male,
            "languages": sorted(sarvam.LANGUAGES),
            "pace": "0.5 (slow) to 2.0 (fast); 1.0 is normal",
            "note": "The grouping is read off the names; Sarvam does not describe the voices. "
                    "Use `voice_sample` to hear one before choosing.",
            "voice_available": bool(os.environ.get("SARVAM_API_KEY")),
        }

    def voice_sample(self, speaker: str, language: str, pace: float) -> dict[str, Any]:
        if not os.environ.get("SARVAM_API_KEY"):
            raise ValueError("this server has no SARVAM_API_KEY, so it cannot make a sample")
        if speaker not in sarvam.SPEAKERS:
            raise ValueError(f"unknown speaker `{speaker}`; choose one of: {', '.join(sarvam.SPEAKERS)}")
        sarvam.language_code(language)
        text = SAMPLE_LINES.get(language, SAMPLE_LINES["en"])
        client = sarvam.Sarvam(os.environ["SARVAM_API_KEY"], requests_per_minute=self.requests_per_minute)
        cache = Cache(self.cache_dir / "voice")
        clip = cache.get(SarvamVoice(client, speaker=speaker, pace=pace), text, language)
        name = f"voice-{speaker}-{language}-{pace:g}.wav"
        (self.out_dir / name).write_bytes(Path(clip).read_bytes())
        result: dict[str, Any] = {"speaker": speaker, "language": language, "said": text,
                                  "file": str(self.out_dir / name)}
        if self.link(name):
            result["url"] = self.link(name)
        return result

    def status(self, job_id: str) -> dict[str, Any]:
        job = self.jobs.get(job_id)
        if job is None:
            return {"state": "unknown", "error": f"there is no job `{job_id}`; jobs are forgotten when the server restarts"}
        report: dict[str, Any] = {"job": job.id, "title": job.title, "state": job.state, "progress": job.progress,
                                  "elapsed_seconds": round((job.finished or time.time()) - job.started)}
        if job.state == "done":
            report.update(job.result)
        elif job.state == "failed":
            report["error"] = job.error
        else:
            report["advice"] = "still working; ask again in about 20 seconds"
        return report


# Hints for the app: tools marked read-only change nothing and cost nothing, so an
# app may run them without asking the user each time.
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
MAKES_FILES = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=True)

# Sarvam does not publish a description of each voice. This grouping is read off the
# names and is only a starting point; `voice_sample` lets the user hear one.
FEMALE_NAMES = "ritu priya neha pooja simran kavya ishita shreya roopa tanya shruti suhani kavitha rupali".split()

SAMPLE_LINES = {
    "en": "Hello. This is how I will explain your topic, one step at a time.",
    "hi": "नमस्ते। मैं आपका topic इसी तरह, step by step explain करूँगा।",
    "te": "నమస్తే. నేను మీ topic ను ఇలాగే, step by step explain చేస్తాను.",
}


def build(studio: Studio) -> MCPServer:
    """The MCP server with its eight tools."""
    server = MCPServer("cevg", title="CEVG: explanation videos for CS and maths", instructions=INSTRUCTIONS)

    @server.tool(title="Read the authoring guide", annotations=READ_ONLY)
    def guide() -> str:
        """The reference for writing a CEVG scene script: what can be drawn, how parts are named, every
        action, how to plan scenes, the teaching standard, and how to write narration (including the
        code-mixed style for Hindi and Telugu). Call this once before writing a script."""
        return studio.guide()

    @server.tool(title="Check a scene script", annotations=READ_ONLY)
    def validate(script: dict[str, Any]) -> dict[str, Any]:
        """Check a scene script without drawing it. Returns `ok`, and `diagnostics` with the exact path of
        every problem (for example `scenes[0].steps[1].do[0]`) and how to fix it. Costs nothing; call it
        after every change."""
        return studio.validate(script)

    @server.tool(title="Look at one frame", annotations=READ_ONLY)
    def preview(script: dict[str, Any], scene: str | None = None, step: int | None = None, at: float = 1.0,
                captions: str | None = None) -> Image:
        """Draw one moment of the video as a picture, to check the layout by eye before rendering.
        `scene` is a scene id (default: the last scene); `step` counts from 0 within the scene (default: its
        last step); `at` is how far through the step, 0 to 1 (default 1, the step finished); `captions` is a
        language code such as `en` or `te` to show that narration under the picture."""
        try:
            return Image(data=studio.preview(script, scene, step, at, captions), format="png")
        except (ValueError, NarrateError) as e:
            raise ToolError(str(e)) from None

    @server.tool(title="Estimate length and contents", annotations=READ_ONLY)
    def estimate(script: dict[str, Any], language: str = "en") -> dict[str, Any]:
        """How long the video will be, in minutes, and an outline of its scenes with the time each takes,
        worked out from the narration without rendering. Costs nothing. Use it to bring the script to the
        length the user chose, and to tell the user what the video will contain before `render`."""
        try:
            return studio.estimate(script, language)
        except ValueError as e:
            raise ToolError(str(e)) from None

    @server.tool(title="List the narration voices", annotations=READ_ONLY)
    def voices() -> dict[str, Any]:
        """The voices a video can be narrated in (Sarvam Bulbul v3) and the languages they speak. Every
        voice speaks every language. Show this to the user and let them choose; use `voice_sample` if they
        want to hear one first. Pass the chosen name as `speaker` to `render`."""
        return studio.voices()

    @server.tool(title="Hear a voice", annotations=MAKES_FILES)
    def voice_sample(speaker: str, language: str = "en", pace: float = 1.0) -> dict[str, Any]:
        """Make a short audio sample of one voice in one language so the user can hear it before choosing.
        Returns `file` (and `url` when the server is reachable over the internet). Costs a few Sarvam
        credits the first time for each voice and language; after that it is reused."""
        try:
            return studio.voice_sample(speaker, language, pace)
        except sarvam.SarvamError as e:
            raise ToolError(f"{e}\n{e.advice()}") from None
        except (ValueError, NarrateError) as e:
            raise ToolError(str(e)) from None

    @server.tool(title="Start rendering the video", annotations=MAKES_FILES)
    def render(script: dict[str, Any], language: str = "en", voice: bool = True, captions: bool = False,
               speaker: str = sarvam.DEFAULT_SPEAKER, pace: float = 1.0) -> dict[str, Any]:
        """Start making the video and return a job id at once; then call `status` until it is done.
        `language` picks which narration in each step's `say` is spoken (`en`, `hi`, `te`, ...); every step
        must have it. `voice=false` makes a silent video timed from the text. `captions=true` shows the
        narration under the picture. `speaker` is a Sarvam Bulbul v3 voice and `pace` is 0.5 to 2.0.
        Speech costs the server owner credits per character, so validate and preview first, and do not
        render the same script twice without a reason."""
        try:
            job = studio.render(script, language, voice, captions, speaker, pace)
        except (ValueError, NarrateError) as e:
            raise ToolError(str(e)) from None
        return {"job": job.id, "state": job.state, "advice": "call `status` with this job id in about 20 seconds"}

    @server.tool(title="Ask how a render is going", annotations=READ_ONLY)
    def status(job: str) -> dict[str, Any]:
        """The state of a render job: `queued`, `running` (with what it is doing), `done` or `failed`.
        When done it gives `url` (a link to the video, if the server is reachable over the internet) and
        `file` (the path on the server's computer), the length in seconds and the characters spoken."""
        return studio.status(job)

    return server


def serve_stdio(studio: Studio) -> None:
    build(studio).run("stdio")


def serve_http(out_dir: Path, cache_dir: Path, *, cevg: str | None, host: str, port: int, public_url: str | None,
               secret: str | None, requests_per_minute: float) -> None:
    """Serve over streamable HTTP at /<secret>/mcp, and the videos at /<secret>/videos/<name>."""
    import anyio
    from mcp.server.transport_security import TransportSecuritySettings
    from starlette.responses import FileResponse, PlainTextResponse
    from urllib.parse import urlparse

    secret = secret or os.environ.get("CEVG_SECRET") or secrets.token_urlsafe(18)
    local = f"http://{host}:{port}"
    base = (public_url.rstrip("/") if public_url else local) + f"/{secret}"
    studio = Studio(out_dir, cache_dir, cevg, public_base=base, requests_per_minute=requests_per_minute)
    server = build(studio)

    @server.custom_route(f"/{secret}/videos/{{name}}", methods=["GET"])
    async def video(request):
        name = request.path_params["name"]
        path = studio.out_dir / name
        # Only files this server made: a plain name ending in .mp4, inside the output folder.
        if Path(name).name != name or path.suffix not in (".mp4", ".wav") or not path.is_file():
            return PlainTextResponse("no such video", status_code=404)
        return FileResponse(path, media_type="video/mp4" if path.suffix == ".mp4" else "audio/wav")

    hosts = [f"{host}:{port}", f"localhost:{port}", f"127.0.0.1:{port}"]
    origins = [local, f"http://localhost:{port}"]
    if public_url:
        public = urlparse(public_url)
        hosts += [public.netloc, public.hostname or ""]
        origins.append(f"{public.scheme}://{public.netloc}")
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts,
                                         allowed_origins=origins + ["https://chatgpt.com", "https://claude.ai"])

    print(f"CEVG MCP server\n  connector address: {base}/mcp\n  videos are kept in: {studio.out_dir}\n"
          f"  voice: {'Sarvam key found' if os.environ.get('SARVAM_API_KEY') else 'NO SARVAM_API_KEY, silent videos only'}\n"
          "Treat the connector address like a password: anyone who has it can spend your Sarvam credits.",
          flush=True)
    anyio.run(lambda: server.run_streamable_http_async(host=host, port=port, streamable_http_path=f"/{secret}/mcp",
                                                       transport_security=security))
