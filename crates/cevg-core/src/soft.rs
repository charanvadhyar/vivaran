//! The software backend: a small rasteriser with a depth buffer.
//!
//! It draws at twice the viewport size and averages down, which gives it
//! edges nearly as smooth as the 2D drawing around it. Opaque solids go
//! first with depth writes; translucent ones follow, far to near, tested
//! against the depth buffer but not written to it. Meshes are flat shaded
//! from one light fixed to the camera's upper left, so a surface reads the
//! same from every angle.
//!
//! Everything is plain f32 arithmetic in a fixed order, so the same scene
//! gives the same pixels on every machine. That is what the frame tests
//! rely on.

use crate::render::Rgb;
use crate::space3d::{add, cross, dot, length, normalize, scale, sub, Content, Projection, Scene, Solid, SpaceBackend, Vec3};
use tiny_skia::Pixmap;

const SS: usize = 2;

pub struct SoftBackend;

/// Colour with coverage, kept linear in 0..1 while drawing.
#[derive(Clone, Copy)]
struct Px {
    r: f32,
    g: f32,
    b: f32,
    a: f32,
}

struct Target {
    w: usize,
    h: usize,
    color: Vec<Px>,
    depth: Vec<f32>,
}

impl Target {
    fn new(w: usize, h: usize) -> Target {
        Target { w, h, color: vec![Px { r: 0.0, g: 0.0, b: 0.0, a: 0.0 }; w * h], depth: vec![f32::INFINITY; w * h] }
    }

    /// Source-over with a depth test. `write` says whether the depth is kept.
    #[inline]
    fn put(&mut self, x: usize, y: usize, z: f32, rgb: [f32; 3], alpha: f32, write: bool) {
        let i = y * self.w + x;
        if z > self.depth[i] || alpha <= 0.0 {
            return;
        }
        let d = &mut self.color[i];
        let a = alpha.min(1.0);
        d.r = rgb[0] * a + d.r * (1.0 - a);
        d.g = rgb[1] * a + d.g * (1.0 - a);
        d.b = rgb[2] * a + d.b * (1.0 - a);
        d.a = a + d.a * (1.0 - a);
        if write {
            self.depth[i] = z;
        }
    }

    /// Fill a screen-space triangle with per-vertex depth.
    fn triangle(&mut self, v: [((f32, f32), f32); 3], rgb: [f32; 3], alpha: f32, write: bool) {
        let [(a, za), (b, zb), (c, zc)] = v;
        let area = (b.0 - a.0) * (c.1 - a.1) - (b.1 - a.1) * (c.0 - a.0);
        if area.abs() < 1e-6 {
            return;
        }
        let x0 = a.0.min(b.0).min(c.0).floor().max(0.0) as usize;
        let x1 = (a.0.max(b.0).max(c.0).ceil().min(self.w as f32 - 1.0)).max(0.0) as usize;
        let y0 = a.1.min(b.1).min(c.1).floor().max(0.0) as usize;
        let y1 = (a.1.max(b.1).max(c.1).ceil().min(self.h as f32 - 1.0)).max(0.0) as usize;
        if x0 > x1 || y0 > y1 {
            return;
        }
        let inv = 1.0 / area;
        for y in y0..=y1 {
            let py = y as f32 + 0.5;
            for x in x0..=x1 {
                let px = x as f32 + 0.5;
                // Barycentric weights from the edge functions.
                let wa = ((b.0 - px) * (c.1 - py) - (b.1 - py) * (c.0 - px)) * inv;
                let wb = ((c.0 - px) * (a.1 - py) - (c.1 - py) * (a.0 - px)) * inv;
                let wc = 1.0 - wa - wb;
                if wa < 0.0 || wb < 0.0 || wc < 0.0 {
                    continue;
                }
                let z = wa * za + wb * zb + wc * zc;
                self.put(x, y, z, rgb, alpha, write);
            }
        }
    }

    fn disc(&mut self, centre: (f32, f32), z: f32, radius: f32, rgb: [f32; 3], alpha: f32, write: bool) {
        let x0 = (centre.0 - radius).floor().max(0.0) as usize;
        let x1 = ((centre.0 + radius).ceil().min(self.w as f32 - 1.0)).max(0.0) as usize;
        let y0 = (centre.1 - radius).floor().max(0.0) as usize;
        let y1 = ((centre.1 + radius).ceil().min(self.h as f32 - 1.0)).max(0.0) as usize;
        if x0 > x1 || y0 > y1 {
            return;
        }
        for y in y0..=y1 {
            for x in x0..=x1 {
                let (dx, dy) = (x as f32 + 0.5 - centre.0, y as f32 + 0.5 - centre.1);
                let d = (dx * dx + dy * dy).sqrt();
                // One pixel of soft edge.
                let cover = (radius - d + 0.5).clamp(0.0, 1.0);
                if cover > 0.0 {
                    self.put(x, y, z, rgb, alpha * cover, write);
                }
            }
        }
    }

    /// A segment as a quad of `width` pixels, with depth along it.
    fn segment(&mut self, a: ((f32, f32), f32), b: ((f32, f32), f32), width: f32, rgb: [f32; 3], alpha: f32, write: bool) {
        let ((ax, ay), za) = a;
        let ((bx, by), zb) = b;
        let (dx, dy) = (bx - ax, by - ay);
        let len = (dx * dx + dy * dy).sqrt();
        if len < 0.01 {
            return;
        }
        let (nx, ny) = (-dy / len * width / 2.0, dx / len * width / 2.0);
        // Extend the ends by half the width, so joined runs have no gaps.
        let (ex, ey) = (dx / len * width / 2.0, dy / len * width / 2.0);
        let p0 = ((ax - ex + nx, ay - ey + ny), za);
        let p1 = ((ax - ex - nx, ay - ey - ny), za);
        let p2 = ((bx + ex - nx, by + ey - ny), zb);
        let p3 = ((bx + ex + nx, by + ey + ny), zb);
        self.triangle([p0, p1, p2], rgb, alpha, write);
        self.triangle([p0, p2, p3], rgb, alpha, write);
    }

    fn head(&mut self, from: (f32, f32), tip: ((f32, f32), f32), width: f32, rgb: [f32; 3], alpha: f32, write: bool) {
        let ((tx, ty), z) = tip;
        let (dx, dy) = (tx - from.0, ty - from.1);
        let len = (dx * dx + dy * dy).sqrt();
        if len < 0.01 {
            return;
        }
        let (ux, uy) = (dx / len, dy / len);
        let size = (width * 4.0).min(len * 0.6);
        let base = (tx - ux * size, ty - uy * size);
        let half = size * 0.6;
        let l = ((base.0 - uy * half, base.1 + ux * half), z);
        let r = ((base.0 + uy * half, base.1 - ux * half), z);
        self.triangle([((tx, ty), z), l, r], rgb, alpha, write);
    }
}

fn lin(c: Rgb) -> [f32; 3] {
    [c[0] as f32 / 255.0, c[1] as f32 / 255.0, c[2] as f32 / 255.0]
}

/// Clip a segment in eye space against the near plane; `None` when it is
/// entirely behind the camera.
fn clip_near(a: Vec3, b: Vec3, near: f32) -> Option<(Vec3, Vec3)> {
    let (da, db) = (-a[2] - near, -b[2] - near);
    match (da >= 0.0, db >= 0.0) {
        (true, true) => Some((a, b)),
        (false, false) => None,
        (true, false) => {
            let t = da / (da - db);
            Some((a, add(a, scale(sub(b, a), t))))
        }
        (false, true) => {
            let t = da / (da - db);
            Some((add(a, scale(sub(b, a), t)), b))
        }
    }
}

/// Lambert shading from a light fixed to the camera: above, to the left,
/// and a little in front. Two-sided, so the underside of a surface reads
/// the same as the top.
fn shade(normal_eye: Vec3) -> f32 {
    let light = normalize([-0.45, 0.6, 0.66]);
    0.34 + 0.66 * dot(normalize(normal_eye), light).abs()
}

/// Lines and points are pulled a little toward the camera, so a path drawn
/// on a surface, or a point sitting on a plane, is not swallowed by it.
const LIFT: f32 = 0.012;

impl SpaceBackend for SoftBackend {
    fn name(&self) -> &'static str {
        "soft"
    }

    fn render(&self, scene: &Scene) -> Pixmap {
        let (w, h) = (scene.width as usize, scene.height as usize);
        let (sw, sh) = (w * SS, h * SS);
        let proj = Projection::new(&scene.camera, sw as f32, sh as f32);
        let mut target = Target::new(sw, sh);
        let s = SS as f32;

        // Opaque first (near or far, the depth buffer sorts it out), then
        // translucent from far to near.
        let depth_of = |solid: &Solid| -> f32 {
            let n = solid.vertices.len().max(1) as f32;
            let sum: f32 = solid.vertices.iter().map(|v| -proj.to_eye(*v)[2]).sum();
            sum / n
        };
        let mut order: Vec<(usize, bool, f32)> =
            scene.solids.iter().enumerate().map(|(i, sd)| (i, sd.opacity >= 0.995, depth_of(sd))).collect();
        order.sort_by(|a, b| b.1.cmp(&a.1).then(b.2.partial_cmp(&a.2).unwrap_or(std::cmp::Ordering::Equal)));

        for (i, opaque, _) in order {
            let solid = &scene.solids[i];
            if solid.opacity <= 0.002 {
                continue;
            }
            let rgb = lin(solid.color);
            let eye: Vec<Vec3> = solid.vertices.iter().map(|v| proj.to_eye(*v)).collect();
            match &*solid.content {
                Content::Points { radius } => {
                    for e in &eye {
                        if -e[2] < proj.near {
                            continue;
                        }
                        let (x, y) = proj.screen(*e);
                        let z = -e[2] * (1.0 - LIFT);
                        // A ring in the background colour sets the dot off
                        // from whatever is behind it.
                        target.disc((x, y), z, (radius + 1.5) * s, lin(scene.background), solid.opacity, opaque);
                        target.disc((x, y), z - 0.002, radius * s, rgb, solid.opacity, opaque);
                    }
                }
                Content::Segments { width, head } => {
                    let runs = eye.len().saturating_sub(1);
                    if runs == 0 {
                        continue;
                    }
                    // `drawn` cuts the run short, the way a plot traces.
                    let total: f32 = eye.windows(2).map(|p| length(sub(p[1], p[0]))).sum();
                    let mut left = total * solid.drawn.clamp(0.0, 1.0);
                    let mut last_screen: Option<((f32, f32), (f32, f32))> = None;
                    for pair in eye.windows(2) {
                        if left <= 0.0 {
                            break;
                        }
                        let step = length(sub(pair[1], pair[0]));
                        let end = if step <= left { pair[1] } else { add(pair[0], scale(sub(pair[1], pair[0]), left / step)) };
                        left -= step;
                        let Some((a, b)) = clip_near(pair[0], end, proj.near) else { continue };
                        let (pa, pb) = (proj.screen(a), proj.screen(b));
                        target.segment((pa, -a[2] * (1.0 - LIFT)), (pb, -b[2] * (1.0 - LIFT)), width * s, rgb, solid.opacity, opaque);
                        last_screen = Some((pa, pb));
                    }
                    if *head && solid.drawn >= 0.999 {
                        if let (Some((from, to)), Some(e)) = (last_screen, eye.last()) {
                            target.head(from, (to, -e[2] * (1.0 - LIFT)), width * s, rgb, solid.opacity, opaque);
                        }
                    }
                }
                Content::Mesh { triangles, lit } => {
                    for tri in triangles {
                        let (a, b, c) = (eye[tri[0] as usize], eye[tri[1] as usize], eye[tri[2] as usize]);
                        if -a[2] < proj.near || -b[2] < proj.near || -c[2] < proj.near {
                            continue;
                        }
                        let tone = if *lit { shade(cross(sub(b, a), sub(c, a))) } else { 1.0 };
                        let col = [rgb[0] * tone, rgb[1] * tone, rgb[2] * tone];
                        let v = [(proj.screen(a), -a[2]), (proj.screen(b), -b[2]), (proj.screen(c), -c[2])];
                        target.triangle(v, col, solid.opacity, opaque);
                    }
                }
            }
        }

        // Average the supersamples down into premultiplied bytes.
        let mut out = Pixmap::new(scene.width.max(1), scene.height.max(1)).expect("viewport size");
        let data = out.data_mut();
        for y in 0..h {
            for x in 0..w {
                let (mut r, mut g, mut b, mut a) = (0.0, 0.0, 0.0, 0.0);
                for sy in 0..SS {
                    for sx in 0..SS {
                        let p = target.color[(y * SS + sy) * sw + x * SS + sx];
                        r += p.r * p.a;
                        g += p.g * p.a;
                        b += p.b * p.a;
                        a += p.a;
                    }
                }
                let n = (SS * SS) as f32;
                let i = (y * w + x) * 4;
                data[i] = (r / n * 255.0).round().clamp(0.0, 255.0) as u8;
                data[i + 1] = (g / n * 255.0).round().clamp(0.0, 255.0) as u8;
                data[i + 2] = (b / n * 255.0).round().clamp(0.0, 255.0) as u8;
                data[i + 3] = (a / n * 255.0).round().clamp(0.0, 255.0) as u8;
            }
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::space3d::Camera;
    use std::sync::Arc;

    fn pixel(p: &Pixmap, x: u32, y: u32) -> [u8; 4] {
        let i = ((y * p.width() + x) * 4) as usize;
        p.data()[i..i + 4].try_into().unwrap()
    }

    #[test]
    fn a_triangle_covers_the_centre_and_nothing_else_is_painted() {
        let solid = Solid {
            content: Arc::new(Content::Mesh { triangles: vec![[0, 1, 2]], lit: false }),
            vertices: vec![[-0.5, -0.5, 0.0], [0.5, -0.5, 0.0], [0.0, 0.5, 0.0]],
            color: [255, 0, 0],
            drawn: 1.0,
            opacity: 1.0,
        };
        let camera = Camera { azimuth: 0.0, elevation: 89.0, distance: 3.0, ..Camera::default() };
        let scene = Scene { camera, width: 120, height: 100, background: [0, 0, 0], solids: &[solid] };
        let image = SoftBackend.render(&scene);
        let centre = pixel(&image, 60, 50);
        assert_eq!(centre, [255, 0, 0, 255], "the centre is covered: {centre:?}");
        assert_eq!(pixel(&image, 2, 2), [0, 0, 0, 0], "the corner is transparent");
    }

    #[test]
    fn nearer_solids_hide_farther_ones() {
        let mesh = |z: f32, color: Rgb| Solid {
            content: Arc::new(Content::Mesh { triangles: vec![[0, 1, 2], [0, 2, 3]], lit: false }),
            vertices: vec![[-1.0, -1.0, z], [1.0, -1.0, z], [1.0, 1.0, z], [-1.0, 1.0, z]],
            color,
            drawn: 1.0,
            opacity: 1.0,
        };
        let camera = Camera { azimuth: 0.0, elevation: 89.0, distance: 4.0, ..Camera::default() };
        // The far (green) square is listed first; the near (red) one must win.
        let solids = [mesh(-0.5, [0, 255, 0]), mesh(0.5, [255, 0, 0])];
        let scene = Scene { camera, width: 60, height: 60, background: [0, 0, 0], solids: &solids };
        assert_eq!(pixel(&SoftBackend.render(&scene), 30, 30), [255, 0, 0, 255]);
        let solids = [mesh(0.5, [255, 0, 0]), mesh(-0.5, [0, 255, 0])];
        let scene = Scene { camera, width: 60, height: 60, background: [0, 0, 0], solids: &solids };
        assert_eq!(pixel(&SoftBackend.render(&scene), 30, 30), [255, 0, 0, 255]);
    }

    #[test]
    fn the_same_scene_gives_the_same_pixels() {
        let solid = Solid {
            content: Arc::new(Content::Segments { width: 3.0, head: true }),
            vertices: vec![[0.0, 0.0, 0.0], [1.0, 0.5, 0.3]],
            color: [20, 200, 90],
            drawn: 1.0,
            opacity: 0.8,
        };
        let scene = Scene { camera: Camera::default(), width: 200, height: 150, background: [0, 0, 0], solids: &[solid] };
        let a = SoftBackend.render(&scene);
        let b = SoftBackend.render(&scene);
        assert_eq!(a.data(), b.data());
        assert!(a.data().chunks(4).any(|p| p[3] > 0), "the arrow was drawn");
    }
}
