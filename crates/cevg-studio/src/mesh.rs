//! Parametric modelling: the shapes a studio scene is built from.
//!
//! Everything is generated as a triangle mesh with normals, in metres, `z`
//! up. Mechanical objects are mostly made of a few operations, and those are
//! what is here:
//!
//! * `revolve`  a profile spun about the z axis, optionally only part way
//!   round, which is how a cutaway is made (the cut faces are capped);
//! * `extrude`  an outline pushed along z, with capped ends;
//! * `sweep`    a circle or rectangle carried along a path (coils, pipes,
//!   wires), with path generators for helices, circles, arcs and the
//!   D-shaped loop of a tokamak's field coil;
//! * the primitives built from those: box, cylinder, tube, cone, sphere,
//!   torus, gear.
//!
//! Corners can be rounded (`round`), which gives the small bevels that make
//! machined parts catch the light. Normals are smooth across shallow angles
//! and split at sharp ones, so a cylinder is round and its rim is crisp.

use serde::Deserialize;

pub type V3 = [f32; 3];
pub type V2 = [f32; 2];

/// Normals stay shared across angles shallower than this (degrees).
const CREASE: f32 = 35.0;

#[derive(Debug, Clone, Default)]
pub struct Mesh {
    pub positions: Vec<V3>,
    pub normals: Vec<V3>,
    pub indices: Vec<u32>,
}

// ----------------------------------------------------------- vector math

pub fn sub(a: V3, b: V3) -> V3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn add(a: V3, b: V3) -> V3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
pub fn scale(a: V3, s: f32) -> V3 {
    [a[0] * s, a[1] * s, a[2] * s]
}
pub fn dot(a: V3, b: V3) -> f32 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross(a: V3, b: V3) -> V3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
pub fn length(a: V3) -> f32 {
    dot(a, a).sqrt()
}
pub fn normalize(a: V3) -> V3 {
    let l = length(a);
    if l > 1e-12 { scale(a, 1.0 / l) } else { [0.0, 0.0, 1.0] }
}

impl Mesh {
    pub fn vertex(&mut self, p: V3, n: V3) -> u32 {
        self.positions.push(p);
        self.normals.push(normalize(n));
        (self.positions.len() - 1) as u32
    }

    /// A triangle, wound so that its face agrees with its vertex normals
    /// (counter-clockwise seen from the side the normals point to).
    pub fn tri(&mut self, a: u32, b: u32, c: u32) {
        let (pa, pb, pc) = (self.positions[a as usize], self.positions[b as usize], self.positions[c as usize]);
        let face = cross(sub(pb, pa), sub(pc, pa));
        if length(face) < 1e-14 {
            return;
        }
        let n = add(add(self.normals[a as usize], self.normals[b as usize]), self.normals[c as usize]);
        if dot(face, n) >= 0.0 {
            self.indices.extend([a, b, c]);
        } else {
            self.indices.extend([a, c, b]);
        }
    }

    pub fn quad(&mut self, a: u32, b: u32, c: u32, d: u32) {
        self.tri(a, b, c);
        self.tri(a, c, d);
    }

    pub fn append(&mut self, other: &Mesh) {
        let base = self.positions.len() as u32;
        self.positions.extend_from_slice(&other.positions);
        self.normals.extend_from_slice(&other.normals);
        self.indices.extend(other.indices.iter().map(|i| i + base));
    }

    pub fn triangles(&self) -> usize {
        self.indices.len() / 3
    }

    /// Axis-aligned bounds, (min, max).
    pub fn bounds(&self) -> (V3, V3) {
        let mut lo = [f32::INFINITY; 3];
        let mut hi = [f32::NEG_INFINITY; 3];
        for p in &self.positions {
            for k in 0..3 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
        if self.positions.is_empty() {
            return ([0.0; 3], [0.0; 3]);
        }
        (lo, hi)
    }
}

// ------------------------------------------------------------- 2D helpers

fn area2(poly: &[V2]) -> f32 {
    let mut a = 0.0;
    for i in 0..poly.len() {
        let (p, q) = (poly[i], poly[(i + 1) % poly.len()]);
        a += p[0] * q[1] - q[0] * p[1];
    }
    a / 2.0
}

/// Triangulate a simple polygon (convex or not) by ear clipping. Returns
/// index triples into `poly`.
pub fn triangulate(poly: &[V2]) -> Vec<[usize; 3]> {
    let n = poly.len();
    if n < 3 {
        return vec![];
    }
    let ccw = area2(poly) > 0.0;
    let mut idx: Vec<usize> = (0..n).collect();
    if !ccw {
        idx.reverse();
    }
    let cross2 = |a: V2, b: V2, c: V2| (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
    let inside = |p: V2, a: V2, b: V2, c: V2| cross2(a, b, p) >= 0.0 && cross2(b, c, p) >= 0.0 && cross2(c, a, p) >= 0.0;
    let mut out = vec![];
    let mut guard = 0;
    while idx.len() > 3 && guard < 10 * n * n {
        guard += 1;
        let m = idx.len();
        let mut clipped = false;
        for i in 0..m {
            let (ia, ib, ic) = (idx[(i + m - 1) % m], idx[i], idx[(i + 1) % m]);
            let (a, b, c) = (poly[ia], poly[ib], poly[ic]);
            if cross2(a, b, c) <= 1e-12 {
                continue; // reflex or flat: not an ear
            }
            let blocked = idx.iter().any(|&j| j != ia && j != ib && j != ic && inside(poly[j], a, b, c));
            if blocked {
                continue;
            }
            out.push([ia, ib, ic]);
            idx.remove(i);
            clipped = true;
            break;
        }
        if !clipped {
            // Degenerate input: fall back to a fan so something is drawn.
            for k in 1..idx.len() - 1 {
                out.push([idx[0], idx[k], idx[k + 1]]);
            }
            return out;
        }
    }
    if idx.len() == 3 {
        out.push([idx[0], idx[1], idx[2]]);
    }
    out
}

/// Round the corners of a polyline by `radius`, with `steps` segments per
/// corner. `closed` treats the last point as joined to the first.
pub fn round_corners(poly: &[V2], radius: f32, closed: bool) -> Vec<V2> {
    if radius <= 0.0 || poly.len() < 3 {
        return poly.to_vec();
    }
    let steps = 6;
    let n = poly.len();
    let mut out = vec![];
    for i in 0..n {
        let first_or_last = !closed && (i == 0 || i == n - 1);
        if first_or_last {
            out.push(poly[i]);
            continue;
        }
        let (prev, here, next) = (poly[(i + n - 1) % n], poly[i], poly[(i + 1) % n]);
        let d1 = [prev[0] - here[0], prev[1] - here[1]];
        let d2 = [next[0] - here[0], next[1] - here[1]];
        let (l1, l2) = ((d1[0] * d1[0] + d1[1] * d1[1]).sqrt(), (d2[0] * d2[0] + d2[1] * d2[1]).sqrt());
        if l1 < 1e-9 || l2 < 1e-9 {
            out.push(here);
            continue;
        }
        let (u1, u2) = ([d1[0] / l1, d1[1] / l1], [d2[0] / l2, d2[1] / l2]);
        let cos = (u1[0] * u2[0] + u1[1] * u2[1]).clamp(-1.0, 1.0);
        let angle = cos.acos();
        if !(0.02..=std::f32::consts::PI - 0.02).contains(&angle) {
            out.push(here);
            continue;
        }
        // Tangent points at distance t from the corner along each edge.
        let t = (radius / (angle / 2.0).tan()).min(0.45 * l1).min(0.45 * l2);
        let a = [here[0] + u1[0] * t, here[1] + u1[1] * t];
        let b = [here[0] + u2[0] * t, here[1] + u2[1] * t];
        // A quadratic curve with the corner as control point is a close,
        // well-behaved stand-in for the circular arc.
        for s in 0..=steps {
            let f = s as f32 / steps as f32;
            let g = 1.0 - f;
            out.push([g * g * a[0] + 2.0 * g * f * here[0] + f * f * b[0], g * g * a[1] + 2.0 * g * f * here[1] + f * f * b[1]]);
        }
    }
    out
}

/// Per-vertex 2D normals along a polyline, split where the turn is sharp.
/// For each edge returns the normal to use at its start and at its end.
/// `outward` picks the side: for a counter-clockwise closed loop, the right
/// side of travel is outward.
fn edge_normals(poly: &[V2], closed: bool) -> Vec<(V2, V2)> {
    let n = poly.len();
    let edges = if closed { n } else { n - 1 };
    let face: Vec<V2> = (0..edges)
        .map(|i| {
            let (p, q) = (poly[i], poly[(i + 1) % n]);
            let (dx, dy) = (q[0] - p[0], q[1] - p[1]);
            let l = (dx * dx + dy * dy).sqrt().max(1e-12);
            [dy / l, -dx / l]
        })
        .collect();
    let crease = CREASE.to_radians().cos();
    let blend = |a: V2, b: V2| -> V2 {
        if a[0] * b[0] + a[1] * b[1] >= crease {
            let s = [a[0] + b[0], a[1] + b[1]];
            let l = (s[0] * s[0] + s[1] * s[1]).sqrt().max(1e-12);
            [s[0] / l, s[1] / l]
        } else {
            a
        }
    };
    (0..edges)
        .map(|e| {
            let start = if closed || e > 0 { blend(face[e], face[(e + edges - 1) % edges]) } else { face[e] };
            let end = if closed || e + 1 < edges { blend(face[e], face[(e + 1) % edges]) } else { face[e] };
            (start, end)
        })
        .collect()
}

// --------------------------------------------------------------- revolve

/// Spin a profile of (r, z) points about the z axis, from `start` through
/// `angle` degrees. A closed profile with a partial angle gets its two cut
/// faces filled, so the cutaway looks solid.
pub fn revolve(profile: &[V2], angle: f32, start: f32, closed: bool, segments: Option<usize>) -> Mesh {
    let mut mesh = Mesh::default();
    if profile.len() < 2 {
        return mesh;
    }
    let full = angle >= 359.99;
    let segs = segments.unwrap_or(((angle / 360.0) * 96.0).ceil().max(8.0) as usize);
    let mut poly = profile.to_vec();
    // Orient a closed profile counter-clockwise so the right side is outward.
    if closed && area2(&poly) < 0.0 {
        poly.reverse();
    }
    let normals = edge_normals(&poly, closed);
    let n = poly.len();
    let edges = if closed { n } else { n - 1 };
    let theta = |s: usize| (start + angle * s as f32 / segs as f32).to_radians();
    for e in 0..edges {
        let (p, q) = (poly[e], poly[(e + 1) % n]);
        if p[0].abs() < 1e-7 && q[0].abs() < 1e-7 {
            continue; // an edge on the axis sweeps no surface
        }
        let (na, nb) = normals[e];
        let mut ring_a = vec![];
        let mut ring_b = vec![];
        for s in 0..=segs {
            let (sin, cos) = theta(s).sin_cos();
            ring_a.push(mesh.vertex([p[0] * cos, p[0] * sin, p[1]], [na[0] * cos, na[0] * sin, na[1]]));
            ring_b.push(mesh.vertex([q[0] * cos, q[0] * sin, q[1]], [nb[0] * cos, nb[0] * sin, nb[1]]));
        }
        for s in 0..segs {
            mesh.quad(ring_a[s], ring_a[s + 1], ring_b[s + 1], ring_b[s]);
        }
    }
    if closed && !full {
        for (s, sign) in [(0usize, -1.0f32), (segs, 1.0f32)] {
            let (sin, cos) = theta(s).sin_cos();
            let tangent = [-sin * sign, cos * sign, 0.0];
            let ids: Vec<u32> = poly.iter().map(|p| mesh.vertex([p[0] * cos, p[0] * sin, p[1]], tangent)).collect();
            for t in triangulate(&poly) {
                mesh.tri(ids[t[0]], ids[t[1]], ids[t[2]]);
            }
        }
    }
    mesh
}

// --------------------------------------------------------------- extrude

/// Push an outline in the xy plane along z from `z0` to `z1`, with caps.
pub fn extrude(outline: &[V2], z0: f32, z1: f32) -> Mesh {
    let mut mesh = Mesh::default();
    if outline.len() < 3 {
        return mesh;
    }
    let mut poly = outline.to_vec();
    if area2(&poly) < 0.0 {
        poly.reverse();
    }
    let normals = edge_normals(&poly, true);
    let n = poly.len();
    for e in 0..n {
        let (p, q) = (poly[e], poly[(e + 1) % n]);
        let (na, nb) = normals[e];
        let a0 = mesh.vertex([p[0], p[1], z0], [na[0], na[1], 0.0]);
        let a1 = mesh.vertex([p[0], p[1], z1], [na[0], na[1], 0.0]);
        let b0 = mesh.vertex([q[0], q[1], z0], [nb[0], nb[1], 0.0]);
        let b1 = mesh.vertex([q[0], q[1], z1], [nb[0], nb[1], 0.0]);
        mesh.quad(a0, b0, b1, a1);
    }
    let tris = triangulate(&poly);
    for (z, nz) in [(z0, -1.0f32), (z1, 1.0f32)] {
        let ids: Vec<u32> = poly.iter().map(|p| mesh.vertex([p[0], p[1], z], [0.0, 0.0, nz])).collect();
        for t in &tris {
            mesh.tri(ids[t[0]], ids[t[1]], ids[t[2]]);
        }
    }
    mesh
}

// ----------------------------------------------------------------- sweep

/// The cross-section carried along a sweep path, in the path's normal
/// plane: (along the frame's normal, along its binormal).
#[derive(Debug, Clone)]
pub enum Section {
    Circle { radius: f32, segments: usize },
    Rect { width: f32, height: f32, round: f32 },
}

impl Section {
    /// The outline and whether its normals are smooth (circle) or split.
    fn outline(&self) -> Vec<V2> {
        match self {
            Section::Circle { radius, segments } => (0..*segments)
                .map(|i| {
                    let t = i as f32 / *segments as f32 * std::f32::consts::TAU;
                    [radius * t.cos(), radius * t.sin()]
                })
                .collect(),
            Section::Rect { width, height, round } => {
                let (w, h) = (width / 2.0, height / 2.0);
                round_corners(&[[-w, -h], [w, -h], [w, h], [-w, h]], *round, true)
            }
        }
    }
}

/// Rotation-minimising frames along a path (double reflection method),
/// with the twist spread out so a closed path meets itself.
fn frames(path: &[V3], closed: bool) -> Vec<(V3, V3, V3)> {
    let n = path.len();
    let tangent = |i: usize| -> V3 {
        let (a, b) = if closed {
            (path[(i + n - 1) % n], path[(i + 1) % n])
        } else {
            (path[i.saturating_sub(1)], path[(i + 1).min(n - 1)])
        };
        normalize(sub(b, a))
    };
    let t0 = tangent(0);
    let helper = if t0[2].abs() < 0.9 { [0.0, 0.0, 1.0] } else { [1.0, 0.0, 0.0] };
    let mut r = normalize(cross(cross(t0, helper), t0));
    let mut out = vec![(t0, r, cross(t0, r))];
    for i in 1..n {
        let (x0, x1) = (path[i - 1], path[i]);
        let ti = out[i - 1].0;
        let t1 = tangent(i);
        let v1 = sub(x1, x0);
        let c1 = dot(v1, v1);
        if c1 < 1e-14 {
            out.push((t1, r, cross(t1, r)));
            continue;
        }
        let rl = sub(r, scale(v1, 2.0 / c1 * dot(v1, r)));
        let tl = sub(ti, scale(v1, 2.0 / c1 * dot(v1, ti)));
        let v2 = sub(t1, tl);
        let c2 = dot(v2, v2);
        r = if c2 < 1e-14 { rl } else { sub(rl, scale(v2, 2.0 / c2 * dot(v2, rl))) };
        r = normalize(r);
        out.push((t1, r, cross(t1, r)));
    }
    if closed && n > 2 {
        // How far the last frame has turned from the first, about the tangent.
        let (t, r_end, _) = out[n - 1];
        let r_start = out[0].1;
        let r_proj = normalize(sub(r_start, scale(t, dot(r_start, t))));
        let angle = dot(cross(r_end, r_proj), t).atan2(dot(r_end, r_proj));
        for (i, f) in out.iter_mut().enumerate() {
            let a = angle * i as f32 / n as f32;
            let (s, c) = a.sin_cos();
            let (t, r, b) = *f;
            let r2 = add(scale(r, c), scale(b, s));
            *f = (t, r2, cross(t, r2));
        }
    }
    out
}

/// Carry `section` along `path`. Open paths get flat end caps.
pub fn sweep(path: &[V3], closed: bool, section: &Section) -> Mesh {
    let mut mesh = Mesh::default();
    if path.len() < 2 {
        return mesh;
    }
    let outline = section.outline();
    let m = outline.len();
    let smooth = matches!(section, Section::Circle { .. });
    let fr = frames(path, closed);
    let n = path.len();
    let place = |i: usize, p: V2| -> V3 {
        let (_, r, b) = fr[i];
        add(path[i], add(scale(r, p[0]), scale(b, p[1])))
    };
    let along = if closed { n } else { n - 1 };
    if smooth {
        let rings: Vec<Vec<u32>> = (0..n)
            .map(|i| {
                outline
                    .iter()
                    .map(|p| {
                        let (_, r, b) = fr[i];
                        let normal = add(scale(r, p[0]), scale(b, p[1]));
                        mesh.vertex(place(i, *p), normal)
                    })
                    .collect()
            })
            .collect();
        for i in 0..along {
            let (ra, rb) = (&rings[i], &rings[(i + 1) % n]);
            for k in 0..m {
                mesh.quad(ra[k], ra[(k + 1) % m], rb[(k + 1) % m], rb[k]);
            }
        }
    } else {
        // Split normals at the section's sharp corners.
        let mut poly = outline.clone();
        if area2(&poly) < 0.0 {
            poly.reverse();
        }
        let normals = edge_normals(&poly, true);
        for e in 0..poly.len() {
            let (p, q) = (poly[e], poly[(e + 1) % poly.len()]);
            let (na, nb) = normals[e];
            let col = |mesh: &mut Mesh, pt: V2, nn: V2| -> Vec<u32> {
                (0..n)
                    .map(|i| {
                        let (_, r, b) = fr[i];
                        mesh.vertex(place(i, pt), add(scale(r, nn[0]), scale(b, nn[1])))
                    })
                    .collect()
            };
            let ca = col(&mut mesh, p, na);
            let cb = col(&mut mesh, q, nb);
            for i in 0..along {
                let j = (i + 1) % n;
                mesh.quad(ca[i], cb[i], cb[j], ca[j]);
            }
        }
    }
    if !closed {
        let tris = triangulate(&outline);
        for (i, sign) in [(0usize, -1.0f32), (n - 1, 1.0f32)] {
            let t = scale(fr[i].0, sign);
            let ids: Vec<u32> = outline.iter().map(|p| mesh.vertex(place(i, *p), t)).collect();
            for tri in &tris {
                mesh.tri(ids[tri[0]], ids[tri[1]], ids[tri[2]]);
            }
        }
    }
    mesh
}

// ------------------------------------------------------------------ paths

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PathSpec {
    /// Through the given points; `smooth` rounds them into a curve.
    Points {
        points: Vec<V3>,
        #[serde(default)]
        closed: bool,
        #[serde(default)]
        smooth: bool,
    },
    /// A coil about the z axis, starting at angle 0 and z = 0.
    Helix {
        radius: f32,
        pitch: f32,
        turns: f32,
    },
    /// A circle in the xy plane, centred on the axis.
    Circle { radius: f32 },
    /// An arc in the xy plane: `angle` degrees from `start`.
    Arc {
        radius: f32,
        angle: f32,
        #[serde(default)]
        start: f32,
    },
    /// The D shape of a tokamak field coil, in the xz plane: a straight leg
    /// at x = `inner` and a rounded outer curve reaching x = `outer`.
    DShape { inner: f32, outer: f32, height: f32 },
}

impl PathSpec {
    pub fn closed(&self) -> bool {
        match self {
            PathSpec::Points { closed, .. } => *closed,
            PathSpec::Circle { .. } | PathSpec::DShape { .. } => true,
            _ => false,
        }
    }

    pub fn points(&self) -> Vec<V3> {
        use std::f32::consts::TAU;
        match self {
            PathSpec::Points { points, closed, smooth } => {
                if *smooth && points.len() >= 3 {
                    catmull_rom(points, *closed, 8)
                } else {
                    points.clone()
                }
            }
            PathSpec::Helix { radius, pitch, turns } => {
                let steps = (turns * 48.0).ceil().max(8.0) as usize;
                (0..=steps)
                    .map(|i| {
                        let t = i as f32 / steps as f32 * turns;
                        let a = t * TAU;
                        [radius * a.cos(), radius * a.sin(), pitch * t]
                    })
                    .collect()
            }
            PathSpec::Circle { radius } => (0..96)
                .map(|i| {
                    let a = i as f32 / 96.0 * TAU;
                    [radius * a.cos(), radius * a.sin(), 0.0]
                })
                .collect(),
            PathSpec::Arc { radius, angle, start } => {
                let steps = ((angle.abs() / 360.0) * 96.0).ceil().max(4.0) as usize;
                (0..=steps)
                    .map(|i| {
                        let a = (start + angle * i as f32 / steps as f32).to_radians();
                        [radius * a.cos(), radius * a.sin(), 0.0]
                    })
                    .collect()
            }
            PathSpec::DShape { inner, outer, height } => {
                // Straight inner leg going up, then a half ellipse over the
                // top and down the outside, back to the start.
                let h = height / 2.0;
                let mut pts = vec![];
                let leg = 12;
                for i in 0..leg {
                    pts.push([*inner, 0.0, -h + height * i as f32 / leg as f32]);
                }
                let arc = 48;
                let (cx, rx) = (*inner, outer - inner);
                for i in 0..arc {
                    let a = std::f32::consts::FRAC_PI_2 - std::f32::consts::PI * i as f32 / arc as f32;
                    pts.push([cx + rx * a.cos(), 0.0, h * a.sin()]);
                }
                pts
            }
        }
    }
}

fn catmull_rom(points: &[V3], closed: bool, per: usize) -> Vec<V3> {
    let n = points.len();
    let get = |i: isize| -> V3 {
        if closed {
            points[i.rem_euclid(n as isize) as usize]
        } else {
            points[i.clamp(0, n as isize - 1) as usize]
        }
    };
    let segments = if closed { n } else { n - 1 };
    let mut out = vec![];
    for s in 0..segments {
        let (p0, p1, p2, p3) = (get(s as isize - 1), get(s as isize), get(s as isize + 1), get(s as isize + 2));
        for k in 0..per {
            let t = k as f32 / per as f32;
            let (t2, t3) = (t * t, t * t * t);
            let f = |a: f32, b: f32, c: f32, d: f32| 0.5 * (2.0 * b + (-a + c) * t + (2.0 * a - 5.0 * b + 4.0 * c - d) * t2 + (-a + 3.0 * b - 3.0 * c + d) * t3);
            out.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1]), f(p0[2], p1[2], p2[2], p3[2])]);
        }
    }
    if !closed {
        out.push(points[n - 1]);
    }
    out
}

// ------------------------------------------------------------------ shapes

fn zero() -> f32 {
    0.0
}
fn full() -> f32 {
    360.0
}
fn yes() -> bool {
    true
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum SectionSpec {
    Circle { radius: f32 },
    Rect {
        width: f32,
        height: f32,
        #[serde(default)]
        round: f32,
    },
}

/// What a part is made of, as the script writes it.
#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Shape {
    Box {
        size: V3,
        #[serde(default)]
        round: f32,
    },
    Cylinder {
        radius: f32,
        height: f32,
        #[serde(default = "full")]
        angle: f32,
        #[serde(default)]
        round: f32,
    },
    /// A pipe or ring: a cylinder with a hole.
    Tube {
        inner: f32,
        outer: f32,
        height: f32,
        #[serde(default = "full")]
        angle: f32,
        #[serde(default = "zero")]
        start: f32,
        #[serde(default)]
        round: f32,
    },
    Cone {
        bottom: f32,
        top: f32,
        height: f32,
    },
    Sphere {
        radius: f32,
    },
    Torus {
        major: f32,
        minor: f32,
        #[serde(default = "full")]
        angle: f32,
        #[serde(default = "zero")]
        start: f32,
    },
    /// A profile of [r, z] points spun about z.
    Revolve {
        profile: Vec<V2>,
        #[serde(default = "full")]
        angle: f32,
        #[serde(default = "zero")]
        start: f32,
        #[serde(default = "yes")]
        closed: bool,
        #[serde(default)]
        round: f32,
    },
    /// An outline of [x, y] points pushed up z by `depth`.
    Extrude {
        outline: Vec<V2>,
        depth: f32,
        #[serde(default)]
        round: f32,
    },
    Sweep {
        path: PathSpec,
        section: SectionSpec,
    },
    Gear {
        teeth: u32,
        radius: f32,
        depth: f32,
        #[serde(default)]
        tooth: Option<f32>,
        #[serde(default)]
        bore: f32,
    },
}

impl Shape {
    pub fn kind(&self) -> &'static str {
        match self {
            Shape::Box { .. } => "box",
            Shape::Cylinder { .. } => "cylinder",
            Shape::Tube { .. } => "tube",
            Shape::Cone { .. } => "cone",
            Shape::Sphere { .. } => "sphere",
            Shape::Torus { .. } => "torus",
            Shape::Revolve { .. } => "revolve",
            Shape::Extrude { .. } => "extrude",
            Shape::Sweep { .. } => "sweep",
            Shape::Gear { .. } => "gear",
        }
    }

    /// Problems in the numbers, with the field they are in.
    pub fn check(&self) -> Vec<(String, String)> {
        let mut out = vec![];
        let mut positive = |field: &str, v: f32| {
            if !(v.is_finite() && v > 0.0) {
                out.push((field.to_string(), format!("`{field}` must be a positive number of metres, not {v}")));
            }
        };
        match self {
            Shape::Box { size, .. } => size.iter().for_each(|v| positive("size", *v)),
            Shape::Cylinder { radius, height, .. } => {
                positive("radius", *radius);
                positive("height", *height);
            }
            Shape::Tube { inner, outer, height, .. } => {
                positive("outer", *outer);
                positive("height", *height);
                if *inner < 0.0 || inner >= outer {
                    out.push(("inner".into(), format!("`inner` ({inner}) must be at least 0 and less than `outer` ({outer})")));
                }
            }
            Shape::Cone { bottom, top, height } => {
                positive("height", *height);
                if *bottom < 0.0 || *top < 0.0 || (*bottom == 0.0 && *top == 0.0) {
                    out.push(("bottom".into(), "a cone needs `bottom` and `top` radii of at least 0, not both 0".into()));
                }
            }
            Shape::Sphere { radius } => positive("radius", *radius),
            Shape::Torus { major, minor, .. } => {
                positive("major", *major);
                positive("minor", *minor);
                if minor >= major {
                    out.push(("minor".into(), format!("`minor` ({minor}) must be less than `major` ({major})")));
                }
            }
            Shape::Revolve { profile, .. } => {
                if profile.len() < 2 {
                    out.push(("profile".into(), "a profile needs at least two [r, z] points".into()));
                }
                if profile.iter().any(|p| p[0] < 0.0 || !p[0].is_finite() || !p[1].is_finite()) {
                    out.push(("profile".into(), "every profile point is [r, z] with r (distance from the axis) at least 0".into()));
                }
            }
            Shape::Extrude { outline, depth, .. } => {
                positive("depth", *depth);
                if outline.len() < 3 {
                    out.push(("outline".into(), "an outline needs at least three [x, y] points".into()));
                }
            }
            Shape::Sweep { path, section } => {
                match section {
                    SectionSpec::Circle { radius } => positive("section.radius", *radius),
                    SectionSpec::Rect { width, height, .. } => {
                        positive("section.width", *width);
                        positive("section.height", *height);
                    }
                }
                match path {
                    PathSpec::Points { points, .. } if points.len() < 2 => {
                        out.push(("path.points".into(), "a path needs at least two points".into()));
                    }
                    PathSpec::Helix { radius, pitch, turns } => {
                        positive("path.radius", *radius);
                        positive("path.pitch", *pitch);
                        positive("path.turns", *turns);
                    }
                    PathSpec::DShape { inner, outer, height } => {
                        positive("path.height", *height);
                        if inner >= outer {
                            out.push(("path.outer".into(), format!("`outer` ({outer}) must be greater than `inner` ({inner})")));
                        }
                    }
                    _ => {}
                }
            }
            Shape::Gear { teeth, radius, depth, .. } => {
                positive("radius", *radius);
                positive("depth", *depth);
                if *teeth < 4 {
                    out.push(("teeth".into(), "a gear needs at least 4 teeth".into()));
                }
            }
        }
        if let Shape::Cylinder { angle, .. } | Shape::Tube { angle, .. } | Shape::Torus { angle, .. } | Shape::Revolve { angle, .. } = self {
            if !(*angle > 0.0 && *angle <= 360.0) {
                out.push(("angle".into(), format!("`angle` is in degrees, more than 0 and at most 360, not {angle}")));
            }
        }
        out
    }

    pub fn build(&self) -> Mesh {
        match self {
            Shape::Box { size, round } => {
                let (x, y) = (size[0] / 2.0, size[1] / 2.0);
                let outline = round_corners(&[[-x, -y], [x, -y], [x, y], [-x, y]], *round, true);
                extrude(&outline, -size[2] / 2.0, size[2] / 2.0)
            }
            Shape::Cylinder { radius, height, angle, round } => {
                let h = height / 2.0;
                let profile = round_corners(&[[0.0, -h], [*radius, -h], [*radius, h], [0.0, h]], *round, false);
                revolve(&profile, *angle, 0.0, true, None)
            }
            Shape::Tube { inner, outer, height, angle, start, round } => {
                let h = height / 2.0;
                let profile = round_corners(&[[*inner, -h], [*outer, -h], [*outer, h], [*inner, h]], *round, true);
                revolve(&profile, *angle, *start, true, None)
            }
            Shape::Cone { bottom, top, height } => {
                let h = height / 2.0;
                revolve(&[[0.0, -h], [*bottom, -h], [*top, h], [0.0, h]], 360.0, 0.0, true, None)
            }
            Shape::Sphere { radius } => {
                let profile: Vec<V2> = (0..=32)
                    .map(|i| {
                        let a = -std::f32::consts::FRAC_PI_2 + std::f32::consts::PI * i as f32 / 32.0;
                        [radius * a.cos(), radius * a.sin()]
                    })
                    .collect();
                revolve(&profile, 360.0, 0.0, false, Some(64))
            }
            Shape::Torus { major, minor, angle, start } => {
                let profile: Vec<V2> = (0..32)
                    .map(|i| {
                        let a = i as f32 / 32.0 * std::f32::consts::TAU;
                        [major + minor * a.cos(), minor * a.sin()]
                    })
                    .collect();
                revolve(&profile, *angle, *start, true, None)
            }
            Shape::Revolve { profile, angle, start, closed, round } => {
                let p = round_corners(profile, *round, *closed);
                revolve(&p, *angle, *start, *closed, None)
            }
            Shape::Extrude { outline, depth, round } => extrude(&round_corners(outline, *round, true), 0.0, *depth),
            Shape::Sweep { path, section } => {
                let s = match section {
                    SectionSpec::Circle { radius } => Section::Circle { radius: *radius, segments: 20 },
                    SectionSpec::Rect { width, height, round } => Section::Rect { width: *width, height: *height, round: *round },
                };
                sweep(&path.points(), path.closed(), &s)
            }
            Shape::Gear { teeth, radius, depth, tooth, bore } => {
                let tooth = tooth.unwrap_or(radius * 0.12);
                let n = *teeth as usize;
                let mut outline = vec![];
                for i in 0..n {
                    let base = i as f32 / n as f32 * std::f32::consts::TAU;
                    let step = std::f32::consts::TAU / n as f32;
                    // Root, flank up, tip, flank down: a trapezoidal tooth.
                    for (f, r) in [(0.0, radius - tooth), (0.25, radius - tooth), (0.38, *radius), (0.62, *radius), (0.75, radius - tooth)] {
                        let a = base + f * step;
                        outline.push([r * a.cos(), r * a.sin()]);
                    }
                }
                let mut mesh = extrude(&outline, -depth / 2.0, depth / 2.0);
                if *bore > 0.0 {
                    // A hub ring marks the bore; true holes need booleans.
                    let hub = revolve(&[[*bore, -depth * 0.55], [bore * 1.6, -depth * 0.55], [bore * 1.6, depth * 0.55], [*bore, depth * 0.55]], 360.0, 0.0, true, None);
                    mesh.append(&hub);
                }
                mesh
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sane(mesh: &Mesh) {
        assert!(mesh.triangles() > 0, "no triangles");
        assert_eq!(mesh.positions.len(), mesh.normals.len());
        assert!(mesh.indices.iter().all(|i| (*i as usize) < mesh.positions.len()));
        for n in &mesh.normals {
            assert!((length(*n) - 1.0).abs() < 1e-3, "normal not unit: {n:?}");
        }
        // Faces agree with their normals.
        for t in mesh.indices.chunks(3) {
            let (a, b, c) = (mesh.positions[t[0] as usize], mesh.positions[t[1] as usize], mesh.positions[t[2] as usize]);
            let face = cross(sub(b, a), sub(c, a));
            let n = add(add(mesh.normals[t[0] as usize], mesh.normals[t[1] as usize]), mesh.normals[t[2] as usize]);
            assert!(dot(face, n) >= 0.0);
        }
    }

    #[test]
    fn every_shape_builds_a_sane_mesh() {
        let shapes = [
            Shape::Box { size: [1.0, 2.0, 0.5], round: 0.05 },
            Shape::Cylinder { radius: 1.0, height: 2.0, angle: 360.0, round: 0.05 },
            Shape::Tube { inner: 0.8, outer: 1.0, height: 0.5, angle: 270.0, start: 45.0, round: 0.02 },
            Shape::Cone { bottom: 1.0, top: 0.2, height: 1.0 },
            Shape::Sphere { radius: 0.5 },
            Shape::Torus { major: 2.0, minor: 0.4, angle: 300.0, start: 0.0 },
            Shape::Revolve { profile: vec![[1.0, -1.0], [2.0, -0.5], [2.0, 0.5], [1.0, 1.0]], angle: 270.0, start: 0.0, closed: true, round: 0.1 },
            Shape::Extrude { outline: vec![[0.0, 0.0], [2.0, 0.0], [2.0, 1.0], [1.0, 0.5], [0.0, 1.0]], depth: 0.3, round: 0.0 },
            Shape::Sweep { path: PathSpec::Helix { radius: 1.0, pitch: 0.2, turns: 5.0 }, section: SectionSpec::Circle { radius: 0.05 } },
            Shape::Sweep { path: PathSpec::DShape { inner: 1.0, outer: 3.0, height: 4.0 }, section: SectionSpec::Rect { width: 0.3, height: 0.15, round: 0.02 } },
            Shape::Gear { teeth: 20, radius: 1.0, depth: 0.2, tooth: None, bore: 0.2 },
        ];
        for shape in &shapes {
            assert!(shape.check().is_empty(), "{shape:?}: {:?}", shape.check());
            sane(&shape.build());
        }
    }

    #[test]
    fn a_cylinder_has_the_right_size_and_round_sides() {
        let mesh = Shape::Cylinder { radius: 1.0, height: 2.0, angle: 360.0, round: 0.0 }.build();
        let (lo, hi) = mesh.bounds();
        assert!((hi[0] - 1.0).abs() < 1e-4 && (lo[2] + 1.0).abs() < 1e-4 && (hi[2] - 1.0).abs() < 1e-4);
        // Side vertices carry horizontal normals; cap vertices vertical ones.
        assert!(mesh.normals.iter().any(|n| n[2].abs() < 1e-4));
        assert!(mesh.normals.iter().any(|n| (n[2] - 1.0).abs() < 1e-4));
    }

    #[test]
    fn a_cutaway_is_capped() {
        let mesh = Shape::Tube { inner: 1.0, outer: 2.0, height: 1.0, angle: 180.0, start: 0.0, round: 0.0 }.build();
        // Cut faces at 0 and 180 degrees face along -y and +y... i.e. their
        // normals are tangent to the revolution there.
        assert!(mesh.normals.iter().any(|n| (n[1] + 1.0).abs() < 1e-4 || (n[1] - 1.0).abs() < 1e-4));
    }

    #[test]
    fn ear_clipping_handles_a_concave_outline() {
        let l = [[0.0, 0.0], [2.0, 0.0], [2.0, 1.0], [1.0, 1.0], [1.0, 2.0], [0.0, 2.0]];
        let tris = triangulate(&l);
        assert_eq!(tris.len(), 4);
        let area: f32 = tris.iter().map(|t| area2(&[l[t[0]], l[t[1]], l[t[2]]]).abs()).sum();
        assert!((area - 3.0).abs() < 1e-5);
    }

    #[test]
    fn a_closed_sweep_meets_itself() {
        let path = PathSpec::Circle { radius: 2.0 }.points();
        let fr = frames(&path, true);
        let (first, last) = (fr[0].1, fr[fr.len() - 1].1);
        assert!(dot(first, last) > 0.95, "the frame turns smoothly back to the start");
    }
}
