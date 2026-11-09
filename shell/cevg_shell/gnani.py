"""Gnani text-to-speech (Timbre) and speech-to-text (Prisma), as documented
at https://docs.gnani.ai (read on 1 November 2026).

Timbre speaks each narration line. Prisma listens to what Timbre said and
the result is compared with the script, so a skipped or garbled line is
caught before a video is published.

Facts this module relies on:

* Base https://api.vachana.ai, key in the `X-API-Key-ID` header.
* TTS: POST /api/v1/tts/inference with JSON `text`, `model` (`timbre-v2.5`,
  `timbre-v3.0`), `voice` (from that model's catalogue; voices are not
  shared between models), `language` (`en-IN`, `te-IN`, ..., `hi-en` for
  Hinglish, `auto` to detect from the script, "recommended for mixed
  content"), `speed` 0.85 to 1.15, and `audio_config`. The reply is the raw
  audio. Numbers, dates and currency should be sent as words.
* Only one request may be active at a time (429 `RATE_LIMITED`, no
  Retry-After). Text that is too long is a 500; no limit is published, so
  long lines are split at sentences here.
* Errors: 400/500 `{"success": false, "message": ...}`; 401/402/403/429
  `{"detail": {"error_code": ..., "message": ...}}`; STT errors
  `{"success": false, "error": {"type": ..., "message": ...}}`.
* STT: POST /stt/v3, multipart `audio_file` (at most 30 s), `model`
  `prisma-v3.0`, `language_code` one code or up to four comma-separated as
  hints, `format=codemix` keeps English words in Latin script, `keyterms`
  up to 200 terms. The reply has `transcript`.
"""

from __future__ import annotations

import io
import json
import re
import time
import urllib.error
import urllib.request
import uuid
import wave
from difflib import SequenceMatcher

BASE = "https://api.vachana.ai"
TTS_URL = BASE + "/api/v1/tts/inference"
STT_URL = BASE + "/stt/v3"
STT_MODEL = "prisma-v3.0"
DEFAULT_MODEL = "timbre-v3.0"  # Vivaran's narrator is Vasudha, in every language
MAX_CHARS = 400  # our own cautious limit per request; Gnani publishes none
RATE = 48000
# Gnani sits behind Cloudflare, which refuses Python's default user agent
# (error 1010, seen 2 November 2026); every request names itself instead.
USER_AGENT = "cevg-shell/1.0 (+https://vivaran-kappa.vercel.app)"

LANGUAGES = {
    "en": "en-IN", "hi": "hi-IN", "te": "te-IN", "ta": "ta-IN", "kn": "kn-IN", "ml": "ml-IN",
    "mr": "mr-IN", "pa": "pa-IN", "bn": "bn-IN", "gu": "gu-IN",
}

# name -> (gender, preferred language, what Gnani says it suits)
VOICES = {
    "timbre-v2.5": {
        "Ambuja": ("female", "hi", "calm, composed"), "Asmita": ("female", "ta", "polished, smooth"),
        "Bhavna": ("female", "hi", "friendly"), "Brinda": ("female", "ta", "steady, even-paced"),
        "Chitra": ("female", "hi", "mature, caring"), "Deepak": ("male", "hi", "clear, measured"),
        "Devika": ("female", "en", "authoritative"), "Dhruva": ("male", "bn", "casual"),
        "Falak": ("female", "gu", "youthful, clear narration"), "Girish": ("male", "en", "warm, expressive storytelling"),
        "Hemraj": ("male", "hi", "confident"), "Ishaan": ("male", "mr", "clear narration"),
        "Jalaj": ("male", "hi", "expressive storytelling"), "Jwala": ("female", "hi", "approachable"),
        "Kaveri": ("female", "en", "firm"), "Kavin": ("male", "kn", "firm, articulate"),
        "Kirra": ("female", "bn", "soft-spoken"), "Lavanya": ("female", "te", "soft, empathetic"),
        "Lehara": ("female", "te", "gentle, reassuring"), "Mehuli": ("female", "pa", "expressive"),
        "Nalini": ("female", "hi", "friendly, playful"), "Noopur": ("female", "ta", "warm"),
        "Omkar": ("male", "hi", "energetic"), "Poorvi": ("female", "hi-en", "natural bilingual"),
        "Pranav": ("male", "en", "friendly"), "Reshma": ("female", "ml", "bright"),
        "Riyaan": ("male", "ml", "easygoing"), "Roopesh": ("male", "hi", "grounded, professional"),
        "Saanvi": ("female", "kn", "lively"), "Shlok": ("male", "en", "warm, conversational"),
        "Suhana": ("female", "te", "calm, confident"), "Trisha": ("female", "ta", "warm guidance"),
        "Trupti": ("female", "en", "upbeat, articulate"), "Urmila": ("female", "hi", "refined, formal"),
        "Varuni": ("female", "te", "clear, natural"), "Vedika": ("female", "ta", "crisp, informative"),
        "Veera": ("male", "gu", "friendly"), "Vikrant": ("male", "hi", "warm, genuine"),
        "Yashvi": ("female", "hi", "gentle"), "Yukti": ("female", "te", "warm, welcoming"),
        "Zahira": ("female", "mr", "energetic"), "Zayan": ("male", "pa", "soft, caring"),
    },
    # Every v3.0 voice speaks every language.
    "timbre-v3.0": {
        "Avinash": ("male", "*", "firm, deliberate"), "Chetana": ("female", "*", "gentle"),
        "Devansh": ("male", "*", "energetic, young"), "Kalpana": ("female", "*", "composed"),
        "Lakshmi": ("female", "*", "warm; storytelling and e-learning"), "Prakash": ("male", "*", "steady"),
        "Riyaa": ("female", "*", "lively, confident"), "Shivani": ("female", "*", "patient"),
        "Shubham": ("male", "*", "confident"), "Tarika": ("female", "*", "reassuring"),
        "Vasudha": ("female", "*", "composed; narration and e-learning"),
        "Yashraj": ("male", "*", "narrative; e-learning"), "Harshad": ("male", "*", "firm"),
    },
}

# The voice a video gets when none is chosen: a narration voice for the language.
DEFAULT_VOICES = {
    "timbre-v2.5": {"en": "Girish", "te": "Suhana", "hi": "Jalaj", "ta": "Vedika", "kn": "Kavin",
                    "ml": "Reshma", "mr": "Ishaan", "pa": "Mehuli", "bn": "Dhruva", "gu": "Falak"},
    "timbre-v3.0": {"*": "Vasudha"},
}


class GnaniError(Exception):
    """A request Gnani refused, with its own error code and message."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(f"Gnani said {status} {code}: {message}")
        self.status, self.code, self.message = status, code, message

    def advice(self) -> str:
        if self.status == 401:
            return "The key was not accepted. Check GNANI_API_KEY against app.gnani.ai/voice."
        if self.status == 402:
            return "The account is out of credits. Check the balance at app.gnani.ai/voice."
        if self.status == 403 and "1010" in self.message:
            return "Gnani's firewall refused the request itself (Cloudflare 1010), not the key."
        if self.status == 403:
            return "The key is not allowed to use this API (SCOPE_NOT_ALLOWED)."
        if self.status == 429:
            return "Gnani allows one request at a time; another request was still running."
        if self.status == 0:
            return "Gnani could not be reached. Is api.vachana.ai allowed on this network?"
        return "See https://docs.gnani.ai/api/introduction/errors"


def language_code(language: str) -> str:
    """`te` -> `te-IN`. A full code is passed through."""
    if language in LANGUAGES.values() or language in ("auto", "hi-en"):
        return language
    try:
        return LANGUAGES[language]
    except KeyError:
        raise ValueError(f"Gnani Timbre has no voice for `{language}`; it speaks: {', '.join(sorted(LANGUAGES))}") from None


def default_voice(model: str, language: str) -> str:
    table = DEFAULT_VOICES[model]
    return table.get("*") or table.get(language) or table["en"]


def voices(model: str = DEFAULT_MODEL) -> dict:
    try:
        return VOICES[model]
    except KeyError:
        raise ValueError(f"unknown Gnani model `{model}`; use one of: {', '.join(VOICES)}") from None


_LATIN = re.compile(r"[A-Za-z]")
_INDIC = re.compile(r"[ऀ-෿]")


def request_language(text: str, language: str) -> str:
    """The `language` to send. Our Hindi and Telugu narration is code-mixed:
    regional script with English words in Latin letters. Gnani recommends
    `auto` for mixed content, and has `hi-en` for Hinglish."""
    code = language_code(language)
    if _LATIN.search(text) and _INDIC.search(text):
        return "hi-en" if code == "hi-IN" else "auto"
    return code


# ---------------------------------------------------------------- numbers

_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
_ORDINAL = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth",
            "nine": "ninth", "twelve": "twelfth"}


def number_words(n: int) -> str:
    """Whole numbers in English words, Indian-English style: 1500 -> one thousand five hundred."""
    if n < 0:
        return "minus " + number_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        rest = n % 100
        return _ONES[n // 100] + " hundred" + ("" if rest == 0 else " " + number_words(rest))
    for size, name in ((10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= size:
            rest = n % size
            return number_words(n // size) + " " + name + ("" if rest == 0 else " " + number_words(rest))
    raise AssertionError("unreachable")


def _ordinal(n: int) -> str:
    words = number_words(n).split(" ")
    last = words[-1]
    if last in _ORDINAL:
        words[-1] = _ORDINAL[last]
    elif last.endswith("y"):
        words[-1] = last[:-1] + "ieth"
    else:
        words[-1] = last + "th"
    return " ".join(words)


_NAME = re.compile(r"(?<![\w.])([A-Za-z])(\d{1,2})(?![\w.])")
_NUMBER = re.compile(r"(?<![\w.])(-)?(\d{1,3}(?:,\d{2,3})+|\d+)(?:\.(\d+))?(st|nd|rd|th)?(%)?(?![\w])")


def spoken(text: str) -> str:
    """Write the numbers in a line as English words, as Gnani asks: `75%` ->
    `seventy five percent`, `3.14` -> `three point one four`, `-2` -> `minus
    two`, `2nd` -> `second`, `1,000` -> `one thousand`. Number words stay in
    English in Hindi and Telugu narration too (our code-mixing rule)."""

    def one(m: re.Match) -> str:
        sign, whole, frac, suffix, percent = m.groups()
        n = int(whole.replace(",", ""))
        if suffix and not frac:
            words = _ordinal(n)
        else:
            words = number_words(n)
            if frac:
                words += " point " + " ".join(_ONES[int(d)] for d in frac)
        if sign:
            words = "minus " + words
        if percent:
            words += " percent"
        return words

    text = re.sub(r"(?<=\d)\s*\^\s*(?=\d)", " to the power ", text)
    # Names like P0, P4, R2: a letter with a number glued on. Sent raw, Timbre
    # read "P4" as "P char" in Telugu and "P3" as "Tree" in English.
    text = _NAME.sub(lambda m: m.group(1) + " " + " ".join(_ONES[int(d)] for d in m.group(2)), text)
    return _NUMBER.sub(one, text)


# ---------------------------------------------------------------- audio

def _split(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Pieces of at most `limit` characters, cut after sentences where possible."""
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[.!?।])\s+", text)
    pieces, current = [], ""
    for s in sentences:
        while len(s) > limit:  # a single sentence longer than the limit: cut at a space
            cut = s.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                pieces.append(current)
                current = ""
            pieces.append(s[:cut].strip())
            s = s[cut:].strip()
        candidate = (current + " " + s).strip()
        if len(candidate) > limit and current:
            pieces.append(current)
            current = s
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _join_wavs(parts: list[bytes]) -> bytes:
    """One WAV from the pieces, always with a fresh header: Timbre's header
    gives a streaming placeholder length (seen 9 November 2026), which made a
    3-second clip read as 44,739 seconds."""
    out = io.BytesIO()
    with wave.open(out, "wb") as writer:
        for i, part in enumerate(parts):
            with wave.open(io.BytesIO(part), "rb") as reader:
                if i == 0:  # not setparams: that would copy the bogus frame count
                    writer.setnchannels(reader.getnchannels())
                    writer.setsampwidth(reader.getsampwidth())
                    writer.setframerate(reader.getframerate())
                writer.writeframes(reader.readframes(reader.getnframes()))
    return out.getvalue()


def _multipart(fields: dict[str, str], file_field: str, filename: str, data: bytes) -> tuple[bytes, str]:
    boundary = "cevg-" + uuid.uuid4().hex
    body = io.BytesIO()
    for name, value in fields.items():
        body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode())
        body.write(value.encode("utf-8") + b"\r\n")
    body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{filename}\"\r\n"
               "Content-Type: audio/wav\r\n\r\n".encode())
    body.write(data + b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())
    return body.getvalue(), f"multipart/form-data; boundary={boundary}"


# ---------------------------------------------------------------- client

class Gnani:
    """One client for both directions. Requests go one at a time (Gnani's
    rule), and 429, 500, 503 and network failures are retried with backoff."""

    def __init__(self, api_key: str, *, max_attempts: int = 6, timeout: float = 120,
                 opener=urllib.request.urlopen, sleep=time.sleep):
        if not api_key:
            raise ValueError("no Gnani API key; set the GNANI_API_KEY environment variable")
        self._key = api_key
        self._max_attempts, self._timeout = max_attempts, timeout
        self._open, self._sleep = opener, sleep

    def speak(self, text: str, language: str, *, voice: str | None = None, model: str = DEFAULT_MODEL,
              speed: float = 1.0) -> bytes:
        """WAV bytes (48 kHz mono 16-bit) of `text` spoken in `language`."""
        catalogue = voices(model)
        voice = voice or default_voice(model, language)
        if voice not in catalogue:
            raise ValueError(f"`{voice}` is not a {model} voice; it has: {', '.join(catalogue)}")
        if not 0.85 <= speed <= 1.15:
            raise ValueError(f"speed {speed} is outside 0.85 to 1.15")
        text = say_as(spoken(text), language)
        parts = []
        for piece in _split(text):
            body = {
                "text": piece, "model": model, "voice": voice, "language": request_language(piece, language),
                "speed": speed,
                "audio_config": {"sample_rate": RATE, "num_channels": 1, "sample_width": 2,
                                 "encoding": "linear_pcm", "container": "wav"},
            }
            parts.append(self._send(TTS_URL, json.dumps(body).encode("utf-8"), "application/json"))
        return _join_wavs(parts)

    def transcribe(self, wav: bytes, language: str, *, keyterms: list[str] | None = None) -> str:
        """What Prisma hears in a clip of at most 30 seconds. For Hindi and
        Telugu the hints are that language plus English, and `codemix`
        keeps the English words in Latin letters, as our scripts write them."""
        code = language_code(language)
        hints = code if code == "en-IN" else f"{code},en-IN"
        fields = {"model": STT_MODEL, "language_code": hints, "format": "codemix"}
        if keyterms:
            fields["keyterms"] = json.dumps(keyterms[:200])
        body, content_type = _multipart(fields, "audio_file", "clip.wav", wav)
        reply = json.loads(self._send(STT_URL, body, content_type).decode("utf-8"))
        return reply.get("transcript", "")

    def _send(self, url: str, data: bytes, content_type: str) -> bytes:
        wait = 1.0
        for attempt in range(1, self._max_attempts + 1):
            request = urllib.request.Request(url, data=data, method="POST",
                                             headers={"X-API-Key-ID": self._key, "Content-Type": content_type,
                                                      "User-Agent": USER_AGENT})
            try:
                with self._open(request, timeout=self._timeout) as response:
                    return response.read()
            except urllib.error.HTTPError as http:
                error = self._read_error(http)
            except urllib.error.URLError as net:
                error = GnaniError(0, "NETWORK_ERROR", str(net.reason))
            if error.status not in (0, 429, 500, 503) or attempt == self._max_attempts:
                raise error
            self._sleep(wait)
            wait = min(wait * 2, 30.0)
        raise AssertionError("unreachable")

    @staticmethod
    def _read_error(http: urllib.error.HTTPError) -> GnaniError:
        raw = b""
        try:
            raw = http.read()
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, AttributeError):
            text = raw.decode("utf-8", "replace").strip()[:200] if raw else ""
            return GnaniError(http.code, "UNKNOWN", text or http.reason or "")
        detail = payload.get("detail") if isinstance(payload, dict) else None
        if isinstance(detail, dict):
            return GnaniError(http.code, detail.get("error_code") or "UNKNOWN", detail.get("message", ""))
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            return GnaniError(http.code, error.get("type", "UNKNOWN"), error.get("message", ""))
        return GnaniError(http.code, "UNKNOWN", str(payload.get("message", payload)) if isinstance(payload, dict) else str(payload))


# ---------------------------------------------------------------- listening back

# Bump when `spoken` changes what is sent, so cached clips are spoken again.
TEXT_VERSION = 4

# Words the voice gets wrong, and the spelling that makes it say them right,
# per language ("*" for any language without its own). Only what Timbre hears
# changes; captions keep the real spelling.
SAY_AS = {
    # "vi-va-run". Latin spellings come out as "vivvaaran" or "vivran" in a
    # sentence; the Indic spellings are the ones Sai picked by ear (9 Nov 2026),
    # and English uses the Telugu one.
    "Vivaran": {"hi": "विवरन", "*": "వివరన్"},
}
_SAY_AS = re.compile(r"\b(" + "|".join(map(re.escape, SAY_AS)) + r")\b", re.IGNORECASE)


def say_as(text: str, language: str) -> str:
    """`text` with the words in SAY_AS respelled for `language`."""
    lang = language.split("-")[0].lower()
    def swap(m):
        by = next(v for k, v in SAY_AS.items() if k.lower() == m.group(1).lower())
        return by.get(lang, by["*"])
    return _SAY_AS.sub(swap, text)


def _words(text: str, digits: bool = False) -> list[str]:
    """Words of a line. With `digits`, a run of digits in a transcript is read
    one digit at a time: Prisma writes "743" where we said "seven four three"."""
    if digits:
        text = re.sub(r"\d+", lambda m: " " + " ".join(_ONES[int(d)] for d in m.group()) + " ", text)
    text = spoken(text).lower()
    return [w for w in re.split(r"[^\w\u0900-\u0DFF]+", text) if w]


# Devanagari and Telugu share one layout (Telugu is Devanagari + 0x300), so
# one table romanises both, roughly: enough to see that సెర్చ్ is "search".
_CONSONANTS = dict(zip(
    "कखगघङचछजझञटठडढणतथदधनपफबभमयरलळवशषसह",
    "k kh g gh n ch ch j jh n t th d dh n t th d dh n p ph b bh m y r l l v sh sh s h".split()))
_VOWELS = dict(zip("अआइईउऊऋएऐओऔऎऒ", "a a i i u u ru e ai o au e o".split()))
_SIGNS = dict(zip("ािीुूृेैोौॆॊ", "a i i u u ru e ai o au e o".split()))
_VIRAMA, _ANUSVARA = "्", "ं"


def _romanise(word: str) -> str:
    out, pending = [], False  # pending: a consonant still carrying its inherent "a"
    for ch in word:
        code = ord(ch)
        if 0x0C00 <= code <= 0x0C7F:
            ch = chr(code - 0x300)
        if ch in _CONSONANTS:
            if pending:
                out.append("a")
            out.append(_CONSONANTS[ch])
            pending = True
        elif ch in _SIGNS:
            out.append(_SIGNS[ch])
            pending = False
        elif ch == _VIRAMA:
            pending = False
        else:
            if pending:
                out.append("a")
                pending = False
            if ch in _VOWELS:
                out.append(_VOWELS[ch])
            elif ch == _ANUSVARA:
                out.append("n")
            elif ch.isascii():
                out.append(ch)
    if pending:
        out.append("a")
    return "".join(out)


def _sound(word: str) -> str:
    """A rough key for how a word sounds, the same for both scripts: vowels
    and doubled letters squeezed, so "search" and "serch", "hi" and "high" are close."""
    w = _romanise(word.lower())
    w = re.sub(r"gh$", "", w)            # high -> hi
    w = re.sub(r"[aeiouy]+", "a", w)     # every vowel run is one vowel
    return re.sub(r"(.)\1+", r"\1", w)


def _alike(a: str, b: str) -> bool:
    if a == b:
        return True
    sa, sb = _sound(a), _sound(b)
    if sa == sb:
        return True
    return len(sa) > 2 and len(sb) > 2 and SequenceMatcher(None, sa, sb).ratio() >= 0.7


def match(said: str, heard: str) -> float:
    """How much of the line was heard, from 0 to 1: the share of the script's
    words found, in order, in the transcript. Words match across scripts
    (Prisma may write an English word in Telugu letters), loosely enough that
    "lo" and "low" agree, and a word heard glued to a suffix ("arrayలో") still counts."""
    expected, got = _words(said), _words(heard, digits=True)
    if not expected:
        return 1.0
    found, j = 0, 0
    for word in expected:
        for k in range(j, min(j + 4, len(got))):
            if _alike(word, got[k]) or (len(_sound(word)) > 3 and _sound(got[k]).startswith(_sound(word))):
                found += 1
                j = k + 1
                break
    return found / len(expected)


def keyterms(text: str) -> list[str]:
    """English terms in a line (`Dijkstra`, `B+ tree`, `LRU`), to help Prisma hear them."""
    return sorted({w for w in re.findall(r"[A-Za-z][A-Za-z+'-]{2,}", text) if not w.islower() or len(w) > 6})
