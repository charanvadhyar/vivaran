//! Space family: three-dimensional scenes. Script type `space`.
//!
//! Axes with points, vectors, planes, surfaces from an expression of `x`
//! and `y`, and paths, seen through an orbiting camera with `z` up. The
//! family computes all geometry on the CPU in scene coordinates (the axis
//! ranges scaled uniformly into a cube of side 2, so angles stay true) and
//! records it as solids; a `SpaceBackend` rasterises the viewport. Labels
//! are projected and drawn flat on top by the compositor.
//!
//! Parts: `sp.name`. Actions: `orbit`, `look`, `add_point`, `add_vector`,
//! `add_plane`, `move_to`, `set`, `project`, `rotate`, `span`, `trace`,
//! `remove`, plus the actions every object takes.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::expr::Expr;
use crate::render::{Cx, Rect, Rgb};
use crate::space3d::{add, cross, dot, normalize, scale, sub, Camera, Content, Projection, Vec3};
use crate::script::{ActionKind, Cell};
use crate::target::{is_valid_name, Part};
use crate::text::{Face, HAlign};
use serde::Deserialize;
use std::sync::Arc;

/// Samples per side of a surface. Fixed, so that a surface can morph.
const SURFACE_SAMPLES: usize = 40;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Color {
    Amber,
    Green,
    Blue,
    Pink,
    Purple,
    Orange,
    Muted,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Axis {
    X,
    Y,
    Z,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Grid {
    #[default]
    Xy,
    Xz,
    Yz,
    None,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct AxesSpec {
    pub x: [f64; 2],
    pub y: [f64; 2],
    pub z: [f64; 2],
    /// Names at the tips. Default x, y, z.
    pub labels: Option<[String; 3]>,
    pub grid: Grid,
}

impl Default for AxesSpec {
    fn default() -> Self {
        AxesSpec { x: [-1.0, 1.0], y: [-1.0, 1.0], z: [-1.0, 1.0], labels: None, grid: Grid::Xy }
    }
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct CameraSpec {
    /// Degrees from +x toward +y.
    pub azimuth: f64,
    /// Degrees above the xy plane.
    pub elevation: f64,
    /// In scene units, where the axes fill a cube of side 2. Default fits the cube.
    pub distance: Option<f64>,
    /// What the camera looks at, in the axes' coordinates. Default the centre.
    pub target: Option<[f64; 3]>,
    pub fov: f64,
}

impl Default for CameraSpec {
    fn default() -> Self {
        CameraSpec { azimuth: 35.0, elevation: 24.0, distance: None, target: None, fov: 36.0 }
    }
}

fn yes() -> bool {
    true
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(tag = "kind", rename_all = "lowercase", deny_unknown_fields)]
pub enum PartSpec {
    Point {
        id: String,
        at: [f64; 3],
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<Color>,
        #[serde(default = "yes")]
        visible: bool,
    },
    Vector {
        id: String,
        to: [f64; 3],
        #[serde(default)]
        from: Option<[f64; 3]>,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<Color>,
        #[serde(default = "yes")]
        visible: bool,
    },
    /// A plane through a point: give `normal`, or `span` (two vector ids).
    /// With `size` it is a square of that side; a spanned plane without
    /// `size` is the parallelogram of the two vectors.
    Plane {
        id: String,
        #[serde(default)]
        through: Option<[f64; 3]>,
        #[serde(default)]
        normal: Option<[f64; 3]>,
        #[serde(default)]
        span: Option<[String; 2]>,
        #[serde(default)]
        size: Option<f64>,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<Color>,
        #[serde(default = "yes")]
        visible: bool,
    },
    /// z = f(x, y) over the axes' x and y ranges (or its own).
    Surface {
        id: String,
        #[serde(rename = "fn")]
        func: String,
        #[serde(default)]
        x: Option<[f64; 2]>,
        #[serde(default)]
        y: Option<[f64; 2]>,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<Color>,
        #[serde(default = "yes")]
        visible: bool,
    },
    Path {
        id: String,
        points: Vec<[f64; 3]>,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<Color>,
        #[serde(default = "yes")]
        visible: bool,
    },
    Label {
        id: String,
        at: [f64; 3],
        text: String,
        #[serde(default = "yes")]
        visible: bool,
    },
}

impl PartSpec {
    pub fn id(&self) -> &str {
        match self {
            PartSpec::Point { id, .. }
            | PartSpec::Vector { id, .. }
            | PartSpec::Plane { id, .. }
            | PartSpec::Surface { id, .. }
            | PartSpec::Path { id, .. }
            | PartSpec::Label { id, .. } => id,
        }
    }

    fn visible(&self) -> bool {
        match self {
            PartSpec::Point { visible, .. }
            | PartSpec::Vector { visible, .. }
            | PartSpec::Plane { visible, .. }
            | PartSpec::Surface { visible, .. }
            | PartSpec::Path { visible, .. }
            | PartSpec::Label { visible, .. } => *visible,
        }
    }

    fn set_visible(&mut self, on: bool) {
        match self {
            PartSpec::Point { visible, .. }
            | PartSpec::Vector { visible, .. }
            | PartSpec::Plane { visible, .. }
            | PartSpec::Surface { visible, .. }
            | PartSpec::Path { visible, .. }
            | PartSpec::Label { visible, .. } => *visible = on,
        }
    }

    fn kind(&self) -> &'static str {
        match self {
            PartSpec::Point { .. } => "point",
            PartSpec::Vector { .. } => "vector",
            PartSpec::Plane { .. } => "plane",
            PartSpec::Surface { .. } => "surface",
            PartSpec::Path { .. } => "path",
            PartSpec::Label { .. } => "label",
        }
    }

    fn label_mut(&mut self) -> Option<&mut Option<String>> {
        match self {
            PartSpec::Point { label, .. }
            | PartSpec::Vector { label, .. }
            | PartSpec::Plane { label, .. }
            | PartSpec::Surface { label, .. }
            | PartSpec::Path { label, .. } => Some(label),
            PartSpec::Label { .. } => None,
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    #[serde(default)]
    pub axes: AxesSpec,
    /// Draw the axes and grid. Default true.
    #[serde(default = "yes")]
    pub show_axes: bool,
    #[serde(default)]
    pub camera: CameraSpec,
    #[serde(default)]
    pub parts: Vec<PartSpec>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct PartState {
    pub spec: PartSpec,
    expr: Option<Expr>,
    pub emphasis: Emphasis,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub axes: AxesSpec,
    pub show_axes: bool,
    pub camera: Camera,
    pub parts: Vec<PartState>,
}

fn finite3(p: &[f64; 3]) -> bool {
    p.iter().all(|v| v.is_finite())
}

fn check_part(part: &PartSpec, path: &str, ids: &[&str], out: &mut Vec<Problem>) {
    let id = part.id();
    if !is_valid_name(id) {
        out.push(Problem::error(format!("{path}.id"), format!("`{id}` is not a valid id; use only letters, digits and `_`")));
    } else if ids.contains(&id) {
        out.push(Problem::error(format!("{path}.id"), format!("duplicate id `{id}`; the parts of a space share one set of ids")));
    }
    match part {
        PartSpec::Point { at, .. } | PartSpec::Label { at, .. } if !finite3(at) => {
            out.push(Problem::error(format!("{path}.at"), "all three coordinates must be finite numbers"));
        }
        PartSpec::Vector { to, from, .. } if !finite3(to) || from.is_some_and(|f| !finite3(&f)) => {
            out.push(Problem::error(path, "all three coordinates must be finite numbers"));
        }
        PartSpec::Plane { normal, span, size, .. } => match (normal, span) {
            (Some(_), Some(_)) => out.push(Problem::error(path, "give `normal` or `span`, not both")),
            (None, None) => out.push(Problem::error(path, "a plane needs `normal` (a direction) or `span` (two vector ids)")),
            (Some(n), None) => {
                if !finite3(n) || (n[0] == 0.0 && n[1] == 0.0 && n[2] == 0.0) {
                    out.push(Problem::error(format!("{path}.normal"), "the normal must be a finite, non-zero direction"));
                }
                if size.is_none() {
                    out.push(Problem::error(path, "a plane given by `normal` needs `size` (the side of the square drawn)"));
                }
            }
            (None, Some([a, b])) => {
                for v in [a, b] {
                    if !ids.contains(&v.as_str()) {
                        out.push(Problem::error(format!("{path}.span"), format!("`{v}` is not a vector declared before this plane")));
                    }
                }
            }
        },
        PartSpec::Surface { func, x, y, .. } => {
            if let Err(message) = Expr::parse_xy(func) {
                out.push(Problem::error(format!("{path}.fn"), message));
            }
            for (name, range) in [("x", x), ("y", y)] {
                if let Some([lo, hi]) = range {
                    if lo >= hi {
                        out.push(Problem::error(format!("{path}.{name}"), format!("the range [{lo}, {hi}] must go up")));
                    }
                }
            }
        }
        PartSpec::Path { points, .. } => {
            if points.len() < 2 {
                out.push(Problem::error(format!("{path}.points"), "a path needs at least two points"));
            }
            if !points.iter().all(finite3) {
                out.push(Problem::error(format!("{path}.points"), "every coordinate must be a finite number"));
            }
        }
        _ => {}
    }
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    for (name, [lo, hi]) in [("x", spec.axes.x), ("y", spec.axes.y), ("z", spec.axes.z)] {
        if lo >= hi || lo.is_nan() || hi.is_nan() {
            out.push(Problem::error(format!("axes.{name}"), format!("the range [{lo}, {hi}] must go up")));
        }
    }
    if spec.camera.fov < 5.0 || spec.camera.fov > 120.0 {
        out.push(Problem::error("camera.fov", "the field of view is in degrees, between 5 and 120"));
    }
    let mut ids: Vec<&str> = vec![];
    for (i, part) in spec.parts.iter().enumerate() {
        check_part(part, &format!("parts[{i}]"), &ids, &mut out);
        ids.push(part.id());
    }
    out
}

/// Tick positions at round numbers, about five across the range.
fn ticks(min: f64, max: f64) -> Vec<f64> {
    let rough = (max - min) / 5.0;
    let power = 10f64.powf(rough.log10().floor());
    let step = [1.0, 2.0, 5.0, 10.0].iter().map(|m| m * power).find(|s| *s >= rough).unwrap_or(power * 10.0);
    let first = (min / step).ceil() as i64;
    let last = (max / step).floor() as i64;
    (first..=last).map(|k| k as f64 * step).collect()
}

/// Rotate `p` about the named axis through the origin.
fn rotate(p: [f64; 3], about: Axis, degrees: f64) -> [f64; 3] {
    let (s, c) = degrees.to_radians().sin_cos();
    match about {
        Axis::X => [p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c],
        Axis::Y => [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c],
        Axis::Z => [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]],
    }
}

fn v3(p: [f64; 3]) -> Vec3 {
    [p[0] as f32, p[1] as f32, p[2] as f32]
}

/// A plane as a point, two spanning directions and, for a square, its side.
type PlaneFrame = ([f64; 3], [f64; 3], [f64; 3], Option<f64>);

/// Two unit directions in the plane with the given normal.
fn basis_of(normal: Vec3) -> (Vec3, Vec3) {
    let n = normalize(normal);
    let helper = if n[2].abs() < 0.9 { [0.0, 0.0, 1.0] } else { [1.0, 0.0, 0.0] };
    let u = normalize(cross(helper, n));
    let v = cross(n, u);
    (u, v)
}

impl State {
    pub fn new(spec: &Spec) -> State {
        let mut state = State {
            axes: spec.axes.clone(),
            show_axes: spec.show_axes,
            camera: Camera {
                azimuth: spec.camera.azimuth as f32,
                elevation: spec.camera.elevation as f32,
                distance: spec.camera.distance.unwrap_or(3.3) as f32,
                target: [0.0, 0.0, 0.0],
                fov: spec.camera.fov as f32,
            },
            parts: spec
                .parts
                .iter()
                .map(|p| PartState {
                    spec: p.clone(),
                    expr: match p {
                        PartSpec::Surface { func, .. } => Expr::parse_xy(func).ok(),
                        _ => None,
                    },
                    emphasis: Emphasis::Normal,
                })
                .collect(),
        };
        if let Some(t) = spec.camera.target {
            state.camera.target = state.to_scene(t);
        }
        state
    }

    // ------------------------------------------------------- coordinates

    fn centre(&self) -> [f64; 3] {
        let mid = |[a, b]: [f64; 2]| (a + b) / 2.0;
        [mid(self.axes.x), mid(self.axes.y), mid(self.axes.z)]
    }

    /// Scene units per data unit: the longest axis spans 2.
    fn unit(&self) -> f64 {
        let span = |[a, b]: [f64; 2]| b - a;
        2.0 / span(self.axes.x).max(span(self.axes.y)).max(span(self.axes.z)).max(1e-9)
    }

    pub fn to_scene(&self, p: [f64; 3]) -> Vec3 {
        let (c, u) = (self.centre(), self.unit());
        [((p[0] - c[0]) * u) as f32, ((p[1] - c[1]) * u) as f32, ((p[2] - c[2]) * u) as f32]
    }

    fn part(&self, id: &str) -> Option<usize> {
        self.parts.iter().position(|p| p.spec.id() == id)
    }

    fn names(&self) -> String {
        let names: Vec<&str> = self.parts.iter().map(|p| p.spec.id()).collect();
        if names.is_empty() { "(none)".to_string() } else { names.join(", ") }
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        match part {
            Part::Name(name) if self.part(name).is_some() => Ok(()),
            Part::Name(name) => Err(format!("`{id}` has no part `{name}`; it has: {}", self.names())),
            _ => Err(format!("`{id}{part}` is not a part of a space; use `{id}.name`")),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        if let Part::Name(name) = part {
            if let Some(i) = self.part(name) {
                self.parts[i].emphasis = emphasis;
            }
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.parts.iter_mut().for_each(|p| f(&mut p.emphasis));
    }

    fn named<'a>(&self, id: &str, target: &'a crate::target::Target, action: &str) -> Result<&'a str, ActError> {
        match &target.part {
            Part::Name(name) => match self.check_part(id, &target.part) {
                Ok(()) => Ok(name),
                Err(message) => at("target", message),
            },
            _ => at("target", format!("`{action}` needs a part such as `{id}.name`, not `{target}`")),
        }
    }

    fn whole(&self, id: &str, target: &crate::target::Target, action: &str) -> Result<(), ActError> {
        if target.is_whole() { Ok(()) } else { at("target", format!("`{action}` takes the whole space; use `{id}`")) }
    }

    fn new_id(&self, new: &str) -> Result<(), ActError> {
        if !is_valid_name(new) {
            return at("id", format!("`{new}` is not a valid id; use only letters, digits and `_`"));
        }
        if self.part(new).is_some() {
            return at("id", format!("duplicate id `{new}`; the parts of a space share one set of ids"));
        }
        Ok(())
    }

    fn push(&mut self, spec: PartSpec) {
        let expr = match &spec {
            PartSpec::Surface { func, .. } => Expr::parse_xy(func).ok(),
            _ => None,
        };
        self.parts.push(PartState { spec, expr, emphasis: Emphasis::Normal });
    }

    /// A vector part's start and end, in data coordinates.
    fn vector(&self, name: &str) -> Option<([f64; 3], [f64; 3])> {
        match &self.parts[self.part(name)?].spec {
            PartSpec::Vector { from, to, .. } => Some((from.unwrap_or([0.0; 3]), *to)),
            _ => None,
        }
    }

    /// A plane's point and two spanning directions (not unit), in data
    /// coordinates, and whether it is a bounded parallelogram.
    fn plane(&self, name: &str) -> Option<PlaneFrame> {
        let PartSpec::Plane { through, normal, span, size, .. } = &self.parts[self.part(name)?].spec else { return None };
        if let Some([a, b]) = span {
            let (fa, ta) = self.vector(a)?;
            let (_, tb) = self.vector(b)?;
            let u = [ta[0] - fa[0], ta[1] - fa[1], ta[2] - fa[2]];
            let (fb, _) = self.vector(b)?;
            let v = [tb[0] - fb[0], tb[1] - fb[1], tb[2] - fb[2]];
            return Some((through.unwrap_or(fa), u, v, *size));
        }
        let n = normal.as_ref()?;
        let (u, v) = basis_of(v3(*n));
        let f = |a: Vec3| [a[0] as f64, a[1] as f64, a[2] as f64];
        Some((through.unwrap_or([0.0; 3]), f(u), f(v), *size))
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Orbit { target, azimuth, elevation, distance } => {
                self.whole(id, target, "orbit")?;
                if azimuth.is_none() && elevation.is_none() && distance.is_none() {
                    return at("", "`orbit` needs `azimuth`, `elevation` or `distance`");
                }
                if let Some(a) = azimuth {
                    self.camera.azimuth = *a as f32;
                }
                if let Some(e) = elevation {
                    self.camera.elevation = (*e as f32).clamp(-89.0, 89.0);
                }
                if let Some(d) = distance {
                    if *d <= 0.0 {
                        return at("distance", "the distance must be positive");
                    }
                    self.camera.distance = *d as f32;
                }
                Ok(Changed::Content)
            }
            ActionKind::Look { target, at: point } => {
                self.whole(id, target, "look")?;
                if !finite3(point) {
                    return at("at", "all three coordinates must be finite numbers");
                }
                self.camera.target = self.to_scene(*point);
                Ok(Changed::Content)
            }
            ActionKind::AddPoint { target, id: new, at: place, label } => {
                self.whole(id, target, "add_point")?;
                self.new_id(new)?;
                let [x, y, z] = match place[..] {
                    [x, y, z] if x.is_finite() && y.is_finite() && z.is_finite() => [x, y, z],
                    _ => return at("at", format!("a point in space takes `[x, y, z]`, three finite numbers, not {}", place.len())),
                };
                self.push(PartSpec::Point { id: new.clone(), at: [x, y, z], label: label.clone(), color: None, visible: true });
                Ok(Changed::Structure)
            }
            ActionKind::AddVector { target, id: new, to, from, label, color } => {
                self.whole(id, target, "add_vector")?;
                self.new_id(new)?;
                if !finite3(to) || from.is_some_and(|f| !finite3(&f)) {
                    return at("to", "all three coordinates must be finite numbers");
                }
                self.push(PartSpec::Vector { id: new.clone(), to: *to, from: *from, label: label.clone(), color: *color, visible: true });
                Ok(Changed::Structure)
            }
            ActionKind::AddPlane { target, id: new, through, normal, span, size, label } => {
                self.whole(id, target, "add_plane")?;
                self.new_id(new)?;
                let spec = PartSpec::Plane {
                    id: new.clone(),
                    through: *through,
                    normal: *normal,
                    span: span.clone(),
                    size: *size,
                    label: label.clone(),
                    color: None,
                    visible: true,
                };
                let ids: Vec<&str> = self.parts.iter().map(|p| p.spec.id()).collect();
                let mut problems = vec![];
                check_part(&spec, "", &ids, &mut problems);
                if let Some(p) = problems.into_iter().find(|p| !p.warning) {
                    return Err(ActError::At("", p.message));
                }
                self.push(spec);
                Ok(Changed::Structure)
            }
            ActionKind::Span { target, a, b, id: new } => {
                self.whole(id, target, "span")?;
                self.new_id(new)?;
                for v in [a, b] {
                    if self.vector(v).is_none() {
                        return at("a", format!("`{v}` is not a vector of `{id}`; it has: {}", self.names()));
                    }
                }
                self.push(PartSpec::Plane {
                    id: new.clone(),
                    through: None,
                    normal: None,
                    span: Some([a.clone(), b.clone()]),
                    size: None,
                    label: None,
                    color: None,
                    visible: true,
                });
                Ok(Changed::Structure)
            }
            ActionKind::MoveTo { target, at: place } => {
                let name = self.named(id, target, "move_to")?.to_string();
                let p = match place[..] {
                    [x, y, z] if x.is_finite() && y.is_finite() && z.is_finite() => [x, y, z],
                    _ => return at("at", format!("in space `move_to` takes `[x, y, z]`, three finite numbers, not {}", place.len())),
                };
                let i = self.part(&name).expect("checked");
                match &mut self.parts[i].spec {
                    PartSpec::Point { at: a, .. } | PartSpec::Label { at: a, .. } => *a = p,
                    PartSpec::Vector { to, .. } => *to = p,
                    other => return at("target", format!("`move_to` moves a point, a label or a vector's tip; `{name}` is a {}", other.kind())),
                }
                Ok(Changed::Content)
            }
            ActionKind::Trace { target } => {
                let name = self.named(id, target, "trace")?.to_string();
                let i = self.part(&name).expect("checked");
                self.parts[i].spec.set_visible(true);
                Ok(Changed::Content)
            }
            ActionKind::Set { target, value } => {
                let name = self.named(id, target, "set")?.to_string();
                let i = self.part(&name).expect("checked");
                match &mut self.parts[i].spec {
                    PartSpec::Surface { func, .. } => {
                        let Cell::Text(text) = value else {
                            return at("value", "a surface is set to a new function of x and y, so `value` must be a string");
                        };
                        match Expr::parse_xy(text) {
                            Ok(expr) => {
                                *func = text.clone();
                                self.parts[i].expr = Some(expr);
                            }
                            Err(message) => return at("value", message),
                        }
                    }
                    PartSpec::Label { text, .. } => *text = value.to_string(),
                    other => {
                        if let Some(label) = other.label_mut() {
                            *label = Some(value.to_string());
                        }
                    }
                }
                Ok(Changed::Content)
            }
            ActionKind::Project { target, onto, id: new } => {
                let name = self.named(id, target, "project")?.to_string();
                self.new_id(new)?;
                let drop_id = format!("{new}_drop");
                if self.part(&drop_id).is_some() {
                    return at("id", format!("`{drop_id}` is already taken; `project` needs it for the drop line"));
                }
                // Where things go: onto a plane, the foot of the perpendicular;
                // onto a vector, the nearest point of its line.
                let foot = |p: [f64; 3]| -> Option<[f64; 3]> {
                    if let Some((through, u, v, _)) = self.plane(onto) {
                        let n = cross(v3(u), v3(v));
                        let n = normalize(n);
                        let d = dot(sub(v3(p), v3(through)), n);
                        let f = sub(v3(p), scale(n, d));
                        return Some([f[0] as f64, f[1] as f64, f[2] as f64]);
                    }
                    let (from, to) = self.vector(onto)?;
                    let dir = sub(v3(to), v3(from));
                    let len2 = dot(dir, dir).max(1e-12);
                    let t = dot(sub(v3(p), v3(from)), dir) / len2;
                    let f = add(v3(from), scale(dir, t));
                    Some([f[0] as f64, f[1] as f64, f[2] as f64])
                };
                let i = self.part(&name).expect("checked");
                let (added, drop): (PartSpec, Vec<[f64; 3]>) = match self.parts[i].spec.clone() {
                    PartSpec::Point { at: p, label, color, .. } => {
                        let Some(f) = foot(p) else { return at("onto", format!("`{onto}` is not a plane or a vector of `{id}`")) };
                        let label = label.map(|l| format!("{l}′"));
                        (PartSpec::Point { id: new.clone(), at: f, label, color, visible: true }, vec![p, f])
                    }
                    PartSpec::Vector { from, to, label, color, .. } => {
                        let start = from.unwrap_or([0.0; 3]);
                        let (Some(f0), Some(f1)) = (foot(start), foot(to)) else {
                            return at("onto", format!("`{onto}` is not a plane or a vector of `{id}`"));
                        };
                        let label = label.map(|l| format!("{l}′"));
                        (PartSpec::Vector { id: new.clone(), from: Some(f0), to: f1, label, color, visible: true }, vec![to, f1])
                    }
                    other => return at("target", format!("`project` drops a point or a vector; `{name}` is a {}", other.kind())),
                };
                self.push(added);
                self.push(PartSpec::Path { id: drop_id, points: drop, label: None, color: Some(Color::Muted), visible: true });
                Ok(Changed::Structure)
            }
            ActionKind::Rotate { target, about, degrees } => {
                if !degrees.is_finite() {
                    return at("degrees", "the angle must be a finite number of degrees");
                }
                let which: Vec<usize> = if target.is_whole() {
                    (0..self.parts.len()).collect()
                } else {
                    let name = self.named(id, target, "rotate")?.to_string();
                    vec![self.part(&name).expect("checked")]
                };
                for i in &which {
                    if matches!(self.parts[*i].spec, PartSpec::Surface { .. }) && !target.is_whole() {
                        return at("target", "a surface is a function of x and y and cannot be rotated; rotate the camera with `orbit`");
                    }
                }
                for i in which {
                    let r = |p: &mut [f64; 3]| *p = rotate(*p, *about, *degrees);
                    match &mut self.parts[i].spec {
                        PartSpec::Point { at: p, .. } | PartSpec::Label { at: p, .. } => r(p),
                        PartSpec::Vector { from, to, .. } => {
                            r(to);
                            if let Some(f) = from {
                                r(f);
                            }
                        }
                        PartSpec::Plane { through, normal, .. } => {
                            if let Some(t) = through {
                                r(t);
                            }
                            if let Some(n) = normal {
                                r(n);
                            }
                        }
                        PartSpec::Path { points, .. } => points.iter_mut().for_each(r),
                        PartSpec::Surface { .. } => {}
                    }
                }
                Ok(Changed::Content)
            }
            ActionKind::Remove { target } => {
                let name = self.named(id, target, "remove")?.to_string();
                self.parts.retain(|p| p.spec.id() != name);
                Ok(Changed::Structure)
            }
            _ => Err(ActError::Unsupported),
        }
    }

    // --------------------------------------------------------- drawing

    fn color_of(&self, index: usize, chosen: Option<Color>, pal: &crate::render::Palette) -> Rgb {
        let named = |c: Color| match c {
            Color::Amber => pal.accent,
            Color::Green => pal.mark,
            Color::Blue => pal.pointers[0],
            Color::Pink => pal.pointers[1],
            Color::Purple => pal.pointers[2],
            Color::Orange => pal.pointers[3],
            Color::Muted => pal.muted,
        };
        if let Some(c) = chosen {
            return named(c);
        }
        match &self.parts[index].spec {
            PartSpec::Point { .. } => {
                let nth = self.parts[..index].iter().filter(|p| matches!(p.spec, PartSpec::Point { .. })).count();
                pal.pointers[nth % pal.pointers.len()]
            }
            PartSpec::Vector { .. } => pal.accent,
            PartSpec::Plane { .. } => pal.muted,
            PartSpec::Surface { .. } => pal.pointers[0],
            PartSpec::Path { .. } => pal.pointers[1],
            PartSpec::Label { .. } => pal.text,
        }
    }

    /// The viewport: the slot, kept to a 16:10 box at most.
    fn viewport(slot: Rect) -> Rect {
        let w = slot.w.min(slot.h * 1.6);
        Rect { x: slot.cx() - w / 2.0, y: slot.y, w, h: slot.h }
    }

    /// The corners of a plane, in data coordinates.
    fn plane_corners(&self, name: &str) -> Option<[[f64; 3]; 4]> {
        let (through, u, v, size) = self.plane(name)?;
        let f = |a: Vec3| [a[0] as f64, a[1] as f64, a[2] as f64];
        let add3 = |a: [f64; 3], b: [f64; 3], s: f64| [a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s];
        Some(match size {
            Some(size) => {
                let (u, v) = (f(normalize(v3(u))), f(normalize(v3(v))));
                let h = size / 2.0;
                let c = through;
                [
                    add3(add3(c, u, -h), v, -h),
                    add3(add3(c, u, h), v, -h),
                    add3(add3(c, u, h), v, h),
                    add3(add3(c, u, -h), v, h),
                ]
            }
            None => [through, add3(through, u, 1.0), add3(add3(through, u, 1.0), v, 1.0), add3(through, v, 1.0)],
        })
    }

    /// Where a part's anchor is, for labels and for pointers.
    fn anchor(&self, index: usize) -> Option<[f64; 3]> {
        let mid = |a: [f64; 3], b: [f64; 3]| [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0];
        Some(match &self.parts[index].spec {
            PartSpec::Point { at, .. } | PartSpec::Label { at, .. } => *at,
            PartSpec::Vector { to, .. } => *to,
            PartSpec::Plane { id, .. } => {
                let c = self.plane_corners(id)?;
                mid(c[0], c[2])
            }
            PartSpec::Surface { x, y, .. } => {
                let xr = x.unwrap_or(self.axes.x);
                let yr = y.unwrap_or(self.axes.y);
                let (cx, cy) = ((xr[0] + xr[1]) / 2.0, (yr[0] + yr[1]) / 2.0);
                let z = self.parts[index].expr.as_ref().map_or(0.0, |e| e.eval_xy(cx, cy));
                [cx, cy, if z.is_finite() { z } else { 0.0 }]
            }
            PartSpec::Path { points, .. } => *points.last()?,
        })
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let u = cx.u;
        let area = Self::viewport(slot);
        let proj = Projection::new(&self.camera, area.w, area.h);
        let mut nodes = vec![];
        for (i, part) in self.parts.iter().enumerate() {
            if !part.spec.visible() {
                continue;
            }
            let Some(anchor) = self.anchor(i) else { continue };
            if let Some(((x, y), _)) = proj.project(self.to_scene(anchor)) {
                let r = 14.0 * u;
                nodes.push((part.spec.id().to_string(), Rect { x: area.x + x - r, y: area.y + y - r, w: 2.0 * r, h: 2.0 * r }));
            }
        }
        Placed { bounds: area, skirt: 0.0, scale: 1.0, geometry: Geometry::Nodes(nodes) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let (pal, u, area) = (cx.pal, cx.u, placed.bounds);
        let frame = cx.tone(Emphasis::Normal, whole);
        let scene = cx.scene_id();
        let small = 26.0 * u;

        cx.at("viewport");
        cx.viewport(scene, area, &self.camera, frame.ink_opacity);

        if self.show_axes {
            let names = self.axes.labels.clone().unwrap_or(["x".into(), "y".into(), "z".into()]);
            let ranges = [self.axes.x, self.axes.y, self.axes.z];
            // Axes cross at the origin when it is in view, otherwise at the
            // near corner, so they always sit on the edge of the grid.
            let mut c = [0.0; 3];
            for k in 0..3 {
                if !(ranges[k][0] <= 0.0 && 0.0 <= ranges[k][1]) {
                    c[k] = ranges[k][0];
                }
            }
            for (k, range) in ranges.iter().enumerate() {
                let mut lo = c;
                let mut hi = c;
                lo[k] = range[0];
                hi[k] = range[1];
                cx.at(format!("axis {}", "xyz".chars().nth(k).unwrap()));
                let line = vec![self.to_scene(lo), self.to_scene(hi)];
                cx.solid(scene, Arc::new(Content::Segments { width: 2.0 * u, head: true }), line, pal.muted, 1.0, frame.ink_opacity * 0.9);
                let (dx, dy) = match k {
                    0 => (small * 0.9, small * 0.5),
                    1 => (small * 0.9, 0.0),
                    _ => (0.0, -small * 0.9),
                };
                cx.label3d(scene, &names[k], Face::SansBold, HAlign::Center, self.to_scene(hi), dx, dy, 30.0 * u, pal.muted, frame.ink_opacity);
            }
            // Grid lines on one plane, at round numbers.
            let (plane_axes, fixed) = match self.axes.grid {
                Grid::Xy => (Some((0, 1)), 2),
                Grid::Xz => (Some((0, 2)), 1),
                Grid::Yz => (Some((1, 2)), 0),
                Grid::None => (None, 0),
            };
            if let Some((a, b)) = plane_axes {
                let content = Arc::new(Content::Segments { width: 1.0 * u, head: false });
                for (along, across) in [(a, b), (b, a)] {
                    for t in ticks(ranges[along][0], ranges[along][1]) {
                        cx.at(format!("grid {along} {t:.6}"));
                        let mut p = c;
                        let mut q = c;
                        p[fixed] = ranges[fixed][0];
                        q[fixed] = ranges[fixed][0];
                        p[along] = t;
                        q[along] = t;
                        p[across] = ranges[across][0];
                        q[across] = ranges[across][1];
                        let line = vec![self.to_scene(p), self.to_scene(q)];
                        cx.solid(scene, content.clone(), line, pal.border, 1.0, frame.ink_opacity * 0.5);
                    }
                }
            }
        }

        for (i, part) in self.parts.iter().enumerate() {
            if !part.spec.visible() {
                continue;
            }
            let id = part.spec.id().to_string();
            let tone = cx.tone(part.emphasis, whole);
            let chosen = match &part.spec {
                PartSpec::Point { color, .. }
                | PartSpec::Vector { color, .. }
                | PartSpec::Plane { color, .. }
                | PartSpec::Surface { color, .. }
                | PartSpec::Path { color, .. } => *color,
                PartSpec::Label { .. } => None,
            };
            let color = if tone.heavy { tone.border } else { self.color_of(i, chosen, pal) };
            let ink = tone.ink_opacity;
            cx.at(format!("part {id}"));
            let label_at: Option<([f64; 3], (f32, f32))> = match &part.spec {
                PartSpec::Point { at: p, .. } => {
                    let r = if tone.heavy { 15.0 * u } else { 12.0 * u };
                    cx.solid(scene, Arc::new(Content::Points { radius: r }), vec![self.to_scene(*p)], color, 1.0, ink);
                    Some((*p, (small * 0.9, -small * 0.9)))
                }
                PartSpec::Vector { from, to, .. } => {
                    let start = from.unwrap_or([0.0; 3]);
                    let width = if tone.heavy { 7.0 * u } else { 5.0 * u };
                    cx.solid(scene, Arc::new(Content::Segments { width, head: true }), vec![self.to_scene(start), self.to_scene(*to)], color, 1.0, ink);
                    Some((*to, (small * 0.8, -small * 0.8)))
                }
                PartSpec::Plane { .. } => {
                    let Some(corners) = self.plane_corners(&id) else { continue };
                    let quad: Vec<Vec3> = corners.iter().map(|p| self.to_scene(*p)).collect();
                    let fill = Arc::new(Content::Mesh { triangles: vec![[0, 1, 2], [0, 2, 3]], lit: true });
                    cx.solid(scene, fill, quad.clone(), color, 1.0, ink * 0.42);
                    let mut edge = quad.clone();
                    edge.push(quad[0]);
                    cx.solid(scene, Arc::new(Content::Segments { width: 2.0 * u, head: false }), edge, color, 1.0, ink * 0.9);
                    self.anchor(i).map(|a| (a, (0.0, -small * 0.6)))
                }
                PartSpec::Surface { x, y, .. } => {
                    let Some(expr) = &part.expr else { continue };
                    let xr = x.unwrap_or(self.axes.x);
                    let yr = y.unwrap_or(self.axes.y);
                    let n = SURFACE_SAMPLES;
                    let zr = self.axes.z;
                    let slack = (zr[1] - zr[0]) * 0.25;
                    let mut vertices = Vec::with_capacity((n + 1) * (n + 1));
                    for j in 0..=n {
                        for k in 0..=n {
                            let px = xr[0] + (xr[1] - xr[0]) * k as f64 / n as f64;
                            let py = yr[0] + (yr[1] - yr[0]) * j as f64 / n as f64;
                            let z = expr.eval_xy(px, py);
                            let z = if z.is_finite() { z.clamp(zr[0] - slack, zr[1] + slack) } else { zr[0] };
                            vertices.push(self.to_scene([px, py, z]));
                        }
                    }
                    let mut triangles = Vec::with_capacity(2 * n * n);
                    for j in 0..n {
                        for k in 0..n {
                            let a = (j * (n + 1) + k) as u32;
                            let b = a + 1;
                            let c = a + (n as u32 + 1);
                            let d = c + 1;
                            triangles.push([a, b, d]);
                            triangles.push([a, d, c]);
                        }
                    }
                    cx.solid(scene, Arc::new(Content::Mesh { triangles, lit: true }), vertices, color, 1.0, ink * 0.88);
                    self.anchor(i).map(|a| (a, (0.0, -small)))
                }
                PartSpec::Path { points, .. } => {
                    let line: Vec<Vec3> = points.iter().map(|p| self.to_scene(*p)).collect();
                    let width = if tone.heavy { 5.0 * u } else { 3.0 * u };
                    cx.solid(scene, Arc::new(Content::Segments { width, head: false }), line, color, 1.0, ink);
                    points.last().map(|p| (*p, (small * 0.8, -small * 0.8)))
                }
                PartSpec::Label { at: p, text, .. } => {
                    cx.label3d(scene, text, Face::Sans, HAlign::Center, self.to_scene(*p), 0.0, 0.0, 30.0 * u, color, ink);
                    None
                }
            };
            let label = match &part.spec {
                PartSpec::Point { label, .. }
                | PartSpec::Vector { label, .. }
                | PartSpec::Plane { label, .. }
                | PartSpec::Surface { label, .. }
                | PartSpec::Path { label, .. } => label.as_deref(),
                PartSpec::Label { .. } => None,
            };
            if let (Some(text), Some((anchor, (dx, dy)))) = (label, label_at) {
                cx.at(format!("label {id}"));
                let face = if tone.heavy { Face::SansBold } else { Face::Sans };
                cx.label3d(scene, text, face, HAlign::Left, self.to_scene(anchor), dx, dy, 30.0 * u, color, ink);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rotation_about_z_turns_x_into_y() {
        let p = rotate([1.0, 0.0, 0.0], Axis::Z, 90.0);
        assert!((p[0]).abs() < 1e-9 && (p[1] - 1.0).abs() < 1e-9 && p[2].abs() < 1e-9);
    }

    #[test]
    fn scene_coordinates_are_uniform() {
        let spec: Spec = serde_json::from_value(serde_json::json!({ "axes": { "x": [0, 4], "y": [0, 2], "z": [0, 2] } })).unwrap();
        let state = State::new(&spec);
        // The longest axis spans 2; the others keep the same scale.
        assert_eq!(state.to_scene([4.0, 2.0, 2.0]), [1.0, 0.5, 0.5]);
        assert_eq!(state.to_scene([2.0, 1.0, 1.0]), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn a_point_projects_onto_a_plane() {
        let spec: Spec = serde_json::from_value(serde_json::json!({
            "parts": [
                { "kind": "vector", "id": "u", "to": [1, 0, 0] },
                { "kind": "vector", "id": "v", "to": [0, 1, 0] },
                { "kind": "plane", "id": "p", "span": ["u", "v"] },
                { "kind": "point", "id": "a", "at": [0.3, 0.4, 0.9], "label": "A" }
            ]
        }))
        .unwrap();
        assert!(check(&spec).is_empty());
        let mut state = State::new(&spec);
        let action = ActionKind::Project { target: "sp.a".parse().unwrap(), onto: "p".into(), id: "a2".into() };
        assert!(state.act("sp", &action).is_ok());
        let PartSpec::Point { at, label, .. } = &state.parts[state.part("a2").unwrap()].spec else { panic!() };
        assert!((at[0] - 0.3).abs() < 1e-6 && (at[1] - 0.4).abs() < 1e-6 && at[2].abs() < 1e-6);
        assert_eq!(label.as_deref(), Some("A′"));
        assert!(state.part("a2_drop").is_some());
    }
}
