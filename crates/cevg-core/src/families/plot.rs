//! Plot family: axes with curves and points. Script type `plot`.
//!
//! A curve is either a function of `x` (`"fn": "(x - 3)^2"`, see `expr`) or
//! a line through data (`"points": [[0, 1], [1, 0.6]]`). Points are labelled
//! markers that can move. Axis ranges are best given; a missing y range is
//! worked out from the curves and points.
//!
//! Parts: `p.name` for a curve or a point. Actions: `trace` draws a hidden
//! curve, `move_to` moves a point, `add_point`, `set` (a curve's function or
//! a point's label), `remove`.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::expr::Expr;
use crate::render::{Cx, Rect};
use crate::script::{ActionKind, Cell};
use crate::target::{is_valid_name, Part};
use crate::text::{Face, HAlign};
use serde::Deserialize;

/// Samples per function curve. Fixed, so that a curve can morph into another.
const SAMPLES: usize = 160;

#[derive(Debug, Clone, PartialEq, Default, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct Axis {
    pub label: Option<String>,
    pub min: Option<f64>,
    pub max: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CurveSpec {
    pub id: String,
    /// A function of `x`. Give this or `points`.
    #[serde(default, rename = "fn")]
    pub func: Option<String>,
    /// Data to join with straight lines, as `[x, y]` pairs.
    #[serde(default)]
    pub points: Option<Vec<[f64; 2]>>,
    #[serde(default)]
    pub label: Option<String>,
    /// A hidden curve is drawn later with `trace`. Default true.
    #[serde(default = "yes")]
    pub visible: bool,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PointSpec {
    pub id: String,
    pub at: [f64; 2],
    #[serde(default)]
    pub label: Option<String>,
}

fn yes() -> bool {
    true
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    #[serde(default)]
    pub x: Axis,
    #[serde(default)]
    pub y: Axis,
    #[serde(default)]
    pub curves: Vec<CurveSpec>,
    #[serde(default)]
    pub points: Vec<PointSpec>,
    /// Faint lines at the ticks. Default true.
    #[serde(default = "yes")]
    pub grid: bool,
    /// Use the same scale on both axes, so that angles and distances are
    /// true: a 45 degree line looks 45 degrees. Default false.
    #[serde(default)]
    pub equal: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Curve {
    pub spec: CurveSpec,
    expr: Option<Expr>,
    pub emphasis: Emphasis,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Point {
    pub spec: PointSpec,
    pub emphasis: Emphasis,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub x: Axis,
    pub y: Axis,
    pub grid: bool,
    pub equal: bool,
    pub curves: Vec<Curve>,
    pub points: Vec<Point>,
}

fn finite(at: &[f64; 2]) -> bool {
    at[0].is_finite() && at[1].is_finite()
}

/// A plot takes `[x, y]`; three coordinates belong to a space object.
fn pair(at: &[f64]) -> Result<[f64; 2], ActError> {
    match at {
        [x, y] if x.is_finite() && y.is_finite() => Ok([*x, *y]),
        [_, _] => at_err("at", "both coordinates must be finite numbers"),
        _ => at_err("at", format!("a plot point takes `[x, y]`, two coordinates, not {}", at.len())),
    }
}

fn at_err<T>(field: &'static str, message: impl Into<String>) -> Result<T, ActError> {
    Err(ActError::At(field, message.into()))
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    for (name, axis) in [("x", &spec.x), ("y", &spec.y)] {
        if let (Some(min), Some(max)) = (axis.min, axis.max) {
            if min >= max {
                out.push(Problem::error(name, format!("`min` ({min}) must be less than `max` ({max})")));
            }
        }
    }
    let mut ids: Vec<&str> = vec![];
    fn claim(ids: &[&str], id: &str, path: String, out: &mut Vec<Problem>) {
        if !is_valid_name(id) {
            out.push(Problem::error(path, format!("`{id}` is not a valid id; use only letters, digits and `_`")));
        } else if ids.contains(&id) {
            out.push(Problem::error(path, format!("duplicate id `{id}`; curves and points share one set of ids")));
        }
    }
    for (i, curve) in spec.curves.iter().enumerate() {
        let path = format!("curves[{i}]");
        claim(&ids, &curve.id, format!("{path}.id"), &mut out);
        ids.push(&curve.id);
        match (&curve.func, &curve.points) {
            (Some(_), Some(_)) => out.push(Problem::error(&path, "give `fn` or `points`, not both")),
            (None, None) => out.push(Problem::error(&path, "a curve needs `fn` (a function of x) or `points` (data)")),
            (Some(func), None) => {
                if let Err(message) = Expr::parse(func) {
                    out.push(Problem::error(format!("{path}.fn"), message));
                }
                if spec.x.min.is_none() || spec.x.max.is_none() {
                    out.push(Problem::error(&path, "drawing a function needs `x.min` and `x.max` on the plot"));
                }
            }
            (None, Some(points)) => {
                if points.len() < 2 {
                    out.push(Problem::error(format!("{path}.points"), "a data curve needs at least two points"));
                }
                if !points.iter().all(finite) {
                    out.push(Problem::error(format!("{path}.points"), "every coordinate must be a finite number"));
                }
            }
        }
    }
    for (i, point) in spec.points.iter().enumerate() {
        claim(&ids, &point.id, format!("points[{i}].id"), &mut out);
        ids.push(&point.id);
        if !finite(&point.at) {
            out.push(Problem::error(format!("points[{i}].at"), "both coordinates must be finite numbers"));
        }
    }
    if spec.curves.is_empty() && spec.points.is_empty() {
        out.push(Problem::error("", "a plot needs at least one curve or point"));
    }
    out
}

/// Tick positions at round numbers, about five across the range.
fn ticks(min: f64, max: f64) -> (Vec<f64>, usize) {
    let rough = (max - min) / 5.0;
    let power = 10f64.powf(rough.log10().floor());
    let step = [1.0, 2.0, 5.0, 10.0].iter().map(|m| m * power).find(|s| *s >= rough).unwrap_or(power * 10.0);
    let decimals = (-step.log10().floor()).max(0.0) as usize;
    let first = (min / step).ceil() as i64;
    let last = (max / step).floor() as i64;
    ((first..=last).map(|k| k as f64 * step).collect(), decimals)
}

impl State {
    pub fn new(spec: &Spec) -> State {
        State {
            x: spec.x.clone(),
            y: spec.y.clone(),
            grid: spec.grid,
            equal: spec.equal,
            curves: spec
                .curves
                .iter()
                .map(|c| Curve {
                    spec: c.clone(),
                    expr: c.func.as_deref().and_then(|f| Expr::parse(f).ok()),
                    emphasis: Emphasis::Normal,
                })
                .collect(),
            points: spec.points.iter().map(|p| Point { spec: p.clone(), emphasis: Emphasis::Normal }).collect(),
        }
    }

    fn curve(&self, id: &str) -> Option<usize> {
        self.curves.iter().position(|c| c.spec.id == id)
    }

    fn point(&self, id: &str) -> Option<usize> {
        self.points.iter().position(|p| p.spec.id == id)
    }

    fn names(&self) -> String {
        let names: Vec<&str> =
            self.curves.iter().map(|c| c.spec.id.as_str()).chain(self.points.iter().map(|p| p.spec.id.as_str())).collect();
        names.join(", ")
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        match part {
            Part::Name(name) if self.curve(name).is_some() || self.point(name).is_some() => Ok(()),
            Part::Name(name) => {
                Err(format!("`{id}` has no curve or point `{name}`; it has: {}", self.names()))
            }
            _ => Err(format!("`{id}{part}` is not a part of a plot; use `{id}.name` for a curve or a point")),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        let Part::Name(name) = part else { return };
        if let Some(i) = self.curve(name) {
            self.curves[i].emphasis = emphasis;
        } else if let Some(i) = self.point(name) {
            self.points[i].emphasis = emphasis;
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.curves.iter_mut().for_each(|c| f(&mut c.emphasis));
        self.points.iter_mut().for_each(|p| f(&mut p.emphasis));
    }

    fn named<'a>(&self, id: &str, target: &'a crate::target::Target, action: &str) -> Result<&'a str, ActError> {
        match &target.part {
            Part::Name(name) => match self.check_part(id, &target.part) {
                Ok(()) => Ok(name),
                Err(message) => at("target", message),
            },
            _ => at("target", format!("`{action}` needs a curve or a point such as `{id}.name`, not `{target}`")),
        }
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Trace { target } => {
                let name = self.named(id, target, "trace")?;
                let Some(i) = self.curve(name) else {
                    return at("target", format!("`trace` draws a curve, but `{name}` is a point"));
                };
                self.curves[i].spec.visible = true;
                Ok(Changed::Content)
            }
            ActionKind::MoveTo { target, at: to } => {
                let name = self.named(id, target, "move_to")?;
                let Some(i) = self.point(name) else {
                    return at("target", format!("`move_to` moves a point, but `{name}` is a curve"));
                };
                self.points[i].spec.at = pair(to)?;
                Ok(Changed::Content)
            }
            ActionKind::AddPoint { target, id: point_id, at: place, label } => {
                if !target.is_whole() {
                    return at("target", format!("`add_point` takes the whole plot; use `{id}`"));
                }
                if !is_valid_name(point_id) {
                    return at("id", format!("`{point_id}` is not a valid id; use only letters, digits and `_`"));
                }
                if self.curve(point_id).is_some() || self.point(point_id).is_some() {
                    return at("id", format!("duplicate id `{point_id}`; curves and points share one set of ids"));
                }
                let spec = PointSpec { id: point_id.clone(), at: pair(place)?, label: label.clone() };
                self.points.push(Point { spec, emphasis: Emphasis::Normal });
                Ok(Changed::Structure)
            }
            ActionKind::Set { target, value } => {
                let name = self.named(id, target, "set")?;
                if let Some(i) = self.point(name) {
                    self.points[i].spec.label = Some(value.to_string());
                    return Ok(Changed::Content);
                }
                let i = self.curve(name).expect("checked");
                let Cell::Text(func) = value else {
                    return at("value", "a curve is set to a function of x, so `value` must be a string");
                };
                if self.curves[i].spec.func.is_none() {
                    return at("target", format!("`{name}` is a data curve; only a function curve can be set to a new function"));
                }
                match Expr::parse(func) {
                    Ok(expr) => {
                        self.curves[i].expr = Some(expr);
                        self.curves[i].spec.func = Some(func.clone());
                        Ok(Changed::Content)
                    }
                    Err(message) => at("value", message),
                }
            }
            ActionKind::Remove { target } => {
                let name = self.named(id, target, "remove")?;
                self.curves.retain(|c| c.spec.id != name);
                self.points.retain(|p| p.spec.id != name);
                Ok(Changed::Structure)
            }
            _ => Err(ActError::Unsupported),
        }
    }

    // ------------------------------------------------------------- shape

    fn x_range(&self) -> (f64, f64) {
        let data = || {
            let xs = self
                .curves
                .iter()
                .flat_map(|c| c.spec.points.iter().flatten().map(|p| p[0]))
                .chain(self.points.iter().map(|p| p.spec.at[0]));
            xs.fold(None, |r: Option<(f64, f64)>, x| Some(r.map_or((x, x), |(a, b)| (a.min(x), b.max(x)))))
        };
        match (self.x.min, self.x.max) {
            (Some(min), Some(max)) if min < max => (min, max),
            _ => match data() {
                Some((a, b)) if a < b => (self.x.min.unwrap_or(a), self.x.max.unwrap_or(b)),
                Some((a, _)) => (a - 1.0, a + 1.0),
                None => (0.0, 1.0),
            },
        }
    }

    /// The (x, y) samples of a curve over the x range.
    fn samples(&self, curve: &Curve, (x0, x1): (f64, f64)) -> Vec<[f64; 2]> {
        if let Some(points) = &curve.spec.points {
            return points.clone();
        }
        let Some(expr) = &curve.expr else { return vec![] };
        let mut last = 0.0;
        (0..=SAMPLES)
            .map(|i| {
                let x = x0 + (x1 - x0) * i as f64 / SAMPLES as f64;
                let y = expr.eval(x);
                // Where the function has no value, hold the last one.
                if y.is_finite() {
                    last = y;
                }
                [x, last]
            })
            .collect()
    }

    fn y_range(&self, xr: (f64, f64)) -> (f64, f64) {
        if let (Some(min), Some(max)) = (self.y.min, self.y.max) {
            if min < max {
                return (min, max);
            }
        }
        let ys = self
            .curves
            .iter()
            .flat_map(|c| self.samples(c, xr).into_iter().map(|p| p[1]))
            .chain(self.points.iter().map(|p| p.spec.at[1]));
        let seen = ys.fold(None, |r: Option<(f64, f64)>, y| Some(r.map_or((y, y), |(a, b)| (a.min(y), b.max(y)))));
        let (lo, hi) = match seen {
            Some((a, b)) if a < b => (a, b),
            Some((a, _)) => (a - 1.0, a + 1.0),
            None => (0.0, 1.0),
        };
        let pad = (hi - lo) * 0.08;
        (self.y.min.unwrap_or(lo - pad), self.y.max.unwrap_or(hi + pad))
    }

    /// The box the data is drawn in, inside the slot, leaving room for tick
    /// labels and axis titles.
    fn area(&self, slot: Rect, u: f32, xr: (f64, f64), yr: (f64, f64)) -> Rect {
        let (left, right, top, bottom) = (130.0 * u, 50.0 * u, 76.0 * u, 100.0 * u);
        let (room_w, room_h) = (slot.w - left - right, slot.h - top - bottom);
        let (w, h) = if self.equal {
            // One data unit is the same number of pixels both ways.
            let per_unit = (room_w / (xr.1 - xr.0) as f32).min(room_h / (yr.1 - yr.0) as f32);
            (per_unit * (xr.1 - xr.0) as f32, per_unit * (yr.1 - yr.0) as f32)
        } else {
            (room_w.min(room_h * 1.9), room_h)
        };
        Rect {
            x: slot.cx() - (w + left + right) / 2.0 + left,
            y: slot.cy() - (h + top + bottom) / 2.0 + top,
            w,
            h,
        }
    }

    /// The label drawn for a point. Points that sit on the same spot share
    /// one label ("B, C") instead of printing over each other.
    fn label_of(&self, index: usize, spots: &[(f32, f32)], reach: f32) -> String {
        let near = |a: (f32, f32), b: (f32, f32)| (a.0 - b.0).abs() < reach && (a.1 - b.1).abs() < reach;
        let group: Vec<usize> = (0..self.points.len()).filter(|j| near(spots[index], spots[*j])).collect();
        if group.first() != Some(&index) {
            return String::new();
        }
        let labels: Vec<&str> = group.iter().filter_map(|j| self.points[*j].spec.label.as_deref()).collect();
        labels.join(", ")
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let u = cx.u;
        let (xr, yr) = (self.x_range(), self.y_range(self.x_range()));
        let area = self.area(slot, u, xr, yr);
        let px = |p: &[f64; 2]| map(area, xr, yr, p);
        let mut nodes = vec![];
        for point in &self.points {
            let (x, y) = px(&point.spec.at);
            let r = 13.0 * u;
            nodes.push((point.spec.id.clone(), Rect { x: x - r, y: y - r, w: 2.0 * r, h: 2.0 * r }));
        }
        for curve in &self.curves {
            if let Some(end) = self.samples(curve, xr).last() {
                let (x, y) = px(end);
                nodes.push((curve.spec.id.clone(), Rect { x: x - 8.0 * u, y: y - 8.0 * u, w: 16.0 * u, h: 16.0 * u }));
            }
        }
        Placed { bounds: area, skirt: 8.0 * u, scale: 1.0, geometry: Geometry::Nodes(nodes) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let (pal, u, area) = (cx.pal, cx.u, placed.bounds);
        let frame = cx.tone(Emphasis::Normal, whole);
        let (xr, yr) = (self.x_range(), self.y_range(self.x_range()));
        let px = |p: &[f64; 2]| map(area, xr, yr, p);
        let small = 26.0 * u;

        cx.at("frame");
        cx.fill_rect(area, pal.surface, frame.box_opacity * 0.6);

        // Ticks are named by their value, so that they slide when a range
        // changes instead of jumping.
        let (x_ticks, x_dec) = ticks(xr.0, xr.1);
        for t in x_ticks {
            cx.at(format!("x tick {t:.6}"));
            let (x, _) = px(&[t, yr.0]);
            if self.grid {
                cx.line((x, area.y), (x, area.bottom()), pal.border, 1.5 * u, frame.box_opacity * 0.5);
            }
            let label = format!("{t:.x_dec$}");
            cx.text(&label, small, Face::Sans, pal.muted, frame.ink_opacity, x, area.bottom() + small * 1.1, HAlign::Center, None);
        }
        let (y_ticks, y_dec) = ticks(yr.0, yr.1);
        for t in y_ticks {
            cx.at(format!("y tick {t:.6}"));
            let (_, y) = px(&[xr.0, t]);
            if self.grid {
                cx.line((area.x, y), (area.x + area.w, y), pal.border, 1.5 * u, frame.box_opacity * 0.5);
            }
            let label = format!("{t:.y_dec$}");
            cx.text(&label, small, Face::Sans, pal.muted, frame.ink_opacity, area.x - small * 0.6, y, HAlign::Right, None);
        }

        cx.at("axes");
        cx.line((area.x, area.bottom()), (area.x + area.w, area.bottom()), pal.muted, 3.0 * u, frame.box_opacity);
        cx.line((area.x, area.y), (area.x, area.bottom()), pal.muted, 3.0 * u, frame.box_opacity);
        let title = 30.0 * u;
        cx.text(
            self.x.label.as_deref().unwrap_or(""),
            title,
            Face::SansBold,
            pal.text,
            frame.ink_opacity,
            area.cx(),
            area.bottom() + small * 1.1 + title * 1.5,
            HAlign::Center,
            None,
        );
        cx.text(
            self.y.label.as_deref().unwrap_or(""),
            title,
            Face::SansBold,
            pal.text,
            frame.ink_opacity,
            area.x,
            area.y - title * 1.5,
            HAlign::Center,
            None,
        );

        for (i, curve) in self.curves.iter().enumerate() {
            if !curve.spec.visible {
                continue;
            }
            cx.at(format!("curve {}", curve.spec.id));
            let tone = cx.tone(curve.emphasis, whole);
            let color = if tone.heavy { tone.border } else { pal.pointers[i % pal.pointers.len()] };
            let width = if tone.heavy { 7.0 * u } else { 5.0 * u };
            // The curve is clipped to the plot area. Wild values are reined
            // in first so that the geometry stays finite.
            let span = yr.1 - yr.0;
            let samples = self.samples(curve, xr);
            let line: Vec<(f32, f32)> =
                samples.iter().map(|p| px(&[p[0], p[1].clamp(yr.0 - 20.0 * span, yr.1 + 20.0 * span)])).collect();
            cx.path(&line, area, color, width, tone.ink_opacity);
            // The label sits by the last sample that is inside the area.
            let inside = samples.iter().rposition(|p| p[1] >= yr.0 && p[1] <= yr.1);
            if let (Some(label), Some(i)) = (&curve.spec.label, inside) {
                let (size, end) = (28.0 * u, line[i]);
                let (x, y) = (end.0 - 10.0 * u, end.1 - 30.0 * u);
                let (w, _) = cx.fonts.measure(label, size, Face::SansBold, None);
                // A patch of background keeps the name readable over lines.
                let patch = Rect { x: x - w - size * 0.3, y: y - size * 0.7, w: w + size * 0.6, h: size * 1.4 };
                cx.fill_round_rect(patch, size * 0.3, pal.background, tone.ink_opacity * 0.8);
                cx.text(label, size, Face::SansBold, color, tone.ink_opacity, x, y, HAlign::Right, None);
            }
        }

        let spots: Vec<(f32, f32)> = self.points.iter().map(|p| px(&p.spec.at)).collect();
        for (i, point) in self.points.iter().enumerate() {
            cx.at(format!("point {}", point.spec.id));
            let tone = cx.tone(point.emphasis, whole);
            let color = if tone.heavy { tone.border } else { pal.pointers[(i + 1) % pal.pointers.len()] };
            let (x, y) = px(&point.spec.at);
            let r = 13.0 * u;
            let dot = Rect { x: x - r, y: y - r, w: 2.0 * r, h: 2.0 * r };
            cx.fill_round_rect(dot, r, color, tone.ink_opacity);
            cx.stroke_round_rect(dot, r, pal.background, 3.0 * u, tone.ink_opacity);
            let label = self.label_of(i, &spots, r);
            let size = 30.0 * u;
            let (w, _) = cx.fonts.measure(&label, size, Face::SansBold, None);
            let patch = Rect { x: x + r * 1.3 - size * 0.25, y: y - r * 2.6 - size * 0.7, w: w + size * 0.5, h: size * 1.4 };
            cx.fill_round_rect(patch, size * 0.3, pal.background, if label.is_empty() { 0.0 } else { tone.ink_opacity * 0.8 });
            cx.text(&label, size, Face::SansBold, color, tone.ink_opacity, x + r * 1.3, y - r * 2.6, HAlign::Left, None);
        }
    }
}

/// From data coordinates to pixels inside `area`. The y axis points up.
fn map(area: Rect, (x0, x1): (f64, f64), (y0, y1): (f64, f64), p: &[f64; 2]) -> (f32, f32) {
    let fx = ((p[0] - x0) / (x1 - x0)) as f32;
    let fy = ((p[1] - y0) / (y1 - y0)) as f32;
    (area.x + fx * area.w, area.bottom() - fy * area.h)
}
