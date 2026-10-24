//! The display list: what a frame is made of, before any pixel is touched.
//!
//! Families do not paint. They record [`Cmd`]s: a filled box here, a line
//! there, this text at that size. Two things follow from that:
//!
//! * Animation needs no knowledge of families. [`blend`] takes the lists
//!   before and after each action and mixes them: numbers (positions, sizes,
//!   colours, opacity) are interpolated, content that changed is crossfaded,
//!   and things that appear fade in.
//! * Frames can be rasterised on any thread, since a list is plain data.
//!
//! Every command has a key that says which thing it draws ("the box of array
//! cell 7", "the label of node h1"). Blending matches commands by key, so a
//! key must stay with its thing for as long as that thing exists.

use crate::render::{Rect, Rgb};
use crate::space3d::{Camera, Content, Projection, Scene, Solid, SpaceBackend, Vec3, CAMERA_NUMBERS};
use crate::text::{Face, Fonts, HAlign, Style};
use std::collections::HashMap;
use std::sync::Arc;
use tiny_skia::{
    BlendMode, Color, FillRule, FilterQuality, LineCap, LineJoin, Paint, Path, PathBuilder, Pixmap, PixmapPaint, Stroke, Transform,
};

#[derive(Debug, Clone)]
pub struct Cmd {
    pub key: String,
    pub shape: Shape,
}

#[derive(Debug, Clone)]
pub enum Shape {
    Fill { rect: Rect, radius: f32, color: Rgb, opacity: f32 },
    Stroke { rect: Rect, radius: f32, color: Rgb, width: f32, opacity: f32 },
    /// A straight line, with an arrowhead at `b` when `head` is set.
    Line { a: (f32, f32), b: (f32, f32), color: Rgb, width: f32, opacity: f32, head: bool },
    /// A line through many points. `drawn` is how much of its length is
    /// shown, from 0 to 1, which is how a curve traces itself.
    /// Only the part inside `clip` is painted.
    Path { points: Vec<(f32, f32)>, clip: Rect, color: Rgb, width: f32, drawn: f32, opacity: f32 },
    /// `y` is the vertical centre; `x` is the left edge, centre or right edge
    /// according to `align`.
    Text { text: String, face: Face, align: HAlign, max_w: Option<f32>, x: f32, y: f32, size: f32, color: Rgb, opacity: f32 },
    /// A premultiplied image drawn into the box (x, y, w, h). `id` says what
    /// the image shows: two renderings of the same thing at different sizes
    /// share an id, and are scaled into each other instead of crossfaded.
    Image { image: Arc<Pixmap>, id: u64, x: f32, y: f32, w: f32, h: f32, opacity: f32 },
    /// A window onto a 3D scene: the box it fills and the camera. The solids
    /// of the same `scene` are drawn into it by the space backend.
    Viewport { scene: u64, rect: Rect, camera: [f32; CAMERA_NUMBERS], opacity: f32 },
    /// One thing inside a 3D scene, in scene coordinates. Not painted on its
    /// own: the viewport of its scene gathers it.
    Solid { scene: u64, content: Arc<Content>, vertices: Vec<Vec3>, color: Rgb, drawn: f32, opacity: f32 },
    /// Text pinned to a point of a 3D scene, drawn flat on top of the
    /// viewport, offset by (`dx`, `dy`) pixels from the projected point.
    Label3d { scene: u64, text: String, face: Face, align: HAlign, at: Vec3, dx: f32, dy: f32, size: f32, color: Rgb, opacity: f32 },
}

fn rgb(c: Rgb) -> [f32; 3] {
    [c[0] as f32, c[1] as f32, c[2] as f32]
}

fn to_rgb(n: &[f32]) -> Rgb {
    [n[0].round().clamp(0.0, 255.0) as u8, n[1].round().clamp(0.0, 255.0) as u8, n[2].round().clamp(0.0, 255.0) as u8]
}

impl Shape {
    /// Everything about the shape that can be interpolated. Opacity is last.
    fn numbers(&self) -> Vec<f32> {
        match self {
            Shape::Fill { rect, radius, color, opacity } => {
                let [r, g, b] = rgb(*color);
                vec![rect.x, rect.y, rect.w, rect.h, *radius, r, g, b, *opacity]
            }
            Shape::Stroke { rect, radius, color, width, opacity } => {
                let [r, g, b] = rgb(*color);
                vec![rect.x, rect.y, rect.w, rect.h, *radius, r, g, b, *width, *opacity]
            }
            Shape::Line { a, b, color, width, opacity, .. } => {
                let [r, g, bl] = rgb(*color);
                vec![a.0, a.1, b.0, b.1, r, g, bl, *width, *opacity]
            }
            Shape::Path { points, clip, color, width, drawn, opacity } => {
                let mut n: Vec<f32> = points.iter().flat_map(|p| [p.0, p.1]).collect();
                n.extend([clip.x, clip.y, clip.w, clip.h]);
                n.extend(rgb(*color));
                n.extend([*width, *drawn, *opacity]);
                n
            }
            Shape::Text { x, y, size, color, opacity, .. } => {
                let [r, g, b] = rgb(*color);
                vec![*x, *y, *size, r, g, b, *opacity]
            }
            Shape::Image { x, y, w, h, opacity, .. } => vec![*x, *y, *w, *h, *opacity],
            Shape::Viewport { rect, camera, opacity, .. } => {
                let mut n = vec![rect.x, rect.y, rect.w, rect.h];
                n.extend_from_slice(camera);
                n.push(*opacity);
                n
            }
            Shape::Solid { vertices, color, drawn, opacity, .. } => {
                let mut n: Vec<f32> = vertices.iter().flat_map(|v| *v).collect();
                n.push(*drawn);
                n.extend(rgb(*color));
                n.push(*opacity);
                n
            }
            Shape::Label3d { at, dx, dy, size, color, opacity, .. } => {
                let [r, g, b] = rgb(*color);
                vec![at[0], at[1], at[2], *dx, *dy, *size, r, g, b, *opacity]
            }
        }
    }

    /// The same shape with other numbers.
    fn with_numbers(&self, n: &[f32]) -> Shape {
        let rect = |n: &[f32]| Rect { x: n[0], y: n[1], w: n[2].max(0.0), h: n[3].max(0.0) };
        match self {
            Shape::Fill { .. } => Shape::Fill { rect: rect(n), radius: n[4], color: to_rgb(&n[5..8]), opacity: n[8] },
            Shape::Stroke { .. } => {
                Shape::Stroke { rect: rect(n), radius: n[4], color: to_rgb(&n[5..8]), width: n[8], opacity: n[9] }
            }
            Shape::Line { head, .. } => Shape::Line {
                a: (n[0], n[1]),
                b: (n[2], n[3]),
                color: to_rgb(&n[4..7]),
                width: n[7],
                opacity: n[8],
                head: *head,
            },
            Shape::Path { .. } => {
                let tail = n.len() - 10;
                Shape::Path {
                    points: n[..tail].chunks(2).map(|p| (p[0], p[1])).collect(),
                    clip: Rect { x: n[tail], y: n[tail + 1], w: n[tail + 2].max(0.0), h: n[tail + 3].max(0.0) },
                    color: to_rgb(&n[tail + 4..tail + 7]),
                    width: n[tail + 7],
                    drawn: n[tail + 8].clamp(0.0, 1.0),
                    opacity: n[tail + 9],
                }
            }
            Shape::Text { text, face, align, max_w, .. } => Shape::Text {
                text: text.clone(),
                face: *face,
                align: *align,
                max_w: *max_w,
                x: n[0],
                y: n[1],
                size: n[2],
                color: to_rgb(&n[3..6]),
                opacity: n[6],
            },
            Shape::Image { image, id, .. } => {
                Shape::Image { image: image.clone(), id: *id, x: n[0], y: n[1], w: n[2].max(0.0), h: n[3].max(0.0), opacity: n[4] }
            }
            Shape::Viewport { scene, .. } => {
                let mut camera = [0.0; CAMERA_NUMBERS];
                camera.copy_from_slice(&n[4..4 + CAMERA_NUMBERS]);
                Shape::Viewport { scene: *scene, rect: rect(n), camera, opacity: n[4 + CAMERA_NUMBERS] }
            }
            Shape::Solid { scene, content, .. } => {
                let tail = n.len() - 5;
                Shape::Solid {
                    scene: *scene,
                    content: content.clone(),
                    vertices: n[..tail].chunks(3).map(|v| [v[0], v[1], v[2]]).collect(),
                    drawn: n[tail].clamp(0.0, 1.0),
                    color: to_rgb(&n[tail + 1..tail + 4]),
                    opacity: n[tail + 4],
                }
            }
            Shape::Label3d { scene, text, face, align, .. } => Shape::Label3d {
                scene: *scene,
                text: text.clone(),
                face: *face,
                align: *align,
                at: [n[0], n[1], n[2]],
                dx: n[3],
                dy: n[4],
                size: n[5],
                color: to_rgb(&n[6..9]),
                opacity: n[9],
            },
        }
    }

    /// Same kind of shape showing the same thing; only numbers may differ.
    fn same_content(&self, other: &Shape) -> bool {
        match (self, other) {
            (Shape::Fill { .. }, Shape::Fill { .. }) | (Shape::Stroke { .. }, Shape::Stroke { .. }) => true,
            // Two paths with the same number of points morph into each
            // other; otherwise one replaces the other.
            (Shape::Path { points: a, .. }, Shape::Path { points: b, .. }) => a.len() == b.len(),
            (Shape::Line { head: a, .. }, Shape::Line { head: b, .. }) => a == b,
            (
                Shape::Text { text: a, face: fa, align: aa, max_w: wa, .. },
                Shape::Text { text: b, face: fb, align: ab, max_w: wb, .. },
            ) => a == b && fa == fb && aa == ab && wa.is_some() == wb.is_some(),
            (Shape::Image { id: a, .. }, Shape::Image { id: b, .. }) => a == b,
            (Shape::Viewport { scene: a, .. }, Shape::Viewport { scene: b, .. }) => a == b,
            // Solids morph when they are the same kind of thing over the
            // same number of vertices: a surface reshapes, a vector swings.
            (
                Shape::Solid { scene: sa, content: ca, vertices: va, .. },
                Shape::Solid { scene: sb, content: cb, vertices: vb, .. },
            ) => sa == sb && va.len() == vb.len() && (Arc::ptr_eq(ca, cb) || ca == cb),
            (
                Shape::Label3d { scene: sa, text: ta, face: fa, align: aa, .. },
                Shape::Label3d { scene: sb, text: tb, face: fb, align: ab, .. },
            ) => sa == sb && ta == tb && fa == fb && aa == ab,
            _ => false,
        }
    }

    fn same_kind(&self, other: &Shape) -> bool {
        std::mem::discriminant(self) == std::mem::discriminant(other)
    }

    /// The numbers of this shape just before it appears (or just after it has
    /// gone): fully transparent, and for a line about to appear, not yet
    /// drawn out from its start.
    fn ghost(&self, appearing: bool) -> Vec<f32> {
        let mut n = self.numbers();
        match (self, appearing) {
            (Shape::Line { .. }, true) => {
                n[2] = n[0];
                n[3] = n[1];
            }
            (Shape::Path { .. }, true) => {
                let drawn = n.len() - 2;
                n[drawn] = 0.0;
            }
            (Shape::Solid { content, .. }, true) if matches!(**content, Content::Segments { .. }) => {
                let drawn = n.len() - 5;
                n[drawn] = 0.0;
            }
            _ => {}
        }
        *n.last_mut().expect("opacity") = 0.0;
        n
    }
}

/// Mix the display lists around a run of actions.
///
/// `lists[0]` is the picture before the first action and `lists[i]` the
/// picture after action `i`; `progress[i - 1]` says how far action `i` has
/// got, from 0 to 1. Each action moves only what it changed, so actions that
/// overlap in time do not disturb each other.
pub fn blend(lists: &[Vec<Cmd>], progress: &[f32]) -> Vec<Cmd> {
    assert_eq!(lists.len(), progress.len() + 1, "one list more than actions");
    let last = lists.len() - 1;
    if progress.iter().all(|p| *p >= 1.0) {
        return lists[last].clone();
    }
    if progress.iter().all(|p| *p <= 0.0) {
        return lists[0].clone();
    }

    let index: Vec<HashMap<&str, usize>> =
        lists.iter().map(|l| l.iter().enumerate().map(|(i, c)| (c.key.as_str(), i)).collect()).collect();

    // Paint order: the final list's order, with things that are on their way
    // out slotted in after whatever they followed while they existed.
    let mut order: Vec<&str> = lists[last].iter().map(|c| c.key.as_str()).collect();
    let mut placed: HashMap<&str, ()> = order.iter().map(|k| (*k, ())).collect();
    for list in lists[..last].iter().rev() {
        for (i, cmd) in list.iter().enumerate() {
            if placed.contains_key(cmd.key.as_str()) {
                continue;
            }
            let after = i.checked_sub(1).and_then(|p| order.iter().position(|k| *k == list[p].key));
            order.insert(after.map_or(0, |a| a + 1), &cmd.key);
            placed.insert(&cmd.key, ());
        }
    }

    let mut out = Vec::with_capacity(order.len());
    for key in order {
        let track: Vec<Option<&Cmd>> = lists.iter().zip(&index).map(|(l, ix)| ix.get(key).map(|i| &l[*i])).collect();
        mix(key, &track, progress, &mut out);
    }
    out
}

/// Blend one key's commands across the lists.
fn mix(key: &str, track: &[Option<&Cmd>], progress: &[f32], out: &mut Vec<Cmd>) {
    // For every list, the shape to use and its numbers. Where the key is
    // absent, borrow the nearest shape as a transparent ghost: the next one
    // if the thing is about to appear, otherwise the previous one.
    let nearest = |j: usize| -> (&Shape, bool) {
        let next = track[j..].iter().flatten().next();
        let prev = track[..j].iter().rev().flatten().next();
        match (next, prev) {
            (Some(c), _) => (&c.shape, true),
            (None, Some(c)) => (&c.shape, false),
            (None, None) => unreachable!("a key is in at least one list"),
        }
    };
    let states: Vec<(&Shape, Vec<f32>)> = track
        .iter()
        .enumerate()
        .map(|(j, slot)| match slot {
            Some(c) => (&c.shape, c.shape.numbers()),
            None => {
                let (shape, appearing) = nearest(j);
                (shape, shape.ghost(appearing))
            }
        })
        .collect();

    // Numbers can only be mixed between shapes of one kind and one length.
    let one_kind = states.iter().all(|(s, n)| s.same_kind(states[0].0) && n.len() == states[0].1.len());

    let enter = |p: f32| (2.0 * p - 1.0).clamp(0.0, 1.0);
    let leave = |p: f32| (1.0 - 2.0 * p).clamp(0.0, 1.0);

    // Numbers: start from the first list and add each action's change,
    // scaled by that action's progress. Opacity is the exception when a
    // thing appears or goes: it arrives in the second half of the action,
    // once the things around it have made room, and leaves in the first
    // half, before they close up. A line is drawn out over the whole action.
    let mut numbers = states[0].1.clone();
    let opacity = numbers.len() - 1;
    let is_line = match states[0].0 {
        Shape::Line { .. } | Shape::Path { .. } => true,
        Shape::Solid { content, .. } => matches!(**content, Content::Segments { .. }),
        _ => false,
    };
    if one_kind {
        for (i, p) in progress.iter().enumerate() {
            let fade = match (track[i].is_some(), track[i + 1].is_some()) {
                (false, true) if !is_line => enter(*p),
                (true, false) => 1.0 - leave(*p),
                _ => *p,
            };
            for (k, (n, (after, before))) in numbers.iter_mut().zip(states[i + 1].1.iter().zip(&states[i].1)).enumerate() {
                *n += if k == opacity { fade } else { *p } * (after - before);
            }
        }
    }

    // Content: each run of lists with the same content is one layer. When
    // an action replaces content, the old layer fades out over the first half
    // of the action and the new one fades in over the second half, so the two
    // are never legible on top of each other.
    let mut j = 0;
    while j < states.len() {
        let mut end = j + 1;
        while end < states.len() && states[end].0.same_content(states[j].0) {
            end += 1;
        }
        let fade_in = if j == 0 { 1.0 } else { enter(progress[j - 1]) };
        let fade_out: f32 = (j + 1..states.len())
            .filter(|m| !states[*m].0.same_content(states[*m - 1].0))
            .map(|m| leave(progress[m - 1]))
            .product();
        let weight = fade_in * fade_out;
        if weight > 0.002 {
            // A key that changed its kind of shape cannot share numbers; each
            // layer then keeps its own and simply crossfades.
            let mut n = if one_kind { numbers.clone() } else { states[j].1.clone() };
            *n.last_mut().expect("opacity") *= weight;
            if *n.last().expect("opacity") > 0.002 {
                // Use the layer's latest shape: for an image that is being
                // resized, that is the rendering at the size it is heading to.
                out.push(Cmd { key: key.to_string(), shape: states[end - 1].0.with_numbers(&n) });
            }
        }
        j = end;
    }
}

// ------------------------------------------------------------ rasteriser

fn paint(color: Rgb, opacity: f32) -> Paint<'static> {
    let mut paint = Paint::default();
    let alpha = (opacity.clamp(0.0, 1.0) * 255.0).round() as u8;
    paint.set_color_rgba8(color[0], color[1], color[2], alpha);
    paint.anti_alias = true;
    paint
}

fn round_rect_path(r: Rect, radius: f32) -> Option<Path> {
    if r.w <= 0.0 || r.h <= 0.0 {
        return None;
    }
    let rad = radius.min(r.w / 2.0).min(r.h / 2.0).max(0.0);
    let k = rad * 0.5523; // control-point distance for a quarter circle
    let (x0, y0, x1, y1) = (r.x, r.y, r.x + r.w, r.y + r.h);
    let mut pb = PathBuilder::new();
    pb.move_to(x0 + rad, y0);
    pb.line_to(x1 - rad, y0);
    pb.cubic_to(x1 - rad + k, y0, x1, y0 + rad - k, x1, y0 + rad);
    pb.line_to(x1, y1 - rad);
    pb.cubic_to(x1, y1 - rad + k, x1 - rad + k, y1, x1 - rad, y1);
    pb.line_to(x0 + rad, y1);
    pb.cubic_to(x0 + rad - k, y1, x0, y1 - rad + k, x0, y1 - rad);
    pb.line_to(x0, y0 + rad);
    pb.cubic_to(x0, y0 + rad - k, x0 + rad - k, y0, x0 + rad, y0);
    pb.close();
    pb.finish()
}

fn stroke_line(pixmap: &mut Pixmap, from: (f32, f32), to: (f32, f32), color: Rgb, width: f32, opacity: f32) {
    let mut pb = PathBuilder::new();
    pb.move_to(from.0, from.1);
    pb.line_to(to.0, to.1);
    if let Some(path) = pb.finish() {
        let stroke = Stroke { width, line_cap: LineCap::Round, ..Stroke::default() };
        pixmap.stroke_path(&path, &paint(color, opacity), &stroke, Transform::identity(), None);
    }
}

fn draw_line(pixmap: &mut Pixmap, a: (f32, f32), b: (f32, f32), color: Rgb, width: f32, opacity: f32, head: bool) {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len = (dx * dx + dy * dy).sqrt();
    if len < 1.0 {
        return;
    }
    if !head {
        return stroke_line(pixmap, a, b, color, width, opacity);
    }
    let (ux, uy) = (dx / len, dy / len);
    let size = (width * 4.0).min(len * 0.6);
    let base = (b.0 - ux * size, b.1 - uy * size);
    stroke_line(pixmap, a, base, color, width, opacity);

    let half = size * 0.6;
    let mut pb = PathBuilder::new();
    pb.move_to(b.0, b.1);
    pb.line_to(base.0 - uy * half, base.1 + ux * half);
    pb.line_to(base.0 + uy * half, base.1 - ux * half);
    pb.close();
    if let Some(path) = pb.finish() {
        pixmap.fill_path(&path, &paint(color, opacity), FillRule::Winding, Transform::identity(), None);
    }
}

/// The part of the segment a-b that lies inside `r`, if any.
fn clip_segment(a: (f32, f32), b: (f32, f32), r: &Rect) -> Option<((f32, f32), (f32, f32))> {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let (mut t0, mut t1) = (0.0f32, 1.0f32);
    // Liang-Barsky: narrow [t0, t1] against each of the four edges.
    for (p, q) in [(-dx, a.0 - r.x), (dx, r.x + r.w - a.0), (-dy, a.1 - r.y), (dy, r.y + r.h - a.1)] {
        if p == 0.0 {
            if q < 0.0 {
                return None;
            }
        } else {
            let t = q / p;
            if p < 0.0 {
                t0 = t0.max(t);
            } else {
                t1 = t1.min(t);
            }
        }
    }
    (t0 <= t1).then_some(((a.0 + dx * t0, a.1 + dy * t0), (a.0 + dx * t1, a.1 + dy * t1)))
}

/// Stroke the first `drawn` part of a line through `points`, keeping only
/// what falls inside `clip`.
fn draw_path(pixmap: &mut Pixmap, points: &[(f32, f32)], clip: &Rect, color: Rgb, width: f32, drawn: f32, opacity: f32) {
    if points.len() < 2 || drawn <= 0.0 {
        return;
    }
    let length = |a: (f32, f32), b: (f32, f32)| ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt();
    let total: f32 = points.windows(2).map(|w| length(w[0], w[1])).sum();
    let mut left = total * drawn.min(1.0);
    let mut pb = PathBuilder::new();
    let mut pen: Option<(f32, f32)> = None;
    for w in points.windows(2) {
        let step = length(w[0], w[1]);
        let whole = step <= left || drawn >= 1.0;
        let end = if whole {
            w[1]
        } else {
            let f = if step > 0.0 { left / step } else { 0.0 };
            (w[0].0 + (w[1].0 - w[0].0) * f, w[0].1 + (w[1].1 - w[0].1) * f)
        };
        if let Some((a, b)) = clip_segment(w[0], end, clip) {
            // Start a new stroke wherever the line re-enters the box.
            if pen.is_none_or(|p| (p.0 - a.0).abs() > 0.01 || (p.1 - a.1).abs() > 0.01) {
                pb.move_to(a.0, a.1);
            }
            pb.line_to(b.0, b.1);
            pen = Some(b);
        }
        if !whole {
            break;
        }
        left -= step;
    }
    if let Some(path) = pb.finish() {
        let stroke = Stroke { width, line_cap: LineCap::Round, line_join: LineJoin::Round, ..Stroke::default() };
        pixmap.stroke_path(&path, &paint(color, opacity), &stroke, Transform::identity(), None);
    }
}

/// Lay a premultiplied image over the opaque canvas, at its own size.
fn blit(pixmap: &mut Pixmap, image: &Pixmap, x: f32, y: f32, opacity: f32) {
    let (ox, oy) = (x.round() as i32, y.round() as i32);
    let (pw, ph) = (pixmap.width() as i32, pixmap.height() as i32);
    let (iw, ih) = (image.width() as i32, image.height() as i32);
    let opacity = (opacity.clamp(0.0, 1.0) * 256.0) as u32;
    let src = image.data();
    let dst = pixmap.data_mut();
    for sy in (-oy).max(0)..ih.min(ph - oy) {
        for sx in (-ox).max(0)..iw.min(pw - ox) {
            let s = ((sy * iw + sx) * 4) as usize;
            let alpha = src[s + 3] as u32 * opacity / 256;
            if alpha == 0 {
                continue;
            }
            let d = (((oy + sy) * pw + ox + sx) * 4) as usize;
            for c in 0..3 {
                let over = src[s + c] as u32 * opacity / 256;
                dst[d + c] = (over + dst[d + c] as u32 * (255 - alpha) / 255).min(255) as u8;
            }
        }
    }
}

/// Draw an image into a box. At its own size it is copied exactly; while it
/// is being resized it is scaled smoothly.
fn draw_image(pixmap: &mut Pixmap, image: &Pixmap, x: f32, y: f32, w: f32, h: f32, opacity: f32) {
    let (iw, ih) = (image.width() as f32, image.height() as f32);
    if (w - iw).abs() < 1.0 && (h - ih).abs() < 1.0 {
        return blit(pixmap, image, x, y, opacity);
    }
    if w < 1.0 || h < 1.0 {
        return;
    }
    let paint = PixmapPaint { opacity: opacity.clamp(0.0, 1.0), blend_mode: BlendMode::SourceOver, quality: FilterQuality::Bilinear };
    let transform = Transform::from_row(w / iw, 0.0, 0.0, h / ih, x, y);
    pixmap.draw_pixmap(0, 0, image.as_ref(), &paint, transform, None);
}

/// The solids of one scene, as the backend takes them.
fn solids_of(cmds: &[Cmd], scene: u64) -> Vec<Solid> {
    cmds.iter()
        .filter_map(|c| match &c.shape {
            Shape::Solid { scene: s, content, vertices, color, drawn, opacity } if *s == scene => Some(Solid {
                content: content.clone(),
                vertices: vertices.clone(),
                color: *color,
                drawn: *drawn,
                opacity: *opacity,
            }),
            _ => None,
        })
        .collect()
}

/// The viewport a 3D label belongs to: its box, camera and opacity.
fn viewport_of(cmds: &[Cmd], scene: u64) -> Option<(Rect, Camera, f32)> {
    cmds.iter().find_map(|c| match &c.shape {
        Shape::Viewport { scene: s, rect, camera, opacity } if *s == scene => Some((*rect, Camera::from_numbers(camera), *opacity)),
        _ => None,
    })
}

/// Paint a display list onto a fresh canvas. 3D viewports are rendered by
/// `space` and laid in where they sit.
pub fn raster(cmds: &[Cmd], width: u32, height: u32, background: Rgb, fonts: &mut Fonts, space: &dyn SpaceBackend) -> Pixmap {
    let mut pixmap = Pixmap::new(width, height).expect("validated canvas size");
    pixmap.fill(Color::from_rgba8(background[0], background[1], background[2], 255));
    let identity = Transform::identity();
    for cmd in cmds {
        match &cmd.shape {
            Shape::Viewport { scene, rect, camera, opacity } => {
                let (w, h) = (rect.w.round() as u32, rect.h.round() as u32);
                if w == 0 || h == 0 || *opacity <= 0.002 {
                    continue;
                }
                let solids = solids_of(cmds, *scene);
                let view = Scene { camera: Camera::from_numbers(camera), width: w, height: h, background, solids: &solids };
                let image = space.render(&view);
                blit(&mut pixmap, &image, rect.x, rect.y, *opacity);
            }
            Shape::Solid { .. } => {}
            Shape::Label3d { scene, text, face, align, at, dx, dy, size, color, opacity } => {
                let Some((rect, camera, whole)) = viewport_of(cmds, *scene) else { continue };
                let proj = Projection::new(&camera, rect.w, rect.h);
                let Some(((px, py), _)) = proj.project(*at) else { continue };
                let style = Style { size: *size, face: *face, color: *color, opacity: opacity * whole };
                fonts.draw(&mut pixmap, text, style, rect.x + px + dx, rect.y + py + dy, *align, None);
            }
            Shape::Fill { rect, radius, color, opacity } => {
                if let Some(path) = round_rect_path(*rect, *radius) {
                    pixmap.fill_path(&path, &paint(*color, *opacity), FillRule::Winding, identity, None);
                }
            }
            Shape::Stroke { rect, radius, color, width, opacity } => {
                if let Some(path) = round_rect_path(*rect, *radius) {
                    let stroke = Stroke { width: *width, ..Stroke::default() };
                    pixmap.stroke_path(&path, &paint(*color, *opacity), &stroke, identity, None);
                }
            }
            Shape::Line { a, b, color, width, opacity, head } => {
                draw_line(&mut pixmap, *a, *b, *color, *width, *opacity, *head);
            }
            Shape::Path { points, clip, color, width, drawn, opacity } => {
                draw_path(&mut pixmap, points, clip, *color, *width, *drawn, *opacity);
            }
            Shape::Text { text, face, align, max_w, x, y, size, color, opacity } => {
                let style = Style { size: *size, face: *face, color: *color, opacity: *opacity };
                fonts.draw(&mut pixmap, text, style, *x, *y, *align, *max_w);
            }
            Shape::Image { image, x, y, w, h, opacity, .. } => draw_image(&mut pixmap, image, *x, *y, *w, *h, *opacity),
        }
    }
    pixmap
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fill(key: &str, x: f32, opacity: f32) -> Cmd {
        Cmd { key: key.into(), shape: Shape::Fill { rect: Rect { x, y: 0.0, w: 10.0, h: 10.0 }, radius: 0.0, color: [0, 0, 0], opacity } }
    }

    fn text(key: &str, text: &str) -> Cmd {
        Cmd {
            key: key.into(),
            shape: Shape::Text { text: text.into(), face: Face::Sans, align: HAlign::Center, max_w: None, x: 0.0, y: 0.0, size: 10.0, color: [0, 0, 0], opacity: 1.0 },
        }
    }

    fn x_and_opacity(c: &Cmd) -> (f32, f32) {
        let n = c.shape.numbers();
        (n[0], *n.last().unwrap())
    }

    #[test]
    fn numbers_move_with_their_own_action() {
        // Action 1 moves `a`; action 2 moves `b`. Each follows its own progress.
        let lists = vec![
            vec![fill("a", 0.0, 1.0), fill("b", 0.0, 1.0)],
            vec![fill("a", 100.0, 1.0), fill("b", 0.0, 1.0)],
            vec![fill("a", 100.0, 1.0), fill("b", 100.0, 1.0)],
        ];
        let out = blend(&lists, &[0.5, 0.25]);
        assert_eq!(x_and_opacity(&out[0]), (50.0, 1.0));
        assert_eq!(x_and_opacity(&out[1]), (25.0, 1.0));
    }

    #[test]
    fn appearing_and_disappearing_fade() {
        let lists = vec![vec![fill("old", 0.0, 1.0)], vec![fill("new", 5.0, 1.0)]];
        // What goes leaves in the first half; what comes arrives in the second.
        let at = |p: f32, k: &str| blend(&lists, &[p]).iter().find(|c| c.key == k).map(x_and_opacity);
        assert_eq!(at(0.25, "old"), Some((0.0, 0.5)));
        assert_eq!(at(0.25, "new"), None);
        assert_eq!(at(0.75, "old"), None);
        assert_eq!(at(0.75, "new"), Some((5.0, 0.5)));
    }

    #[test]
    fn changed_text_fades_out_then_in() {
        let lists = vec![vec![text("t", "before")], vec![text("t", "after")]];
        let shown = |p: f32| -> Vec<(String, f32)> {
            blend(&lists, &[p])
                .iter()
                .map(|c| match &c.shape {
                    Shape::Text { text, opacity, .. } => (text.clone(), *opacity),
                    _ => unreachable!(),
                })
                .collect()
        };
        assert_eq!(shown(0.25), [("before".to_string(), 0.5)]);
        assert!(shown(0.5).is_empty(), "the two are never on screen together");
        assert_eq!(shown(0.75), [("after".to_string(), 0.5)]);
    }

    #[test]
    fn segments_are_clipped_to_a_box() {
        let r = Rect { x: 0.0, y: 0.0, w: 10.0, h: 10.0 };
        assert_eq!(clip_segment((2.0, 2.0), (8.0, 8.0), &r), Some(((2.0, 2.0), (8.0, 8.0))));
        assert_eq!(clip_segment((-5.0, 5.0), (15.0, 5.0), &r), Some(((0.0, 5.0), (10.0, 5.0))));
        assert_eq!(clip_segment((5.0, 5.0), (5.0, 25.0), &r), Some(((5.0, 5.0), (5.0, 10.0))));
        assert_eq!(clip_segment((-5.0, -5.0), (-1.0, 20.0), &r), None);
    }

    #[test]
    fn ends_are_exact() {
        let lists = vec![vec![fill("a", 0.0, 1.0)], vec![fill("a", 100.0, 1.0)]];
        assert_eq!(x_and_opacity(&blend(&lists, &[0.0])[0]).0, 0.0);
        assert_eq!(x_and_opacity(&blend(&lists, &[1.0])[0]).0, 100.0);
    }
}
