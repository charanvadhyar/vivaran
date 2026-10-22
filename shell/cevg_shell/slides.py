"""Turn a scene script into a slide deck: one slide per step.

Each slide is the picture at the end of that step, full-bleed, with the
narration as speaker notes. Section dividers mark the scenes. The deck is
what a teacher takes into a classroom when they would rather talk over the
pictures themselves than play the video.

Needs `pip install python-pptx`.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .narrate import NarrateError, find_cevg

# The videos' own palette, so the title slides match the frames.
SLATE = RGBColor(0x10, 0x13, 0x1C)
CHALK = RGBColor(0xEE, 0xF0, 0xF4)
MUTED = RGBColor(0xAA, 0xB2, 0xC2)
AMBER = RGBColor(0xF2, 0xB0, 0x3D)

WIDTH, HEIGHT = Inches(13.333), Inches(7.5)  # 16:9


def _scene_title(scene: dict) -> str:
    """A scene has no title of its own; its id, written out, serves."""
    return scene["id"].replace("-", " ").replace("_", " ").capitalize()


def _text(slide, left, top, width, height, text, size, color, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return box


def _fill(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _moments(actions: int, frames: int) -> list[int]:
    """Which exact states of a step to show, as counts of actions complete.
    Two frames: half the actions done, then all of them. Three: a third, two thirds, all."""
    if frames <= 1 or actions <= 1:
        return [actions]
    if frames == 2:
        return [max(1, actions // 2), actions]
    return sorted({max(1, actions // 3), max(1, (2 * actions) // 3), actions})


CHANGES_CONTENT = {"set", "replace", "write", "reveal"}


def _formula_and_output(step: dict, math_ids: set[str]) -> list[int]:
    """The two states that matter when a step works a formula: the formula as written, and the
    output once numbers have gone in. Found from the actions on math objects:
    the state just before the first action that changes a formula's content (or just after the
    action that shows it, when the step shows it first), and the end of the step. A step that
    changes no formula gives only its end."""
    actions = step.get("do", [])
    intro = change = None
    for i, action in enumerate(actions):
        target = str(action.get("target", "")).split("[")[0].split(".")[0]
        if target not in math_ids:
            continue
        kind = action.get("action")
        if kind == "show" and intro is None:
            intro = i
        elif kind in CHANGES_CONTENT and change is None:
            change = i
    end = len(actions)
    if change is None:
        return [end]
    formula = intro + 1 if intro is not None and intro < change else change
    return [formula, end] if formula != end else [end]


def parse_pick(text: str) -> list[tuple[str, int, int | None]]:
    """`scene:step` items, comma separated, each with an optional `@n` (actions done): "centre:4,kept:2@1"."""
    picks = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        where, _, after = item.partition("@")
        scene, _, step = where.partition(":")
        if not scene or not step.isdigit() or (after and not after.isdigit()):
            raise NarrateError(f"`{item}` is not a step; write scene:step, for example centre:4 or kept:2@1")
        picks.append((scene, int(step), int(after) if after else None))
    return picks


def _front_slide(deck, blank, spec: dict) -> None:
    """A text slide before the pictures: heading, a lead sentence, points, and a callout on the right.
    spec = {"heading", "lead"?, "points"?: [..], "callout"?: {"big", "small"}, "notes"?}"""
    slide = deck.slides.add_slide(blank)
    _fill(slide, SLATE)
    has_callout = bool(spec.get("callout"))
    text_w = Inches(7.4) if has_callout else Inches(11.3)
    _text(slide, Inches(1), Inches(0.9), text_w, Inches(1.2), spec.get("heading", ""), 32, CHALK, bold=True)
    y = Inches(2.1)
    if spec.get("lead"):
        _text(slide, Inches(1), y, text_w, Inches(1.4), spec["lead"], 18, MUTED)
        y += Inches(1.5)
    points = spec.get("points") or []
    if points:
        box = slide.shapes.add_textbox(Inches(1), y, text_w, Inches(7.5) - y - Inches(0.8))
        frame = box.text_frame
        frame.word_wrap = True
        for i, point in enumerate(points):
            paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            paragraph.space_after = Pt(10)
            head, _, rest = point.partition(": ")
            lead_run = paragraph.add_run()
            lead_run.text = (head + ": ") if rest else point
            lead_run.font.size, lead_run.font.bold, lead_run.font.name = Pt(16), True, "Calibri"
            lead_run.font.color.rgb = AMBER if rest else CHALK
            if rest:
                run = paragraph.add_run()
                run.text = rest
                run.font.size, run.font.name = Pt(16), "Calibri"
                run.font.color.rgb = CHALK
    if has_callout:
        big, small = spec["callout"].get("big", ""), spec["callout"].get("small", "")
        card = slide.shapes.add_shape(1, Inches(9.1), Inches(2.1), Inches(3.3), Inches(3.3))  # 1 = rectangle
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(0x1C, 0x22, 0x30)
        card.line.color.rgb = RGBColor(0x3B, 0x45, 0x59)
        _text(slide, Inches(9.3), Inches(2.6), Inches(2.9), Inches(1.4), big, 48, AMBER, bold=True, align=PP_ALIGN.CENTER)
        _text(slide, Inches(9.3), Inches(4.0), Inches(2.9), Inches(1.2), small, 14, MUTED, align=PP_ALIGN.CENTER)
    if spec.get("notes"):
        slide.notes_slide.notes_text_frame.text = spec["notes"]


def build(script_path: Path, out: Path, language: str = "en", cevg: str | None = None, dividers: bool = True,
          frames: int | str = "formula", title: bool = True, pick: list[tuple[str, int, int | None]] | None = None,
          front: list[dict] | None = None, back: list[dict] | None = None, subtitle: str | None = None,
          progress=lambda message: None) -> dict:
    """Write the deck. `frames` is "formula" (the formula as written and the output with the numbers
    in, for steps that work a formula; otherwise the end of the step) or 1 to 3 pictures per step at
    exact states part way through its actions and at its end. Identical pictures are dropped.
    Returns a summary: slides, steps, scenes."""
    if frames not in (1, 2, 3, "formula"):
        raise NarrateError("frames per step must be 1, 2, 3 or formula")
    script_path, out = Path(script_path), Path(out)
    binary = find_cevg(cevg)
    script = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = script.get("scenes", [])
    math_ids = {o["id"] for o in script.get("objects", []) if o.get("type") == "math"}
    if not scenes:
        raise NarrateError("the script has no scenes")

    deck = Presentation()
    deck.slide_width, deck.slide_height = WIDTH, HEIGHT
    blank = deck.slide_layouts[6]

    steps_total = sum(len(s.get("steps", [])) for s in scenes)
    made = 0
    if pick:
        known = {(sc["id"], i) for sc in scenes for i in range(len(sc.get("steps", [])))}
        for scene_id, step, _ in pick:
            if (scene_id, step) not in known:
                raise NarrateError(f"there is no step {scene_id}:{step}; scenes are {', '.join(sc['id'] for sc in scenes)}")
        chosen = {(scene_id, step): after for scene_id, step, after in pick}
        dividers = False
    else:
        chosen = None

    if title:
        slide = deck.slides.add_slide(blank)
        _fill(slide, SLATE)
        _text(slide, Inches(1), Inches(2.4), Inches(11.3), Inches(1.6), str(script.get("title", "Untitled")), 40, CHALK, bold=True)
        _text(slide, Inches(1), Inches(4.1), Inches(11.3), Inches(0.8),
              subtitle or f"{len(scenes)} parts · {steps_total} steps · narration in the speaker notes", 18, MUTED)
        _text(slide, Inches(1), Inches(6.4), Inches(11.3), Inches(0.5), "Made with Vivaran", 12, AMBER)
        made = 1
    for spec in front or []:
        _front_slide(deck, blank, spec)
        made += 1
    last_digest = ""
    with tempfile.TemporaryDirectory(prefix="cevg-slides-") as tmp:
        tmp = Path(tmp)
        for s_index, scene in enumerate(scenes):
            steps = scene.get("steps", [])
            if dividers and len(scenes) > 1:
                slide = deck.slides.add_slide(blank)
                _fill(slide, SLATE)
                _text(slide, Inches(1), Inches(2.6), Inches(11.3), Inches(0.6), f"Part {s_index + 1} of {len(scenes)}", 16, AMBER)
                _text(slide, Inches(1), Inches(3.2), Inches(11.3), Inches(1.4), _scene_title(scene), 36, CHALK, bold=True)
                first = steps[0].get("say", {}) if steps else {}
                opening = first.get(language) or first.get("en") or ""
                if opening:
                    _text(slide, Inches(1), Inches(4.6), Inches(11.3), Inches(1.4), opening, 16, MUTED)
                made += 1
            for t_index, step in enumerate(steps):
                if chosen is not None and (scene["id"], t_index) not in chosen:
                    continue
                say = step.get("say", {})
                line = say.get(language) or say.get("en") or ""
                actions = len(step.get("do", []))
                pictures = []
                if chosen is not None and chosen[(scene["id"], t_index)] is not None:
                    moments = [chosen[(scene["id"], t_index)]]
                elif chosen is not None:
                    moments = [actions]
                else:
                    moments = _formula_and_output(step, math_ids) if frames == "formula" else _moments(actions, frames)
                for done in moments:
                    progress(f"slide {made + len(pictures)}: {scene['id']} step {t_index + 1}/{len(steps)}, {done}/{actions} actions")
                    png = tmp / f"{s_index:02}-{t_index:03}-{done}.png"
                    # --after draws an exact state: the first `done` actions complete, nothing half-faded.
                    result = subprocess.run([binary, "frame", str(script_path), "--scene", scene["id"], "--step", str(t_index),
                                             "--after", str(done), "-o", str(png)],
                                            capture_output=True, text=True, encoding="utf-8", errors="replace")
                    if result.returncode != 0:
                        raise NarrateError(f"could not draw {scene['id']} step {t_index}:\n{(result.stdout + result.stderr).strip()}")
                    pictures.append(png)
                # Keep only pictures that differ from the one before them (and from the previous slide).
                kept = []
                for png in pictures:
                    digest = hashlib.sha1(png.read_bytes()).hexdigest()
                    if digest != last_digest:
                        kept.append(png)
                        last_digest = digest
                if not kept:
                    kept = [pictures[-1]]  # a step that changed nothing still gets its narration
                for i, png in enumerate(kept):
                    slide = deck.slides.add_slide(blank)
                    _fill(slide, SLATE)
                    slide.shapes.add_picture(str(png), Emu(0), Emu(0), width=WIDTH, height=HEIGHT)
                    # The narration goes with the first picture of the step; later ones say they continue it.
                    slide.notes_slide.notes_text_frame.text = line if i == 0 else f"(continues) {line}"
                    made += 1

    for spec in back or []:
        _front_slide(deck, blank, spec)
        made += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    deck.save(str(out))
    return {"slides": made, "steps": steps_total, "scenes": len(scenes), "file": str(out)}
