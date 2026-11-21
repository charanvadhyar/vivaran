"""A reviewer agent for scene scripts, on the Claude API.

The assistant in the user's chat writes the script; this reviewer reads it
the way an exacting examiner would, together with one drawn frame per scene,
and says what must change before it is rendered: wrong facts or arithmetic,
working a student could not redo in an exam, drifting off what the user
asked for, narration that does not match the picture, and length. The
assistant fixes what it flags and asks again, so the two loop until the
script passes. The platform will not render a script that has not passed
(see `hosted.Platform._review_gate`).

The reviewer judges by the same rules the writer was given: the teaching
standard, planning, length and narration sections of the authoring guide.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable

from . import figures

MAX_FRAMES = 8

SYSTEM = """You review scene scripts for Vivaran, which turns an explanation of a computer science or
mathematics topic into an animated, narrated video for Indian university students preparing for exams.
Another assistant wrote the script; you are the examiner and editor who must catch what is wrong before
students see it. Be exacting and concrete. Do not praise.

You get: what the user asked for, the length they chose, the estimated length, the narration of every
step with what that step does on screen, the full script JSON, one drawn frame per scene (the end of the
scene), and the authoring rules the writer was given.

Check, in this order:
1. Correctness. Every definition, claim and formula. Redo every worked example yourself, step by step,
   and compare each number, index, comparison and result with the script. One wrong number is blocking.
2. The exam standard. Could a student redo the working from the video alone, as the rules require? A
   skipped step, an unexplained jump, or a missing standard figure the exam expects is blocking.
3. The brief. Does it teach what the user asked, at the level and in the language they asked? Drift,
   padding or a different topic is blocking.
4. Narration against the picture. At each step, does the narration describe what is on screen then?
   A highlight, pointer or value that contradicts the narration is blocking. In a frame, overlapping or
   unreadable text, or something cut off, is blocking.
5. Length. More than about 15% off the chosen length is blocking; say which scenes to cut or expand.
6. Narration quality: written to be spoken, numbers in words where the rules say so, the code-mixed
   style for Hindi and Telugu (English technical terms in Latin letters). Problems here are minor
   unless they would mislead.

Recompute the working yourself before you judge it. Your answer is only this JSON, in a ```json block,
with nothing before or after it:
{"verdict": "pass" | "revise",
 "summary": "one or two sentences for the user",
 "scores": {"correctness": 1-5, "exam_standard": 1-5, "on_brief": 1-5, "narration_matches_picture": 1-5, "length": 1-5},
 "issues": [{"severity": "blocking" | "minor", "where": "scene <id>, step <n> (counting from 0)" or "whole script",
             "problem": "what is wrong, with the correct value where it is a number",
             "fix": "exactly what to change"}]}
The verdict is "pass" only when there is no blocking issue. List at most 12 issues, blocking first."""

RULE_SECTIONS = ("Planning scenes", "The teaching standard", "Length", "Writing narration", "Common mistakes")


class ReviewError(Exception):
    pass


def script_hash(script: dict[str, Any]) -> str:
    """The same script, however its keys are ordered, has the same hash."""
    return hashlib.sha256(json.dumps(script, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def rules(guide: str) -> str:
    """The parts of the authoring guide the reviewer judges by."""
    parts = re.split(r"(?m)^## ", guide)
    keep = [p for p in parts if p.startswith(RULE_SECTIONS)]
    return "\n\n".join("## " + p.strip() for p in keep)


def _steps(script: dict[str, Any], language: str) -> str:
    lines = []
    for scene in script.get("scenes", []):
        lines.append(f"Scene {scene.get('id')}:")
        for i, step in enumerate(scene.get("steps", [])):
            say = step.get("say", {})
            text = say.get(language) or say.get("en") or ""
            acts = "; ".join(json.dumps(a, ensure_ascii=False, separators=(",", ":")) for a in step.get("do", []))
            lines.append(f"  step {i}: \"{text}\"\n    on screen: {acts or '(nothing changes)'}")
    return "\n".join(lines)


def review(script: dict[str, Any], brief: str, *, language: str, target_minutes: float | None,
           estimate: dict[str, Any], guide: str, frame: Callable[[str], bytes], model: str | None = None) -> dict[str, Any]:
    """Review a script. `frame(scene_id)` draws the end of a scene as PNG."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise ReviewError("the reviewer needs ANTHROPIC_API_KEY on the render server")
    scenes = [s.get("id") for s in script.get("scenes", [])]
    if len(scenes) > MAX_FRAMES:  # spread the frames across the video
        scenes = [scenes[round(i * (len(scenes) - 1) / (MAX_FRAMES - 1))] for i in range(MAX_FRAMES)]
    head = (f"What the user asked for: {brief.strip() or '(not given)'}\n"
            f"Length they chose: {f'{target_minutes:g} minutes' if target_minutes else 'not given'}\n"
            f"Estimated length: {estimate.get('minutes')} minutes ({estimate.get('steps')} steps)\n"
            f"Narration language: {language}\n\n"
            f"Steps:\n{_steps(script, language)}\n\n")
    with_rules = f"The authoring rules the writer was given:\n{rules(guide)}\n\n"
    full = f"The full script:\n{json.dumps(script, ensure_ascii=False)}"
    content: list[dict[str, Any]] = [{"type": "text", "text": head + with_rules + full}]
    for scene in scenes:
        try:
            png = frame(scene)
        except Exception as e:  # a frame that will not draw is itself worth reporting
            content.append({"type": "text", "text": f"Frame for scene {scene}: could not be drawn ({e})."})
            continue
        content.append({"type": "text", "text": f"Frame at the end of scene {scene}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                     "data": base64.b64encode(png).decode()}})
    model = model or os.environ.get("CEVG_REVIEW_MODEL") or os.environ.get("CEVG_FIGURE_MODEL") or figures.DEFAULT_MODEL
    # On 21 Nov 2026 the API declined reviews with stop_reason "refusal", category
    # "reasoning_extraction": the prompt asked the model to write out its reasoning inside
    # <analysis> tags, which the API treats as an attempt to extract the model's reasoning. The prompt
    # now asks for the verdict alone. If a request is still declined, step down through smaller ones
    # and log which is accepted.
    attempts = [
        ("full, with frames", content, SYSTEM),
        ("text only", [{"type": "text", "text": head + with_rules + full}], SYSTEM),
        ("text, no rules", [{"type": "text", "text": head + full}], SYSTEM),
        ("steps only", [{"type": "text", "text": head}], SYSTEM),
        ("steps only, short system", [{"type": "text", "text": head + SHORT_FORMAT}], SHORT_SYSTEM),
    ]
    for name, blocks, system in attempts:
        reply, stop = _call(blocks, model, key, max_tokens=32000, system=system)
        print(f"review: {name}: stop_reason={stop}, {len(reply)} chars (model {model})", flush=True)
        if stop != "refusal" and reply.strip():
            break
    else:
        raise ReviewError(f"the Claude API declined to review this script (stop_reason {stop}) in every form "
                          "tried; this is a problem on Vivaran's side, not in the script")
    try:
        return parse(reply, model)
    except ReviewError:
        # Log what came back, so a failure can be understood, then ask once more for the JSON alone.
        print(f"review: no verdict in the reply (stop_reason={stop}, {len(reply)} chars): ...{reply[-400:]!r}", flush=True)
    # Only a reply with a review in it can be turned into a verdict; never judge from nothing.
    repair = [{"type": "text", "text": (
        "Here is a review of a video script. Give its verdict as the JSON described in your instructions, "
        "in a ```json block, and nothing else. If the review was cut off, judge from what it says; any "
        "error it found in the working is blocking.\n\n" + reply[-24000:])}]
    reply2, stop2 = _call(repair, model, key, max_tokens=4000)
    try:
        return parse(reply2, model)
    except ReviewError:
        print(f"review: repair failed too (stop_reason={stop2}): ...{reply2[-400:]!r}", flush=True)
        raise ReviewError("the reviewer did not return a verdict (the reply was "
                          f"{'cut off' if stop == 'max_tokens' else 'not in the expected form'}); "
                          "this is a problem on Vivaran's side, not in the script") from None


SHORT_SYSTEM = ("You check scripts for short educational videos on computer science and mathematics for "
                "university students: whether the facts and worked examples are correct and complete.")
SHORT_FORMAT = ("\nCheck each step for errors. Answer with only this JSON in a ```json block: "
                '{"verdict": "pass" or "revise", "summary": "...", "scores": {"correctness": 1-5, "exam_standard": '
                '1-5, "on_brief": 1-5, "narration_matches_picture": 1-5, "length": 1-5}, "issues": [{"severity": '
                '"blocking" or "minor", "where": "scene <id>, step <n>", "problem": "...", "fix": "..."}]}. '
                'The verdict is "pass" only when no issue is blocking.')


def _call(content: list[dict[str, Any]], model: str, key: str, max_tokens: int,
          system: str | None = None) -> tuple[str, str]:
    """One request to the Messages API: the reply's text and why it stopped."""
    body = json.dumps({"model": model, "max_tokens": max_tokens, "system": system or SYSTEM,
                       "messages": [{"role": "user", "content": content}]}).encode()
    request = urllib.request.Request(figures.API_URL, data=body, method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                data = json.loads(response.read())
            text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            if data.get("stop_reason") == "refusal":
                # Everything but the content, in case the API says why.
                print("review: refusal response: " + json.dumps({k: v for k, v in data.items() if k != "content"})[:600],
                      flush=True)
            return text, str(data.get("stop_reason"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise ReviewError(f"the Claude API refused the review request ({e.code}): {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise ReviewError(f"cannot reach the Claude API: {getattr(e, 'reason', e)}") from None
    raise ReviewError("the Claude API did not answer")


def _verdict_json(reply: str) -> dict[str, Any] | None:
    """The last JSON object in the reply that has a verdict: from ```json blocks first, then any object."""
    for block in reversed(re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", reply, flags=re.S)):
        try:
            data = json.loads(block)
            if isinstance(data, dict) and "verdict" in data:
                return data
        except json.JSONDecodeError:
            pass
    decoder = json.JSONDecoder()
    for m in reversed(list(re.finditer(r"\{", reply))):
        try:
            data, _ = decoder.raw_decode(reply, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "verdict" in data:
            return data
    return None


def parse(reply: str, model: str = "") -> dict[str, Any]:
    """The reviewer's JSON, made consistent: the verdict follows the blocking issues."""
    data = _verdict_json(reply)
    if data is None:
        raise ReviewError("the reviewer did not return its verdict; try again")
    issues = [i for i in data.get("issues", []) if isinstance(i, dict)][:12]
    for i in issues:
        i["severity"] = "blocking" if str(i.get("severity", "")).lower() == "blocking" else "minor"
    blocking = sum(i["severity"] == "blocking" for i in issues)
    return {"verdict": "revise" if blocking else "pass", "summary": str(data.get("summary", ""))[:600],
            "scores": data.get("scores", {}), "issues": issues, "blocking": blocking, "model": model}
