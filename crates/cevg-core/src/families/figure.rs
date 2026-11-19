//! Figure family: a drawn diagram given as SVG. Script type `figure`.
//!
//! Textbook figures (the three-schema architecture, a three-tier system, the
//! OSI stack) need a layout that the node-link family cannot give. A figure
//! is an SVG picture whose top-level groups with an `id` are its parts:
//! `fig.conceptual` is `<g id="conceptual">`. Parts can be built up one by
//! one with `reveal` and highlighted, marked or dimmed like any other part.
//!
//! The SVG is drawn by resvg with the bundled fonts only. External files,
//! raster images and scripts are never loaded: a figure is shapes and text.
//!
//! On the hosted platform a figure may give a `prompt` instead of `svg`; the
//! server has the SVG drawn from the prompt before the script reaches here.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::ActionKind;
use crate::target::{is_valid_name, Part};
use resvg::tiny_skia::{Pixmap, Transform};
use resvg::usvg;
use serde::Deserialize;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex, OnceLock};

/// Largest SVG accepted, in bytes.
const MAX_SVG: usize = 400_000;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// The picture. Required when the script is rendered.
    #[serde(default)]
    pub svg: Option<String>,
    /// What to draw, for the hosted platform to turn into `svg`.
    #[serde(default)]
    pub prompt: Option<String>,
    /// Start with every part hidden, to be brought in one by one with `reveal`.
    #[serde(default)]
    pub build: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    svg: Arc<str>,
    key: u64,
    /// Parts in document order: name, visible, emphasis.
    parts: Vec<(String, bool, Emphasis)>,
}

// ------------------------------------------------------------------ parsing

/// One parsed figure: the whole picture, the picture with its parts cut out,
/// and each part on its own with its box in SVG units (from its drawn pixels).
struct Parsed {
    full: usvg::Tree,
    base: Option<usvg::Tree>,
    size: (f32, f32),
    parts: Vec<(String, Option<usvg::Tree>, Option<[f32; 4]>)>,
}

fn fontdb() -> Arc<usvg::fontdb::Database> {
    static DB: OnceLock<Arc<usvg::fontdb::Database>> = OnceLock::new();
    DB.get_or_init(|| {
        let mut db = usvg::fontdb::Database::new();
        for data in crate::text::FONT_DATA {
            db.load_font_data(data.to_vec());
        }
        db.set_sans_serif_family("Noto Sans");
        db.set_serif_family("Noto Sans");
        db.set_monospace_family("JetBrains Mono");
        Arc::new(db)
    })
    .clone()
}

fn options() -> usvg::Options<'static> {
    let mut opt = usvg::Options { fontdb: fontdb(), font_family: "Noto Sans".into(), ..Default::default() };
    opt.resources_dir = None;
    // Never fetch anything an SVG points at.
    opt.image_href_resolver = usvg::ImageHrefResolver {
        resolve_data: Box::new(|_, _, _| None),
        resolve_string: Box::new(|_, _| None),
    };
    opt
}

/// Top-level children that define things rather than draw them; every layer keeps them.
const DEFINING: &[&str] = &["defs", "style", "marker", "linearGradient", "radialGradient", "pattern", "clipPath", "mask", "filter", "symbol", "title", "desc"];

struct Outline {
    /// Byte ranges of the top-level element children, with their part name if they are one.
    children: Vec<(Option<String>, bool, std::ops::Range<usize>)>,
}

/// The top-level element children of the root `<svg>`.
fn outline(svg: &str) -> Result<Outline, String> {
    let doc = roxmltree::Document::parse(svg).map_err(|e| format!("the SVG is not well-formed XML: {e}"))?;
    let root = doc.root_element();
    if root.tag_name().name() != "svg" {
        return Err("the document must start with an <svg> element".into());
    }
    let children = root
        .children()
        .filter(|n| n.is_element())
        .map(|n| {
            let name = n.tag_name().name();
            let part = (name == "g").then(|| n.attribute("id").map(str::to_string)).flatten();
            (part, DEFINING.contains(&name), n.range())
        })
        .collect();
    Ok(Outline { children })
}

/// The SVG text with only the top-level children that `keep` accepts.
fn only(svg: &str, o: &Outline, keep: impl Fn(&Option<String>, bool) -> bool) -> String {
    let mut text = String::with_capacity(svg.len());
    let mut pos = 0;
    for (part, defining, range) in &o.children {
        if !keep(part, *defining) {
            text.push_str(&svg[pos..range.start]);
            pos = range.end;
        }
    }
    text.push_str(&svg[pos..]);
    text
}

/// The box of the drawn pixels of a pixmap, if any.
fn ink_box(pm: &Pixmap) -> Option<[u32; 4]> {
    let (w, h) = (pm.width(), pm.height());
    let data = pm.data();
    let (mut x0, mut y0, mut x1, mut y1) = (w, h, 0, 0);
    for y in 0..h {
        for x in 0..w {
            if data[((y * w + x) * 4 + 3) as usize] > 8 {
                x0 = x0.min(x);
                y0 = y0.min(y);
                x1 = x1.max(x);
                y1 = y1.max(y);
            }
        }
    }
    (x1 >= x0 && y1 >= y0).then(|| [x0, y0, x1 - x0 + 1, y1 - y0 + 1])
}

fn draw(tree: &usvg::Tree, size: (f32, f32), scale: f32) -> Option<Pixmap> {
    let mut pm = Pixmap::new((size.0 * scale).ceil().max(1.0) as u32, (size.1 * scale).ceil().max(1.0) as u32)?;
    resvg::render(tree, Transform::from_scale(scale, scale), &mut pm.as_mut());
    Some(pm)
}

fn parse(svg: &str) -> Result<Parsed, String> {
    if svg.len() > MAX_SVG {
        return Err(format!("the SVG is {} bytes; keep it under {MAX_SVG}", svg.len()));
    }
    let o = outline(svg)?;
    let opt = options();
    let tree = |text: &str, what: &str| usvg::Tree::from_str(text, &opt).map_err(|e| format!("{what} cannot be drawn: {e}"));
    let full = tree(svg, "the SVG")?;
    let size = (full.size().width(), full.size().height());
    if size.0 < 1.0 || size.1 < 1.0 {
        return Err("the SVG has no size: give it a viewBox".into());
    }
    let names: Vec<String> = o.children.iter().filter_map(|c| c.0.clone()).collect();
    let base = if names.is_empty() { None } else { Some(tree(&only(svg, &o, |part, _| part.is_none()), "the SVG without its parts")?) };
    // Each part alone, measured at one pixel per SVG unit.
    let mut parts = vec![];
    for name in names {
        let text = only(svg, &o, |part, defining| defining || part.as_deref() == Some(name.as_str()));
        let t = tree(&text, &format!("part `{name}`"))?;
        let bbox = draw(&t, size, 1.0).and_then(|pm| ink_box(&pm)).map(|b| {
            let pad = 2.0;
            [b[0] as f32 - pad, b[1] as f32 - pad, b[2] as f32 + 2.0 * pad, b[3] as f32 + 2.0 * pad]
        });
        parts.push((name, Some(t), bbox));
    }
    Ok(Parsed { full, base, size, parts })
}

fn hash_of(svg: &str) -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    svg.hash(&mut h);
    h.finish()
}

type ParsedCache = Mutex<HashMap<u64, Arc<Result<Parsed, String>>>>;

fn parsed(svg: &str, key: u64) -> Arc<Result<Parsed, String>> {
    static CACHE: OnceLock<ParsedCache> = OnceLock::new();
    let cache = CACHE.get_or_init(Default::default);
    if let Some(p) = cache.lock().unwrap().get(&key) {
        return p.clone();
    }
    let p = Arc::new(parse(svg));
    cache.lock().unwrap().insert(key, p.clone());
    p
}

/// What one layer is: the base, or a part by index.
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
enum Layer {
    Base,
    Part(usize),
}

type RasterCache = Mutex<HashMap<(u64, Layer, u32), Option<Arc<Pixmap>>>>;

/// A layer drawn at `scale` pixels per SVG unit. A part is cut to its box
/// (`bbox` times `scale`); the base covers the whole picture.
fn raster(p: &Parsed, key: u64, layer: Layer, scale: f32) -> Option<Arc<Pixmap>> {
    static CACHE: OnceLock<RasterCache> = OnceLock::new();
    let cache = CACHE.get_or_init(Default::default);
    let ck = (key, layer, (scale * 1000.0).round() as u32);
    if let Some(r) = cache.lock().unwrap().get(&ck) {
        return r.clone();
    }
    let out = match layer {
        Layer::Base => draw(p.base.as_ref().unwrap_or(&p.full), p.size, scale).map(Arc::new),
        Layer::Part(i) => {
            let (_, tree, bbox) = &p.parts[i];
            let (tree, b) = (tree.as_ref()?, (*bbox)?);
            let whole = draw(tree, p.size, scale)?;
            let (x, y) = ((b[0] * scale).floor() as i32, (b[1] * scale).floor() as i32);
            let (w, h) = ((b[2] * scale).ceil().max(1.0) as u32, (b[3] * scale).ceil().max(1.0) as u32);
            let mut cut = Pixmap::new(w, h)?;
            cut.draw_pixmap(-x, -y, whole.as_ref(), &resvg::tiny_skia::PixmapPaint::default(), Transform::identity(), None);
            Some(Arc::new(cut))
        }
    };
    let mut c = cache.lock().unwrap();
    if c.len() > 400 {
        c.clear();
    }
    c.insert(ck, out.clone());
    out
}

/// The pixel box a part layer covers at `scale`, matching `raster`.
fn part_rect(b: [f32; 4], scale: f32) -> (f32, f32, f32, f32) {
    ((b[0] * scale).floor(), (b[1] * scale).floor(), (b[2] * scale).ceil().max(1.0), (b[3] * scale).ceil().max(1.0))
}

// ------------------------------------------------------------------ checks

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    let Some(svg) = &spec.svg else {
        if spec.prompt.is_some() {
            out.push(Problem::warn(
                "prompt",
                "this figure has only a prompt: the hosted platform draws it before rendering; locally, give `svg`",
            ));
        } else {
            out.push(Problem::error("svg", "a figure needs `svg` (the picture) or, on the hosted platform, a `prompt`"));
        }
        return out;
    };
    match parse(svg) {
        Err(message) => out.push(Problem::error("svg", message)),
        Ok(p) => {
            for (name, _, bbox) in &p.parts {
                if !is_valid_name(name) {
                    out.push(Problem::warn(
                        "svg",
                        format!("part id `{name}` cannot be named in a target: use letters, digits and `_` only"),
                    ));
                }
                if bbox.is_none() {
                    out.push(Problem::warn("svg", format!("part `{name}` draws nothing")));
                }
            }
            if p.parts.is_empty() && spec.build {
                out.push(Problem::error("build", "`build` needs parts: top-level <g id=\"…\"> groups in the SVG"));
            }
        }
    }
    out
}

/// The part names of an SVG, for tools that write figures.
pub fn part_names(svg: &str) -> Result<Vec<String>, String> {
    outline(svg).map(|o| o.children.into_iter().filter_map(|c| c.0).collect())
}

/// Draw a whole SVG as the renderer would, for checking a figure on its own.
pub fn rasterize(svg: &str, width: u32) -> Result<Pixmap, String> {
    let p = parse(svg)?;
    let scale = width as f32 / p.size.0;
    let mut pm = Pixmap::new(width, (p.size.1 * scale).ceil() as u32).ok_or("bad size")?;
    resvg::render(&p.full, Transform::from_scale(scale, scale), &mut pm.as_mut());
    Ok(pm)
}

// ------------------------------------------------------------------ state

impl State {
    pub fn new(spec: &Spec) -> State {
        let svg: Arc<str> = spec.svg.clone().unwrap_or_default().into();
        let key = hash_of(&svg);
        let names = part_names(&svg).unwrap_or_default();
        State { parts: names.into_iter().map(|n| (n, !spec.build, Emphasis::Normal)).collect(), svg, key }
    }

    fn index(&self, name: &str) -> Option<usize> {
        self.parts.iter().position(|(n, _, _)| n == name)
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        match part {
            Part::Name(name) if self.index(name).is_some() => Ok(()),
            Part::Name(name) => Err(format!(
                "{id} has no part `{name}`; its parts are {}",
                if self.parts.is_empty() {
                    "none (give top-level <g id=\"…\"> groups in the SVG)".to_string()
                } else {
                    self.parts.iter().map(|(n, _, _)| format!("`{id}.{n}`")).collect::<Vec<_>>().join(", ")
                }
            )),
            _ => Err(format!("`{id}{part}` is not a part of a figure; parts are named after the SVG groups, like `{id}.name`")),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        if let Part::Name(name) = part {
            if let Some(i) = self.index(name) {
                self.parts[i].2 = emphasis;
            }
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.parts.iter_mut().for_each(|p| f(&mut p.2));
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Reveal { target } => match &target.part {
                Part::Whole => self.parts.iter_mut().for_each(|p| p.1 = true),
                part => {
                    if let Err(message) = self.check_part(id, part) {
                        return at("target", message);
                    }
                    let Part::Name(name) = part else { unreachable!() };
                    let i = self.index(name).unwrap();
                    self.parts[i].1 = true;
                }
            },
            _ => return Err(ActError::Unsupported),
        }
        Ok(Changed::Content)
    }

    /// The picture keeps its proportions and fills as much of the slot as it can.
    pub fn layout(&self, slot: Rect, _cx: &mut Cx) -> Placed {
        let res = parsed(&self.svg, self.key);
        let Ok(p) = res.as_ref() else {
            return Placed { bounds: slot, skirt: 0.0, scale: 1.0, geometry: Geometry::None };
        };
        let scale = (slot.w / p.size.0).min(slot.h / p.size.1);
        let (w, h) = (p.size.0 * scale, p.size.1 * scale);
        let bounds = Rect { x: slot.cx() - w / 2.0, y: slot.cy() - h / 2.0, w, h };
        let nodes = p
            .parts
            .iter()
            .filter_map(|(name, _, bbox)| {
                let (x, y, w, h) = part_rect((*bbox)?, scale);
                Some((name.clone(), Rect { x: bounds.x + x, y: bounds.y + y, w, h }))
            })
            .collect();
        Placed { bounds, skirt: 8.0, scale, geometry: Geometry::Nodes(nodes) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let res = parsed(&self.svg, self.key);
        let Ok(p) = res.as_ref() else { return };
        let scale = placed.scale;
        let wt = cx.tone(Emphasis::Normal, whole);
        cx.at("base");
        if let Some(img) = raster(p, self.key, Layer::Base, scale) {
            cx.image(&img, self.key, placed.bounds, wt.ink_opacity);
        }
        for (i, ((name, visible, emphasis), (_, _, bbox))) in self.parts.iter().zip(&p.parts).enumerate() {
            let Some(b) = bbox else { continue };
            if !visible {
                continue;
            }
            cx.at(name.clone());
            let (x, y, w, h) = part_rect(*b, scale);
            let r = Rect { x: placed.bounds.x + x, y: placed.bounds.y + y, w, h };
            let tone = cx.tone(*emphasis, whole);
            // The band is always there, clear when the part is plain, so a
            // highlight fades in and out in place.
            let pad = 10.0 * cx.u;
            let band = Rect { x: r.x - pad, y: r.y - pad, w: r.w + 2.0 * pad, h: r.h + 2.0 * pad };
            let on = if tone.heavy { 1.0 } else { 0.0 };
            cx.fill_round_rect(band, 14.0 * cx.u, tone.fill, 0.55 * on);
            cx.stroke_round_rect(band, 14.0 * cx.u, tone.border, 3.0 * cx.u, on);
            if let Some(img) = raster(p, self.key, Layer::Part(i), scale) {
                let mut h = std::collections::hash_map::DefaultHasher::new();
                (self.key, name).hash(&mut h);
                cx.image(&img, h.finish(), r, tone.ink_opacity);
            }
        }
    }
}

/// Every layer of a figure drawn on its own, for checking: the base, then each
/// part with its box in pixels at the given width.
pub fn layers(svg: &str, width: u32) -> Result<Vec<(String, [f32; 4], Pixmap)>, String> {
    let p = parse(svg)?;
    let key = hash_of(svg);
    let scale = width as f32 / p.size.0;
    let mut out = vec![];
    if let Some(img) = raster(&p, key, Layer::Base, scale) {
        out.push(("(base)".to_string(), [0.0, 0.0, p.size.0 * scale, p.size.1 * scale], (*img).clone()));
    }
    for (i, (name, _, bbox)) in p.parts.iter().enumerate() {
        if let (Some(b), Some(img)) = (bbox, raster(&p, key, Layer::Part(i), scale)) {
            let (x, y, w, h) = part_rect(*b, scale);
            out.push((name.clone(), [x, y, w, h], (*img).clone()));
        }
    }
    Ok(out)
}
