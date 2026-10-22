//! Table family: rows and columns. Script type `table`.
//!
//! With `columns` it is a database table with a header row. Without, it is a
//! plain grid: a matrix, a DP table, a page table.
//!
//! Parts: `tbl[r]` a row, `tbl[a..b]` rows, `tbl[r][c]` a cell, `tbl.name` a
//! column by its header, `tbl.c2` a column by position. Actions: `set` a cell, `add_row`, `remove` a row.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::{ActionKind, Cell};
use crate::target::Part;
use crate::text::{Face, HAlign};
use serde::Deserialize;

const MAX_COMFORTABLE_ROWS: usize = 10;
/// Text size in layout units, before any shrinking to fit.
const SIZE: f32 = 40.0;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    #[serde(default)]
    pub columns: Option<Vec<String>>,
    pub rows: Vec<Vec<Cell>>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub columns: Option<Vec<String>>,
    pub rows: Vec<Vec<(Cell, Emphasis)>>,
    /// Emphasis of each header cell.
    pub head: Vec<Emphasis>,
    /// One identity per row, which stays with the row as others come and go.
    row_ids: Vec<usize>,
    next_id: usize,
    width: usize,
}

fn width_of(spec: &Spec) -> usize {
    spec.columns.as_ref().map(Vec::len).or(spec.rows.first().map(Vec::len)).unwrap_or(0)
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    let width = width_of(spec);
    if width == 0 {
        out.push(Problem::error("", "a table needs `columns` or at least one row, so that it has a width"));
    }
    if let Some(columns) = &spec.columns {
        for (i, name) in columns.iter().enumerate() {
            if columns[..i].contains(name) {
                out.push(Problem::error(format!("columns[{i}]"), format!("duplicate column `{name}`")));
            }
        }
    }
    for (i, row) in spec.rows.iter().enumerate() {
        if row.len() != width {
            out.push(Problem::error(
                format!("rows[{i}]"),
                format!("this row has {} values, but the table has {width} columns", row.len()),
            ));
        }
    }
    if spec.rows.len() > MAX_COMFORTABLE_ROWS {
        out.push(Problem::warn(
            "rows",
            format!(
                "{} rows may not fit the region at a readable size; {MAX_COMFORTABLE_ROWS} or fewer is safe",
                spec.rows.len()
            ),
        ));
    }
    out
}

impl State {
    pub fn new(spec: &Spec) -> State {
        let width = width_of(spec);
        State {
            columns: spec.columns.clone(),
            rows: spec
                .rows
                .iter()
                .map(|r| r.iter().map(|v| (v.clone(), Emphasis::Normal)).collect())
                .collect(),
            head: vec![Emphasis::Normal; width],
            row_ids: (0..spec.rows.len()).collect(),
            next_id: spec.rows.len(),
            width,
        }
    }

    /// A column by its header, or by position as `c0`, `c1`, ... The second
    /// form works for grids without headers and for headers that are not
    /// plain names ("x - 4").
    pub fn column(&self, name: &str) -> Option<usize> {
        let by_header = self.columns.as_ref().and_then(|cols| cols.iter().position(|c| c == name));
        by_header.or_else(|| {
            let index: usize = name.strip_prefix('c')?.parse().ok()?;
            (index < self.width).then_some(index)
        })
    }

    fn rows_text(&self) -> String {
        match self.rows.len() {
            1 => "1 row".to_string(),
            n => format!("{n} rows"),
        }
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        let row_ok = |r: usize| {
            if r >= self.rows.len() {
                return Err(format!("{id}{part} is out of range, {id} has {}", self.rows_text()));
            }
            Ok(())
        };
        match part {
            Part::Index(r) => row_ok(*r),
            Part::Range { end, .. } => row_ok(end - 1),
            Part::Cell { row, col } => {
                row_ok(*row)?;
                if *col >= self.width {
                    return Err(format!("{id}{part} is out of range, {id} has {} columns", self.width));
                }
                Ok(())
            }
            Part::Name(name) => match (&self.columns, self.column(name)) {
                (_, Some(_)) => Ok(()),
                (Some(columns), None) => Err(format!(
                    "`{id}` has no column `{name}`; its columns are: {} (or by position, c0 to c{})",
                    columns.join(", "),
                    self.width.saturating_sub(1)
                )),
                (None, None) => {
                    Err(format!("`{id}` has no column `{name}`; its columns are c0 to c{}", self.width.saturating_sub(1)))
                }
            },
            _ => Err(format!(
                "`{id}{part}` is not a part of a table; use `{id}[2]` for a row, `{id}[2][0]` for a cell or `{id}.name` for a column"
            )),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        match part {
            Part::Index(r) => self.rows[*r].iter_mut().for_each(|c| c.1 = emphasis),
            Part::Range { start, end } => {
                self.rows[*start..*end].iter_mut().flatten().for_each(|c| c.1 = emphasis);
            }
            Part::Cell { row, col } => self.rows[*row][*col].1 = emphasis,
            Part::Name(name) => {
                if let Some(col) = self.column(name) {
                    self.rows.iter_mut().for_each(|r| r[col].1 = emphasis);
                    if let Some(head) = self.head.get_mut(col) {
                        *head = emphasis;
                    }
                }
            }
            _ => {}
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.rows.iter_mut().flatten().for_each(|c| f(&mut c.1));
        self.head.iter_mut().for_each(f);
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Set { target, value } => {
                let Part::Cell { row, col } = target.part else {
                    return at("target", format!("`set` on a table needs one cell such as `{id}[0][0]`, not `{target}`"));
                };
                if let Err(message) = self.check_part(id, &target.part) {
                    return at("target", message);
                }
                self.rows[row][col].0 = value.clone();
                Ok(Changed::Content)
            }
            ActionKind::AddRow { target, values, index } => {
                if !target.is_whole() {
                    return at("target", format!("`add_row` takes the whole table; use `{id}`"));
                }
                if values.len() != self.width {
                    return at(
                        "values",
                        format!("this row has {} values, but `{id}` has {} columns", values.len(), self.width),
                    );
                }
                let index = index.unwrap_or(self.rows.len());
                if index > self.rows.len() {
                    return at(
                        "index",
                        format!("{index} is past the end; `{id}` has {}, so the largest index is {}", self.rows_text(), self.rows.len()),
                    );
                }
                self.rows.insert(index, values.iter().map(|v| (v.clone(), Emphasis::Normal)).collect());
                self.row_ids.insert(index, self.next_id);
                self.next_id += 1;
                Ok(Changed::Structure)
            }
            ActionKind::Remove { target } => {
                let Part::Index(row) = target.part else {
                    return at("target", format!("`remove` on a table takes one row such as `{id}[0]`, not `{target}`"));
                };
                if let Err(message) = self.check_part(id, &target.part) {
                    return at("target", message);
                }
                self.rows.remove(row);
                self.row_ids.remove(row);
                Ok(Changed::Structure)
            }
            _ => Err(ActError::Unsupported),
        }
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let u = cx.u;
        let (size, pad, row_h) = (SIZE * u, 30.0 * u, 78.0 * u);
        let has_head = self.columns.is_some();

        // Column widths from the widest text in each column.
        let mut widths = vec![row_h; self.width];
        for (c, w) in widths.iter_mut().enumerate() {
            if let Some(columns) = &self.columns {
                *w = w.max(cx.fonts.measure(&columns[c], size, Face::SansBold, None).0 + 2.0 * pad);
            }
            for row in &self.rows {
                if let Some((value, _)) = row.get(c) {
                    *w = w.max(cx.fonts.measure(&value.to_string(), size, Face::Sans, None).0 + 2.0 * pad);
                }
            }
        }
        let n_rows = self.rows.len() + has_head as usize;
        let (total_w, total_h) = (widths.iter().sum::<f32>(), n_rows.max(1) as f32 * row_h);
        let scale = (slot.w / total_w).min(slot.h / total_h).min(1.0);
        let (row_h, total_w, total_h) = (row_h * scale, total_w * scale, total_h * scale);
        let (x0, y0) = (slot.cx() - total_w / 2.0, slot.cy() - total_h / 2.0);

        let line = |k: usize| -> Vec<Rect> {
            let mut x = x0;
            widths
                .iter()
                .map(|w| {
                    let r = Rect { x, y: y0 + k as f32 * row_h, w: w * scale, h: row_h };
                    x += w * scale;
                    r
                })
                .collect()
        };
        let header = if has_head { line(0) } else { vec![] };
        let cells = (0..self.rows.len()).map(|r| line(r + has_head as usize)).collect();
        Placed {
            bounds: Rect { x: x0, y: y0, w: total_w, h: total_h },
            skirt: 8.0 * u,
            scale,
            geometry: Geometry::Grid { header, cells },
        }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let Geometry::Grid { header, cells } = &placed.geometry else { return };
        let (pal, u, bounds) = (cx.pal, cx.u, placed.bounds);
        let size = SIZE * u * placed.scale;
        let frame = cx.tone(Emphasis::Normal, whole);
        let radius = 6.0 * u;

        cx.at("frame");
        cx.fill_round_rect(bounds, radius, pal.surface, frame.box_opacity);

        // Cell backgrounds first, so that grid lines stay crisp on top.
        if let Some(columns) = &self.columns {
            for (c, ((name, rect), emphasis)) in columns.iter().zip(header).zip(&self.head).enumerate() {
                cx.at(format!("head{c}"));
                let tone = cx.tone(*emphasis, whole);
                let fill = if tone.heavy { tone.fill } else { pal.header };
                cx.fill_rect(*rect, fill, tone.box_opacity);
                let fitted = cx.fit(name, size, Face::SansBold, rect.w * 0.9);
                cx.text(name, fitted, Face::SansBold, tone.ink, tone.ink_opacity, rect.cx(), rect.cy(), HAlign::Center, None);
            }
        }
        for ((row, rects), id) in self.rows.iter().zip(cells).zip(&self.row_ids) {
            for (c, ((value, emphasis), rect)) in row.iter().zip(rects).enumerate() {
                cx.at(format!("row{id}c{c}"));
                let tone = cx.tone(*emphasis, whole);
                // Always there, transparent when plain, so emphasis fades in place.
                cx.fill_rect(*rect, tone.fill, if tone.heavy { tone.box_opacity } else { 0.0 });
                let label = value.to_string();
                let face = if tone.heavy { Face::SansBold } else { Face::Sans };
                let fitted = cx.fit(&label, size, face, rect.w * 0.9);
                cx.text(&label, fitted, face, tone.ink, tone.ink_opacity, rect.cx(), rect.cy(), HAlign::Center, None);
            }
        }

        // Grid lines.
        cx.at("grid");
        let width = 2.0 * u;
        let first = header.first().or(cells.first().and_then(|r| r.first()));
        if let Some(first) = first {
            let mut x = bounds.x;
            let columns: &Vec<Rect> = if header.is_empty() { &cells[0] } else { header };
            for rect in columns.iter().take(columns.len().saturating_sub(1)) {
                x += rect.w;
                cx.line((x, bounds.y), (x, bounds.bottom()), pal.border, width, frame.box_opacity);
            }
            let n_rows = cells.len() + !header.is_empty() as usize;
            for k in 1..n_rows {
                let y = bounds.y + k as f32 * first.h;
                // The line under the header is heavier.
                let w = if k == 1 && !header.is_empty() { width * 1.6 } else { width };
                cx.line((bounds.x, y), (bounds.x + bounds.w, y), pal.border, w, frame.box_opacity);
            }
        }
        cx.at("border");
        cx.stroke_round_rect(bounds.inset(1.5 * u), radius, frame.border, 3.0 * u, frame.box_opacity);
    }
}
