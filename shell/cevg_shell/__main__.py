"""Command line for the CEVG shell.

    python -m cevg_shell narrate script.json -o out.mp4 --lang te --listen
    python -m cevg_shell check --lang te --speaker Suhana --listen
    python -m cevg_shell voices

The voice service is Gnani (Timbre speaks, Prisma listens back) unless
CEVG_TTS=sarvam. Keys are read from GNANI_API_KEY or SARVAM_API_KEY and
never written to disk, to the cache or to any output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import providers
from .narrate import NarrateError, narrate
from .voice import StandInVoice


def _voice(args) -> object:
    if args.dry_run:
        return StandInVoice()
    provider = providers.current(args.service)
    provider.check(args.speaker, args.lang, args.pace)
    if provider.name == "sarvam":
        return provider.voice(args.speaker, args.pace, requests_per_minute=args.rate,
                              temperature=args.temperature, preprocess=args.preprocess)
    return provider.voice(args.speaker, args.pace)


def _add_voice_options(p: argparse.ArgumentParser) -> None:
    p.add_argument("--lang", default="en", help="narration language: en, hi, te, ta, kn, ml, mr, pa, bn, gu")
    p.add_argument("--service", default=None, help="gnani or sarvam (default: $CEVG_TTS, else gnani)")
    p.add_argument("--speaker", "--voice", dest="speaker", default=None,
                   help="a voice name; see `voices` (default: the service's narration voice for the language)")
    p.add_argument("--pace", type=float, default=1.0, help="speaking speed (Gnani 0.85 to 1.15, Sarvam 0.5 to 2.0)")
    p.add_argument("--listen", action="store_true", help="Gnani: have Prisma transcribe each clip and flag lines that do not match")
    p.add_argument("--temperature", type=float, default=None, help="Sarvam only: expressiveness, 0.01 to 2.0")
    p.add_argument("--preprocess", action="store_true", help="Sarvam only: let Sarvam normalise numbers")
    p.add_argument("--rate", type=float, default=30, help="Sarvam only: requests per minute your plan allows")
    p.add_argument("--dry-run", action="store_true", help="no key, no network: stand-in audio of about the right length")


def main(argv: list[str] | None = None) -> int:
    # A Windows console may not be able to show Telugu or Hindi; never fail on printing.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(prog="cevg_shell", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    n = sub.add_parser("narrate", help="render a script as a narrated video")
    n.add_argument("script", type=Path)
    n.add_argument("-o", "--out", type=Path, default=Path("narrated.mp4"))
    n.add_argument("--captions", action="store_true", help="also show the narration under the picture")
    n.add_argument("--cache", type=Path, default=Path(".cevg-cache"), help="where spoken lines are kept between runs")
    n.add_argument("--cevg", default=None, help="path to the cevg program (default: $CEVG_BIN, PATH, target/release)")
    _add_voice_options(n)

    c = sub.add_parser("check", help="speak one sentence, to test the key, a language and a voice")
    c.add_argument("--text", default=None, help="what to say (default: a short sentence in the language)")
    c.add_argument("-o", "--out", type=Path, default=Path("check.wav"))
    _add_voice_options(c)

    v = sub.add_parser("voices", aliases=["speakers"], help="list the voices of the voice service")
    v.add_argument("--service", default=None, help="gnani or sarvam (default: $CEVG_TTS, else gnani)")
    v.add_argument("--lang", default=None, help="only voices that suit this language")

    m = sub.add_parser("serve", help="run the MCP server, for Claude, ChatGPT and other assistants")
    m.add_argument("--http", action="store_true", help="serve over HTTP (for ChatGPT and claude.ai) instead of stdio")
    m.add_argument("--host", default="127.0.0.1")
    m.add_argument("--port", type=int, default=8765)
    m.add_argument("--public-url", default=None, help="the https address of your tunnel or host, for video links")
    m.add_argument("--secret", default=None, help="the secret part of the address (default: $CEVG_SECRET, or a new one)")
    m.add_argument("--out", type=Path, default=Path.home() / "cevg-videos", help="where videos are kept")
    m.add_argument("--cache", type=Path, default=Path.home() / ".cevg-cache", help="where spoken lines are kept")
    m.add_argument("--cevg", default=None, help="path to the cevg program")
    m.add_argument("--rate", type=float, default=30, help="Sarvam requests per minute your plan allows")

    d = sub.add_parser("slides", help="turn a script into a slide deck, one slide per step, narration in the notes")
    d.add_argument("script", type=Path)
    d.add_argument("-o", "--out", type=Path, default=Path("slides.pptx"))
    d.add_argument("--lang", default="en", help="which narration goes in the notes")
    d.add_argument("--frames", default="formula", choices=("formula", "1", "2", "3"),
                   help="per step: formula = the formula and then the output with numbers in (default); 1-3 = that many exact states")
    d.add_argument("--no-dividers", action="store_true", help="no section slide before each scene")
    d.add_argument("--no-title", action="store_true", help="no title slide")
    d.add_argument("--subtitle", default=None, help="the line under the title on the title slide")
    d.add_argument("--front", type=Path, default=None, help="a JSON list of text slides to put before the pictures (heading, lead, points, callout)")
    d.add_argument("--back", type=Path, default=None, help="a JSON list of text slides to put after the pictures")
    d.add_argument("--pick", default=None, help="only these steps, finished: scene:step,... (add @n for the state after n actions)")
    d.add_argument("--cevg", default=None, help="path to the cevg program")

    h = sub.add_parser("serve-platform", help="run the multi-user MCP server beside the website")
    h.add_argument("--host", default="127.0.0.1")
    h.add_argument("--port", type=int, default=8765)

    args = parser.parse_args(argv)
    try:
        if args.command == "slides":
            try:
                from . import slides
            except ImportError:
                print("cevg_shell: the slides command needs python-pptx; run: pip install python-pptx", file=sys.stderr)
                return 2
            def show(message: str) -> None:
                print(f"\r{message:<48}", end="", file=sys.stderr, flush=True)
            result = slides.build(args.script, args.out, language=args.lang, cevg=args.cevg, dividers=not args.no_dividers, frames=args.frames if args.frames == "formula" else int(args.frames),
                                  title=not args.no_title, pick=slides.parse_pick(args.pick) if args.pick else None,
                                  front=json.loads(args.front.read_text(encoding="utf-8")) if args.front else None,
                                  back=json.loads(args.back.read_text(encoding="utf-8")) if args.back else None,
                                  subtitle=args.subtitle, progress=show)
            print(file=sys.stderr)
            print(f"wrote {result['file']}: {result['slides']} slides for {result['steps']} steps in {result['scenes']} parts")
            return 0

        if args.command == "serve-platform":
            try:
                from . import hosted
            except ImportError as e:
                print(f"cevg_shell: {e}; run: pip install \"mcp>=2.3\" \"psycopg[binary]\"", file=sys.stderr)
                return 2
            hosted.serve(args.host, args.port)
            return 0

        if args.command == "serve":
            try:
                from . import server
            except ImportError:
                print("cevg_shell: the MCP server needs the `mcp` package; run: pip install \"mcp>=2.3\"", file=sys.stderr)
                return 2
            if args.http:
                server.serve_http(args.out, args.cache, cevg=args.cevg, host=args.host, port=args.port,
                                  public_url=args.public_url, secret=args.secret, requests_per_minute=args.rate)
            else:
                server.serve_stdio(server.Studio(args.out, args.cache, args.cevg, requests_per_minute=args.rate))
            return 0

        if args.command in ("voices", "speakers"):
            provider = providers.current(args.service)
            info = provider.describe()
            print(f"{info['service']}: default " + ", ".join(f"{k} {v}" for k, v in info["default"].items()))
            for entry in info["voices"]:
                if args.lang and entry.get("language") not in ("any", args.lang):
                    continue
                print("  " + "  ".join(str(entry.get(k, "")) for k in ("name", "gender", "language", "suits")).rstrip())
            return 0

        if args.command == "check":
            samples = {
                "en": "This is a test of the narration voice.",
                "hi": "यह narration की आवाज़ का एक परीक्षण है।",
                "te": "ఇది narration voice కోసం ఒక పరీక్ష.",
            }
            text = args.text or samples.get(args.lang, samples["en"])
            voice = _voice(args)
            audio = voice.speak(text, args.lang)
            args.out.write_bytes(audio)
            print(f"wrote {args.out}: \"{text}\"")
            if args.listen and hasattr(voice, "listen"):
                score, heard = voice.listen(audio, text, args.lang)
                print(f"heard ({score:.0%} of the words): \"{heard}\"")
            return 0

        def show(message: str) -> None:
            print(f"\r{message:<40}", end="", file=sys.stderr, flush=True)

        result = narrate(args.script, args.out, _voice(args), language=args.lang, cache_dir=args.cache,
                         cevg=args.cevg, burn_captions=args.captions, listen=args.listen, progress=show)
        print(file=sys.stderr)
        minutes, seconds = divmod(round(result.seconds), 60)
        print(f"wrote {result.video} ({minutes} min {seconds} s, {result.steps} steps) and {result.captions}")
        print(f"voice: {result.spoken} lines spoken, {result.reused} reused from the cache, "
              f"{result.characters} characters of narration in all")
        if result.heard is not None:
            doubtful = result.doubtful()
            checked = sum(1 for h in result.heard if h.get("match") is not None)
            print(f"listened back to {checked} of {result.steps} lines: {len(doubtful)} to check by ear")
            for h in doubtful:
                print(f"  step {h['step']} ({h['match']:.0%}): said \"{h['said']}\"\n      heard \"{h['heard']}\"")
        return 0
    except providers.VoiceError as e:
        print(f"\ncevg_shell: {e}\n{e.advice()}", file=sys.stderr)
        return 1
    except (NarrateError, ValueError) as e:
        print(f"\ncevg_shell: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
