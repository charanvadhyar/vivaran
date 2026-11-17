"""Which voice service speaks the narration.

`CEVG_TTS` chooses: `gnani` (the default: Timbre speaks, Prisma listens
back) or `sarvam` (Bulbul v3, kept for anyone with a Sarvam key). Each
reads its key from its own environment variable and never writes it
anywhere.
"""

from __future__ import annotations

import os
from typing import Any

from . import gnani, sarvam
from .voice import GnaniVoice, SarvamVoice

# Both errors carry `.advice()`.
VoiceError = (gnani.GnaniError, sarvam.SarvamError)


class Gnani:
    name = "gnani"
    key_env = "GNANI_API_KEY"
    label = "Gnani Timbre"
    pace_range = (0.85, 1.15)

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or os.environ.get("GNANI_MODEL", "").strip() or gnani.DEFAULT_MODEL
        # A per-caller key (bring-your-own-key) overrides the server's env key when given.
        self._api_key = (api_key or "").strip() or None
        gnani.voices(self.model)  # an unknown model fails here, not mid-render

    def available(self) -> bool:
        return bool(self._api_key or os.environ.get(self.key_env, "").strip())

    def key(self) -> str:
        key = self._api_key or os.environ.get(self.key_env, "").strip()
        if not key:
            raise ValueError(
                "GNANI_API_KEY is not set. Make a key at app.gnani.ai/voice, then run\n"
                "    export GNANI_API_KEY=your-key        (Linux, macOS)\n"
                "    $env:GNANI_API_KEY = \"your-key\"      (Windows PowerShell)\n"
                "or add --dry-run to test the pipeline with stand-in audio and no key.")
        return key

    def speakers(self, language: str | None = None) -> list[str]:
        table = gnani.voices(self.model)
        if language is None:
            return list(table)
        return [v for v, (_, lang, _) in table.items() if lang in ("*", language)] or list(table)

    def default_speaker(self, language: str) -> str:
        return gnani.default_voice(self.model, language)

    def check(self, speaker: str | None, language: str, pace: float = 1.0) -> None:
        gnani.language_code(language)
        if speaker and speaker not in gnani.voices(self.model):
            raise ValueError(f"unknown voice `{speaker}`; {self.model} has: {', '.join(gnani.voices(self.model))}")
        low, high = self.pace_range
        if not low <= pace <= high:
            raise ValueError(f"pace {pace} is outside {low} to {high} for Gnani")

    def voice(self, speaker: str | None = None, pace: float = 1.0, **_) -> GnaniVoice:
        return GnaniVoice(gnani.Gnani(self.key()), voice=speaker or None, model=self.model, speed=pace)

    def describe(self) -> dict[str, Any]:
        table = gnani.voices(self.model)
        return {
            "service": f"{self.label} ({self.model})",
            "default": {lang: gnani.default_voice(self.model, lang) for lang in ("en", "te", "hi")},
            "voices": [{"name": n, "gender": g, "language": "any" if lang == "*" else lang, "suits": what}
                       for n, (g, lang, what) in table.items()],
            "languages": sorted(gnani.LANGUAGES),
            "pace": "0.85 (slow) to 1.15 (fast); 1.0 is normal",
            "note": "timbre-v2.5 voices each have a preferred language; pick one whose language matches the "
                    "video's. Use `voice_sample` to hear one before choosing.",
            "voice_available": self.available(),
        }


class Sarvam:
    name = "sarvam"
    key_env = "SARVAM_API_KEY"
    label = "Sarvam Bulbul v3"
    pace_range = (0.5, 2.0)

    def available(self) -> bool:
        return bool(os.environ.get(self.key_env, "").strip())

    def key(self) -> str:
        key = os.environ.get(self.key_env, "").strip()
        if not key:
            raise ValueError("SARVAM_API_KEY is not set. Get a key at dashboard.sarvam.ai, or add --dry-run.")
        return key

    def speakers(self, language: str | None = None) -> list[str]:
        return list(sarvam.SPEAKERS)

    def default_speaker(self, language: str) -> str:
        return sarvam.DEFAULT_SPEAKER

    def check(self, speaker: str | None, language: str, pace: float = 1.0) -> None:
        sarvam.language_code(language)
        if speaker and speaker not in sarvam.SPEAKERS:
            raise ValueError(f"unknown speaker `{speaker}`; choose one of: {', '.join(sarvam.SPEAKERS)}")
        if not 0.5 <= pace <= 2.0:
            raise ValueError(f"pace {pace} is outside 0.5 to 2.0")

    def voice(self, speaker: str | None = None, pace: float = 1.0, *, requests_per_minute: float = 30,
              temperature: float | None = None, preprocess: bool = False) -> SarvamVoice:
        client = sarvam.Sarvam(self.key(), requests_per_minute=requests_per_minute)
        return SarvamVoice(client, speaker=speaker or sarvam.DEFAULT_SPEAKER, pace=pace,
                           temperature=temperature, preprocess=preprocess)

    def describe(self) -> dict[str, Any]:
        return {
            "service": self.label,
            "default": {"en": sarvam.DEFAULT_SPEAKER},
            "voices": [{"name": n, "language": "any"} for n in sarvam.SPEAKERS],
            "languages": sorted(sarvam.LANGUAGES),
            "pace": "0.5 (slow) to 2.0 (fast); 1.0 is normal",
            "voice_available": self.available(),
        }


def current(name: str | None = None, api_key: str | None = None):
    """The provider named, else $CEVG_TTS, else Gnani.

    `api_key`, when given, is a per-caller key (bring-your-own-key) that overrides
    the server's env key for this provider instance. Only Gnani uses it today.
    """
    name = (name or os.environ.get("CEVG_TTS") or "gnani").strip().lower()
    if name == "gnani":
        return Gnani(api_key=api_key)
    if name == "sarvam":
        return Sarvam()
    raise ValueError(f"unknown voice service `{name}`; CEVG_TTS must be `gnani` or `sarvam`")
