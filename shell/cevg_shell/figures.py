"""Figures drawn by the Claude API.

A `figure` object in a scene script can give a `prompt` ("the ANSI/SPARC
three-schema architecture, built level by level") instead of `svg`. Before a
preview or a render, this module has Claude draw the SVG, then checks the
drawing: `cevg figure` rasterises it exactly as the renderer will, and Claude
looks at the picture and corrects overlaps, clipped text or a wrong layout.
Finished figures are cached by prompt, so each one is drawn once.

Environment:
    ANTHROPIC_API_KEY     required to draw figures
    CEVG_FIGURE_MODEL     the model to draw with (default below)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-opus-5-5"
STYLE_VERSION = "1"  # change when the style rules change, so cached figures are redrawn
ROUNDS = 3  # drawings, counting the first: at most two corrections

STYLE = """\
You draw figures for narrated teaching videos about computer science and mathematics. The figure
must look like the standard textbook figure for its topic, so a student recognises it and can redraw
it in an exam, but it must be your own drawing, never a copy of a particular book's figure.

Reply with one SVG document and nothing else: no prose, no Markdown fences.

Canvas and style:
- <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">. No width/height other than these.
- Transparent background: never paint a full-canvas background rectangle. The video's background
  is dark navy (#0f121a).
- Colours: boxes fill #1c2230 with stroke #cfd6e4 (2-3 px); bands or regions fill #161c28 with stroke
  #3a4458; text #e8ecf4; secondary text #8b95a9; the single accent, used sparingly, #f5b83d.
- Text: font-family="sans-serif" only. Sizes 20-34 px; nothing smaller than 18 px. Use
  font-weight="600" for labels in boxes. Centre text in boxes with text-anchor="middle" and leave at
  least 14 px of padding; break long labels into two <text> lines rather than shrinking them.
- Use plain ASCII and common Latin punctuation in text. Draw arrows as lines with markers, never as
  text glyphs such as an arrow character.
- Arrows: <line> or <path> with marker-end (and marker-start for two-way links) defined in <defs>.
  Arrows must start and end on box edges, not inside boxes, and must not cross text.
- Keep 40 px of margin inside the canvas. No element may overlap another unless it is meant to sit
  on it (a box on a band).
- Never use <image>, <foreignObject>, <script>, external fonts, CSS @import or links of any kind.

Parts:
- Put every logical piece of the figure in its own top-level <g id="..."> (a direct child of <svg>),
  in the order a teacher would draw them on a board. Ids: lowercase letters, digits and underscores,
  such as id="conceptual_level". The video reveals and highlights these groups one by one.
- Keep each group compact: a box and its own label belong together; an arrow and its label belong
  together. Do not put far-apart things in one group.
- Shared definitions go in <defs>, outside the groups.
"""

REVIEW = """\
This is the figure you drew, rendered exactly as the video will show it on a dark background.
Its parts are: {parts}.
The request was: {prompt}

Check it carefully against the request and the style rules: text overlapping lines or other text,
text running outside its box, arrows that miss their boxes or pass through text, anything clipped at
the canvas edge, unreadable sizes, a layout that differs from the standard textbook figure, wrong
labels or facts, and parts that are not compact.
{problems}
If the figure is right, reply with exactly: OK
Otherwise reply with the complete corrected SVG document and nothing else."""


class FigureError(Exception):
    pass


def _api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise FigureError("this server has no ANTHROPIC_API_KEY, so it cannot draw figures from a prompt; "
                          "give the figure's `svg` instead")
    return key


def _call(messages: list[dict[str, Any]], model: str, key: str, max_tokens: int = 16000) -> str:
    body = json.dumps({"model": model, "max_tokens": max_tokens, "system": STYLE, "messages": messages}).encode()
    request = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                data = json.loads(response.read())
            return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise FigureError(f"the Claude API refused the figure request ({e.code}): {detail}") from None
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise FigureError(f"cannot reach the Claude API: {e.reason}") from None
    raise FigureError("the Claude API did not answer")


def _svg_in(text: str) -> str | None:
    m = re.search(r"<svg\b.*?</svg>", text, flags=re.S)
    return m.group(0) if m else None


def _rasterise(cevg: str, svg: str) -> tuple[bytes, dict[str, Any]]:
    """Draw the SVG exactly as the renderer will, on the video background."""
    with tempfile.TemporaryDirectory(prefix="cevg-fig-") as tmp:
        src, png = Path(tmp) / "f.svg", Path(tmp) / "f.png"
        src.write_text(svg, encoding="utf-8")
        done = subprocess.run([cevg, "figure", str(src), "--width", "1600", "--dark", "-o", str(png)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        if done.returncode != 0:
            raise FigureError((done.stderr or done.stdout).strip().splitlines()[0] if (done.stderr or done.stdout) else "cevg figure failed")
        info = json.loads(done.stdout.strip().splitlines()[-1])
        return png.read_bytes(), info


def draw(prompt: str, cevg: str, *, model: str | None = None, log: Callable[[str], None] = lambda m: None) -> dict[str, Any]:
    """Draw one figure from a prompt and check it. Returns svg, parts, png and how many rounds it took."""
    key = _api_key()
    model = model or os.environ.get("CEVG_FIGURE_MODEL", DEFAULT_MODEL)
    messages: list[dict[str, Any]] = [{"role": "user", "content": f"Draw this figure:\n{prompt}"}]
    svg, png, info = None, b"", {}
    for round_ in range(1, ROUNDS + 1):
        reply = _call(messages, model, key)
        found = _svg_in(reply)
        if found is None:
            if svg is not None and reply.strip().upper().startswith("OK"):
                return {"svg": svg, "parts": info.get("parts", []), "png": png, "rounds": round_ - 1}
            if svg is None:
                raise FigureError("the Claude API did not return an SVG for the figure")
            break
        svg = found
        try:
            png, info = _rasterise(cevg, svg)
            problems = info.get("problems", [])
        except FigureError as e:
            png, info, problems = b"", {}, [str(e)]
        log(f"figure: round {round_}, parts {', '.join(info.get('parts', [])) or 'none'}")
        if round_ == ROUNDS:
            break
        listed = "".join(f"\n- {p}" for p in problems)
        note = f"\nThe renderer also reported:{listed}\n" if problems else ""
        content: list[dict[str, Any]] = []
        if png:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                          "data": base64.b64encode(png).decode()}})
        content.append({"type": "text", "text": REVIEW.format(parts=", ".join(info.get("parts", [])) or "none",
                                                              prompt=prompt, problems=note)})
        messages += [{"role": "assistant", "content": svg}, {"role": "user", "content": content}]
    if svg is None or not png:
        raise FigureError("the figure could not be drawn cleanly; give its `svg` or reword the prompt")
    return {"svg": svg, "parts": info.get("parts", []), "png": png, "rounds": ROUNDS}


def _key_for(prompt: str, model: str) -> str:
    return hashlib.sha256(f"{STYLE_VERSION}\n{model}\n{prompt.strip()}".encode()).hexdigest()[:24]


def cache_path(prompt: str, cache_dir: Path) -> Path:
    model = os.environ.get("CEVG_FIGURE_MODEL", DEFAULT_MODEL)
    return Path(cache_dir) / "figures" / f"{_key_for(prompt, model)}.json"


def cached_draw(prompt: str, cevg: str, cache_dir: Path, *, log: Callable[[str], None] = lambda m: None,
                draw_missing: bool = True) -> dict[str, Any]:
    model = os.environ.get("CEVG_FIGURE_MODEL", DEFAULT_MODEL)
    path = cache_path(prompt, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if not draw_missing:
        raise FigureError("this figure has not been drawn yet: call the `figure` tool with its prompt first, "
                          "then use the same prompt here (or put the returned `svg` in the figure)")
    result = draw(prompt, cevg, model=model, log=log)
    saved = {"svg": result["svg"], "parts": result["parts"], "prompt": prompt, "model": model, "rounds": result["rounds"]}
    path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
    return saved


def resolve(script: dict[str, Any], cevg: str, cache_dir: Path, *, log: Callable[[str], None] = lambda m: None,
            draw_missing: bool = True) -> dict[str, Any]:
    """A copy of the script in which every prompt-only figure has its `svg` drawn."""
    todo = [o for o in script.get("objects", []) if o.get("type") == "figure" and o.get("prompt") and not o.get("svg")]
    if not todo:
        return script
    script = json.loads(json.dumps(script))
    for obj in script.get("objects", []):
        if obj.get("type") == "figure" and obj.get("prompt") and not obj.get("svg"):
            log(f"drawing figure `{obj.get('id')}`")
            obj["svg"] = cached_draw(obj["prompt"], cevg, cache_dir, log=log, draw_missing=draw_missing)["svg"]
    return script
