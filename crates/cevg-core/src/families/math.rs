//! Math family: typeset equations, shown line by line. Script type `math`.
//!
//! The typesetting is done by Typst, embedded as a library. Each line of a
//! `math` object is written in Typst's math syntax, which is close to how
//! math is spoken: `x^2`, `a/b` for a fraction, `sqrt(x)`, `sum_(i=1)^n i`,
//! `integral_0^1 f(x) dif x`, `mat(1, 2; 3, 4)`, Greek letters by name.
//!
//! Parts: `eq[i]` a line, zero-based. Actions: `reveal` shows lines up to the
//! target, `set` rewrites a line.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::{ActionKind, Cell};
use crate::target::Part;
use serde::Deserialize;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, OnceLock};
use tiny_skia::Pixmap;
use typst::diag::{FileError, FileResult};
use typst::foundations::{Bytes, Datetime, Duration};
use typst::syntax::{FileId, Source};
use typst::text::{Font, FontBook};
use typst::utils::{LazyHash, Scalar};
use typst::{Library, LibraryExt};
use typst_layout::PagedDocument;

/// Height of the letters of a full-size line, in layout units.
const SIZE: f32 = 54.0;
/// Space between lines, as a multiple of the size.
const GAP: f32 = 0.45;
/// The font size Typst sets the math in. Only the ratio to pixels matters.
const TYPST_PT: f32 = 20.0;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// One equation per line, in Typst math syntax.
    pub lines: Vec<String>,
    /// How many lines are visible at the start. Default 1.
    #[serde(default)]
    pub shown: Option<usize>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub lines: Vec<(String, Emphasis)>,
    pub shown: usize,
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    if spec.lines.is_empty() {
        out.push(Problem::error("lines", "a math object needs at least one line"));
    }
    for (i, line) in spec.lines.iter().enumerate() {
        if let Err(message) = check_line(line) {
            out.push(Problem::error(format!("lines[{i}]"), message));
        }
    }
    if let Some(shown) = spec.shown {
        if shown > spec.lines.len() {
            out.push(Problem::error(
                "shown",
                format!("{shown} is more than the {} lines there are", spec.lines.len()),
            ));
        }
    }
    out
}

impl State {
    pub fn new(spec: &Spec) -> State {
        State {
            lines: spec.lines.iter().map(|l| (l.clone(), Emphasis::Normal)).collect(),
            shown: spec.shown.unwrap_or(1).min(spec.lines.len()),
        }
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        let last = match part {
            Part::Index(i) => *i,
            Part::Range { end, .. } => end - 1,
            _ => return Err(format!("`{id}{part}` is not a part of a math object; its lines are written `{id}[0]`")),
        };
        if last >= self.lines.len() {
            return Err(format!("{id}{part} is out of range, {id} has {} lines", self.lines.len()));
        }
        Ok(())
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        let range = match part {
            Part::Index(i) => *i..i + 1,
            Part::Range { start, end } => *start..*end,
            _ => return,
        };
        for line in self.lines.iter_mut().take(range.end).skip(range.start) {
            line.1 = emphasis;
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.lines.iter_mut().for_each(|l| f(&mut l.1));
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        let line_of = |target: &crate::target::Target, name: &str| match target.part {
            Part::Index(i) => match self.check_part(id, &target.part) {
                Ok(()) => Ok(i),
                Err(message) => at("target", message),
            },
            _ => at("target", format!("`{name}` needs one line such as `{id}[1]`, not `{target}`")),
        };
        match action {
            ActionKind::Reveal { target } => {
                let i = line_of(target, "reveal")?;
                self.shown = i + 1;
            }
            ActionKind::Set { target, value } => {
                let i = line_of(target, "set")?;
                let Cell::Text(line) = value else {
                    return at("value", "a math line is text in Typst math syntax, so `value` must be a string");
                };
                if let Err(message) = check_line(line) {
                    return at("value", message);
                }
                self.lines[i].0 = line.clone();
            }
            _ => return Err(ActError::Unsupported),
        }
        Ok(Changed::Content)
    }

    /// Every line keeps its place whether or not it is revealed yet, so that
    /// revealing one never moves the others.
    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let size = SIZE * cx.u;
        let ink = cx.pal.text;
        let sizes: Vec<(f32, f32)> = self
            .lines
            .iter()
            .map(|(line, _)| cx.math.image(line, size, ink).map_or((0.0, size), |p| (p.width() as f32, p.height() as f32)))
            .collect();
        let gap = size * GAP;
        let total_h = sizes.iter().map(|s| s.1).sum::<f32>() + gap * sizes.len().saturating_sub(1) as f32;
        let total_w = sizes.iter().map(|s| s.0).fold(1.0f32, f32::max);
        let scale = (slot.w / total_w).min(slot.h / total_h).min(1.0);

        let mut y = slot.cy() - total_h * scale / 2.0;
        let rects: Vec<Rect> = sizes
            .iter()
            .map(|(w, h)| {
                let r = Rect { x: slot.cx() - w * scale / 2.0, y, w: w * scale, h: h * scale };
                y += (h + gap) * scale;
                r
            })
            .collect();
        let bounds = rects.iter().copied().reduce(|a, b| a.union(&b)).unwrap_or(slot);
        Placed { bounds, skirt: 8.0 * cx.u, scale, geometry: Geometry::Cells(rects) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let Geometry::Cells(rects) = &placed.geometry else { return };
        let size = SIZE * cx.u * placed.scale;
        for (i, ((line, emphasis), rect)) in self.lines.iter().zip(rects).enumerate().take(self.shown) {
            cx.at(format!("line{i}"));
            let tone = cx.tone(*emphasis, whole);
            // The band is always there, transparent when the line is plain,
            // so that a highlight fades in and out in place.
            let band = Rect { x: rect.x - size * 0.5, y: rect.y - size * 0.15, w: rect.w + size, h: rect.h + size * 0.3 };
            cx.fill_round_rect(band, size * 0.25, tone.fill, if tone.heavy { tone.box_opacity } else { 0.0 });
            if let Some(image) = cx.math.image(line, size, tone.ink) {
                // The same line in the same colour is the same picture at
                // any size, so a change of scale glides instead of fading.
                let mut hasher = std::collections::hash_map::DefaultHasher::new();
                (line, tone.ink).hash(&mut hasher);
                cx.image(&image, hasher.finish(), *rect, tone.ink_opacity);
            }
        }
    }
}

// ------------------------------------------------------------------ Typst

/// What every compile shares: the standard library and the bundled fonts.
struct Shared {
    library: LazyHash<Library>,
    book: LazyHash<FontBook>,
    fonts: Vec<Font>,
}

fn shared() -> &'static Shared {
    static SHARED: OnceLock<Shared> = OnceLock::new();
    SHARED.get_or_init(|| {
        let fonts: Vec<Font> = typst_assets::fonts().flat_map(|data| Font::iter(Bytes::new(data))).collect();
        Shared {
            library: LazyHash::new(Library::default()),
            book: LazyHash::new(FontBook::from_fonts(&fonts)),
            fonts,
        }
    })
}

/// A Typst world with exactly one file in it and no access to anything else.
struct OneFile(Source);

impl typst::World for OneFile {
    fn library(&self) -> &LazyHash<Library> {
        &shared().library
    }
    fn book(&self) -> &LazyHash<FontBook> {
        &shared().book
    }
    fn main(&self) -> FileId {
        self.0.id()
    }
    fn source(&self, id: FileId) -> FileResult<Source> {
        if id == self.0.id() {
            Ok(self.0.clone())
        } else {
            Err(FileError::AccessDenied)
        }
    }
    fn file(&self, _: FileId) -> FileResult<Bytes> {
        Err(FileError::AccessDenied)
    }
    fn font(&self, index: usize) -> Option<Font> {
        shared().fonts.get(index).cloned()
    }
    fn today(&self, _: Option<Duration>) -> Option<Datetime> {
        None
    }
}

fn compile(line: &str, ink: [u8; 3]) -> Result<PagedDocument, String> {
    // A line is math only. `$` would end math mode and `#` would start Typst
    // code, so neither is allowed in.
    if let Some(bad) = line.chars().find(|c| matches!(c, '$' | '#')) {
        return Err(format!("`{bad}` is not allowed in a math line; write only the math, without `$` signs"));
    }
    if line.trim().is_empty() {
        return Err("the line is empty".to_string());
    }
    let [r, g, b] = ink;
    let source = format!(
        "#set page(width: auto, height: auto, margin: 2pt, fill: none)\n\
         #set text(size: {TYPST_PT}pt, fill: rgb({r}, {g}, {b}))\n\
         $ {line} $\n"
    );
    let world = OneFile(Source::detached(source));
    typst::compile::<PagedDocument>(&world).output.map_err(|errors| {
        let mut text = String::from("not valid Typst math: ");
        for (i, e) in errors.iter().enumerate() {
            if i > 0 {
                text.push_str("; ");
            }
            text.push_str(&e.message);
            for hint in &e.hints {
                text.push_str(" (hint: ");
                text.push_str(&hint.v);
                text.push(')');
            }
        }
        text
    })
}

/// Does the line typeset? The answer is cached: a script is validated once
/// and then replayed for every frame.
pub fn check_line(line: &str) -> Result<(), String> {
    thread_local! {
        static SEEN: std::cell::RefCell<HashMap<String, Result<(), String>>> = Default::default();
    }
    SEEN.with(|seen| {
        seen.borrow_mut()
            .entry(line.to_string())
            .or_insert_with(|| compile(line, [0, 0, 0]).map(|_| ()))
            .clone()
    })
}

/// Typesets lines into images and remembers them, since the same line is
/// drawn in every frame of a step.
#[derive(Default)]
pub struct Engine {
    cache: HashMap<(String, u32, [u8; 3]), Option<Arc<Pixmap>>>,
}

impl Engine {
    /// The line as a transparent image whose letters are about `size` pixels
    /// tall, in the given colour. `None` if it does not typeset.
    pub fn image(&mut self, line: &str, size: f32, ink: [u8; 3]) -> Option<Arc<Pixmap>> {
        // Sizes are rounded to a tenth of a pixel for the cache key.
        let key = (line.to_string(), (size * 10.0).round() as u32, ink);
        self.cache
            .entry(key)
            .or_insert_with(|| {
                let document = compile(line, ink).ok()?;
                let page = document.pages().first()?;
                let options = typst_render::RenderOptions {
                    pixel_per_pt: Scalar::new((size / TYPST_PT) as f64),
                    render_bleed: false,
                };
                Some(Arc::new(typst_render::render(page, &options)))
            })
            .clone()
    }
}
