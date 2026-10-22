//! Rendering: a [`World`] in, a picture out.
//!
//! This module knows nothing about any particular family. It divides the
//! canvas into regions, hands each placed object a slot, asks the object's
//! family to lay itself out and draw itself, and then lets pointers and
//! arrows attach to the results. Families draw through [`Cx`], which records
//! a display list (see `draw`); the list is painted afterwards.
//!
//! All sizes are in units of 1/1080 of the canvas height (`cx.u`), so the
//! same script renders identically at 720p, 1080p or 4K.

use crate::families::{connect, math, Emphasis, Geometry, Placed};
use crate::script::{Canvas, Region, Script, Theme};
use crate::state::{Item, World};
use crate::target::Target;
use crate::draw::{raster, Cmd, Shape};
use crate::text::{Face, Fonts, HAlign};
use std::collections::BTreeMap;
use std::sync::Arc;
use tiny_skia::Pixmap;

pub type Rgb = [u8; 3];

pub struct Palette {
    pub background: Rgb,
    pub surface: Rgb,
    /// Table headers.
    pub header: Rgb,
    pub border: Rgb,
    pub text: Rgb,
    pub muted: Rgb,
    /// Highlight: the moving focus.
    pub accent: Rgb,
    pub accent_fill: Rgb,
    /// Mark: visited, sorted, done.
    pub mark: Rgb,
    pub mark_fill: Rgb,
    /// One colour per pointer, in declaration order.
    pub pointers: [Rgb; 4],
}

const DARK: Palette = Palette {
    background: [15, 18, 26],
    surface: [28, 34, 48],
    header: [40, 48, 68],
    border: [66, 78, 105],
    text: [232, 236, 244],
    muted: [139, 149, 169],
    accent: [245, 184, 61],
    accent_fill: [74, 58, 24],
    mark: [94, 214, 150],
    mark_fill: [24, 64, 48],
    pointers: [[94, 196, 255], [255, 138, 168], [201, 160, 255], [255, 170, 100]],
};

const LIGHT: Palette = Palette {
    background: [250, 250, 247],
    surface: [255, 255, 255],
    header: [236, 239, 245],
    border: [176, 184, 200],
    text: [24, 28, 38],
    muted: [104, 113, 130],
    accent: [201, 122, 0],
    accent_fill: [255, 236, 196],
    mark: [22, 140, 82],
    mark_fill: [214, 244, 226],
    pointers: [[0, 112, 201], [204, 51, 102], [122, 77, 204], [196, 98, 0]],
};

/// A dimmed part fades its box strongly but keeps its content readable: the
/// viewer should still be able to read what was ruled out.
const DIM_BOX: f32 = 0.35;
const DIM_INK: f32 = 0.6;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Rect {
    pub x: f32,
    pub y: f32,
    pub w: f32,
    pub h: f32,
}

impl Rect {
    pub fn cx(&self) -> f32 {
        self.x + self.w / 2.0
    }
    pub fn cy(&self) -> f32 {
        self.y + self.h / 2.0
    }
    pub fn bottom(&self) -> f32 {
        self.y + self.h
    }
    pub fn union(&self, o: &Rect) -> Rect {
        let (x, y) = (self.x.min(o.x), self.y.min(o.y));
        let r = (self.x + self.w).max(o.x + o.w);
        let b = self.bottom().max(o.bottom());
        Rect { x, y, w: r - x, h: b - y }
    }
    pub fn inset(&self, d: f32) -> Rect {
        Rect { x: self.x + d, y: self.y + d, w: self.w - 2.0 * d, h: self.h - 2.0 * d }
    }
}

/// How a part should look, given its own emphasis and its object's.
pub struct Tone {
    pub fill: Rgb,
    pub border: Rgb,
    pub ink: Rgb,
    pub box_opacity: f32,
    pub ink_opacity: f32,
    /// Highlighted or marked: draw heavier borders.
    pub heavy: bool,
}

/// The drawing context handed to families. It records commands into a
/// display list; nothing is painted here.
pub struct Cx<'a> {
    list: &'a mut Vec<Cmd>,
    pub fonts: &'a mut Fonts,
    pub math: &'a mut math::Engine,
    pub pal: &'static Palette,
    /// One layout unit in pixels.
    pub u: f32,
    object: String,
    part: String,
    seq: usize,
}

impl Cx<'_> {
    /// A part's own emphasis wins; otherwise it takes its object's.
    pub fn tone(&self, part: Emphasis, whole: Emphasis) -> Tone {
        let pal = self.pal;
        let emphasis = if part == Emphasis::Normal { whole } else { part };
        let plain = Tone { fill: pal.surface, border: pal.border, ink: pal.text, box_opacity: 1.0, ink_opacity: 1.0, heavy: false };
        match emphasis {
            Emphasis::Normal => plain,
            Emphasis::Highlight => Tone { fill: pal.accent_fill, border: pal.accent, ink: pal.accent, heavy: true, ..plain },
            Emphasis::Mark => Tone { fill: pal.mark_fill, border: pal.mark, ink: pal.mark, heavy: true, ..plain },
            Emphasis::Dim => Tone { box_opacity: DIM_BOX, ink_opacity: DIM_INK, ..plain },
        }
    }

    /// Start drawing another object. The renderer calls this, not families.
    pub fn object(&mut self, id: &str) {
        self.object = id.to_string();
        self.at("");
    }

    /// Say which part of the object the next commands draw. Animation
    /// matches commands by object, part and order within the part, so a part
    /// name must stay with its thing: name an array cell by the identity of
    /// its element, not by where it currently sits.
    pub fn at(&mut self, part: impl Into<String>) {
        self.part = part.into();
        self.seq = 0;
    }

    fn push(&mut self, shape: Shape) {
        let key = format!("{}|{}|{}", self.object, self.part, self.seq);
        self.seq += 1;
        self.list.push(Cmd { key, shape });
    }

    #[allow(clippy::too_many_arguments)]
    pub fn text(&mut self, text: &str, size: f32, face: Face, color: Rgb, opacity: f32, x: f32, y: f32, align: HAlign, max_w: Option<f32>) {
        self.push(Shape::Text { text: text.to_string(), face, align, max_w, x, y, size, color, opacity });
    }

    /// The largest size up to `size` at which the text is no wider than `room`.
    pub fn fit(&mut self, text: &str, size: f32, face: Face, room: f32) -> f32 {
        let (w, _) = self.fonts.measure(text, size, face, None);
        if w > room { size * room / w } else { size }
    }

    pub fn fill_rect(&mut self, rect: Rect, color: Rgb, opacity: f32) {
        self.fill_round_rect(rect, 0.0, color, opacity);
    }

    pub fn fill_round_rect(&mut self, rect: Rect, radius: f32, color: Rgb, opacity: f32) {
        self.push(Shape::Fill { rect, radius, color, opacity });
    }

    pub fn stroke_round_rect(&mut self, rect: Rect, radius: f32, color: Rgb, width: f32, opacity: f32) {
        self.push(Shape::Stroke { rect, radius, color, width, opacity });
    }

    pub fn line(&mut self, a: (f32, f32), b: (f32, f32), color: Rgb, width: f32, opacity: f32) {
        self.push(Shape::Line { a, b, color, width, opacity, head: false });
    }

    /// A straight line with a filled triangular head at `b`.
    pub fn arrow(&mut self, a: (f32, f32), b: (f32, f32), color: Rgb, width: f32, opacity: f32) {
        self.push(Shape::Line { a, b, color, width, opacity, head: true });
    }

    /// A line through the points, in order, painted only inside `clip`.
    pub fn path(&mut self, points: &[(f32, f32)], clip: Rect, color: Rgb, width: f32, opacity: f32) {
        self.push(Shape::Path { points: points.to_vec(), clip, color, width, opacity, drawn: 1.0 });
    }

    /// A transparent image drawn into `rect`. `id` names what it shows, so
    /// that the same thing at another size is recognised as the same.
    pub fn image(&mut self, image: &Arc<Pixmap>, id: u64, rect: Rect, opacity: f32) {
        self.push(Shape::Image { image: image.clone(), id, x: rect.x, y: rect.y, w: rect.w, h: rect.h, opacity });
    }
}

/// The point where a line from the centre of `r` toward `toward` leaves the
/// rectangle, pushed out by `gap`.
pub fn edge_point(r: Rect, toward: (f32, f32), gap: f32) -> (f32, f32) {
    let (cx, cy) = (r.cx(), r.cy());
    let (dx, dy) = (toward.0 - cx, toward.1 - cy);
    if dx == 0.0 && dy == 0.0 {
        return (cx, cy);
    }
    let tx = if dx != 0.0 { (r.w / 2.0) / dx.abs() } else { f32::INFINITY };
    let ty = if dy != 0.0 { (r.h / 2.0) / dy.abs() } else { f32::INFINITY };
    let t = tx.min(ty);
    let len = (dx * dx + dy * dy).sqrt();
    (cx + dx * t + dx / len * gap, cy + dy * t + dy / len * gap)
}

fn region_rect(canvas: &Canvas, region: Region, u: f32) -> Rect {
    let w = canvas.width as f32;
    let margin = 96.0 * u;
    let full = w - 2.0 * margin;
    let half = full / 2.0 - 60.0 * u;
    match region {
        Region::Title => Rect { x: margin, y: 56.0 * u, w: full, h: 140.0 * u },
        Region::Center => Rect { x: margin, y: 230.0 * u, w: full, h: 620.0 * u },
        Region::Left => Rect { x: margin, y: 230.0 * u, w: half, h: 620.0 * u },
        Region::Right => Rect { x: w - margin - half, y: 230.0 * u, w: half, h: 620.0 * u },
        Region::Bottom => Rect { x: margin, y: 884.0 * u, w: full, h: 140.0 * u },
    }
}

pub fn palette(theme: Theme) -> &'static Palette {
    match theme {
        Theme::Dark => &DARK,
        Theme::Light => &LIGHT,
    }
}

pub struct Renderer {
    pub(crate) fonts: Fonts,
    math: math::Engine,
}

impl Default for Renderer {
    fn default() -> Self {
        Self::new()
    }
}

impl Renderer {
    pub fn new() -> Renderer {
        Renderer { fonts: Fonts::new(), math: math::Engine::default() }
    }

    /// Draw one world. The script supplies the canvas size and theme.
    pub fn render(&mut self, script: &Script, world: &World) -> Pixmap {
        let cmds = self.display_list(script, world);
        let canvas = &script.canvas;
        raster(&cmds, canvas.width, canvas.height, palette(canvas.theme).background, &mut self.fonts)
    }

    /// Everything one world draws, in paint order, without painting it.
    pub fn display_list(&mut self, script: &Script, world: &World) -> Vec<Cmd> {
        self.display_list_scaled(script, world, 1.0)
    }

    /// The same, with the picture using only the top `scale` of the canvas
    /// height. Captions go in the space this leaves at the bottom. The layout
    /// itself is done smaller, so text and math stay sharp.
    pub fn display_list_scaled(&mut self, script: &Script, world: &World, scale: f32) -> Vec<Cmd> {
        let canvas = &script.canvas;
        let u = canvas.height as f32 / 1080.0 * scale;
        let mut list = Vec::new();
        let mut cx = Cx {
            list: &mut list,
            fonts: &mut self.fonts,
            math: &mut self.math,
            pal: palette(canvas.theme),
            u,
            object: String::new(),
            part: String::new(),
            seq: 0,
        };

        // Layout. The visible objects of a region stack top to bottom in
        // equal slots. A hidden object takes no room, so a region can show
        // one thing in one scene and another in the next; when something is
        // shown or hidden, its neighbours glide to their new places.
        let mut placed: BTreeMap<&str, (Placed, Region)> = BTreeMap::new();
        for region in [Region::Title, Region::Center, Region::Left, Region::Right, Region::Bottom] {
            let items: Vec<&Item> = world.items.iter().filter(|i| i.visible && i.region == Some(region)).collect();
            let area = region_rect(canvas, region, u);
            let slot_h = area.h / items.len().max(1) as f32;
            // Stacked objects keep a little air between them.
            let air = if items.len() > 1 { 14.0 * u } else { 0.0 };
            for (k, item) in items.into_iter().enumerate() {
                let slot = Rect { x: area.x, y: area.y + slot_h * k as f32 + air, w: area.w, h: slot_h - 2.0 * air };
                if let Some(p) = item.body.layout(slot, region, &mut cx) {
                    placed.insert(item.id.as_str(), (p, region));
                }
            }
        }

        // Paint placed objects in declaration order, then what attaches.
        for item in world.items.iter().filter(|i| i.visible) {
            if let Some((p, region)) = placed.get(item.id.as_str()) {
                cx.object(&item.id);
                item.body.paint(p, item.emphasis, *region, &mut cx);
            }
        }
        let resolve = |t: &Target| -> Option<connect::Spot> {
            let item = world.get(&t.object).filter(|i| i.visible)?;
            let (p, _) = placed.get(t.object.as_str())?;
            let rect = item.body.part_rect(p, &t.part)?;
            // Only diagram nodes crowd a pointer; array cells and table
            // cells sit in rows that leave the space below free.
            let neighbours = match &p.geometry {
                Geometry::Nodes(nodes) => nodes.iter().map(|(_, r)| *r).filter(|r| *r != rect).collect(),
                _ => vec![],
            };
            Some(connect::Spot { rect, skirt: p.skirt, neighbours })
        };
        connect::paint_arrows(world, &resolve, &mut cx);
        connect::paint_pointers(world, &resolve, &mut cx);
        list
    }
}
