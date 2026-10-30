//! Export: the scene baked into the two files every renderer reads.
//!
//! * `scene.glb` is standard glTF 2.0: meshes, the node tree, PBR
//!   materials (with the emissive-strength, transmission and IOR
//!   extensions), a camera, and the transform animation. Any glTF viewer
//!   or Blender opens it.
//! * `timeline.json` carries what glTF cannot: per-frame opacity and glow,
//!   the camera track, the resolved lights and background, render settings
//!   and the step timings. It is the authority on time for every renderer;
//!   the glTF animation is there for previews.
//!
//! The scene is z-up; glTF is y-up. Positions go (x, y, z) -> (x, z, -y)
//! and a viewer that converts back (Blender does) gets the scene exactly.

use crate::mesh::V3;
use crate::rig::{Quat, Rig};
use crate::scene::{EnvPreset, Scene};
use crate::timeline::{camera_transform, StepTime, Timeline};
use serde::Serialize;
use serde_json::{json, Value};

#[derive(Debug, Clone, Serialize)]
pub struct Track {
    pub node: String,
    /// translation, rotation (w, x, y, z), scale, opacity, emission_strength, emission_color
    pub path: &'static str,
    pub frames: Vec<u32>,
    pub values: Vec<Vec<f32>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct CameraTrack {
    pub frames: Vec<u32>,
    pub position: Vec<V3>,
    pub rotation: Vec<Quat>,
    /// Vertical field of view, degrees.
    pub fov: Vec<f32>,
}

#[derive(Debug, Clone, Serialize)]
pub struct NodeOut {
    pub name: String,
    pub parent: Option<String>,
    pub mesh: Option<String>,
    pub material: Option<String>,
    pub translation: V3,
    pub rotation: Quat,
    pub scale: V3,
}

#[derive(Debug, Clone, Serialize)]
pub struct TimelineFile {
    pub format: &'static str,
    pub title: String,
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    pub samples: u32,
    pub frames: usize,
    pub seconds: f32,
    pub environment: Value,
    pub lights: Vec<crate::rig::Light>,
    pub materials: Vec<Value>,
    pub nodes: Vec<NodeOut>,
    pub steps: Vec<StepTime>,
    pub tracks: Vec<Track>,
    pub camera: CameraTrack,
}

fn close(a: &[f32], b: &[f32]) -> bool {
    a.iter().zip(b).all(|(x, y)| (x - y).abs() < 1e-5)
}

/// Keep a frame only where the value starts or stops changing, so a
/// still stretch costs two keys and a moving one a key per frame.
fn thin(values: &[Vec<f32>]) -> Vec<usize> {
    let n = values.len();
    (0..n).filter(|&f| f == 0 || f + 1 == n || !close(&values[f], &values[f - 1]) || !close(&values[f], &values[f + 1])).collect()
}

/// Bake every animated channel and the camera, one value per frame.
pub fn bake(rig: &Rig, tl: &Timeline) -> (Vec<Track>, CameraTrack, Vec<NodeOut>) {
    let n = rig.nodes.len();
    let frames = tl.frames.max(1);
    // Per node: translation, rotation, scale, opacity, glow, glow colour.
    let mut series: Vec<[Vec<Vec<f32>>; 6]> = (0..n).map(|_| Default::default()).collect();
    let mut cam: Vec<Vec<f32>> = Vec::with_capacity(frames);
    let mut rest = None;
    for f in 0..frames {
        let pose = tl.pose_at_frame(rig, f);
        #[allow(clippy::needless_range_loop)] // i indexes pose.local and series together
        for i in 0..n {
            let l = &pose.local[i];
            let mut r = l.r;
            if let Some(prev) = series[i][1].last() {
                // Keep quaternions on one side so they interpolate the short way.
                if prev[0] * r[0] + prev[1] * r[1] + prev[2] * r[2] + prev[3] * r[3] < 0.0 {
                    r = [-r[0], -r[1], -r[2], -r[3]];
                }
            }
            series[i][0].push(l.t.to_vec());
            series[i][1].push(r.to_vec());
            series[i][2].push(l.s.to_vec());
            series[i][3].push(vec![pose.opacity[i]]);
            series[i][4].push(vec![pose.glow[i]]);
            series[i][5].push(pose.glow_color[i].to_vec());
        }
        let (p, q) = camera_transform(&pose.camera);
        cam.push(vec![p[0], p[1], p[2], q[0], q[1], q[2], q[3], pose.camera.fov]);
        if f == 0 {
            rest = Some(pose);
        }
    }
    let rest = rest.expect("at least one frame");
    let paths = ["translation", "rotation", "scale", "opacity", "emission_strength", "emission_color"];
    let mut tracks = vec![];
    for (i, s) in series.into_iter().enumerate() {
        for (c, values) in s.into_iter().enumerate() {
            // A constant channel needs no track, except an object that is
            // hidden the whole time, which must still be hidden.
            let hidden = c == 3 && values[0][0] < 0.999;
            if values.iter().all(|v| close(v, &values[0])) && !hidden {
                continue;
            }
            // Opacity and glow only matter where there is a surface.
            if c >= 3 && rig.nodes[i].mesh.is_none() {
                continue;
            }
            let keep = thin(&values);
            tracks.push(Track {
                node: rig.nodes[i].name.clone(),
                path: paths[c],
                frames: keep.iter().map(|f| *f as u32).collect(),
                values: keep.iter().map(|f| values[*f].clone()).collect(),
            });
        }
    }
    let keep = thin(&cam);
    let camera = CameraTrack {
        frames: keep.iter().map(|f| *f as u32).collect(),
        position: keep.iter().map(|f| [cam[*f][0], cam[*f][1], cam[*f][2]]).collect(),
        rotation: keep.iter().map(|f| [cam[*f][3], cam[*f][4], cam[*f][5], cam[*f][6]]).collect(),
        fov: keep.iter().map(|f| cam[*f][7]).collect(),
    };
    let nodes = rig
        .nodes
        .iter()
        .enumerate()
        .map(|(i, nd)| NodeOut {
            name: nd.name.clone(),
            parent: nd.parent.map(|p| rig.nodes[p].name.clone()),
            mesh: nd.mesh.map(|m| rig.meshes[m].0.clone()),
            material: nd.material.map(|m| rig.materials[m].name.clone()),
            translation: rest.local[i].t,
            rotation: rest.local[i].r,
            scale: rest.local[i].s,
        })
        .collect();
    (tracks, camera, nodes)
}

pub fn timeline_file(scene: &Scene, rig: &Rig, tl: &Timeline, tracks: Vec<Track>, camera: CameraTrack, nodes: Vec<NodeOut>) -> TimelineFile {
    let preset = match scene.environment.preset {
        EnvPreset::DarkStudio => "dark_studio",
        EnvPreset::Studio => "studio",
        EnvPreset::Black => "black",
    };
    TimelineFile {
        format: "vivaran-studio-timeline/1",
        title: scene.title.clone(),
        width: scene.canvas.width,
        height: scene.canvas.height,
        fps: scene.canvas.fps,
        samples: scene.canvas.samples,
        frames: tl.frames,
        seconds: tl.seconds,
        environment: json!({ "preset": preset, "background": rig.background, "strength": rig.env_strength,
                             "reflection_top": rig.reflection_top, "reflection_bottom": rig.reflection_bottom }),
        lights: rig.lights.clone(),
        materials: rig
            .materials
            .iter()
            .map(|m| {
                json!({ "name": m.name, "base": m.base, "metallic": m.metallic, "roughness": m.roughness, "emission": m.emission,
                        "strength": m.strength, "transmission": m.transmission, "ior": m.ior, "opacity": m.opacity })
            })
            .collect(),
        nodes,
        steps: tl.steps.clone(),
        tracks,
        camera,
    }
}

// ------------------------------------------------------------------ glTF

fn y_up(v: V3) -> V3 {
    [v[0], v[2], -v[1]]
}
/// (w, x, y, z) z-up to glTF's (x, y, z, w) y-up.
fn y_up_quat(q: &[f32]) -> [f32; 4] {
    [q[1], q[3], -q[2], q[0]]
}
fn y_up_scale(s: &[f32]) -> V3 {
    [s[0], s[2], s[1]]
}

struct Bin {
    data: Vec<u8>,
    views: Vec<Value>,
    accessors: Vec<Value>,
}

impl Bin {
    fn align(&mut self) {
        while !self.data.len().is_multiple_of(4) {
            self.data.push(0);
        }
    }

    /// Append floats as one accessor; returns its index.
    fn floats(&mut self, values: &[f32], kind: &str, width: usize, target: Option<u32>, bounds: bool) -> usize {
        self.align();
        let offset = self.data.len();
        for v in values {
            self.data.extend_from_slice(&v.to_le_bytes());
        }
        let mut view = json!({ "buffer": 0, "byteOffset": offset, "byteLength": values.len() * 4 });
        if let Some(t) = target {
            view["target"] = json!(t);
        }
        self.views.push(view);
        let mut acc = json!({ "bufferView": self.views.len() - 1, "componentType": 5126, "count": values.len() / width, "type": kind });
        if bounds {
            let mut lo = vec![f32::INFINITY; width];
            let mut hi = vec![f32::NEG_INFINITY; width];
            for chunk in values.chunks(width) {
                for k in 0..width {
                    lo[k] = lo[k].min(chunk[k]);
                    hi[k] = hi[k].max(chunk[k]);
                }
            }
            acc["min"] = json!(lo);
            acc["max"] = json!(hi);
        }
        self.accessors.push(acc);
        self.accessors.len() - 1
    }

    fn indices(&mut self, values: &[u32]) -> usize {
        self.align();
        let offset = self.data.len();
        for v in values {
            self.data.extend_from_slice(&v.to_le_bytes());
        }
        self.views.push(json!({ "buffer": 0, "byteOffset": offset, "byteLength": values.len() * 4, "target": 34963 }));
        self.accessors.push(json!({ "bufferView": self.views.len() - 1, "componentType": 5125, "count": values.len(), "type": "SCALAR" }));
        self.accessors.len() - 1
    }
}

/// The scene as a binary glTF file.
pub fn glb(scene: &Scene, rig: &Rig, tl: &Timeline, tracks: &[Track], camera: &CameraTrack, nodes: &[NodeOut]) -> Vec<u8> {
    let mut bin = Bin { data: vec![], views: vec![], accessors: vec![] };

    let materials: Vec<Value> = rig
        .materials
        .iter()
        .map(|m| {
            let peak = m.emission.iter().cloned().fold(0.0f32, f32::max);
            let (emissive, strength) = if peak > 0.0 && m.strength > 0.0 { ([m.emission[0] / peak, m.emission[1] / peak, m.emission[2] / peak], m.strength * peak) } else { ([0.0; 3], 0.0) };
            let mut mat = json!({
                "name": m.name,
                "pbrMetallicRoughness": { "baseColorFactor": [m.base[0], m.base[1], m.base[2], m.opacity], "metallicFactor": m.metallic, "roughnessFactor": m.roughness },
                "emissiveFactor": emissive,
                "doubleSided": true,
                "extensions": {}
            });
            if strength > 1.0 {
                mat["extensions"]["KHR_materials_emissive_strength"] = json!({ "emissiveStrength": strength });
            }
            if m.transmission > 0.0 {
                mat["extensions"]["KHR_materials_transmission"] = json!({ "transmissionFactor": m.transmission });
            }
            if (m.ior - 1.5).abs() > 1e-4 {
                mat["extensions"]["KHR_materials_ior"] = json!({ "ior": m.ior });
            }
            if m.opacity < 1.0 {
                mat["alphaMode"] = json!("BLEND");
            }
            mat
        })
        .collect();

    let meshes: Vec<Value> = rig
        .meshes
        .iter()
        .map(|(name, mesh)| {
            let positions: Vec<f32> = mesh.positions.iter().flat_map(|p| y_up(*p)).collect();
            let normals: Vec<f32> = mesh.normals.iter().flat_map(|p| y_up(*p)).collect();
            let pos = bin.floats(&positions, "VEC3", 3, Some(34962), true);
            let nor = bin.floats(&normals, "VEC3", 3, Some(34962), false);
            let idx = bin.indices(&mesh.indices);
            let material = rig.nodes.iter().find(|n| n.mesh.is_some() && rig.meshes[n.mesh.unwrap()].0 == *name).and_then(|n| n.material);
            let mut prim = json!({ "attributes": { "POSITION": pos, "NORMAL": nor }, "indices": idx, "mode": 4 });
            if let Some(m) = material {
                prim["material"] = json!(m);
            }
            json!({ "name": name, "primitives": [prim] })
        })
        .collect();

    let mut gnodes: Vec<Value> = nodes
        .iter()
        .enumerate()
        .map(|(i, nd)| {
            let mut node = json!({
                "name": nd.name,
                "translation": y_up(nd.translation),
                "rotation": y_up_quat(&nd.rotation),
                "scale": y_up_scale(&nd.scale),
            });
            if let Some(m) = rig.nodes[i].mesh {
                node["mesh"] = json!(m);
            }
            let children: Vec<usize> = rig.nodes[i].children.clone();
            if !children.is_empty() {
                node["children"] = json!(children);
            }
            node
        })
        .collect();
    let camera_node = gnodes.len();
    gnodes.push(json!({
        "name": "camera",
        "camera": 0,
        "translation": y_up(camera.position[0]),
        "rotation": y_up_quat(&camera.rotation[0]),
    }));
    let roots: Vec<usize> = rig.nodes.iter().enumerate().filter(|(_, n)| n.parent.is_none()).map(|(i, _)| i).chain([camera_node]).collect();

    // Transform animation, plus the camera move, for previews.
    let fps = tl.fps as f32;
    let mut samplers = vec![];
    let mut channels = vec![];
    let mut push = |bin: &mut Bin, frames: &[u32], values: Vec<f32>, kind: &str, width: usize, node: usize, path: &str| {
        let times: Vec<f32> = frames.iter().map(|f| *f as f32 / fps).collect();
        let input = bin.floats(&times, "SCALAR", 1, None, true);
        let output = bin.floats(&values, kind, width, None, false);
        samplers.push(json!({ "input": input, "output": output, "interpolation": "LINEAR" }));
        channels.push(json!({ "sampler": samplers.len() - 1, "target": { "node": node, "path": path } }));
    };
    for t in tracks {
        let Some(node) = rig.nodes.iter().position(|n| n.name == t.node) else { continue };
        match t.path {
            "translation" => push(&mut bin, &t.frames, t.values.iter().flat_map(|v| y_up([v[0], v[1], v[2]])).collect(), "VEC3", 3, node, "translation"),
            "rotation" => push(&mut bin, &t.frames, t.values.iter().flat_map(|v| y_up_quat(v)).collect(), "VEC4", 4, node, "rotation"),
            "scale" => push(&mut bin, &t.frames, t.values.iter().flat_map(|v| y_up_scale(v)).collect(), "VEC3", 3, node, "scale"),
            _ => {}
        }
    }
    if camera.frames.len() > 1 {
        push(&mut bin, &camera.frames, camera.position.iter().flat_map(|p| y_up(*p)).collect(), "VEC3", 3, camera_node, "translation");
        push(&mut bin, &camera.frames, camera.rotation.iter().flat_map(|q| y_up_quat(q)).collect(), "VEC4", 4, camera_node, "rotation");
    }
    bin.align();

    let mut doc = json!({
        "asset": { "version": "2.0", "generator": "Vivaran Studio (cevg-studio)" },
        "extensionsUsed": ["KHR_materials_emissive_strength", "KHR_materials_transmission", "KHR_materials_ior"],
        "scene": 0,
        "scenes": [ { "name": scene.title, "nodes": roots } ],
        "nodes": gnodes,
        "meshes": meshes,
        "materials": materials,
        "cameras": [ { "type": "perspective", "perspective": {
            "yfov": scene.camera.fov.to_radians(),
            "aspectRatio": scene.canvas.width as f32 / scene.canvas.height as f32,
            "znear": 0.05, "zfar": 2000.0 } } ],
        "accessors": bin.accessors,
        "bufferViews": bin.views,
        "buffers": [ { "byteLength": bin.data.len() } ],
    });
    if !channels.is_empty() {
        doc["animations"] = json!([ { "name": "timeline", "samplers": samplers, "channels": channels } ]);
    }

    let mut json_bytes = serde_json::to_vec(&doc).expect("json");
    while !json_bytes.len().is_multiple_of(4) {
        json_bytes.push(b' ');
    }
    let total = 12 + 8 + json_bytes.len() + 8 + bin.data.len();
    let mut out = Vec::with_capacity(total);
    out.extend_from_slice(b"glTF");
    out.extend_from_slice(&2u32.to_le_bytes());
    out.extend_from_slice(&(total as u32).to_le_bytes());
    out.extend_from_slice(&(json_bytes.len() as u32).to_le_bytes());
    out.extend_from_slice(b"JSON");
    out.extend_from_slice(&json_bytes);
    out.extend_from_slice(&(bin.data.len() as u32).to_le_bytes());
    out.extend_from_slice(b"BIN\0");
    out.extend_from_slice(&bin.data);
    out
}
