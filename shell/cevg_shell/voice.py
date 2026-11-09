"""Voices: something that turns one narration line into one WAV file.

`GnaniVoice` (Timbre) is the default; `SarvamVoice` is kept for anyone with
a Sarvam key. `StandInVoice` needs no key and no network:
it makes a quiet tick followed by silence of about the right length, so the
whole pipeline (timing, track assembly, muxing, captions) can be run and
checked before any credits are spent.

Every line is cached on disk under a name built from everything that affects
the sound. Re-running after editing one sentence speaks one sentence.
"""

from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from pathlib import Path

from . import gnani, sarvam


class GnaniVoice:
    def __init__(self, client: gnani.Gnani, *, voice: str | None = None, model: str = gnani.DEFAULT_MODEL,
                 speed: float = 1.0):
        self.client, self.voice, self.model, self.speed = client, voice, model, speed

    def identity(self) -> str:
        return f"gnani|{self.model}|{self.voice or 'default'}|{self.speed}|text{gnani.TEXT_VERSION}"

    def speak(self, text: str, language: str) -> bytes:
        return self.client.speak(text, language, voice=self.voice, model=self.model, speed=self.speed)

    def listen(self, wav: bytes, text: str, language: str) -> tuple[float, str]:
        """Have Prisma transcribe a clip and score it against the line."""
        heard = self.client.transcribe(wav, language, keyterms=gnani.keyterms(text))
        return gnani.match(text, heard), heard


class SarvamVoice:
    def __init__(self, client: sarvam.Sarvam, *, speaker: str = sarvam.DEFAULT_SPEAKER, pace: float = 1.0,
                 temperature: float | None = None, preprocess: bool = False):
        self.client, self.speaker, self.pace = client, speaker, pace
        self.temperature, self.preprocess = temperature, preprocess

    def identity(self) -> str:
        return f"sarvam|{sarvam.MODEL}|{self.speaker}|{self.pace}|{self.temperature}|{self.preprocess}"

    def speak(self, text: str, language: str) -> bytes:
        return self.client.speak(text, language, speaker=self.speaker, pace=self.pace,
                                 temperature=self.temperature, preprocess=self.preprocess)


class StandInVoice:
    """No speech: a short tick at the start, then silence, as long as the
    sentence would roughly take to say (2.6 words a second)."""

    RATE = 48000

    def identity(self) -> str:
        return "stand-in|v1"

    def speak(self, text: str, language: str) -> bytes:
        seconds = max(1.5, len(text.split()) / 2.6)
        frames = bytearray()
        for i in range(int(seconds * self.RATE)):
            t = i / self.RATE
            # A 60 ms tick at 880 Hz that fades out, so sync can be heard.
            level = 0.25 * math.sin(2 * math.pi * 880 * t) * max(0.0, 1 - t / 0.06) if t < 0.06 else 0.0
            frames += struct.pack("<h", int(level * 32767))
        return _wav_bytes(bytes(frames), self.RATE)


def _wav_bytes(pcm: bytes, rate: int) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return out.getvalue()


class Cache:
    """WAV files on disk, one per (voice, language, text)."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.spoken = 0  # lines that had to be synthesised this run
        self.reused = 0  # lines served from disk

    def path(self, voice, text: str, language: str) -> Path:
        key = hashlib.sha256(f"{voice.identity()}|{language}|{text}".encode("utf-8")).hexdigest()[:24]
        return self.folder / f"{language}-{key}.wav"

    def get(self, voice, text: str, language: str) -> Path:
        path = self.path(voice, text, language)
        if path.exists() and path.stat().st_size > 44:
            self.reused += 1
            return path
        audio = voice.speak(text, language)
        # Write to a temporary name first, so an interrupted run never leaves
        # a half-written file that a later run would trust.
        partial = path.with_suffix(".part")
        partial.write_bytes(audio)
        partial.replace(path)
        self.spoken += 1
        return path
