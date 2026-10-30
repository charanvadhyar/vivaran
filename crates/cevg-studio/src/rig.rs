//! The rig: a scene turned into nodes, meshes, materials and lights, with
//! the small amount of 3D maths both renderers share.
//!
//! Every part becomes a node. An array becomes a group node with one child
//! node per copy, all sharing one mesh. Parents become node parents, so an
//! exploded assembly moves its sub-parts with it.

use crate::mesh::{add, cross, normalize, scale, sub, Mesh, V3};
use crate::scene::{hex, ArraySpec, Axis, EnvPreset, LightKind, Material, Scene};
use serde::Serialize;

pub type Quat = [f32; 4]; // w, x, y, z

pub fn quat_mul(a: Quat, b: Quat) -> Quat {
    [
        a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
        a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
        a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
        a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0],
    ]
}

pub fn quat_axis(axis: usize, degrees: f32) -> Quat {
    let h = degrees.to_radians() / 2.0;
    let mut q = [h.cos(), 0.0, 0.0, 0.0];
    q[1 + axis] = h.sin();
    q
}

/// Euler degrees, applied about x, then y, then z (Blender's "XYZ").
pub fn quat_euler(e: V3) -> Quat {
    quat_mul(quat_axis(2, e[2]), quat_mul(quat_axis(1, e[1]), quat_axis(0, e[0])))
}

pub fn quat_rotate(q: Quat, v: V3) -> V3 {
    let u = [q[1], q[2], q[3]];
    let t = scale(cross(u, v), 2.0);
    add(add(v, scale(t, q[0])), cross(u, t))
}

/// The rotation whose columns are the given orthonormal axes.
pub fn quat_from_axes(x: V3, y: V3, z: V3) -> Quat {
    let (m00, m11, m22) = (x[0], y[1], z[2]);
    let trace = m00 + m11 + m22;
    let q = if trace > 0.0 {
        let s = (trace + 1.0).sqrt() * 2.0;
        [0.25 * s, (y[2] - z[1]) / s, (z[0] - x[2]) / s, (x[1] - y[0]) / s]
    } else if m00 > m11 && m00 > m22 {
        let s = (1.0 + m00 - m11 - m22).sqrt() * 2.0;
        [(y[2] - z[1]) / s, 0.25 * s, (y[0] + x[1]) / s, (z[0] + x[2]) / s]
    } else if m11 > m22 {
        let s = (1.0 + m11 - m00 - m22).sqrt() * 2.0;
        [(z[0] - x[2]) / s, (y[0] + x[1]) / s, 0.25 * s, (z[1] + y[2]) / s]
    } else {
        let s = (1.0 + m22 - m00 - m11).sqrt() * 2.0;
        [(x[1] - y[0]) / s, (z[0] + x[2]) / s, (z[1] + y[2]) / s, 0.25 * s]
    };
    let l = (q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]).sqrt();
    [q[0] / l, q[1] / l, q[2] / l, q[3] / l]
}

/// A local transform: translation, rotation, scale.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Trs {
    pub t: V3,
    pub r: Quat,
    pub s: V3,
}

impl Trs {
    pub fn apply(&self, p: V3) -> V3 {
        add(self.t, quat_rotate(self.r, [p[0] * self.s[0], p[1] * self.s[1], p[2] * self.s[2]]))
    }
}

#[derive(Debug, Clone)]
pub struct Node {
    pub name: String,
    pub part: usize,
    pub parent: Option<usize>,
    pub children: Vec<usize>,
    pub mesh: Option<usize>,
    pub material: Option<usize>,
    pub base_t: V3,
    /// Euler degrees.
    pub base_r: V3,
    pub base_s: V3,
    /// For copies of an array: which way this copy moves when exploded.
    pub spread: Option<V3>,
    pub visible: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct Light {
    pub id: String,
    pub kind: &'static str,
    pub position: V3,
    /// The light shines down its local -z.
    pub rotation: Quat,
    pub power: f32,
    pub color: V3,
    pub size: f32,
}

pub struct Rig {
    pub nodes: Vec<Node>,
    /// The node each part became (its group node, for an array).
    pub part_node: Vec<usize>,
    /// One per part with a shape, named after the part.
    pub meshes: Vec<(String, Mesh)>,
    pub materials: Vec<Material>,
    pub lights: Vec<Light>,
    pub background: V3,
    pub env_strength: f32,
    /// What reflective surfaces see instead of the background: a soft
    /// gradient, brighter overhead. The camera still sees `background`.
    /// Without it, metal on a dark background reflects nothing and reads as
    /// black or as chrome.
    pub reflection_top: V3,
    pub reflection_bottom: V3,
}

/// Orientation that points local -z from `from` toward `to`, with z up.
pub fn look_at(from: V3, to: V3) -> Quat {
    let forward = normalize(sub(to, from));
    let up = if forward[2].abs() > 0.999 { [0.0, 1.0, 0.0] } else { [0.0, 0.0, 1.0] };
    let right = normalize(cross(forward, up));
    let true_up = cross(right, forward);
    quat_from_axes(right, true_up, scale(forward, -1.0))
}

impl Rig {
    pub fn build(scene: &Scene) -> Rig {
        let materials: Vec<Material> = scene.materials.iter().map(|(name, m)| m.resolve(name)).collect();
        let material_index = |name: &str| materials.iter().position(|m| m.name == name);
        let mut nodes: Vec<Node> = vec![];
        let mut meshes = vec![];
        let mut part_node = vec![];
        for (pi, part) in scene.parts.iter().enumerate() {
            let parent = part.parent.as_ref().and_then(|p| scene.parts.iter().position(|q| &q.id == p)).map(|i| part_node[i]);
            let visible = part.visible && parent.is_none_or(|p: usize| nodes[p].visible);
            let mesh = part.shape.as_ref().map(|shape| {
                meshes.push((part.id.clone(), shape.build()));
                meshes.len() - 1
            });
            let material = part.material.as_deref().and_then(material_index);
            let own = Node {
                name: part.id.clone(),
                part: pi,
                parent,
                children: vec![],
                mesh: if part.array.is_some() { None } else { mesh },
                material: if part.array.is_some() { None } else { material },
                base_t: part.at,
                base_r: part.rotate,
                base_s: part.scale.vector(),
                spread: None,
                visible,
            };
            let index = nodes.len();
            if let Some(p) = parent {
                nodes[p].children.push(index);
            }
            nodes.push(own);
            part_node.push(index);
            if let Some(array) = &part.array {
                for k in 0..array.count() as usize {
                    let (t, r, spread) = match array {
                        ArraySpec::Radial { count, axis, angle, start } => {
                            let step = if *angle >= 359.99 { 360.0 / *count as f32 } else if *count > 1 { angle / (*count - 1) as f32 } else { 0.0 };
                            let a = start + step * k as f32;
                            let mut e = [0.0; 3];
                            e[axis.index()] = a;
                            // Outward is the axis's first perpendicular turned by `a`.
                            let out = match axis {
                                Axis::Z => [a.to_radians().cos(), a.to_radians().sin(), 0.0],
                                Axis::X => [0.0, a.to_radians().cos(), a.to_radians().sin()],
                                Axis::Y => [a.to_radians().sin(), 0.0, a.to_radians().cos()],
                            };
                            ([0.0; 3], e, out)
                        }
                        ArraySpec::Linear { count, step } => {
                            let centre = k as f32 - (*count as f32 - 1.0) / 2.0;
                            (scale(*step, k as f32), [0.0; 3], scale(normalize(*step), centre))
                        }
                    };
                    let child = nodes.len();
                    nodes[index].children.push(child);
                    nodes.push(Node {
                        name: format!("{}[{k}]", part.id),
                        part: pi,
                        parent: Some(index),
                        children: vec![],
                        mesh,
                        material,
                        base_t: t,
                        base_r: r,
                        base_s: [1.0; 3],
                        spread: Some(spread),
                        visible,
                    });
                }
            }
        }

        // Lights: the scene's own, or the environment's rig placed around
        // what the camera looks at, scaled to the scene's size.
        let target = scene.camera.target;
        let (lo, hi) = Self::scene_bounds(&nodes, &meshes);
        let radius = (0.5 * crate::mesh::length(sub(hi, lo))).max(0.5);
        let env = &scene.environment;
        let light = |id: &str, kind: LightKind, at: V3, to: V3, power: f32, color: V3, size: f32| Light {
            id: id.to_string(),
            kind: match kind {
                LightKind::Area => "area",
                LightKind::Point => "point",
                LightKind::Spot => "spot",
                LightKind::Sun => "sun",
            },
            position: at,
            rotation: look_at(at, to),
            power,
            color,
            size,
        };
        let lights: Vec<Light> = if !scene.lights.is_empty() {
            scene
                .lights
                .iter()
                .map(|l| light(&l.id, l.kind, l.at, l.target, l.power, l.color.as_deref().and_then(hex).unwrap_or([1.0; 3]), l.size.unwrap_or(radius * 0.5)))
                .collect()
        } else {
            let k = env.strength * radius * radius;
            let around = |az: f32, el: f32, d: f32| -> V3 {
                let (az, el) = (az.to_radians(), el.to_radians());
                add(target, scale([el.cos() * az.cos(), el.cos() * az.sin(), el.sin()], d * radius))
            };
            let az = scene.camera.azimuth;
            match env.preset {
                EnvPreset::DarkStudio => vec![
                    light("key", LightKind::Area, around(az - 50.0, 45.0, 3.0), target, 900.0 * k, [1.0, 0.86, 0.72], radius * 1.2),
                    light("rim", LightKind::Area, around(az + 160.0, 30.0, 3.0), target, 1200.0 * k, [0.55, 0.75, 1.0], radius * 0.8),
                    light("fill", LightKind::Area, around(az + 60.0, 10.0, 3.5), target, 250.0 * k, [0.85, 0.9, 1.0], radius * 1.6),
                ],
                EnvPreset::Studio => vec![
                    light("key", LightKind::Area, around(az - 45.0, 50.0, 3.0), target, 1100.0 * k, [1.0, 0.97, 0.92], radius * 1.6),
                    light("fill", LightKind::Area, around(az + 70.0, 20.0, 3.0), target, 500.0 * k, [1.0, 1.0, 1.0], radius * 2.0),
                    light("top", LightKind::Area, around(az, 85.0, 3.0), target, 400.0 * k, [1.0, 1.0, 1.0], radius * 2.0),
                ],
                EnvPreset::Black => vec![light("key", LightKind::Area, around(az - 40.0, 40.0, 3.0), target, 500.0 * k, [1.0, 0.95, 0.9], radius)],
            }
        };
        let background = env.background.as_deref().and_then(hex).unwrap_or(match env.preset {
            EnvPreset::DarkStudio => [0.006, 0.007, 0.010],
            EnvPreset::Studio => [0.55, 0.56, 0.58],
            EnvPreset::Black => [0.0, 0.0, 0.0],
        });
        let (reflection_top, reflection_bottom) = match env.preset {
            EnvPreset::DarkStudio => ([0.16, 0.17, 0.2], [0.004, 0.004, 0.005]),
            EnvPreset::Studio => ([0.75, 0.76, 0.78], [0.25, 0.25, 0.27]),
            EnvPreset::Black => ([0.0; 3], [0.0; 3]),
        };
        Rig { nodes, part_node, meshes, materials, lights, background, env_strength: env.strength, reflection_top, reflection_bottom }
    }

    /// World-space bounds of every mesh at the rest pose.
    fn scene_bounds(nodes: &[Node], meshes: &[(String, Mesh)]) -> (V3, V3) {
        let rest: Vec<Trs> = nodes.iter().map(|n| Trs { t: n.base_t, r: quat_euler(n.base_r), s: n.base_s }).collect();
        let world = world_transforms(nodes, &rest);
        let mut lo = [f32::INFINITY; 3];
        let mut hi = [f32::NEG_INFINITY; 3];
        for (i, n) in nodes.iter().enumerate() {
            if let Some(m) = n.mesh {
                for p in corners(meshes[m].1.bounds()) {
                    let w = apply_chain(&world[i], p);
                    for k in 0..3 {
                        lo[k] = lo[k].min(w[k]);
                        hi[k] = hi[k].max(w[k]);
                    }
                }
            }
        }
        if !lo[0].is_finite() {
            return ([-1.0; 3], [1.0; 3]);
        }
        (lo, hi)
    }

    /// The node and every node below it, in order.
    pub fn subtree(&self, node: usize) -> Vec<usize> {
        let mut out = vec![node];
        let mut i = 0;
        while i < out.len() {
            out.extend(self.nodes[out[i]].children.iter().copied());
            i += 1;
        }
        out
    }

    /// The node a target names: a part, or one copy of an array.
    pub fn node_of(&self, scene: &Scene, target: &str) -> Option<usize> {
        let (id, index) = crate::scene::split_target(target);
        let part = scene.parts.iter().position(|p| p.id == id)?;
        let node = self.part_node[part];
        match index {
            None => Some(node),
            Some(k) => self.nodes[node].children.iter().copied().filter(|c| self.nodes[*c].part == part).nth(k),
        }
    }
}

/// The eight corners of a box.
pub fn corners((lo, hi): (V3, V3)) -> [V3; 8] {
    let mut out = [[0.0; 3]; 8];
    for (i, c) in out.iter_mut().enumerate() {
        *c = [if i & 1 == 0 { lo[0] } else { hi[0] }, if i & 2 == 0 { lo[1] } else { hi[1] }, if i & 4 == 0 { lo[2] } else { hi[2] }];
    }
    out
}

/// For each node, the chain of transforms from the node up to the root.
pub fn world_transforms(nodes: &[Node], local: &[Trs]) -> Vec<Vec<Trs>> {
    (0..nodes.len())
        .map(|i| {
            let mut chain = vec![local[i]];
            let mut p = nodes[i].parent;
            while let Some(j) = p {
                chain.push(local[j]);
                p = nodes[j].parent;
            }
            chain
        })
        .collect()
}

pub fn apply_chain(chain: &[Trs], p: V3) -> V3 {
    chain.iter().fold(p, |acc, t| t.apply(acc))
}
