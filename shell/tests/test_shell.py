"""Tests that need no Sarvam key and no network.

    cd shell && python -m unittest -v

The Sarvam client is tested against a fake server that answers the way the
documentation says the real one does. The pipeline test runs the real `cevg`
binary and ffmpeg with stand-in audio, and is skipped if either is missing.
"""

import base64
import io
import json
import time
import os
import shutil
import subprocess
import tempfile
import unittest
import urllib.error
import wave
from pathlib import Path

from cevg_shell import gnani, providers, sarvam
from cevg_shell.narrate import NarrateError, find_cevg, narrate, narration
from cevg_shell.voice import Cache, SarvamVoice, StandInVoice

ROOT = Path(__file__).resolve().parents[2]


def wav(seconds: float = 0.1, rate: int = 48000) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(int(seconds * rate) * 2))
    return out.getvalue()


class FakeServer:
    """Stands in for urllib.request.urlopen. `replies` are served in order:
    a dict is a 200 body, a (status, code) pair is an error."""

    def __init__(self, replies):
        self.replies, self.requests = list(replies), []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, tuple):
            status, code = reply
            body = json.dumps({"error": {"message": "nope", "code": code}}).encode()
            raise urllib.error.HTTPError(request.full_url, status, "error", {}, io.BytesIO(body))
        return io.BytesIO(json.dumps(reply).encode())


def client(replies, **kw):
    server, sleeps = FakeServer(replies), []
    made = sarvam.Sarvam("test-key", opener=server, sleep=sleeps.append, clock=lambda: 0.0, **kw)
    return made, server, sleeps


OK = {"request_id": "r1", "audios": [base64.b64encode(wav()).decode()]}


class SarvamClient(unittest.TestCase):
    def test_request_matches_the_documented_api(self):
        c, server, _ = client([OK])
        audio = c.speak("నమస్తే", "te", speaker="kavya", pace=1.1)
        self.assertEqual(audio[:4], b"RIFF")
        request = server.requests[0]
        self.assertEqual(request.full_url, "https://api.sarvam.ai/text-to-speech")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Api-subscription-key"), "test-key")
        body = json.loads(request.data)
        self.assertEqual(body["text"], "నమస్తే")
        self.assertEqual(body["target_language_code"], "te-IN")
        self.assertEqual(body["model"], "bulbul:v3")
        self.assertEqual((body["speaker"], body["pace"], body["speech_sample_rate"]), ("kavya", 1.1, 48000))
        self.assertEqual(body["output_audio_codec"], "wav")
        self.assertNotIn("temperature", body)

    def test_several_audio_pieces_become_one_file(self):
        piece = base64.b64encode(wav(0.1)).decode()
        c, _, _ = client([{"audios": [piece, piece]}])
        with wave.open(io.BytesIO(c.speak("hello", "en")), "rb") as w:
            self.assertAlmostEqual(w.getnframes() / w.getframerate(), 0.2, places=3)

    def test_bad_input_is_refused_before_any_request(self):
        c, server, _ = client([])
        with self.assertRaisesRegex(ValueError, "over the 2500"):
            c.speak("x" * 2501, "en")
        with self.assertRaisesRegex(ValueError, "unknown speaker"):
            c.speak("hi", "en", speaker="nobody")
        with self.assertRaisesRegex(ValueError, "no voice for language `fr`"):
            c.speak("bonjour", "fr")
        with self.assertRaisesRegex(ValueError, "outside 0.5 to 2.0"):
            c.speak("hi", "en", pace=3)
        self.assertEqual(server.requests, [])

    def test_a_rejected_key_is_reported_and_not_retried(self):
        c, server, sleeps = client([(403, "invalid_api_key_error")])
        with self.assertRaises(sarvam.SarvamError) as caught:
            c.speak("hi", "en")
        self.assertEqual(caught.exception.code, "invalid_api_key_error")
        self.assertIn("SARVAM_API_KEY", caught.exception.advice())
        self.assertEqual((len(server.requests), sleeps), (1, []))

    def test_rate_limits_and_server_errors_are_retried_with_backoff(self):
        c, server, sleeps = client([(429, "rate_limit_exceeded_error"), (503, "internal_server_error"), OK],
                                   requests_per_minute=0)
        self.assertEqual(c.speak("hi", "en")[:4], b"RIFF")
        self.assertEqual((len(server.requests), sleeps), (3, [1.0, 2.0]))

    def test_running_out_of_credits_is_not_retried(self):
        c, server, _ = client([(429, "insufficient_quota_error")])
        with self.assertRaises(sarvam.SarvamError) as caught:
            c.speak("hi", "en")
        self.assertIn("credits", caught.exception.advice())
        self.assertEqual(len(server.requests), 1)

    def test_requests_are_spaced_to_the_plan(self):
        c, _, sleeps = client([OK, OK], requests_per_minute=30)
        c.speak("one", "en")
        c.speak("two", "en")
        self.assertEqual(sleeps, [2.0])  # 60 s / 30 requests, and the fake clock never moves

    def test_a_key_is_required(self):
        with self.assertRaisesRegex(ValueError, "SARVAM_API_KEY"):
            sarvam.Sarvam("")


class VoiceCache(unittest.TestCase):
    def test_a_line_is_spoken_once(self):
        c, server, _ = client([OK, OK], requests_per_minute=0)
        voice = SarvamVoice(c, speaker="ritu")
        with tempfile.TemporaryDirectory() as folder:
            cache = Cache(Path(folder))
            first = cache.get(voice, "same line", "hi")
            again = cache.get(voice, "same line", "hi")
            other = cache.get(voice, "another line", "hi")
            self.assertEqual(first, again)
            self.assertNotEqual(first, other)
            self.assertEqual((cache.spoken, cache.reused, len(server.requests)), (2, 1, 2))
            # A different voice is a different sound, so a different file.
            self.assertNotEqual(cache.path(SarvamVoice(c, speaker="kavya"), "same line", "hi"), first)


@unittest.skipUnless(shutil.which("ffmpeg") and ((ROOT / "target/release/cevg").is_file() or (ROOT / "target/release/cevg.exe").is_file()),
                     "needs ffmpeg and a built target/release/cevg")
class Pipeline(unittest.TestCase):
    SCRIPT = ROOT / "examples" / "binary_search.json"

    def test_missing_language_is_explained(self):
        self.assertEqual(len(narration(self.SCRIPT, "en")), 7)
        self.assertEqual(len(narration(self.SCRIPT, "te")), 7)
        with self.assertRaisesRegex(NarrateError, "7 of 7 steps have no `ta` narration"):
            narration(self.SCRIPT, "ta")

    def _small(self, folder):
        """The example at a small size, so the test is quick."""
        script = json.loads(self.SCRIPT.read_text(encoding="utf-8"))
        script["canvas"]["width"], script["canvas"]["height"] = 480, 270
        small = Path(folder) / "script.json"
        small.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
        return small

    def test_a_silent_voice_stops_the_run_at_once(self):
        class Silent(StandInVoice):
            calls = 0

            def identity(self):
                return "silent"

            def speak(self, text, language):
                Silent.calls += 1
                return b"".join([super().speak(text, language)[:44], bytes(48000 * 2)])

        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            with self.assertRaisesRegex(NarrateError, "came back silent"):
                narrate(self._small(folder), folder / "out.mp4", Silent(), cache_dir=folder / "cache", cevg=find_cevg())
            self.assertEqual(Silent.calls, 1)
            self.assertEqual(list((folder / "cache" / "voice").glob("*.wav")), [])

    def test_a_narrated_video_is_made_and_is_in_sync(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            small = self._small(folder)
            out = folder / "out.mp4"
            result = narrate(small, out, StandInVoice(), cache_dir=folder / "cache", cevg=find_cevg())
            self.assertEqual((result.steps, result.spoken, result.reused), (7, 7, 0))

            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", str(out)],
                capture_output=True, text=True, check=True)
            streams = {s["codec_type"]: float(s["duration"]) for s in json.loads(probe.stdout)["streams"]}
            self.assertEqual(set(streams), {"video", "audio"})
            self.assertAlmostEqual(streams["video"], result.seconds, delta=0.1)
            self.assertAlmostEqual(streams["audio"], result.seconds, delta=0.1)

            srt = result.captions.read_text(encoding="utf-8")
            self.assertTrue(srt.startswith("1\n00:00:00,000 --> "))
            self.assertEqual(srt.count(" --> "), 7)

            # A second run speaks nothing: every line comes from the cache.
            again = narrate(small, out, StandInVoice(), cache_dir=folder / "cache", cevg=find_cevg())
            self.assertEqual((again.spoken, again.reused), (0, 7))

    def test_listening_back_flags_lines_the_voice_got_wrong_and_is_cached(self):
        class Listening(StandInVoice):
            heard = 0

            def identity(self):
                return "listening"

            def listen(self, wav_bytes, text, language):
                Listening.heard += 1
                # Pretend the voice dropped most of the third line.
                transcript = text if Listening.heard != 3 else text.split()[0]
                return gnani.match(text, transcript), transcript

        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            small = self._small(folder)
            result = narrate(small, folder / "out.mp4", Listening(), cache_dir=folder / "cache", cevg=find_cevg(),
                             listen=True)
            self.assertEqual(len(result.heard), 7)
            self.assertEqual([h["step"] for h in result.doubtful()], [3])
            again = narrate(small, folder / "out.mp4", Listening(), cache_dir=folder / "cache", cevg=find_cevg(),
                            listen=True)
            self.assertEqual(Listening.heard, 7)  # the second run reads the saved answers
            self.assertEqual([h["step"] for h in again.doubtful()], [3])


class GnaniServer:
    """Stands in for urllib.request.urlopen for Gnani. Replies in order: bytes
    are a 200 body, (status, payload) an error with that JSON body."""

    def __init__(self, replies):
        self.replies, self.requests = list(replies), []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, tuple):
            status, payload = reply
            raise urllib.error.HTTPError(request.full_url, status, "error", {}, io.BytesIO(json.dumps(payload).encode()))
        return io.BytesIO(reply)


def gnani_client(replies):
    server, sleeps = GnaniServer(replies), []
    return gnani.Gnani("test-key", opener=server, sleep=sleeps.append), server, sleeps


class GnaniWords(unittest.TestCase):
    def test_numbers_become_english_words(self):
        cases = {
            "We look for 23.": "We look for twenty three.",
            "about 150 million degrees": "about one hundred fifty million degrees",
            "1,000 views and 1,00,000 more": "one thousand views and one hundred thousand more",
            "75% of the variance": "seventy five percent of the variance",
            "pi is 3.14": "pi is three point one four",
            "x goes to -2": "x goes to minus two",
            "the 2nd and 21st row": "the second and twenty first row",
            "2^10 is 1024": "two to the power ten is one thousand twenty four",
            "ఈ sorted array లో మనం 23 ను search": "ఈ sorted array లో మనం twenty three ను search",
            "timbre-v2.5 and B+ tree": "timbre-v2.5 and B+ tree",
            "P1, P3, P4, P0, P2": "P one, P three, P four, P zero, P two",
            "P10 కు one two two need": "P one zero కు one two two need",
        }
        for said, expected in cases.items():
            self.assertEqual(gnani.spoken(said), expected, said)
        self.assertEqual(gnani.number_words(0), "zero")
        self.assertEqual(gnani.number_words(1500), "one thousand five hundred")
        self.assertEqual(gnani.number_words(2026), "two thousand twenty six")

    def test_mixed_script_lines_ask_for_auto_or_hinglish(self):
        self.assertEqual(gnani.request_language("This is English.", "en"), "en-IN")
        self.assertEqual(gnani.request_language("ఇది పరీక్ష.", "te"), "te-IN")
        self.assertEqual(gnani.request_language("ఇది ఒక sorted array.", "te"), "auto")
        self.assertEqual(gnani.request_language("यह एक sorted array है।", "hi"), "hi-en")
        with self.assertRaisesRegex(ValueError, "no voice for `od`"):
            gnani.request_language("x", "od")

    def test_long_lines_are_split_after_sentences(self):
        line = " ".join(f"Sentence number {i} is here." for i in range(40))
        pieces = gnani._split(line, 120)
        self.assertTrue(all(len(p) <= 120 for p in pieces), pieces)
        self.assertEqual(" ".join(pieces), line)
        self.assertTrue(all(p.endswith(".") for p in pieces))
        self.assertEqual(gnani._split("short", 120), ["short"])

    def test_match_scores_skipped_and_garbled_words(self):
        said = "Two pointers, lo and hi, mark the part we still have to search."
        self.assertEqual(gnani.match(said, "two pointers lo and hi mark the part we still have to search"), 1.0)
        self.assertLess(gnani.match(said, "two pointers mark the part"), 0.5)
        self.assertEqual(gnani.match("We look for 23.", "we look for twenty three"), 1.0)
        self.assertEqual(gnani.match("For P0, seven five three minus zero one zero gives seven four three.",
                                     "For P zero, 753 minus 010 gives 743."), 1.0)
        self.assertEqual(gnani.match("ఈ sorted array లో", "ఈ sorted array లో"), 1.0)
        self.assertIn("Dijkstra", gnani.keyterms("Run Dijkstra on the graph from LRU"))

    def test_match_reads_english_words_heard_in_telugu_letters(self):
        # Real Prisma codemix transcripts of Timbre clips, 2 November 2026.
        said = "ఈ sorted array లో మనం 23 ను search చేస్తున్నాం. lo, hi అనే two pointers, మనం ఇంకా search చేయాల్సిన part ను mark చేస్తాయి."
        heard_in_telugu = ("ఈ సోర్టెడ్ అరేలో మనం twenty three ను సెర్చ్ చేస్తున్నాం, లో హాయ్ అనే టూ పాయింటర్స్ మనం ఇంకా "
                           "సెర్చ్ చేయాల్సిన పార్ట్ ను మార్క్ చేస్తాయి.")
        heard_mixed = "ఈ sorted arrayలో మనం twenty three ను search చేస్తున్నాం. లో, హై అనే two pointers మనం ఇంకా search చేయాల్సిన partను mark చేస్తాయి."
        self.assertGreaterEqual(gnani.match(said, heard_in_telugu), 0.85)
        self.assertGreaterEqual(gnani.match(said, heard_mixed), 0.85)
        self.assertLess(gnani.match(said, "ఈ sorted array లో మనం twenty three ను search చేస్తున్నాం."), 0.5)
        self.assertEqual(gnani._romanise("సెర్చ్"), "serch")


class GnaniClient(unittest.TestCase):
    def test_a_line_is_spoken_with_the_documented_request(self):
        made, server, _ = gnani_client([wav(0.2)])
        audio = made.speak("We look for 23 in this sorted array.", "en", model="timbre-v2.5")
        self.assertEqual(audio[:4], b"RIFF")
        request = server.requests[0]
        self.assertEqual(request.full_url, "https://api.vachana.ai/api/v1/tts/inference")
        self.assertEqual(request.get_header("X-api-key-id"), "test-key")
        self.assertTrue(request.get_header("User-agent").startswith("cevg-shell/"))
        body = json.loads(request.data)
        self.assertEqual(body["text"], "We look for twenty three in this sorted array.")
        self.assertEqual((body["model"], body["voice"], body["language"], body["speed"]), ("timbre-v2.5", "Girish", "en-IN", 1.0))
        self.assertEqual(body["audio_config"], {"sample_rate": 48000, "num_channels": 1, "sample_width": 2,
                                                "encoding": "linear_pcm", "container": "wav"})

    def test_the_name_is_spelled_the_way_it_should_sound(self):
        made, server, _ = gnani_client([wav(), wav(), wav(), wav()])
        made.speak("Vivaran shows you every step.", "en")
        made.speak("Watch at vivaran kappa dot vercel dot app.", "en")
        made.speak("Vivaran మీకు ప్రతి step చూపిస్తుంది.", "te")
        made.speak("Vivaran आपको हर step दिखाता है।", "hi")
        sent = [json.loads(r.data) for r in server.requests]
        self.assertEqual(sent[0]["text"], "వివరన్ shows you every step.")
        self.assertEqual(sent[0]["language"], "auto")  # mixed scripts
        self.assertEqual(sent[1]["text"], "Watch at వివరన్ kappa dot vercel dot app.")
        self.assertTrue(sent[2]["text"].startswith("వివరన్ మీకు"))
        self.assertTrue(sent[3]["text"].startswith("विवरन आपको"))

    def test_telugu_gets_its_default_voice_and_long_text_is_joined(self):
        made, server, _ = gnani_client([wav(0.1), wav(0.2)])
        line = "ఇది ఒక sorted array. " * 30
        audio = made.speak(line.strip(), "te", model="timbre-v2.5")
        self.assertEqual(len(server.requests), 2)
        self.assertEqual(json.loads(server.requests[0].data)["voice"], "Suhana")
        self.assertEqual(json.loads(server.requests[0].data)["language"], "auto")
        with wave.open(io.BytesIO(audio)) as w:
            self.assertAlmostEqual(w.getnframes() / w.getframerate(), 0.3, places=2)

    def test_a_streaming_header_is_rewritten_with_the_true_length(self):
        clip = bytearray(wav(0.5))
        clip[40:44] = (0xFFFFFFFF - 8).to_bytes(4, "little")  # data size as a streaming placeholder
        made, _, _ = gnani_client([bytes(clip)])
        with wave.open(io.BytesIO(made.speak("hello", "en"))) as w:
            self.assertAlmostEqual(w.getnframes() / w.getframerate(), 0.5, places=3)

    def test_bad_voices_and_speeds_are_refused_before_any_request(self):
        made, server, _ = gnani_client([])
        self.assertEqual(gnani.default_voice(gnani.DEFAULT_MODEL, "te"), "Vasudha")
        with self.assertRaisesRegex(ValueError, "`shubh` is not a timbre-v3.0 voice"):
            made.speak("hi", "en", voice="shubh")
        with self.assertRaisesRegex(ValueError, "speed 2 is outside"):
            made.speak("hi", "en", speed=2)
        self.assertEqual(server.requests, [])

    def test_busy_and_failing_requests_are_retried_but_bad_keys_are_not(self):
        busy = (429, {"detail": {"error_code": "RATE_LIMITED", "message": "Only 1 active request", "status_code": 429}})
        made, server, sleeps = gnani_client([busy, (503, {"success": False, "message": "busy"}), wav()])
        made.speak("hello", "en")
        self.assertEqual((len(server.requests), sleeps), (3, [1.0, 2.0]))

        bad = (401, {"detail": {"error_code": "INVALID_API_KEY", "message": "no", "status_code": 401}})
        made, server, _ = gnani_client([bad])
        with self.assertRaises(gnani.GnaniError) as caught:
            made.speak("hello", "en")
        self.assertEqual((caught.exception.status, caught.exception.code), (401, "INVALID_API_KEY"))
        self.assertIn("GNANI_API_KEY", caught.exception.advice())
        self.assertEqual(len(server.requests), 1)

        made, _, _ = gnani_client([(402, {"detail": {"message": "no credit"}})])
        with self.assertRaises(gnani.GnaniError) as caught:
            made.speak("hello", "en")
        self.assertIn("out of credits", caught.exception.advice())

    def test_listening_back_sends_the_clip_as_codemix(self):
        reply = json.dumps({"success": True, "transcript": "ఈ sorted array లో twenty three", "model": "prisma-v3.0"}).encode()
        made, server, _ = gnani_client([reply])
        heard = made.transcribe(wav(0.5), "te", keyterms=["sorted", "array"])
        self.assertEqual(heard, "ఈ sorted array లో twenty three")
        request = server.requests[0]
        self.assertEqual(request.full_url, "https://api.vachana.ai/stt/v3")
        self.assertTrue(request.get_header("Content-type").startswith("multipart/form-data; boundary="))
        body = request.data
        for part in (b'name="model"\r\n\r\nprisma-v3.0', b'name="language_code"\r\n\r\nte-IN,en-IN',
                     b'name="format"\r\n\r\ncodemix', b'name="keyterms"\r\n\r\n["sorted", "array"]',
                     b'name="audio_file"; filename="clip.wav"', b"RIFF"):
            self.assertIn(part, body)

        stt_error = (400, {"success": False, "error": {"type": "MAX_AUDIO_DURATION_EXCEEDED", "message": "too long"}})
        made, _, _ = gnani_client([stt_error])
        with self.assertRaises(gnani.GnaniError) as caught:
            made.transcribe(wav(), "en")
        self.assertEqual(caught.exception.code, "MAX_AUDIO_DURATION_EXCEEDED")


class Providers(unittest.TestCase):
    def test_gnani_is_the_default_and_sarvam_is_kept(self):
        saved = os.environ.pop("CEVG_TTS", None)
        try:
            self.assertEqual(providers.current().name, "gnani")
            self.assertEqual(providers.current("sarvam").name, "sarvam")
            os.environ["CEVG_TTS"] = "sarvam"
            self.assertEqual(providers.current().name, "sarvam")
            with self.assertRaisesRegex(ValueError, "must be `gnani` or `sarvam`"):
                providers.current("other")
        finally:
            os.environ.pop("CEVG_TTS", None)
            if saved:
                os.environ["CEVG_TTS"] = saved
        g = providers.Gnani("timbre-v2.5")
        self.assertEqual(g.default_speaker("te"), "Suhana")
        self.assertIn("Suhana", g.speakers("te"))
        self.assertNotIn("Girish", g.speakers("te"))
        v3 = providers.Gnani("timbre-v3.0")
        self.assertEqual(v3.default_speaker("te"), "Vasudha")
        self.assertEqual(providers.Gnani().model, "timbre-v3.0")
        self.assertEqual(len(v3.speakers("te")), 13)
        with self.assertRaisesRegex(ValueError, "unknown Gnani model"):
            providers.Gnani("timbre-v9")


try:
    from cevg_shell import server as mcp_server
except ImportError:  # the `mcp` package is optional
    mcp_server = None


@unittest.skipUnless(mcp_server and shutil.which("ffmpeg") and
                     ((ROOT / "target/release/cevg").is_file() or (ROOT / "target/release/cevg.exe").is_file()),
                     "needs the mcp package, ffmpeg and a built cevg")
class McpServer(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        base = Path(self.folder.name)
        self.studio = mcp_server.Studio(base / "videos", base / "cache", public_base="https://example.test/s")
        self.script = json.loads((ROOT / "examples" / "binary_search.json").read_text(encoding="utf-8"))
        self.script["canvas"]["width"], self.script["canvas"]["height"] = 480, 270

    def tearDown(self):
        self.folder.cleanup()

    def test_the_tools_are_listed_with_descriptions(self):
        import asyncio
        tools = asyncio.run(mcp_server.build(self.studio).list_tools())
        self.assertEqual([t.name for t in tools], ["guide", "validate", "preview", "figure", "estimate", "voices", "voice_sample", "render", "status"])
        self.assertTrue(all(t.description for t in tools))

    def test_guide_validate_and_preview(self):
        self.assertIn("teaching standard", self.studio.guide())
        self.assertTrue(self.studio.validate(self.script)["ok"])
        self.assertFalse(self.studio.validate({"version": 1})["ok"])
        self.assertTrue(self.studio.preview(self.script, None, None, 1.0, "te").startswith(b"\x89PNG"))

    def test_voices_are_listed_and_read_only_tools_are_marked(self):
        import asyncio
        listed = self.studio.voices()
        self.assertTrue(listed["service"].startswith("Gnani Timbre"))
        self.assertEqual(listed["default"], {"en": "Vasudha", "te": "Vasudha", "hi": "Vasudha"})
        self.assertEqual(len(listed["voices"]), 13)
        self.assertIn({"name": "Vasudha", "gender": "female", "language": "any", "suits": "composed; narration and e-learning"},
                      listed["voices"])
        tools = {t.name: t for t in asyncio.run(mcp_server.build(self.studio).list_tools())}
        for name in ("guide", "validate", "preview", "estimate", "voices", "status"):
            self.assertTrue(tools[name].annotations.read_only_hint, name)
        for name in ("render", "voice_sample"):
            self.assertFalse(tools[name].annotations.read_only_hint, name)

    def test_estimate_gives_length_and_outline(self):
        report = self.studio.estimate(self.script, "te")
        self.assertEqual(report["steps"], 7)
        self.assertEqual([o["scene"] for o in report["outline"]], ["setup", "first-check", "second-check"])
        self.assertTrue(15 < report["seconds"] < 45, report)
        self.assertNotIn("problem", report)
        self.assertIn("7 steps have no `ta`", self.studio.estimate(self.script, "ta")["problem"])

    def test_a_silent_render_job_runs_to_the_end(self):
        job = self.studio.render(self.script, "te", False, True, "", 1.0)
        for _ in range(600):
            report = self.studio.status(job.id)
            if report["state"] in ("done", "failed"):
                break
            time.sleep(0.1)
        self.assertEqual(report["state"], "done", report)
        self.assertTrue(Path(report["file"]).is_file())
        self.assertEqual(report["url"], f"https://example.test/s/videos/{job.id}.mp4")
        self.assertEqual(self.studio.status("nope")["state"], "unknown")

    def test_speech_is_refused_without_a_key_and_broken_scripts_before_rendering(self):
        saved = os.environ.pop("GNANI_API_KEY", None)
        try:
            with self.assertRaisesRegex(ValueError, "no GNANI_API_KEY"):
                self.studio.render(self.script, "en", True, False, "", 1.0)
            os.environ["GNANI_API_KEY"] = "test-key"
            with self.assertRaisesRegex(ValueError, "unknown voice `shubh`"):
                self.studio.render(self.script, "en", True, False, "shubh", 1.0)
            with self.assertRaisesRegex(ValueError, "pace 1.5 is outside"):
                self.studio.render(self.script, "en", True, False, "Vasudha", 1.5)
        finally:
            os.environ.pop("GNANI_API_KEY", None)
            if saved:
                os.environ["GNANI_API_KEY"] = saved
        with self.assertRaisesRegex(ValueError, "has errors"):
            self.studio.render({"version": 1}, "en", False, False, "", 1.0)


if __name__ == "__main__":
    unittest.main()


class Figures(unittest.TestCase):
    """Figures drawn from a prompt: the API is replaced by a stub, the renderer is real."""

    SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">'
           '<g id="a"><rect x="20" y="20" width="120" height="60" fill="#1c2230" stroke="#cfd6e4"/></g>'
           '<g id="b"><rect x="220" y="20" width="120" height="60" fill="#1c2230" stroke="#cfd6e4"/></g></svg>')

    def setUp(self):
        from cevg_shell import figures, narrate
        try:
            self.cevg = narrate.find_cevg(None)
        except Exception:
            self.skipTest("no cevg binary")
        self.figures = figures
        self.tmp = Path(tempfile.mkdtemp())
        self.calls = []
        replies = [self.SVG, "OK"]

        def fake(messages, model, key, max_tokens=16000, system=None):
            self.calls.append(messages)
            return replies.pop(0)
        self._real = figures._call
        figures._call = fake
        os.environ["ANTHROPIC_API_KEY"] = "test-key"

    def tearDown(self):
        self.figures._call = self._real
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def script(self):
        return {"version": 1, "title": "t", "objects": [{"id": "fig", "type": "figure", "region": "center", "prompt": "two boxes"}],
                "scenes": [{"id": "s", "steps": [{"say": {"en": "Go."}, "do": [{"action": "show", "target": "fig"}]}]}]}

    def test_a_prompt_is_drawn_checked_and_cached(self):
        out = self.figures.resolve(self.script(), self.cevg, self.tmp)
        self.assertEqual(out["objects"][0]["svg"], self.SVG)
        self.assertEqual(len(self.calls), 2)  # the drawing, then the review with the rendered picture
        review = self.calls[1][-1]["content"]
        self.assertEqual(review[0]["type"], "image")
        self.figures.resolve(self.script(), self.cevg, self.tmp)  # cached: no more calls
        self.assertEqual(len(self.calls), 2)

    def test_the_hosted_platform_only_uses_drawn_figures(self):
        with self.assertRaises(self.figures.FigureError):
            self.figures.resolve(self.script(), self.cevg, self.tmp, draw_missing=False)


class CreditsAndChannel(unittest.TestCase):
    """What a render costs, and the chapters the YouTube description gets."""

    def test_a_credit_covers_ten_minutes_and_silent_is_a_quarter(self):
        from cevg_shell import credits
        p = credits.DEFAULT_PLANS
        self.assertEqual(credits.cost(p, 7 * 60, True), 1)
        self.assertEqual(credits.cost(p, 10 * 60, True), 1)
        self.assertEqual(credits.cost(p, 10 * 60 + 5, True), 2)
        self.assertEqual(credits.cost(p, 7 * 60, False), 0.25)
        self.assertEqual(credits.cost(p, 15, True), 1)  # never free

    def test_chapters_follow_the_outline_scaled_to_the_real_length(self):
        from cevg_shell import youtube
        video = {"seconds": 600, "outline": [{"scene": "a", "seconds": 100, "opens_with": "Start here. More."},
                                              {"scene": "b", "seconds": 100, "opens_with": "The middle"},
                                              {"scene": "c", "seconds": 100, "opens_with": "The end."}]}
        self.assertEqual(youtube._chapters(video), ["0:00 Start here", "3:20 The middle", "6:40 The end"])
        self.assertEqual(youtube._chapters({"seconds": 60, "outline": video["outline"][:2]}), [])

    def test_the_credit_line_names_the_creator_but_not_vivaran_twice(self):
        from cevg_shell import youtube
        self.assertEqual(youtube.credit_line("Asha Rao", "asha-rao", "https://vivaran.tech/v/1"),
                         "Made by Asha Rao (@asha-rao) with Vivaran: https://vivaran.tech/v/1")
        self.assertEqual(youtube.credit_line("Vivaran", "vivaran", "https://vivaran.tech/v/1"),
                         "Made with Vivaran: https://vivaran.tech/v/1")

    def test_thumbnails_go_to_the_upload_host(self):
        from cevg_shell import youtube
        self.assertTrue(youtube.THUMBNAIL.startswith("https://www.googleapis.com/upload/youtube/v3/"))
