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

from cevg_shell import sarvam
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
        self.assertEqual([t.name for t in tools], ["guide", "validate", "preview", "estimate", "voices", "voice_sample", "render", "status"])
        self.assertTrue(all(t.description for t in tools))

    def test_guide_validate_and_preview(self):
        self.assertIn("teaching standard", self.studio.guide())
        self.assertTrue(self.studio.validate(self.script)["ok"])
        self.assertFalse(self.studio.validate({"version": 1})["ok"])
        self.assertTrue(self.studio.preview(self.script, None, None, 1.0, "te").startswith(b"\x89PNG"))

    def test_voices_are_listed_and_read_only_tools_are_marked(self):
        import asyncio
        listed = self.studio.voices()
        self.assertEqual(listed["default"], "shubh")
        self.assertEqual(len(listed["female_sounding_names"]) + len(listed["male_sounding_names"]), 37)
        self.assertIn("kavya", listed["female_sounding_names"])
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
        job = self.studio.render(self.script, "te", False, True, "shubh", 1.0)
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
        saved = os.environ.pop("SARVAM_API_KEY", None)
        try:
            with self.assertRaisesRegex(ValueError, "no SARVAM_API_KEY"):
                self.studio.render(self.script, "en", True, False, "shubh", 1.0)
        finally:
            if saved:
                os.environ["SARVAM_API_KEY"] = saved
        with self.assertRaisesRegex(ValueError, "has errors"):
            self.studio.render({"version": 1}, "en", False, False, "shubh", 1.0)


if __name__ == "__main__":
    unittest.main()
