"""From a scene script to a narrated video.

    script --> one WAV per step (Gnani Timbre or Sarvam, cached)
           --> optionally, listen back: Gnani Prisma transcribes each clip
               and it is scored against the line, to catch skipped words
           --> measure each WAV
           --> `cevg render --speech <lengths>`   (video timed to the audio)
           --> lay each WAV at its step's start on one audio track
           --> ffmpeg: video + track --> MP4, plus an .srt of the narration

The audio is made first and the video is timed to it, so a Telugu sentence
that runs longer than its English version simply gets a longer step.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

from .voice import Cache

RATE = 48000  # every clip is brought to 48 kHz mono 16-bit before assembly


class NarrateError(Exception):
    pass


@dataclass
class Result:
    video: Path
    captions: Path
    seconds: float
    steps: int
    characters: int
    spoken: int
    reused: int
    heard: list = None  # per step, when listened back: {"step", "match", "said", "heard"}

    def doubtful(self, below: float = 0.8) -> list:
        """Steps whose transcript matched less than `below` of the line."""
        return [h for h in (self.heard or []) if h.get("match") is not None and h["match"] < below]


def find_cevg(explicit: str | None = None) -> str:
    """The renderer binary: --cevg, then $CEVG_BIN, then PATH, then the build folder beside this package."""
    built = Path(__file__).resolve().parents[2] / "target" / "release" / "cevg"
    for candidate in (explicit, os.environ.get("CEVG_BIN"), shutil.which("cevg"), str(built)):
        if not candidate:
            continue
        # On Windows the program is `cevg.exe`; accept the name with or without the ending.
        for path in (Path(candidate), Path(str(candidate) + ".exe")):
            if path.is_file():
                return str(path)
    raise NarrateError(
        f"cannot find the `cevg` program (looked for {built} and {built}.exe); run `cargo build --release` "
        "in the folder that holds Cargo.toml, or pass --cevg with the path to the program"
    )


def narration(script_path: Path, language: str) -> list[str]:
    """Each step's line in `language`, in order across all scenes."""
    script = json.loads(Path(script_path).read_text(encoding="utf-8"))
    lines, missing = [], []
    for i, scene in enumerate(script.get("scenes", [])):
        for j, step in enumerate(scene.get("steps", [])):
            text = step.get("say", {}).get(language, "").strip()
            if not text:
                missing.append(f"scenes[{i}].steps[{j}]")
            lines.append(text)
    if missing:
        shown = ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else "")
        raise NarrateError(
            f"{len(missing)} of {len(lines)} steps have no `{language}` narration ({shown}); "
            f"add \"{language}\" beside \"en\" in each step's `say`"
        )
    return lines


def _run(command: list[str], what: str) -> subprocess.CompletedProcess:
    try:
        done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        raise NarrateError(f"cannot run `{command[0]}`; it must be installed and on the PATH") from None
    if done.returncode != 0:
        detail = (done.stdout.strip() + "\n" + done.stderr.strip()).strip()
        raise NarrateError(f"{what} failed:\n{detail}")
    return done


def _peak(clip: Path) -> int:
    """The loudest sample of a 16-bit WAV, from 0 to 32767."""
    import array
    with wave.open(str(clip), "rb") as w:
        samples = array.array("h", w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        samples.byteswap()
    return max((abs(v) for v in samples), default=0)


def _normalise(source: Path, target: Path) -> float:
    """Convert a clip to 48 kHz mono 16-bit WAV and return its length in seconds."""
    _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
          "-ac", "1", "-ar", str(RATE), "-c:a", "pcm_s16le", str(target)], f"converting {source.name}")
    with wave.open(str(target), "rb") as w:
        return w.getnframes() / RATE


def _stamp(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3_600_000:02}:{ms // 60_000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def narrate(script_path: Path, out: Path, voice, *, language: str = "en", cache_dir: Path = Path(".cevg-cache"),
            cevg: str | None = None, burn_captions: bool = False, watermark: str | None = None,
            listen: bool = False, progress=lambda message: None) -> Result:
    """Make `out` (an .mp4) from the script, narrated by `voice` in `language`."""
    script_path, out = Path(script_path), Path(out)
    binary = find_cevg(cevg)
    lines = narration(script_path, language)

    # Refuse a broken script before any voice credits are spent.
    check = subprocess.run([binary, "validate", str(script_path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check.returncode != 0:
        raise NarrateError(f"the script does not validate:\n{check.stdout.strip()}")

    cache = Cache(Path(cache_dir) / "voice")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cevg-") as tmp:
        tmp = Path(tmp)

        # 1. Speak and measure.
        clips, lengths, heard = [], [], []
        for i, line in enumerate(lines):
            progress(f"voice {i + 1}/{len(lines)}")
            raw = cache.get(voice, line, language)
            clip = tmp / f"step{i:04}.wav"
            lengths.append(_normalise(raw, clip))
            # A silent or empty clip means the voice service answered with
            # nothing usable. Stop at once, before paying for more lines,
            # and do not keep the bad clip in the cache.
            if lengths[-1] < 0.2 or _peak(clip) < 300:
                raw.unlink(missing_ok=True)
                raise NarrateError(
                    f"the voice for step {i + 1} came back silent or empty ({lengths[-1]:.2f} s); stopped before "
                    f"speaking the remaining {len(lines) - i - 1} lines. The line was: {line}"
                )
            clips.append(clip)
            if listen and hasattr(voice, "listen"):
                progress(f"listening {i + 1}/{len(lines)}")
                heard.append(_listen(voice, raw, line, language, lengths[-1], i + 1))

        # 2. Render the picture to those lengths.
        progress("rendering video")
        silent = tmp / "silent.mp4"
        command = [binary, "render", str(script_path), "--speech", ",".join(f"{s:.3f}" for s in lengths),
                   "--json", "-o", str(silent)]
        if burn_captions:
            command += ["--captions", language]
        if watermark:
            command += ["--watermark", watermark]
        info = json.loads(_run(command, "rendering").stdout)
        starts, total = info["step_starts"], info["seconds"]

        # 3. One audio track, each clip at the moment its step begins.
        progress("assembling audio")
        track = bytearray()
        for clip, start in zip(clips, starts):
            at = round(start * RATE) * 2  # two bytes per sample
            if len(track) < at:
                track.extend(bytes(at - len(track)))
            with wave.open(str(clip), "rb") as w:
                track.extend(w.readframes(w.getnframes()))
        end = round(total * RATE) * 2
        if len(track) < end:
            track.extend(bytes(end - len(track)))
        track_path = tmp / "narration.wav"
        with wave.open(str(track_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(bytes(track))

        # 4. Put them together. The picture is copied, not re-encoded.
        progress("muxing")
        _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent), "-i", str(track_path),
              "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)], "muxing")

    # 5. Captions, timed to the steps.
    captions = out.with_suffix(".srt")
    blocks = []
    for i, (line, start) in enumerate(zip(lines, starts)):
        finish = starts[i + 1] if i + 1 < len(starts) else total
        blocks.append(f"{i + 1}\n{_stamp(start)} --> {_stamp(finish)}\n{line}\n")
    captions.write_text("\n".join(blocks), encoding="utf-8")

    return Result(video=out, captions=captions, seconds=total, steps=len(lines),
                  characters=sum(len(line) for line in lines), spoken=cache.spoken, reused=cache.reused,
                  heard=heard if listen else None)


def _listen(voice, clip: Path, line: str, language: str, seconds: float, step: int) -> dict:
    """Transcribe one cached clip and score it, keeping the answer beside the
    clip so a re-run does not pay to listen again."""
    record = Path(clip).with_suffix(".heard.json")
    if record.exists():
        return {"step": step, **json.loads(record.read_text(encoding="utf-8"))}
    if seconds > 29.5:  # Prisma takes at most 30 seconds
        return {"step": step, "match": None, "said": line, "heard": "", "note": "longer than 30 s; not checked"}
    score, transcript = voice.listen(Path(clip).read_bytes(), line, language)
    entry = {"match": round(score, 3), "said": line, "heard": transcript}
    record.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
    return {"step": step, **entry}
