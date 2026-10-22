//! Code: source lines with a current-line marker. Script type `code`.
//!
//! Lines are addressed by one-based number, as an editor shows them, through
//! `goto_line` and `mark_lines`.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::ActionKind;
use crate::text::{Face, HAlign};
use serde::Deserialize;

/// Padding in units; font size and gutter as multiples of the line height and
/// font size. Layout and painting must agree on these.
const PAD: f32 = 28.0;
const SIZE: f32 = 0.62;
const GUTTER: f32 = 2.6;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    pub lines: Vec<String>,
    #[serde(default)]
    pub language: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub lines: Vec<String>,
    pub current: Option<usize>,
    pub marked: Option<(usize, usize)>,
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    if spec.lines.is_empty() {
        return vec![Problem::error("lines", "a code object needs at least one line")];
    }
    vec![]
}

impl State {
    pub fn new(spec: &Spec) -> State {
        State { lines: spec.lines.clone(), current: None, marked: None }
    }

    fn line(&self, id: &str, line: usize, field: &'static str) -> Result<(), ActError> {
        if line == 0 || line > self.lines.len() {
            return at(field, format!("line {line} does not exist; `{id}` has lines 1 to {}", self.lines.len()));
        }
        Ok(())
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::GotoLine { line, .. } => {
                self.line(id, *line, "line")?;
                self.current = Some(*line);
            }
            ActionKind::MarkLines { from, to, .. } => {
                self.line(id, *from, "from")?;
                self.line(id, *to, "to")?;
                if from > to {
                    return at("", format!("`from` ({from}) is after `to` ({to})"));
                }
                self.marked = Some((*from, *to));
            }
            _ => return Err(ActError::Unsupported),
        }
        Ok(Changed::Content)
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let n = self.lines.len().max(1) as f32;
        let pad = PAD * cx.u;
        // Start from the comfortable line height, then shrink until the block
        // fits the slot both ways. Width scales with font size, so one
        // measurement is enough.
        let full = 54.0 * cx.u;
        let mut line_h = full.min((slot.h - 2.0 * pad) / n);
        let size = line_h * SIZE;
        let widest = self.lines.iter().map(|l| cx.fonts.measure(l, size, Face::Mono, None).0).fold(0.0f32, f32::max);
        let content = widest + size * GUTTER + pad;
        let room = slot.w - 2.0 * pad;
        if content > room {
            line_h *= room / content;
        }
        let w = (content.min(room) + 2.0 * pad).max(slot.w.min(360.0 * cx.u));
        let h = n * line_h + 2.0 * pad;
        Placed {
            bounds: Rect { x: slot.cx() - w / 2.0, y: slot.cy() - h / 2.0, w, h },
            skirt: 8.0 * cx.u,
            scale: line_h / full,
            geometry: Geometry::None,
        }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let (pal, u, bounds) = (cx.pal, cx.u, placed.bounds);
        let tone = cx.tone(Emphasis::Normal, whole);
        let pad = PAD * u;
        let line_h = (bounds.h - 2.0 * pad) / self.lines.len().max(1) as f32;
        let size = line_h * SIZE;
        let gutter = size * GUTTER;

        cx.at("frame");
        cx.fill_round_rect(bounds, 16.0 * u, pal.surface, tone.box_opacity);
        cx.stroke_round_rect(bounds.inset(1.5 * u), 16.0 * u, tone.border, 3.0 * u, tone.box_opacity);

        let row = |number: usize, count: usize| Rect {
            x: bounds.x + pad / 2.0,
            y: bounds.y + pad + (number - 1) as f32 * line_h,
            w: bounds.w - pad,
            h: line_h * count as f32,
        };
        // Marked lines share one band; the current line is drawn over it.
        if let Some((a, b)) = self.marked {
            cx.at("marked");
            cx.fill_round_rect(row(a, b + 1 - a), 8.0 * u, pal.border, tone.box_opacity * 0.4);
        }
        if let Some(number) = self.current {
            cx.at("current");
            let r = row(number, 1);
            cx.fill_round_rect(r, 8.0 * u, pal.accent_fill, tone.box_opacity);
            cx.fill_round_rect(Rect { w: 6.0 * u, ..r }, 3.0 * u, pal.accent, tone.box_opacity);
        }

        for (i, line) in self.lines.iter().enumerate() {
            let number = i + 1;
            cx.at(format!("line{number}"));
            let y = row(number, 1).cy();
            cx.text(
                &number.to_string(),
                size,
                Face::Mono,
                pal.muted,
                tone.ink_opacity,
                bounds.x + pad + gutter - size * 1.1,
                y,
                HAlign::Right,
                None,
            );
            let color = if self.current == Some(number) { pal.accent } else { pal.text };
            cx.text(line, size, Face::Mono, color, tone.ink_opacity, bounds.x + pad + gutter, y, HAlign::Left, None);
        }
    }
}
