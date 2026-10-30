//! Finishing: callouts, captions and the watermark, drawn over the frames a
//! renderer made, then encoded to MP4.
//!
//! This step is the same whichever renderer made the frames, which is why
//! text never goes into the 3D scene: it stays sharp, is never hidden by a
//! part, and looks identical from Cycles and from our own path tracer. The
//! callout anchors come from the same timeline the renderer used, projected
//! with the same camera, so a line lands exactly on its part.

use crate::mesh::V3;
use crate::rig::{apply_chain, world_transforms, Rig};
use crate::scene::Scene;
use crate::timeline::Timeline;
use std::collections::HashMap;
use cevg_core::space3d::Projection;
use cevg_core::text::{Face, Fonts, HAlign, Style};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use tiny_skia::{Color, LineCap, Paint, PathBuilder, Pixmap, Rect, Stroke, Transform};

#[derive(Debug, Clone, Default)]
pub struct Options {
    /// Show the narration in this language under the picture.
    pub captions: Option<String>,
    /// A short line in the top right corner.
    pub watermark: Option<String>,
    /// Narration lengths, as given to `build`.
    pub speech: Option<Vec<f32>>,
}

const INK: [u8; 3] = [238, 240, 244];
const AMBER: [u8; 3] = [245, 184, 61];

/// The file a renderer writes for frame `f` (frames count from 1).
pub fn frame_path(dir: &Path, f: usize) -> PathBuf {
    dir.join(format!("frame_{f:04}.png"))
}

fn paint(color: [u8; 3], opacity: f32) -> Paint<'static> {
    let mut p = Paint::default();
    p.set_color_rgba8(color[0], color[1], color[2], (opacity.clamp(0.0, 1.0) * 255.0) as u8);
    p.anti_alias = true;
    p
}

fn line(pixmap: &mut Pixmap, pts: &[(f32, f32)], color: [u8; 3], width: f32, opacity: f32) {
    let mut pb = PathBuilder::new();
    pb.move_to(pts[0].0, pts[0].1);
    for p in &pts[1..] {
        pb.line_to(p.0, p.1);
    }
    if let Some(path) = pb.finish() {
        let stroke = Stroke { width, line_cap: LineCap::Round, ..Stroke::default() };
        pixmap.stroke_path(&path, &paint(color, opacity), &stroke, Transform::identity(), None);
    }
}

fn dot(pixmap: &mut Pixmap, at: (f32, f32), r: f32, color: [u8; 3], opacity: f32) {
    if let Some(path) = PathBuilder::from_circle(at.0, at.1, r) {
        pixmap.fill_path(&path, &paint(color, opacity), tiny_skia::FillRule::Winding, Transform::identity(), None);
    }
}

/// Where each visible callout is pinned: a point on one of the part's
/// meshes, in that mesh node's own coordinates. It is chosen when the
/// callout appears (the point of the part nearest the camera, so it is on
/// the surface and in view) and then followed as the part moves.
#[derive(Default)]
pub struct Anchors {
    pinned: HashMap<usize, (usize, V3)>,
}

impl Anchors {
    fn pick(&mut self, rig: &Rig, world: &[Vec<crate::rig::Trs>], eye: V3, node: usize) -> Option<V3> {
        if let Some((mesh_node, local)) = self.pinned.get(&node) {
            return Some(apply_chain(&world[*mesh_node], *local));
        }
        let mut best: Option<(f32, usize, V3, V3)> = None;
        for i in rig.subtree(node) {
            let Some(m) = rig.nodes[i].mesh else { continue };
            let positions = &rig.meshes[m].1.positions;
            let stride = (positions.len() / 1500).max(1);
            for p in positions.iter().step_by(stride) {
                let w = apply_chain(&world[i], *p);
                let d = crate::mesh::length(crate::mesh::sub(w, eye));
                if best.is_none_or(|b| d < b.0) {
                    best = Some((d, i, *p, w));
                }
            }
        }
        let (_, i, local, w) = best?;
        self.pinned.insert(node, (i, local));
        Some(w)
    }

    fn release(&mut self, node: usize) {
        self.pinned.remove(&node);
    }
}

/// Draw everything that goes on top of the 3D picture for one frame.
#[allow(clippy::too_many_arguments)]
pub fn overlay(pixmap: &mut Pixmap, scene: &Scene, rig: &Rig, tl: &Timeline, frame: usize, opts: &Options, fonts: &mut Fonts, anchors: &mut Anchors) {
    let (w, h) = (pixmap.width() as f32, pixmap.height() as f32);
    let u = h / 1080.0;
    let time = frame as f32 / tl.fps as f32;
    let pose = tl.pose(rig, time);
    let proj = Projection::new(&pose.camera, w, h);
    let world = world_transforms(&rig.nodes, &pose.local);
    let eye = pose.camera.eye();

    // Callouts: anchor dot on the part, an elbow, a short level run, the name.
    struct Callout {
        anchor: (f32, f32),
        y: f32,
        left: bool,
        text: String,
        opacity: f32,
    }
    let mut callouts: Vec<Callout> = vec![];
    for (i, (opacity, text)) in pose.labels.iter().enumerate() {
        if *opacity <= 0.01 || text.is_empty() {
            anchors.release(i);
            continue;
        }
        let Some(point) = anchors.pick(rig, &world, eye, i) else { continue };
        let Some(((x, y), _)) = proj.project(point) else { continue };
        let left = x < w / 2.0;
        callouts.push(Callout { anchor: (x, y), y: y - 70.0 * u, left, text: text.clone(), opacity: *opacity * pose.opacity[i].max(0.3) });
    }
    // Keep callouts on one side from sitting on each other.
    for side in [true, false] {
        let mut ids: Vec<usize> = (0..callouts.len()).filter(|k| callouts[*k].left == side).collect();
        ids.sort_by(|a, b| callouts[*a].y.partial_cmp(&callouts[*b].y).unwrap_or(std::cmp::Ordering::Equal));
        for pair in 1..ids.len() {
            let (prev, here) = (ids[pair - 1], ids[pair]);
            let min = callouts[prev].y + 52.0 * u;
            if callouts[here].y < min {
                callouts[here].y = min;
            }
        }
    }
    for c in &callouts {
        let dir = if c.left { -1.0 } else { 1.0 };
        let elbow = (c.anchor.0 + dir * 70.0 * u, c.y.clamp(60.0 * u, h - 160.0 * u));
        let end = (elbow.0 + dir * 60.0 * u, elbow.1);
        line(pixmap, &[c.anchor, elbow, end], INK, 2.2 * u, 0.85 * c.opacity);
        dot(pixmap, c.anchor, 6.0 * u, AMBER, c.opacity);
        let style = Style { size: 32.0 * u, face: Face::SansBold, color: INK, opacity: c.opacity };
        let tx = end.0 + dir * 12.0 * u;
        fonts.draw(pixmap, &c.text, style, tx, end.1, if c.left { HAlign::Right } else { HAlign::Left }, None);
    }

    // Captions: the current step's narration in a band at the bottom.
    if let Some(lang) = &opts.captions {
        if let Some(step) = tl.steps.iter().rev().find(|s| s.start <= time + 1e-3) {
            let text = step.say.get(lang).or_else(|| step.say.get("en")).cloned().unwrap_or_default();
            if !text.is_empty() {
                let band = Rect::from_xywh(0.0, h - 130.0 * u, w, 130.0 * u).expect("band");
                pixmap.fill_rect(band, &paint([8, 10, 14], 0.72), Transform::identity(), None);
                let style = Style { size: 34.0 * u, face: Face::Sans, color: INK, opacity: 1.0 };
                fonts.draw(pixmap, &text, style, w / 2.0, h - 65.0 * u, HAlign::Center, Some(w - 240.0 * u));
            }
        }
    }

    if let Some(mark) = &opts.watermark {
        let style = Style { size: 24.0 * u, face: Face::SansBold, color: INK, opacity: 0.55 };
        fonts.draw(pixmap, mark, style, w - 40.0 * u, 44.0 * u, HAlign::Right, None);
    }
    let _ = scene;
}

/// Overlay one rendered frame (any size: previews are often half size) and
/// save it as a PNG. `frame` counts from 1, as the renderer's files do.
pub fn still(json: &str, frame: usize, image: &Path, out: &Path, opts: &Options) -> Result<(), String> {
    let scene = crate::parse(json).map_err(|p| format!("{}: {}", p.path, p.message))?;
    let rig = Rig::build(&scene);
    let tl = Timeline::build(&scene, &rig, opts.speech.as_deref())?;
    if frame == 0 || frame > tl.frames {
        return Err(format!("frame {frame} is outside 1 to {}", tl.frames));
    }
    let mut pixmap = Pixmap::load_png(image).map_err(|e| format!("{}: {e}", image.display()))?;
    let mut fonts = Fonts::new();
    let mut anchors = Anchors::default();
    // Pin callouts where they were when they appeared, as the video does.
    let first = (0..frame).rev().take_while(|f| tl.pose(&rig, *f as f32 / tl.fps as f32).labels.iter().any(|(o, _)| *o > 0.01)).last();
    if let Some(start) = first {
        let mut scratch = Pixmap::new(pixmap.width(), pixmap.height()).expect("size");
        overlay(&mut scratch, &scene, &rig, &tl, start, opts, &mut fonts, &mut anchors);
    }
    overlay(&mut pixmap, &scene, &rig, &tl, frame - 1, opts, &mut fonts, &mut anchors);
    pixmap.save_png(out).map_err(|e| format!("{}: {e}", out.display()))
}

/// Overlay every frame in `frames` and encode an MP4 at `out`.
pub fn finish(json: &str, frames: &Path, out: &Path, opts: &Options, mut progress: impl FnMut(usize, usize)) -> Result<(), String> {
    let scene = crate::parse(json).map_err(|p| format!("{}: {}", p.path, p.message))?;
    let rig = Rig::build(&scene);
    let tl = Timeline::build(&scene, &rig, opts.speech.as_deref())?;
    let (w, h) = (scene.canvas.width, scene.canvas.height);
    let total = tl.frames;
    if !frame_path(frames, 1).is_file() {
        return Err(format!("no frames found: expected {}", frame_path(frames, 1).display()));
    }
    let mut ffmpeg = Command::new("ffmpeg")
        .args(["-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba"])
        .args(["-s", &format!("{w}x{h}"), "-r", &tl.fps.to_string(), "-i", "-", "-an"])
        .args(["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
        .arg(out)
        .stdin(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("could not start ffmpeg ({e})"))?;
    let mut pipe = ffmpeg.stdin.take().expect("stdin");
    let mut fonts = Fonts::new();
    let mut anchors = Anchors::default();
    let mut last: Option<Pixmap> = None;
    for f in 0..total {
        let path = frame_path(frames, f + 1);
        // A missing frame repeats the one before, so a partial render still
        // makes a watchable preview.
        let mut pixmap = match Pixmap::load_png(&path) {
            Ok(p) => p,
            Err(_) => last.clone().ok_or_else(|| format!("{} is missing", path.display()))?,
        };
        if (pixmap.width(), pixmap.height()) != (w, h) {
            return Err(format!("{} is {}x{}, but the scene is {w}x{h}", path.display(), pixmap.width(), pixmap.height()));
        }
        last = Some(pixmap.clone());
        // Make it opaque over the background before drawing on it.
        let mut canvas = Pixmap::new(w, h).expect("size");
        let bg = rig.background;
        let srgb = |c: f32| ((if c <= 0.0031308 { 12.92 * c } else { 1.055 * c.powf(1.0 / 2.4) - 0.055 }) * 255.0).round().clamp(0.0, 255.0) as u8;
        canvas.fill(Color::from_rgba8(srgb(bg[0]), srgb(bg[1]), srgb(bg[2]), 255));
        canvas.draw_pixmap(0, 0, pixmap.as_ref(), &tiny_skia::PixmapPaint::default(), Transform::identity(), None);
        pixmap = canvas;
        overlay(&mut pixmap, &scene, &rig, &tl, f, opts, &mut fonts, &mut anchors);
        if pipe.write_all(pixmap.data()).is_err() {
            break;
        }
        if f % 30 == 0 || f + 1 == total {
            progress(f + 1, total);
        }
    }
    drop(pipe);
    let output = ffmpeg.wait_with_output().map_err(|e| format!("ffmpeg: {e}"))?;
    if !output.status.success() {
        return Err(format!("ffmpeg failed: {}", String::from_utf8_lossy(&output.stderr).trim()));
    }
    Ok(())
}
