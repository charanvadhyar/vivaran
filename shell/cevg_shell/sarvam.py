"""Sarvam text-to-speech (Bulbul), as documented at
https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert

One call turns one piece of text into one WAV file. The API returns audio
only: no duration and no word timings, so callers measure the audio.

Facts this module relies on, read from the Sarvam docs on 1 October 2026:

* POST https://api.sarvam.ai/text-to-speech, JSON body, key in the
  `api-subscription-key` header.
* `bulbul:v3` takes up to 2,500 characters per request, `pace` 0.5 to 2.0,
  `temperature` 0.01 to 2.0, sample rates up to 48000 Hz over REST. It has
  no pitch or loudness control and no SSML.
* The response is `{"request_id": ..., "audios": [<base64 WAV>, ...]}`.
* Errors are `{"error": {"message": ..., "code": ...}}`. A bad key is HTTP
  403 (not 401). 429 means either too many requests or no credits left;
  only the first is worth retrying. 500 and 503 are retried with backoff
  starting at 1 second, doubling, capped at 60.
* The Starter plan allows 30 requests a minute for bulbul:v3.
"""

from __future__ import annotations

import base64
import io
import json
import time
import urllib.error
import urllib.request
import wave

API_URL = "https://api.sarvam.ai/text-to-speech"
MODEL = "bulbul:v3"
MAX_CHARS = 2500

# Script language key -> Sarvam language code.
LANGUAGES = {
    "en": "en-IN", "hi": "hi-IN", "te": "te-IN", "ta": "ta-IN", "bn": "bn-IN", "gu": "gu-IN",
    "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "pa": "pa-IN", "od": "od-IN",
}

SPEAKERS = (
    "shubh aditya ritu priya neha rahul pooja rohan simran kavya amit dev ishita shreya ratan varun "
    "manan sumit roopa kabir aayan ashutosh advait anand tanya tarun sunny mani gokul vijay shruti "
    "suhani mohit kavitha rehan soham rupali"
).split()

DEFAULT_SPEAKER = "shubh"


class SarvamError(Exception):
    """A request Sarvam refused, with its own error code and message."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(f"Sarvam said {status} {code}: {message}")
        self.status, self.code, self.message = status, code, message

    def advice(self) -> str:
        return {
            "invalid_api_key_error": "The key was not accepted. Check SARVAM_API_KEY against dashboard.sarvam.ai.",
            "insufficient_quota_error": "The account is out of credits. Top up in the Sarvam dashboard.",
            "rate_limit_exceeded_error": "Too many requests per minute for this plan. Lower --rate.",
            "invalid_request_error": "The request was malformed. Check the language, speaker and text.",
            "unprocessable_entity_error": "The values were rejected. Check the speaker suits the model and language.",
        }.get(self.code, "See https://docs.sarvam.ai/api-reference-docs/errors-troubleshooting")


def language_code(language: str) -> str:
    """`te` -> `te-IN`. A full code such as `te-IN` is passed through."""
    if language in LANGUAGES.values():
        return language
    try:
        return LANGUAGES[language]
    except KeyError:
        known = ", ".join(sorted(LANGUAGES))
        raise ValueError(f"Sarvam Bulbul v3 has no voice for language `{language}`; it speaks: {known}") from None


def _join_wavs(parts: list[bytes]) -> bytes:
    """Sarvam may answer with several WAV pieces; make them one."""
    if len(parts) == 1:
        return parts[0]
    out = io.BytesIO()
    with wave.open(out, "wb") as writer:
        for i, part in enumerate(parts):
            with wave.open(io.BytesIO(part), "rb") as reader:
                if i == 0:
                    writer.setparams(reader.getparams())
                writer.writeframes(reader.readframes(reader.getnframes()))
    return out.getvalue()


class Sarvam:
    """A small client that spaces its requests and retries what is worth retrying."""

    def __init__(self, api_key: str, *, requests_per_minute: float = 30, max_attempts: int = 6,
                 timeout: float = 120, opener=urllib.request.urlopen, sleep=time.sleep, clock=time.monotonic):
        if not api_key:
            raise ValueError("no Sarvam API key; set the SARVAM_API_KEY environment variable")
        self._key = api_key
        self._gap = 60.0 / requests_per_minute if requests_per_minute > 0 else 0.0
        self._max_attempts = max_attempts
        self._timeout = timeout
        self._open, self._sleep, self._clock = opener, sleep, clock
        self._last_request = None

    def speak(self, text: str, language: str, *, speaker: str = DEFAULT_SPEAKER, pace: float = 1.0,
              sample_rate: int = 48000, temperature: float | None = None, preprocess: bool = False) -> bytes:
        """Return WAV bytes of `text` spoken in `language`."""
        if len(text) > MAX_CHARS:
            raise ValueError(f"{len(text)} characters is over the {MAX_CHARS} one request accepts; split the step")
        if speaker not in SPEAKERS:
            raise ValueError(f"unknown speaker `{speaker}`; Bulbul v3 has: {', '.join(SPEAKERS)}")
        if not 0.5 <= pace <= 2.0:
            raise ValueError(f"pace {pace} is outside 0.5 to 2.0")
        body = {
            "text": text,
            "target_language_code": language_code(language),
            "model": MODEL,
            "speaker": speaker,
            "pace": pace,
            "speech_sample_rate": sample_rate,
            "output_audio_codec": "wav",
            "enable_preprocessing": preprocess,
        }
        if temperature is not None:
            body["temperature"] = temperature
        reply = self._post(body)
        audios = reply.get("audios") or []
        if not audios:
            raise SarvamError(200, "empty_response", "the reply contained no audio")
        return _join_wavs([base64.b64decode(a) for a in audios])

    def _post(self, body: dict) -> dict:
        data = json.dumps(body).encode("utf-8")
        wait = 1.0
        for attempt in range(1, self._max_attempts + 1):
            self._pace_requests()
            request = urllib.request.Request(
                API_URL, data=data, method="POST",
                headers={"api-subscription-key": self._key, "Content-Type": "application/json"},
            )
            try:
                with self._open(request, timeout=self._timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as http:
                error = self._read_error(http)
            except urllib.error.URLError as net:
                error = SarvamError(0, "network_error", str(net.reason))
            # Out of credits is also a 429, and waiting does not fix it.
            retry = error.status in (0, 500, 503) or error.code == "rate_limit_exceeded_error"
            if not retry or attempt == self._max_attempts:
                raise error
            self._sleep(wait)
            wait = min(wait * 2, 60.0)
        raise AssertionError("unreachable")

    def _pace_requests(self) -> None:
        now = self._clock()
        if self._last_request is not None:
            remaining = self._gap - (now - self._last_request)
            if remaining > 0:
                self._sleep(remaining)
                now = self._clock()
        self._last_request = now

    @staticmethod
    def _read_error(http: urllib.error.HTTPError) -> SarvamError:
        try:
            payload = json.loads(http.read().decode("utf-8"))
            error = payload.get("error", {})
            return SarvamError(http.code, error.get("code", "unknown_error"), error.get("message", ""))
        except (ValueError, AttributeError):
            return SarvamError(http.code, "unknown_error", http.reason or "")
