//! Sequence family: a row of indexed cells. Script type `array`.
//!
//! Parts: `arr[i]` and ranges. Actions: `set`, `insert`, `remove`, and
//! through the world `swap` and `compare`.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::{ActionKind, Cell};
use crate::target::Part;
use crate::text::{Face, HAlign};
use serde::Deserialize;

/// More cells than this are unlikely to fit a region at a readable size.
const MAX_COMFORTABLE_CELLS: usize = 16;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    pub values: Vec<Cell>,
}

/// One element. `uid` stays with the element when it is swapped or shifted,
/// so that animation moves the element instead of repainting two places.
#[derive(Debug, Clone, PartialEq)]
pub struct Slot {
    pub value: Cell,
    pub emphasis: Emphasis,
    pub uid: usize,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub cells: Vec<Slot>,
    next_uid: usize,
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    if spec.values.len() > MAX_COMFORTABLE_CELLS {
        return vec![Problem::warn(
            "values",
            format!(
                "{} cells may not fit the region at a readable size; {MAX_COMFORTABLE_CELLS} or fewer is safe",
                spec.values.len()
            ),
        )];
    }
    vec![]
}

fn count(n: usize) -> String {
    if n == 1 {
        "1 element".to_string()
    } else {
        format!("{n} elements")
    }
}

impl State {
    pub fn new(spec: &Spec) -> State {
        let cells: Vec<Slot> = spec
            .values
            .iter()
            .enumerate()
            .map(|(uid, v)| Slot { value: v.clone(), emphasis: Emphasis::Normal, uid })
            .collect();
        State { next_uid: cells.len(), cells }
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        let last = match part {
            Part::Index(i) => *i,
            Part::Range { end, .. } => end - 1,
            _ => {
                return Err(format!(
                    "`{id}{part}` is not a part of an array; array cells are written `{id}[0]` or `{id}[0..3]`"
                ))
            }
        };
        if last >= self.cells.len() {
            return Err(format!("{id}{part} is out of range, {id} has {}", count(self.cells.len())));
        }
        Ok(())
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        let range = match part {
            Part::Index(i) => *i..i + 1,
            Part::Range { start, end } => *start..*end,
            _ => return,
        };
        for cell in self.cells.iter_mut().take(range.end).skip(range.start) {
            cell.emphasis = emphasis;
        }
    }

    /// Exchange two elements. Emphasis belongs to the place, not the element.
    pub fn swap(&mut self, i: usize, j: usize) {
        self.cells.swap(i, j);
        let (a, b) = (self.cells[i].emphasis, self.cells[j].emphasis);
        self.cells[i].emphasis = b;
        self.cells[j].emphasis = a;
    }

    /// Take an element out and put another in, for a swap between two arrays.
    pub fn exchange(&mut self, i: usize, value: Cell) -> Cell {
        self.next_uid += 1;
        self.cells[i].uid = self.next_uid - 1;
        std::mem::replace(&mut self.cells[i].value, value)
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.cells.iter_mut().for_each(|c| f(&mut c.emphasis));
    }

    /// The index of a target that must be exactly one cell.
    pub fn one_cell(&self, id: &str, part: &Part, action: &str) -> Result<usize, String> {
        match part {
            Part::Index(i) => self.check_part(id, part).map(|_| *i),
            _ => Err(format!("`{action}` needs one array cell such as `{id}[0]`, not `{id}{part}`")),
        }
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Set { target, value } => match self.one_cell(id, &target.part, "set") {
                Ok(i) => {
                    self.cells[i].value = value.clone();
                    Ok(Changed::Content)
                }
                Err(message) => at("target", message),
            },
            ActionKind::Insert { target, index, value } => {
                if !target.is_whole() {
                    return at("target", format!("`insert` takes the whole array; use `{id}` and give the place in `index`"));
                }
                let len = self.cells.len();
                if *index > len {
                    return at(
                        "index",
                        format!("{index} is past the end; `{id}` has {}, so the largest insert index is {len}", count(len)),
                    );
                }
                self.cells.insert(*index, Slot { value: value.clone(), emphasis: Emphasis::Normal, uid: self.next_uid });
                self.next_uid += 1;
                Ok(Changed::Structure)
            }
            ActionKind::Remove { target } => match self.one_cell(id, &target.part, "remove") {
                Ok(i) => {
                    self.cells.remove(i);
                    Ok(Changed::Structure)
                }
                Err(message) => at("target", message),
            },
            _ => Err(ActError::Unsupported),
        }
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let u = cx.u;
        let n = self.cells.len();
        let n_f = n.max(1) as f32;
        // Cell size: as large as 128 units, smaller when the row would not fit.
        let size = (128.0 * u).min(slot.w * 0.94 / (n_f + 0.1 * (n_f - 1.0)));
        let gap = size * 0.1;
        let row_w = n_f * size + (n_f - 1.0) * gap;
        let x0 = slot.cx() - row_w / 2.0;
        // Sit a little above the middle, leaving room for pointers below.
        let y0 = slot.cy() - size / 2.0 - (40.0 * u).min(slot.h * 0.1);
        let cells = (0..n).map(|i| Rect { x: x0 + i as f32 * (size + gap), y: y0, w: size, h: size }).collect();
        Placed {
            bounds: Rect { x: x0, y: y0, w: row_w, h: size },
            skirt: size * 0.36,
            scale: size / (128.0 * u),
            geometry: Geometry::Cells(cells),
        }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let Geometry::Cells(rects) = &placed.geometry else { return };
        for (i, (cell, rect)) in self.cells.iter().zip(rects).enumerate() {
            cx.at(format!("cell{}", cell.uid));
            let tone = cx.tone(cell.emphasis, whole);
            let width = rect.w * if tone.heavy { 0.04 } else { 0.024 };
            let radius = rect.w * 0.12;
            cx.fill_round_rect(*rect, radius, tone.fill, tone.box_opacity);
            cx.stroke_round_rect(rect.inset(width / 2.0), radius, tone.border, width, tone.box_opacity);

            let label = cell.value.to_string();
            let size = cx.fit(&label, rect.w * 0.38, Face::SansBold, rect.w * 0.8);
            cx.text(&label, size, Face::SansBold, tone.ink, tone.ink_opacity, rect.cx(), rect.cy(), HAlign::Center, None);

            // The index, under the cell. It belongs to the place.
            cx.at(format!("index{i}"));
            let muted = cx.pal.muted;
            cx.text(
                &i.to_string(),
                rect.w * 0.2,
                Face::Mono,
                muted,
                tone.ink_opacity,
                rect.cx(),
                rect.bottom() + rect.w * 0.2,
                HAlign::Center,
                None,
            );
        }
    }
}
