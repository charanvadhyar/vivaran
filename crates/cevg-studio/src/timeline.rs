//! Time: when each step plays, what every action does to every node, and
//! the pose of the whole scene at any frame.
//!
//! Actions follow the CEVG rule: each one stretches from its delay to the
//! end of its step's narration, easing in and out. The scene is replayed
//! once, action by action; each action records what it changed as
//! segments (a channel, a time span, a change). The value of a channel at
//! any time is its starting value plus each segment's change scaled by how
//! far that segment has got, so overlapping actions do not disturb one
//! another and every step ends on an exact state.

use crate::mesh::{add, length, scale, sub, V3};
use crate::rig::{apply_chain, corners, look_at, quat_axis, quat_euler, quat_mul, world_transforms, Quat, Rig, Trs};
use crate::scene::{hex, ActionKind, Scene};
use cevg_core::space3d::Camera;

/// Pause after each step's narration, seconds.
pub const HOLD: f32 = 0.35;
/// A little time at the very end so the last frame is not cut short.
pub const TAIL: f32 = 0.6;
const AMBER: &str = "#f5b83d";

fn ease(p: f32) -> f32 {
    let p = p.clamp(0.0, 1.0);
    if p < 0.5 { 4.0 * p * p * p } else { 1.0 - (-2.0 * p + 2.0).powi(3) / 2.0 }
}

/// Narration lengths guessed from the English text: about 2.6 words a
/// second, at least 1.5 seconds.
pub fn estimate_speech(scene: &Scene) -> Vec<f32> {
    scene
        .scenes
        .iter()
        .flat_map(|s| s.steps.iter())
        .map(|step| {
            let words = step.say.get("en").map_or(0, |t| t.split_whitespace().count());
            (words as f32 / 2.6).max(1.5)
        })
        .collect()
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Channel {
    Translate(usize),
    Rotate(usize),
    Scale(usize),
    Opacity(usize),
    Glow(usize),
    GlowColor(usize),
    Label(usize),
    Camera,
}

#[derive(Debug, Clone)]
struct Segment {
    channel: Channel,
    start: f32,
    end: f32,
    delta: [f32; 7],
}

#[derive(Debug, Clone)]
struct Spin {
    node: usize,
    axis: usize,
    degrees_per_second: f32,
    start: f32,
    stop: f32,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct StepTime {
    pub section: String,
    pub index: usize,
    pub start: f32,
    pub end: f32,
    pub say: std::collections::BTreeMap<String, String>,
}

/// What can change, per node, plus the camera.
#[derive(Debug, Clone)]
struct State {
    t: Vec<V3>,
    r: Vec<V3>,
    s: Vec<V3>,
    opacity: Vec<f32>,
    glow: Vec<f32>,
    glow_color: Vec<V3>,
    label: Vec<f32>,
    camera: [f32; 7],
}

pub struct Timeline {
    pub fps: u32,
    pub frames: usize,
    pub seconds: f32,
    pub steps: Vec<StepTime>,
    start: State,
    segments: Vec<Segment>,
    spins: Vec<Spin>,
    /// Callout text per node, as (from time, text), latest last.
    texts: Vec<Vec<(f32, String)>>,
}

/// Everything about the scene at one moment.
#[derive(Debug, Clone)]
pub struct Pose {
    pub local: Vec<Trs>,
    pub opacity: Vec<f32>,
    pub glow: Vec<f32>,
    pub glow_color: Vec<V3>,
    /// Callout opacity and text per node.
    pub labels: Vec<(f32, String)>,
    pub camera: Camera,
}

fn camera_numbers(c: &Camera) -> [f32; 7] {
    c.numbers()
}

impl Timeline {
    pub fn build(scene: &Scene, rig: &Rig, speech: Option<&[f32]>) -> Result<Timeline, String> {
        let estimated = estimate_speech(scene);
        let speech: Vec<f32> = match speech {
            Some(s) if s.len() == estimated.len() => s.to_vec(),
            Some(s) => return Err(format!("{} narration lengths given for {} steps", s.len(), estimated.len())),
            None => estimated,
        };
        let n = rig.nodes.len();
        let cam = &scene.camera;
        let camera = Camera { azimuth: cam.azimuth, elevation: cam.elevation, distance: cam.distance, target: cam.target, fov: cam.fov };
        let mut state = State {
            t: vec![[0.0; 3]; n],
            r: vec![[0.0; 3]; n],
            s: vec![[1.0; 3]; n],
            opacity: rig.nodes.iter().map(|nd| if nd.visible { 1.0 } else { 0.0 }).collect(),
            glow: rig.nodes.iter().map(|nd| nd.material.map_or(0.0, |m| rig.materials[m].strength)).collect(),
            glow_color: rig.nodes.iter().map(|nd| nd.material.map_or([0.0; 3], |m| rig.materials[m].emission)).collect(),
            label: vec![0.0; n],
            camera: camera_numbers(&camera),
        };
        let start_state = state.clone();
        let mut segments = vec![];
        let mut spins: Vec<Spin> = vec![];
        let mut texts: Vec<Vec<(f32, String)>> = vec![vec![]; n];
        let mut steps = vec![];
        let mut clock = 0.0f32;
        let mut flat = 0;
        for section in &scene.scenes {
            for (index, step) in section.steps.iter().enumerate() {
                let len = speech[flat];
                flat += 1;
                steps.push(StepTime { section: section.id.clone(), index, start: clock, end: clock + len, say: step.say.clone() });
                for action in &step.actions {
                    let t0 = clock + action.delay * len;
                    let t1 = (clock + len).max(t0 + 0.05);
                    let before = state.clone();
                    apply(scene, rig, &mut state, &action.kind, t0, &mut spins, &mut texts, &mut segments, t1)?;
                    diff(&before, &state, t0, t1, &mut segments);
                }
                clock += len + HOLD;
            }
        }
        let seconds = clock + TAIL;
        for spin in &mut spins {
            if spin.stop.is_infinite() {
                spin.stop = seconds;
            }
        }
        let frames = (seconds * scene.canvas.fps as f32).ceil() as usize;
        Ok(Timeline { fps: scene.canvas.fps, frames, seconds, steps, start: start_state, segments, spins, texts })
    }

    /// The scene at `time` seconds.
    pub fn pose(&self, rig: &Rig, time: f32) -> Pose {
        let mut s = self.start.clone();
        for seg in &self.segments {
            if time < seg.start {
                continue;
            }
            let p = if seg.end <= seg.start { 1.0 } else { ease((time - seg.start) / (seg.end - seg.start)) };
            let d = &seg.delta;
            let add3 = |v: &mut V3| {
                v[0] += p * d[0];
                v[1] += p * d[1];
                v[2] += p * d[2];
            };
            match seg.channel {
                Channel::Translate(i) => add3(&mut s.t[i]),
                Channel::Rotate(i) => add3(&mut s.r[i]),
                Channel::Scale(i) => add3(&mut s.s[i]),
                Channel::GlowColor(i) => add3(&mut s.glow_color[i]),
                Channel::Opacity(i) => s.opacity[i] += p * d[0],
                Channel::Glow(i) => s.glow[i] += p * d[0],
                Channel::Label(i) => s.label[i] += p * d[0],
                Channel::Camera => (0..7).for_each(|k| s.camera[k] += p * d[k]),
            }
        }
        let local: Vec<Trs> = rig
            .nodes
            .iter()
            .enumerate()
            .map(|(i, nd)| {
                let mut r = quat_euler(add(nd.base_r, s.r[i]));
                for spin in self.spins.iter().filter(|sp| sp.node == i && time > sp.start) {
                    let angle = spin.degrees_per_second * (time.min(spin.stop) - spin.start);
                    r = quat_mul(r, quat_axis(spin.axis, angle));
                }
                let sc = [nd.base_s[0] * s.s[i][0], nd.base_s[1] * s.s[i][1], nd.base_s[2] * s.s[i][2]];
                Trs { t: add(nd.base_t, s.t[i]), r, s: sc }
            })
            .collect();
        let labels = (0..rig.nodes.len())
            .map(|i| {
                let text = self.texts[i].iter().rev().find(|(t, _)| *t <= time).map(|(_, x)| x.clone()).unwrap_or_default();
                (s.label[i].clamp(0.0, 1.0), text)
            })
            .collect();
        Pose {
            local,
            opacity: s.opacity.iter().map(|o| o.clamp(0.0, 1.0)).collect(),
            glow: s.glow.iter().map(|g| g.max(0.0)).collect(),
            glow_color: s.glow_color,
            labels,
            camera: Camera::from_numbers(&s.camera),
        }
    }

    pub fn pose_at_frame(&self, rig: &Rig, frame: usize) -> Pose {
        self.pose(rig, frame as f32 / self.fps as f32)
    }
}

/// World-space bounding box of a node and everything under it, at a pose.
pub fn world_bounds(rig: &Rig, local: &[Trs], node: usize) -> Option<(V3, V3)> {
    let world = world_transforms(&rig.nodes, local);
    let mut lo = [f32::INFINITY; 3];
    let mut hi = [f32::NEG_INFINITY; 3];
    for i in rig.subtree(node) {
        if let Some(m) = rig.nodes[i].mesh {
            for p in corners(rig.meshes[m].1.bounds()) {
                let w = apply_chain(&world[i], p);
                for k in 0..3 {
                    lo[k] = lo[k].min(w[k]);
                    hi[k] = hi[k].max(w[k]);
                }
            }
        }
    }
    lo[0].is_finite().then_some((lo, hi))
}

/// The camera's position and orientation (local -z forward, y up).
pub fn camera_transform(c: &Camera) -> (V3, Quat) {
    let view = c.view();
    (view.eye, look_at(view.eye, add(view.eye, view.forward)))
}

/// Record what changed between two states as segments over [t0, t1].
fn diff(a: &State, b: &State, t0: f32, t1: f32, out: &mut Vec<Segment>) {
    let eps = 1e-6;
    let seg = |channel: Channel, d: [f32; 7]| Segment { channel, start: t0, end: t1, delta: d };
    let v3 = |x: V3, y: V3| [y[0] - x[0], y[1] - x[1], y[2] - x[2], 0.0, 0.0, 0.0, 0.0];
    let changed = |d: &[f32; 7]| d.iter().any(|v| v.abs() > eps);
    for i in 0..a.t.len() {
        for (ch, d) in [
            (Channel::Translate(i), v3(a.t[i], b.t[i])),
            (Channel::Rotate(i), v3(a.r[i], b.r[i])),
            (Channel::Scale(i), v3(a.s[i], b.s[i])),
            (Channel::GlowColor(i), v3(a.glow_color[i], b.glow_color[i])),
            (Channel::Opacity(i), [b.opacity[i] - a.opacity[i], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            (Channel::Glow(i), [b.glow[i] - a.glow[i], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ] {
            if changed(&d) {
                out.push(seg(ch, d));
            }
        }
        let dl = b.label[i] - a.label[i];
        if dl.abs() > eps {
            // Callouts fade quickly rather than over the whole step.
            out.push(Segment { channel: Channel::Label(i), start: t0, end: t0 + (t1 - t0).min(0.5), delta: [dl, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] });
        }
    }
    let dc: [f32; 7] = std::array::from_fn(|k| b.camera[k] - a.camera[k]);
    if changed(&dc) {
        out.push(seg(Channel::Camera, dc));
    }
}

#[allow(clippy::too_many_arguments)]
fn apply(
    scene: &Scene,
    rig: &Rig,
    s: &mut State,
    action: &ActionKind,
    t0: f32,
    spins: &mut Vec<Spin>,
    texts: &mut [Vec<(f32, String)>],
    segments: &mut Vec<Segment>,
    t1: f32,
) -> Result<(), String> {
    let node = |target: &str| rig.node_of(scene, target).ok_or_else(|| format!("unknown target `{target}`"));
    let material_of = |i: usize| rig.nodes[i].material.map(|m| &rig.materials[m]);
    match action {
        ActionKind::Show { target, from } | ActionKind::Hide { target, to: from } => {
            let show = matches!(action, ActionKind::Show { .. });
            let i = node(target)?;
            for j in rig.subtree(i) {
                s.opacity[j] = if show { 1.0 } else { 0.0 };
            }
            if let Some(offset) = from {
                if show {
                    // Jump out to the offset at once (it is still invisible),
                    // then glide home as it fades in. The net change is nil,
                    // so these two segments are recorded here, not by `diff`.
                    let d = |k: f32| [k * offset[0], k * offset[1], k * offset[2], 0.0, 0.0, 0.0, 0.0];
                    segments.push(Segment { channel: Channel::Translate(i), start: t0, end: t0, delta: d(1.0) });
                    segments.push(Segment { channel: Channel::Translate(i), start: t0, end: t1, delta: d(-1.0) });
                } else {
                    s.t[i] = add(s.t[i], *offset);
                }
            }
        }
        ActionKind::Move { target, to, by } => {
            let i = node(target)?;
            let nd = &rig.nodes[i];
            s.t[i] = match (to, by) {
                (Some(to), _) => sub(*to, nd.base_t),
                (None, Some(by)) => add(s.t[i], *by),
                _ => s.t[i],
            };
        }
        ActionKind::Rotate { target, to, by } => {
            let i = node(target)?;
            let nd = &rig.nodes[i];
            s.r[i] = match (to, by) {
                (Some(to), _) => sub(*to, nd.base_r),
                (None, Some(by)) => add(s.r[i], *by),
                _ => s.r[i],
            };
        }
        ActionKind::Spin { target, axis, rpm } => {
            let i = node(target)?;
            spins.push(Spin { node: i, axis: axis.index(), degrees_per_second: rpm * 6.0, start: t0, stop: f32::INFINITY });
        }
        ActionKind::Stop { target } => {
            let i = node(target)?;
            for spin in spins.iter_mut().filter(|sp| sp.node == i && sp.stop.is_infinite()) {
                spin.stop = t0;
            }
        }
        ActionKind::Explode { target, .. } | ActionKind::Assemble { target } => {
            let distance = if let ActionKind::Explode { distance, .. } = action { *distance } else { 0.0 };
            let i = node(target)?;
            let children = rig.nodes[i].children.clone();
            if children.is_empty() {
                // A single part moves along its own direction.
                let dir = scene.parts[rig.nodes[i].part].explode.unwrap_or([0.0, 0.0, 1.0]);
                s.t[i] = scale(crate::mesh::normalize(dir), distance);
            } else {
                for (k, c) in children.into_iter().enumerate() {
                    let nd = &rig.nodes[c];
                    let own = scene.parts[nd.part].explode.filter(|_| nd.spread.is_none());
                    let dir = match (nd.spread, own) {
                        (Some(spread), _) => spread,
                        (None, Some(d)) => crate::mesh::normalize(d),
                        (None, None) if length(nd.base_t) > 1e-6 => crate::mesh::normalize(nd.base_t),
                        (None, None) => [0.0, 0.0, (k + 1) as f32],
                    };
                    s.t[c] = scale(dir, distance);
                }
            }
        }
        ActionKind::Glow { target, strength, color } => {
            let i = node(target)?;
            for j in rig.subtree(i) {
                if let Some(m) = material_of(j) {
                    s.glow[j] = *strength;
                    s.glow_color[j] = match color.as_deref().and_then(hex) {
                        Some(c) => c,
                        None if m.emission != [0.0; 3] => m.emission,
                        None => m.base,
                    };
                }
            }
        }
        ActionKind::Highlight { target } => {
            let i = node(target)?;
            for j in rig.subtree(i) {
                if material_of(j).is_some() {
                    s.glow[j] = 0.9;
                    s.glow_color[j] = hex(AMBER).expect("colour");
                }
            }
        }
        ActionKind::Reset { target } => {
            let i = node(target)?;
            for j in rig.subtree(i) {
                if let Some(m) = material_of(j) {
                    s.glow[j] = m.strength;
                    s.glow_color[j] = m.emission;
                }
            }
        }
        ActionKind::Camera { azimuth, elevation, distance, target, fov } => {
            let c = &mut s.camera;
            if let Some(a) = azimuth {
                c[0] = *a;
            }
            if let Some(e) = elevation {
                c[1] = e.clamp(-89.0, 89.0);
            }
            if let Some(d) = distance {
                c[2] = d.max(0.05);
            }
            if let Some(t) = target {
                c[3..6].copy_from_slice(t);
            }
            if let Some(f) = fov {
                c[6] = *f;
            }
        }
        ActionKind::Focus { target, distance } => {
            let i = node(target)?;
            let local: Vec<Trs> = rig
                .nodes
                .iter()
                .enumerate()
                .map(|(j, nd)| Trs { t: add(nd.base_t, s.t[j]), r: quat_euler(add(nd.base_r, s.r[j])), s: nd.base_s })
                .collect();
            if let Some((lo, hi)) = world_bounds(rig, &local, i) {
                let centre = scale(add(lo, hi), 0.5);
                let radius = 0.5 * length(sub(hi, lo));
                let fov = s.camera[6].to_radians();
                s.camera[3..6].copy_from_slice(&centre);
                s.camera[2] = distance.unwrap_or(radius / (fov / 2.0).tan() * 1.25).max(0.05);
            }
        }
        ActionKind::Label { target, text } => {
            let i = node(target)?;
            let part = &scene.parts[rig.nodes[i].part];
            let words = text.clone().or_else(|| part.label.clone()).unwrap_or_else(|| part.id.clone());
            texts[i].push((t0, words));
            s.label[i] = 1.0;
        }
        ActionKind::Unlabel { target } => {
            let i = node(target)?;
            s.label[i] = 0.0;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scene(json: &str) -> Scene {
        serde_json::from_str(json).unwrap()
    }

    const BASE: &str = r#"{
      "version": 1, "title": "t",
      "materials": { "steel": { "preset": "steel" } },
      "parts": [
        { "id": "hub", "shape": { "kind": "cylinder", "radius": 0.5, "height": 0.2 }, "material": "steel" },
        { "id": "blade", "shape": { "kind": "box", "size": [1, 0.1, 0.05] }, "material": "steel", "parent": "hub",
          "at": [0.8, 0, 0], "array": { "kind": "radial", "count": 4 } }
      ],
      "scenes": [ { "id": "s", "steps": [
        { "say": { "en": "Pull it apart." }, "do": [ { "action": "explode", "target": "blade", "distance": 1 } ] },
        { "say": { "en": "Spin it." }, "do": [ { "action": "spin", "target": "hub", "rpm": 60 }, { "action": "camera", "azimuth": 90 } ] }
      ] } ]
    }"#;

    #[test]
    fn explode_moves_copies_outward_and_steps_end_exactly() {
        let sc = scene(BASE);
        assert!(sc.check().is_empty(), "{:?}", sc.check());
        let rig = Rig::build(&sc);
        let tl = Timeline::build(&sc, &rig, Some(&[2.0, 2.0])).unwrap();
        let copy = rig.node_of(&sc, "blade[1]").unwrap();
        let before = tl.pose(&rig, 0.0).local[copy].t;
        let after = tl.pose(&rig, 2.0).local[copy].t;
        // Copy 1 of 4 is at 90 degrees: it moves along +y by the distance.
        assert!((after[1] - before[1] - 1.0).abs() < 1e-4, "{before:?} -> {after:?}");
        let mid = tl.pose(&rig, 1.0).local[copy].t;
        assert!(mid[1] > before[1] && mid[1] < after[1]);
    }

    #[test]
    fn spin_turns_at_the_given_speed_and_the_camera_glides() {
        let sc = scene(BASE);
        let rig = Rig::build(&sc);
        let tl = Timeline::build(&sc, &rig, Some(&[2.0, 2.0])).unwrap();
        let hub = rig.node_of(&sc, "hub").unwrap();
        // Step 2 starts at 2.35 s; 60 rpm is a turn a second, so a quarter
        // second later the hub has turned 90 degrees about z.
        let p = tl.pose(&rig, 2.6);
        let x = crate::rig::quat_rotate(p.local[hub].r, [1.0, 0.0, 0.0]);
        assert!(x[1] > 0.99, "turned to +y: {x:?}");
        assert!((tl.pose(&rig, 4.35).camera.azimuth - 90.0).abs() < 1e-3);
        assert!((tl.pose(&rig, 0.0).camera.azimuth - 35.0).abs() < 1e-3);
    }
}
