//! The scene script: the one JSON document Claude writes and the renderer reads.
//!
//! Unknown fields are rejected everywhere, so a typo such as `"targett"` is an
//! error instead of a silently ignored key.

use crate::families;
use crate::target::Target;
use serde::de::{self, DeserializeOwned};
use serde::{Deserialize, Deserializer, Serialize};
use serde_json::{Map, Value};
use std::collections::BTreeMap;

pub const SUPPORTED_VERSION: u32 = 1;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Script {
    pub version: u32,
    pub title: String,
    #[serde(default)]
    pub canvas: Canvas,
    pub objects: Vec<Object>,
    pub scenes: Vec<Scene>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct Canvas {
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    pub theme: Theme,
}

impl Default for Canvas {
    fn default() -> Self {
        Canvas { width: 1920, height: 1080, fps: 30, theme: Theme::Dark }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Theme {
    Dark,
    Light,
}

/// Named places on the canvas. Scripts never carry pixel coordinates.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Region {
    Title,
    Center,
    Left,
    Right,
    Bottom,
}

/// One value in an array cell.
#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
#[serde(untagged, expecting = "a number or a string")]
pub enum Cell {
    Int(i64),
    Float(f64),
    Text(String),
}

impl std::fmt::Display for Cell {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Cell::Int(n) => write!(f, "{n}"),
            Cell::Float(x) => write!(f, "{x}"),
            Cell::Text(s) => write!(f, "{s}"),
        }
    }
}

// ---------------------------------------------------------------- objects

#[derive(Debug, Clone)]
pub struct Object {
    pub id: String,
    /// Where the object sits. Required for every family except pointers and
    /// arrows, which attach to other objects and take no region.
    pub region: Option<Region>,
    /// Objects start hidden and are brought in with `show` unless this is true.
    pub visible: bool,
    pub kind: ObjectKind,
}

/// One variant per kind of object. Each family owns its own fields; see the
/// modules under `families/`.
#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ObjectKind {
    Text(families::label::Spec),
    Array(families::array::Spec),
    Code(families::code::Spec),
    Diagram(families::diagram::Spec),
    Table(families::table::Spec),
    Math(families::math::Spec),
    Plot(families::plot::Spec),
    Timeline(families::timeline::Spec),
    Space(families::space::Spec),
    Pointer(families::connect::PointerSpec),
    Arrow(families::connect::ArrowSpec),
}

impl<'de> Deserialize<'de> for Object {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let mut map = Map::<String, Value>::deserialize(d)?;
        let id = take(&mut map, "id")?.ok_or_else(|| de::Error::missing_field("id"))?;
        let region = take(&mut map, "region")?;
        let visible = take(&mut map, "visible")?.unwrap_or(false);
        let kind = ObjectKind::deserialize(Value::Object(map)).map_err(de::Error::custom)?;
        Ok(Object { id, region, visible, kind })
    }
}

// ----------------------------------------------------------------- scenes

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    pub id: String,
    pub steps: Vec<Step>,
}

/// One sentence of narration and the actions that play while it is spoken.
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Step {
    /// Narration keyed by language code. `en` is required.
    pub say: BTreeMap<String, String>,
    #[serde(default, rename = "do")]
    pub actions: Vec<Action>,
}

#[derive(Debug, Clone)]
pub struct Action {
    /// When the action starts, as a fraction of the step (0 = start, 1 = end).
    pub delay: f64,
    pub kind: ActionKind,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case", deny_unknown_fields)]
pub enum ActionKind {
    // ---- every family
    Show { target: Target },
    Hide { target: Target },
    /// The moving focus: highlighting a part clears the parts of the same
    /// object that were highlighted before.
    Highlight { target: Target },
    /// A lasting mark, for "visited", "sorted", "done". Stays until `reset`.
    Mark { target: Target },
    Dim { target: Target },
    /// Back to normal: clears highlight, mark and dim.
    Reset { target: Target },
    Move { target: Target, region: Region },
    /// Change the content of a part: an array cell, a table cell, a diagram
    /// node or edge label, a math line, or a whole text.
    Set { target: Target, value: Cell },
    /// Take a part away: an array cell, a table row, a diagram node or edge.
    Remove { target: Target },
    // ---- text
    Write { target: Target },
    Replace { target: Target, text: String },
    // ---- array
    Swap { a: Target, b: Target },
    Compare { a: Target, b: Target },
    Insert { target: Target, index: usize, value: Cell },
    // ---- pointer and arrow
    Point { target: Target, to: Target },
    Draw { target: Target },
    Retarget {
        target: Target,
        #[serde(default)]
        from: Option<Target>,
        #[serde(default)]
        to: Option<Target>,
    },
    // ---- code (line numbers are 1-based, as an editor shows them)
    GotoLine { target: Target, line: usize },
    MarkLines { target: Target, from: usize, to: usize },
    // ---- diagram
    AddNode {
        target: Target,
        id: String,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        shape: Option<families::diagram::Shape>,
        #[serde(default)]
        layer: Option<usize>,
        #[serde(default)]
        at: Option<[usize; 2]>,
    },
    AddEdge {
        target: Target,
        from: String,
        to: String,
        #[serde(default)]
        label: Option<String>,
    },
    // ---- table
    AddRow {
        target: Target,
        values: Vec<Cell>,
        #[serde(default)]
        index: Option<usize>,
    },
    // ---- math
    /// Show the lines of a derivation up to and including the target line.
    Reveal { target: Target },
    // ---- plot
    /// Draw a curve that was declared with `"visible": false`.
    Trace { target: Target },
    /// Move a point to new coordinates: `[x, y]` on a plot, `[x, y, z]` in
    /// space (where it also moves a vector's tip or a label).
    MoveTo { target: Target, at: Vec<f64> },
    AddPoint {
        target: Target,
        id: String,
        at: Vec<f64>,
        #[serde(default)]
        label: Option<String>,
    },
    // ---- timeline
    AddBlock {
        target: Target,
        id: String,
        lane: String,
        start: f64,
        end: f64,
        #[serde(default)]
        label: Option<String>,
    },
    AddMessage {
        target: Target,
        id: String,
        from: String,
        to: String,
        at: f64,
        #[serde(default)]
        arrive: Option<f64>,
        #[serde(default)]
        label: Option<String>,
    },
    /// Move the "now" cursor to a time.
    Advance { target: Target, to: f64 },
    // ---- space
    /// Glide the camera to a new azimuth, elevation or distance (any subset).
    Orbit {
        target: Target,
        #[serde(default)]
        azimuth: Option<f64>,
        #[serde(default)]
        elevation: Option<f64>,
        #[serde(default)]
        distance: Option<f64>,
    },
    /// Turn the camera to look at a point.
    Look { target: Target, at: [f64; 3] },
    AddVector {
        target: Target,
        id: String,
        to: [f64; 3],
        #[serde(default)]
        from: Option<[f64; 3]>,
        #[serde(default)]
        label: Option<String>,
        #[serde(default)]
        color: Option<families::space::Color>,
    },
    AddPlane {
        target: Target,
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
    },
    /// Drop a point or a vector onto a plane or a line: the projected copy
    /// appears as `id`, joined to the original by a thin drop line.
    Project { target: Target, onto: String, id: String },
    /// Turn a part (or every part) about an axis through the origin.
    Rotate { target: Target, about: families::space::Axis, degrees: f64 },
    /// The parallelogram two vectors span, as a new plane part `id`.
    Span { target: Target, a: String, b: String, id: String },
}

impl ActionKind {
    pub fn name(&self) -> &'static str {
        match self {
            ActionKind::Show { .. } => "show",
            ActionKind::Hide { .. } => "hide",
            ActionKind::Highlight { .. } => "highlight",
            ActionKind::Mark { .. } => "mark",
            ActionKind::Dim { .. } => "dim",
            ActionKind::Reset { .. } => "reset",
            ActionKind::Move { .. } => "move",
            ActionKind::Set { .. } => "set",
            ActionKind::Remove { .. } => "remove",
            ActionKind::Write { .. } => "write",
            ActionKind::Replace { .. } => "replace",
            ActionKind::Swap { .. } => "swap",
            ActionKind::Compare { .. } => "compare",
            ActionKind::Insert { .. } => "insert",
            ActionKind::Point { .. } => "point",
            ActionKind::Draw { .. } => "draw",
            ActionKind::Retarget { .. } => "retarget",
            ActionKind::GotoLine { .. } => "goto_line",
            ActionKind::MarkLines { .. } => "mark_lines",
            ActionKind::AddNode { .. } => "add_node",
            ActionKind::AddEdge { .. } => "add_edge",
            ActionKind::AddRow { .. } => "add_row",
            ActionKind::Reveal { .. } => "reveal",
            ActionKind::Trace { .. } => "trace",
            ActionKind::MoveTo { .. } => "move_to",
            ActionKind::AddPoint { .. } => "add_point",
            ActionKind::AddBlock { .. } => "add_block",
            ActionKind::AddMessage { .. } => "add_message",
            ActionKind::Advance { .. } => "advance",
            ActionKind::Orbit { .. } => "orbit",
            ActionKind::Look { .. } => "look",
            ActionKind::AddVector { .. } => "add_vector",
            ActionKind::AddPlane { .. } => "add_plane",
            ActionKind::Project { .. } => "project",
            ActionKind::Rotate { .. } => "rotate",
            ActionKind::Span { .. } => "span",
        }
    }

    /// Which kinds of object the action works on, for error messages.
    pub fn works_on(&self) -> &'static str {
        match self {
            ActionKind::Set { .. } => "text, array, table, diagram, math, plot, timeline and space objects",
            ActionKind::Remove { .. } => "array, table, diagram, plot, timeline and space objects",
            ActionKind::Write { .. } | ActionKind::Replace { .. } => "text objects",
            ActionKind::Swap { .. } | ActionKind::Compare { .. } | ActionKind::Insert { .. } => "array objects",
            ActionKind::Point { .. } => "pointer objects",
            ActionKind::Draw { .. } | ActionKind::Retarget { .. } => "arrow objects",
            ActionKind::GotoLine { .. } | ActionKind::MarkLines { .. } => "code objects",
            ActionKind::AddNode { .. } | ActionKind::AddEdge { .. } => "diagram objects",
            ActionKind::AddRow { .. } => "table objects",
            ActionKind::Reveal { .. } => "math objects",
            ActionKind::Trace { .. } | ActionKind::MoveTo { .. } | ActionKind::AddPoint { .. } => "plot and space objects",
            ActionKind::AddBlock { .. } | ActionKind::AddMessage { .. } | ActionKind::Advance { .. } => "timeline objects",
            ActionKind::Orbit { .. }
            | ActionKind::Look { .. }
            | ActionKind::AddVector { .. }
            | ActionKind::AddPlane { .. }
            | ActionKind::Project { .. }
            | ActionKind::Rotate { .. }
            | ActionKind::Span { .. } => "space objects",
            _ => "every object",
        }
    }

    /// The object the action is aimed at. `swap` and `compare` have two and
    /// are handled on their own.
    pub fn target(&self) -> Option<&Target> {
        match self {
            ActionKind::Swap { .. } | ActionKind::Compare { .. } => None,
            ActionKind::Show { target }
            | ActionKind::Hide { target }
            | ActionKind::Highlight { target }
            | ActionKind::Mark { target }
            | ActionKind::Dim { target }
            | ActionKind::Reset { target }
            | ActionKind::Move { target, .. }
            | ActionKind::Set { target, .. }
            | ActionKind::Remove { target }
            | ActionKind::Write { target }
            | ActionKind::Replace { target, .. }
            | ActionKind::Insert { target, .. }
            | ActionKind::Point { target, .. }
            | ActionKind::Draw { target }
            | ActionKind::Retarget { target, .. }
            | ActionKind::GotoLine { target, .. }
            | ActionKind::MarkLines { target, .. }
            | ActionKind::AddNode { target, .. }
            | ActionKind::AddEdge { target, .. }
            | ActionKind::AddRow { target, .. }
            | ActionKind::Reveal { target }
            | ActionKind::Trace { target }
            | ActionKind::MoveTo { target, .. }
            | ActionKind::AddPoint { target, .. }
            | ActionKind::AddBlock { target, .. }
            | ActionKind::AddMessage { target, .. }
            | ActionKind::Advance { target, .. }
            | ActionKind::Orbit { target, .. }
            | ActionKind::Look { target, .. }
            | ActionKind::AddVector { target, .. }
            | ActionKind::AddPlane { target, .. }
            | ActionKind::Project { target, .. }
            | ActionKind::Rotate { target, .. }
            | ActionKind::Span { target, .. } => Some(target),
        }
    }
}

impl<'de> Deserialize<'de> for Action {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let mut map = Map::<String, Value>::deserialize(d)?;
        let delay = take(&mut map, "delay")?.unwrap_or(0.0);
        let kind = ActionKind::deserialize(Value::Object(map)).map_err(de::Error::custom)?;
        Ok(Action { delay, kind })
    }
}

/// Pull one shared field out of a JSON object before the rest is parsed as a
/// tagged enum. This keeps `deny_unknown_fields` working, which `flatten`
/// would switch off.
fn take<T: DeserializeOwned, E: de::Error>(
    map: &mut Map<String, Value>,
    key: &str,
) -> Result<Option<T>, E> {
    match map.remove(key) {
        None => Ok(None),
        Some(v) => serde_json::from_value(v)
            .map(Some)
            .map_err(|e| E::custom(format!("{key}: {e}"))),
    }
}
