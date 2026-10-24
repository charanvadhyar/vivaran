//! The visual families. Each module owns one kind of object end to end:
//!
//! * `Spec`   what the script may say about it (its JSON fields)
//! * `State`  what it looks like at one moment
//! * rules    which parts it has and which actions it accepts
//! * layout   where it and its parts sit inside a slot
//! * paint    how it is drawn
//!
//! | Family          | Module     | Script `type`       |
//! | --------------- | ---------- | ------------------- |
//! | Sequence        | `array`    | `array`             |
//! | Node-link       | `diagram`  | `diagram`           |
//! | Table           | `table`    | `table`             |
//! | Math            | `math`     | `math`              |
//! | Code and text   | `code`, `label` | `code`, `text` |
//! | Plot            | `plot`     | `plot`              |
//! | Timeline        | `timeline` | `timeline`          |
//! | Space (3D)      | `space`    | `space`             |
//!
//! `connect` holds pointers and arrows, which attach to parts of the others.
//!
//! [`Body`] is the only place that knows the full list. Adding a family means
//! one new module, one variant here and one in `script::ObjectKind`.

pub mod array;
pub mod code;
pub mod connect;
pub mod diagram;
pub mod label;
pub mod math;
pub mod plot;
pub mod space;
pub mod table;
pub mod timeline;

use crate::render::{Cx, Rect};
use crate::script::{ActionKind, ObjectKind, Region};
use crate::target::Part;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Emphasis {
    #[default]
    Normal,
    /// The moving focus.
    Highlight,
    /// A lasting mark: visited, sorted, done.
    Mark,
    Dim,
}

/// Something wrong with a spec or an action. `field` is the JSON field the
/// problem is in, relative to the object or action (empty for the whole).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Problem {
    pub warning: bool,
    pub field: String,
    pub message: String,
}

impl Problem {
    pub fn error(field: impl Into<String>, message: impl Into<String>) -> Problem {
        Problem { warning: false, field: field.into(), message: message.into() }
    }
    pub fn warn(field: impl Into<String>, message: impl Into<String>) -> Problem {
        Problem { warning: true, field: field.into(), message: message.into() }
    }
}

/// What an accepted action did.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Changed {
    Content,
    /// Parts were added or removed, so pointers and arrows must be rechecked.
    Structure,
}

pub enum ActError {
    /// This family does not know the action at all.
    Unsupported,
    /// The action is known but impossible right now.
    At(&'static str, String),
}

pub type ActResult = Result<Changed, ActError>;

fn at<T>(field: &'static str, message: impl Into<String>) -> Result<T, ActError> {
    Err(ActError::At(field, message.into()))
}

/// Where an object and its parts ended up on the canvas.
#[derive(Debug, Clone)]
pub struct Placed {
    pub bounds: Rect,
    /// Room taken under each part (index labels under array cells), so that
    /// pointers start below it.
    pub skirt: f32,
    /// How much the object was shrunk to fit its slot; 1 means not at all.
    pub scale: f32,
    pub geometry: Geometry,
}

#[derive(Debug, Clone)]
pub enum Geometry {
    None,
    /// Array cells or math lines, in order.
    Cells(Vec<Rect>),
    Grid { header: Vec<Rect>, cells: Vec<Vec<Rect>> },
    Nodes(Vec<(String, Rect)>),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    Text,
    Array,
    Code,
    Diagram,
    Table,
    Math,
    Plot,
    Timeline,
    Space,
    Pointer,
    Arrow,
}

impl Kind {
    pub fn name(self) -> &'static str {
        match self {
            Kind::Text => "text",
            Kind::Array => "array",
            Kind::Code => "code",
            Kind::Diagram => "diagram",
            Kind::Table => "table",
            Kind::Math => "math",
            Kind::Plot => "plot",
            Kind::Timeline => "timeline",
            Kind::Space => "space",
            Kind::Pointer => "pointer",
            Kind::Arrow => "arrow",
        }
    }

    /// With its article: "an array", "a table".
    pub fn a(self) -> String {
        match self {
            Kind::Array | Kind::Arrow => format!("an {}", self.name()),
            _ => format!("a {}", self.name()),
        }
    }

    /// Placed objects sit in a region. Pointers and arrows attach to them.
    pub fn is_placed(self) -> bool {
        !matches!(self, Kind::Pointer | Kind::Arrow)
    }
}

impl ObjectKind {
    pub fn kind(&self) -> Kind {
        match self {
            ObjectKind::Text(_) => Kind::Text,
            ObjectKind::Array(_) => Kind::Array,
            ObjectKind::Code(_) => Kind::Code,
            ObjectKind::Diagram(_) => Kind::Diagram,
            ObjectKind::Table(_) => Kind::Table,
            ObjectKind::Math(_) => Kind::Math,
            ObjectKind::Plot(_) => Kind::Plot,
            ObjectKind::Timeline(_) => Kind::Timeline,
            ObjectKind::Space(_) => Kind::Space,
            ObjectKind::Pointer(_) => Kind::Pointer,
            ObjectKind::Arrow(_) => Kind::Arrow,
        }
    }

    /// Problems that can be seen in the spec alone, before anything plays.
    pub fn check(&self) -> Vec<Problem> {
        match self {
            ObjectKind::Text(_) | ObjectKind::Pointer(_) | ObjectKind::Arrow(_) => vec![],
            ObjectKind::Array(s) => array::check(s),
            ObjectKind::Code(s) => code::check(s),
            ObjectKind::Diagram(s) => diagram::check(s),
            ObjectKind::Table(s) => table::check(s),
            ObjectKind::Math(s) => math::check(s),
            ObjectKind::Plot(s) => plot::check(s),
            ObjectKind::Timeline(s) => timeline::check(s),
            ObjectKind::Space(s) => space::check(s),
        }
    }
}

/// The state of one object, whatever its family.
#[derive(Debug, Clone, PartialEq)]
pub enum Body {
    Text(label::State),
    Array(array::State),
    Code(code::State),
    Diagram(diagram::State),
    Table(table::State),
    Math(math::State),
    Plot(plot::State),
    Timeline(timeline::State),
    Space(space::State),
    Pointer(connect::Pointer),
    Arrow(connect::Arrow),
}

impl Body {
    pub fn new(kind: &ObjectKind) -> Body {
        match kind {
            ObjectKind::Text(s) => Body::Text(label::State::new(s)),
            ObjectKind::Array(s) => Body::Array(array::State::new(s)),
            ObjectKind::Code(s) => Body::Code(code::State::new(s)),
            ObjectKind::Diagram(s) => Body::Diagram(diagram::State::new(s)),
            ObjectKind::Table(s) => Body::Table(table::State::new(s)),
            ObjectKind::Math(s) => Body::Math(math::State::new(s)),
            ObjectKind::Plot(s) => Body::Plot(plot::State::new(s)),
            ObjectKind::Timeline(s) => Body::Timeline(timeline::State::new(s)),
            ObjectKind::Space(s) => Body::Space(space::State::new(s)),
            ObjectKind::Pointer(s) => Body::Pointer(connect::Pointer::new(s)),
            ObjectKind::Arrow(s) => Body::Arrow(connect::Arrow::new(s)),
        }
    }

    pub fn kind(&self) -> Kind {
        match self {
            Body::Text(_) => Kind::Text,
            Body::Array(_) => Kind::Array,
            Body::Code(_) => Kind::Code,
            Body::Diagram(_) => Kind::Diagram,
            Body::Table(_) => Kind::Table,
            Body::Math(_) => Kind::Math,
            Body::Plot(_) => Kind::Plot,
            Body::Timeline(_) => Kind::Timeline,
            Body::Space(_) => Kind::Space,
            Body::Pointer(_) => Kind::Pointer,
            Body::Arrow(_) => Kind::Arrow,
        }
    }

    /// Does this part exist right now? `id` is the object's id, for messages.
    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        if *part == Part::Whole {
            return Ok(());
        }
        match self {
            Body::Array(s) => s.check_part(id, part),
            Body::Diagram(s) => s.check_part(id, part),
            Body::Table(s) => s.check_part(id, part),
            Body::Math(s) => s.check_part(id, part),
            Body::Plot(s) => s.check_part(id, part),
            Body::Timeline(s) => s.check_part(id, part),
            Body::Space(s) => s.check_part(id, part),
            Body::Text(_) | Body::Code(_) | Body::Pointer(_) | Body::Arrow(_) => Err(format!(
                "`{id}{part}` names a part, but {} has no parts that can be named; use `{id}`",
                self.kind().a()
            )),
        }
    }

    /// Set the emphasis of a part that `check_part` has accepted.
    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        match self {
            Body::Array(s) => s.emphasize(part, emphasis),
            Body::Diagram(s) => s.emphasize(part, emphasis),
            Body::Table(s) => s.emphasize(part, emphasis),
            Body::Math(s) => s.emphasize(part, emphasis),
            Body::Plot(s) => s.emphasize(part, emphasis),
            Body::Timeline(s) => s.emphasize(part, emphasis),
            Body::Space(s) => s.emphasize(part, emphasis),
            _ => {}
        }
    }

    /// Set every part to `to` where `from` matches (or everywhere with `None`).
    pub fn repaint(&mut self, from: Option<Emphasis>, to: Emphasis) {
        let swap = |e: &mut Emphasis| {
            if from.is_none_or(|f| *e == f) {
                *e = to;
            }
        };
        match self {
            Body::Array(s) => s.each_emphasis(swap),
            Body::Diagram(s) => s.each_emphasis(swap),
            Body::Table(s) => s.each_emphasis(swap),
            Body::Math(s) => s.each_emphasis(swap),
            Body::Plot(s) => s.each_emphasis(swap),
            Body::Timeline(s) => s.each_emphasis(swap),
            Body::Space(s) => s.each_emphasis(swap),
            _ => {}
        }
    }

    /// Check and carry out an action that belongs to one family.
    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match self {
            Body::Text(s) => s.act(id, action),
            Body::Array(s) => s.act(id, action),
            Body::Code(s) => s.act(id, action),
            Body::Diagram(s) => s.act(id, action),
            Body::Table(s) => s.act(id, action),
            Body::Math(s) => s.act(id, action),
            Body::Plot(s) => s.act(id, action),
            Body::Timeline(s) => s.act(id, action),
            Body::Space(s) => s.act(id, action),
            Body::Pointer(_) | Body::Arrow(_) => Err(ActError::Unsupported),
        }
    }

    pub fn layout(&self, slot: Rect, region: Region, cx: &mut Cx) -> Option<Placed> {
        Some(match self {
            Body::Text(s) => s.layout(slot, region, cx),
            Body::Array(s) => s.layout(slot, cx),
            Body::Code(s) => s.layout(slot, cx),
            Body::Diagram(s) => s.layout(slot, cx),
            Body::Table(s) => s.layout(slot, cx),
            Body::Math(s) => s.layout(slot, cx),
            Body::Plot(s) => s.layout(slot, cx),
            Body::Timeline(s) => s.layout(slot, cx),
            Body::Space(s) => s.layout(slot, cx),
            Body::Pointer(_) | Body::Arrow(_) => return None,
        })
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, region: Region, cx: &mut Cx) {
        match self {
            Body::Text(s) => s.paint(placed, whole, region, cx),
            Body::Array(s) => s.paint(placed, whole, cx),
            Body::Code(s) => s.paint(placed, whole, cx),
            Body::Diagram(s) => s.paint(placed, whole, cx),
            Body::Table(s) => s.paint(placed, whole, cx),
            Body::Math(s) => s.paint(placed, whole, cx),
            Body::Plot(s) => s.paint(placed, whole, cx),
            Body::Timeline(s) => s.paint(placed, whole, cx),
            Body::Space(s) => s.paint(placed, whole, cx),
            Body::Pointer(_) | Body::Arrow(_) => {}
        }
    }

    /// The box of a part, for pointers and arrows to attach to.
    pub fn part_rect(&self, placed: &Placed, part: &Part) -> Option<Rect> {
        let union = |rects: &[Rect]| rects.iter().copied().reduce(|a, b| a.union(&b));
        match (part, &placed.geometry) {
            (Part::Whole, _) => Some(placed.bounds),
            (Part::Index(i), Geometry::Cells(cells)) => cells.get(*i).copied(),
            (Part::Range { start, end }, Geometry::Cells(cells)) => union(cells.get(*start..*end)?),
            (Part::Index(r), Geometry::Grid { cells, .. }) => union(cells.get(*r)?),
            (Part::Range { start, end }, Geometry::Grid { cells, .. }) => {
                let rows: Vec<Rect> = cells.get(*start..*end)?.iter().flatten().copied().collect();
                union(&rows)
            }
            (Part::Cell { row, col }, Geometry::Grid { cells, .. }) => cells.get(*row)?.get(*col).copied(),
            (Part::Name(name), Geometry::Grid { header, cells }) => {
                let Body::Table(table) = self else { return None };
                let col = table.column(name)?;
                let mut rects: Vec<Rect> = cells.iter().filter_map(|r| r.get(col).copied()).collect();
                rects.extend(header.get(col).copied());
                union(&rects)
            }
            (Part::Name(name), Geometry::Nodes(nodes)) => nodes.iter().find(|(id, _)| id == name).map(|(_, r)| *r),
            (Part::Edge { from, to }, Geometry::Nodes(nodes)) => {
                let find = |n: &String| nodes.iter().find(|(id, _)| id == n).map(|(_, r)| *r);
                let (a, b) = (find(from)?, find(to)?);
                let (x, y) = ((a.cx() + b.cx()) / 2.0, (a.cy() + b.cy()) / 2.0);
                Some(Rect { x: x - 4.0, y: y - 4.0, w: 8.0, h: 8.0 })
            }
            _ => None,
        }
    }
}
