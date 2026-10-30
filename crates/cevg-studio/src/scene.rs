//! The studio scene: the JSON document the assistant writes for a 3D video.
//!
//! It has the same narration model as a CEVG script (scenes of steps, each
//! step a sentence and the actions that play while it is spoken) but its
//! objects are physical parts: parametric shapes with real materials, lit
//! and filmed by a camera. Units are metres; `z` is up.
//!
//! Unknown fields are rejected everywhere, so a typo is an error.

use crate::mesh::{Shape, V3};
use serde::de::{self, DeserializeOwned};
use serde::{Deserialize, Deserializer};
use serde_json::{Map, Value};
use std::collections::BTreeMap;

pub const SUPPORTED_VERSION: u32 = 1;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    pub version: u32,
    pub title: String,
    #[serde(default)]
    pub canvas: Canvas,
    #[serde(default)]
    pub environment: Environment,
    #[serde(default)]
    pub materials: BTreeMap<String, MaterialSpec>,
    pub parts: Vec<Part>,
    /// Without lights, the environment's own rig lights the scene.
    #[serde(default)]
    pub lights: Vec<LightSpec>,
    #[serde(default)]
    pub camera: CameraSpec,
    pub scenes: Vec<Section>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct Canvas {
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    /// Light paths per pixel. More is cleaner and slower; the denoiser
    /// does the rest. 64 to 256 is the useful range.
    pub samples: u32,
}

impl Default for Canvas {
    fn default() -> Self {
        Canvas { width: 1920, height: 1080, fps: 30, samples: 128 }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EnvPreset {
    /// Near-black background, a warm key, a cool rim and a soft fill: the
    /// look of an engineering teardown, where glowing parts read best.
    #[default]
    DarkStudio,
    /// A light grey studio with soft, even light.
    Studio,
    /// Pure black, lit only by the scene's own lights and glowing parts.
    Black,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct Environment {
    pub preset: EnvPreset,
    /// Multiplies the rig's light.
    pub strength: f32,
    /// Background colour, `#rrggbb`. Each preset has its own.
    pub background: Option<String>,
}

impl Default for Environment {
    fn default() -> Self {
        Environment { preset: EnvPreset::DarkStudio, strength: 1.0, background: None }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Preset {
    Steel,
    BrushedSteel,
    Aluminium,
    Copper,
    Brass,
    Gold,
    Chrome,
    Titanium,
    Plastic,
    Rubber,
    Ceramic,
    Paint,
    Glass,
    /// A surface that gives off light: plasma, filaments, LEDs.
    Emissive,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MaterialSpec {
    pub preset: Preset,
    /// Base colour, `#rrggbb`.
    #[serde(default)]
    pub color: Option<String>,
    #[serde(default)]
    pub metallic: Option<f32>,
    #[serde(default)]
    pub roughness: Option<f32>,
    /// Colour of emitted light, `#rrggbb`.
    #[serde(default)]
    pub emission: Option<String>,
    /// Brightness of emitted light. 1 is a faint glow, 20 to 50 is plasma.
    #[serde(default)]
    pub strength: Option<f32>,
    #[serde(default)]
    pub transmission: Option<f32>,
    #[serde(default)]
    pub ior: Option<f32>,
    #[serde(default)]
    pub opacity: Option<f32>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Axis {
    X,
    Y,
    #[default]
    Z,
}

impl Axis {
    pub fn index(self) -> usize {
        match self {
            Axis::X => 0,
            Axis::Y => 1,
            Axis::Z => 2,
        }
    }
}

fn full() -> f32 {
    360.0
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum ArraySpec {
    /// `count` copies turned about an axis through the part's origin. A full
    /// circle spaces them evenly; a partial `angle` puts the first at
    /// `start` and the last at `start + angle`.
    Radial {
        count: u32,
        #[serde(default)]
        axis: Axis,
        #[serde(default = "full")]
        angle: f32,
        #[serde(default)]
        start: f32,
    },
    /// `count` copies, each `step` further on.
    Linear { count: u32, step: V3 },
}

impl ArraySpec {
    pub fn count(&self) -> u32 {
        match self {
            ArraySpec::Radial { count, .. } | ArraySpec::Linear { count, .. } => *count,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(untagged)]
pub enum ScaleSpec {
    Uniform(f32),
    Axes(V3),
}

impl Default for ScaleSpec {
    fn default() -> Self {
        ScaleSpec::Uniform(1.0)
    }
}

impl ScaleSpec {
    pub fn vector(self) -> V3 {
        match self {
            ScaleSpec::Uniform(s) => [s, s, s],
            ScaleSpec::Axes(v) => v,
        }
    }
}

fn yes() -> bool {
    true
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Part {
    pub id: String,
    /// What it is. Omit for an empty group that holds other parts.
    #[serde(default)]
    pub shape: Option<Shape>,
    /// A key of `materials`. Required with a shape.
    #[serde(default)]
    pub material: Option<String>,
    /// Position relative to the parent (or the world), metres.
    #[serde(default)]
    pub at: V3,
    /// Rotation in degrees about x, then y, then z.
    #[serde(default)]
    pub rotate: V3,
    #[serde(default)]
    pub scale: ScaleSpec,
    /// A part declared earlier that this one moves with.
    #[serde(default)]
    pub parent: Option<String>,
    #[serde(default)]
    pub array: Option<ArraySpec>,
    /// Which way this part moves when its parent is exploded.
    #[serde(default)]
    pub explode: Option<V3>,
    #[serde(default = "yes")]
    pub visible: bool,
    /// The name used when a callout points at it.
    #[serde(default)]
    pub label: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LightKind {
    /// A glowing rectangle: soft light with soft shadows.
    Area,
    Point,
    Spot,
    /// Parallel light from far away.
    Sun,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LightSpec {
    pub id: String,
    pub kind: LightKind,
    #[serde(default)]
    pub at: V3,
    /// What it points at (area, spot, sun). Default the origin.
    #[serde(default)]
    pub target: V3,
    /// Watts (area, point, spot) or W/m² (sun).
    pub power: f32,
    #[serde(default)]
    pub color: Option<String>,
    /// Side of an area light, metres.
    #[serde(default)]
    pub size: Option<f32>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct CameraSpec {
    pub azimuth: f32,
    pub elevation: f32,
    pub distance: f32,
    pub target: V3,
    pub fov: f32,
}

impl Default for CameraSpec {
    fn default() -> Self {
        CameraSpec { azimuth: 35.0, elevation: 22.0, distance: 8.0, target: [0.0; 3], fov: 35.0 }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Section {
    pub id: String,
    pub steps: Vec<Step>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Step {
    pub say: BTreeMap<String, String>,
    #[serde(default, rename = "do")]
    pub actions: Vec<Action>,
}

#[derive(Debug, Clone)]
pub struct Action {
    /// When the action starts, as a fraction of the step.
    pub delay: f32,
    pub kind: ActionKind,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case", deny_unknown_fields)]
pub enum ActionKind {
    /// Fade in. `from` slides it in from that offset as it appears.
    Show {
        target: String,
        #[serde(default)]
        from: Option<V3>,
    },
    /// Fade out. `to` slides it away by that offset as it goes.
    Hide {
        target: String,
        #[serde(default)]
        to: Option<V3>,
    },
    /// Move to a position (`to`, relative to the parent) or by an offset.
    Move {
        target: String,
        #[serde(default)]
        to: Option<V3>,
        #[serde(default)]
        by: Option<V3>,
    },
    /// Turn to a rotation (`to`, degrees) or by one.
    Rotate {
        target: String,
        #[serde(default)]
        to: Option<V3>,
        #[serde(default)]
        by: Option<V3>,
    },
    /// Keep turning about an axis at `rpm` until `stop`.
    Spin {
        target: String,
        #[serde(default)]
        axis: Axis,
        rpm: f32,
    },
    Stop { target: String },
    /// Pull a part's children (or an array's copies) apart by `distance`.
    Explode { target: String, distance: f32 },
    /// Put them back.
    Assemble { target: String },
    /// Light the part up: emission at `strength`, in its own colour or `color`.
    Glow {
        target: String,
        strength: f32,
        #[serde(default)]
        color: Option<String>,
    },
    /// The teaching highlight: an amber glow.
    Highlight { target: String },
    /// Back to the material's own emission.
    Reset { target: String },
    /// Move the camera: any of these, gliding over the step.
    Camera {
        #[serde(default)]
        azimuth: Option<f32>,
        #[serde(default)]
        elevation: Option<f32>,
        #[serde(default)]
        distance: Option<f32>,
        #[serde(default)]
        target: Option<V3>,
        #[serde(default)]
        fov: Option<f32>,
    },
    /// Aim the camera at a part and frame it.
    Focus {
        target: String,
        #[serde(default)]
        distance: Option<f32>,
    },
    /// A callout: a line from the part to its name.
    Label {
        target: String,
        #[serde(default)]
        text: Option<String>,
    },
    Unlabel { target: String },
}

impl ActionKind {
    pub fn name(&self) -> &'static str {
        match self {
            ActionKind::Show { .. } => "show",
            ActionKind::Hide { .. } => "hide",
            ActionKind::Move { .. } => "move",
            ActionKind::Rotate { .. } => "rotate",
            ActionKind::Spin { .. } => "spin",
            ActionKind::Stop { .. } => "stop",
            ActionKind::Explode { .. } => "explode",
            ActionKind::Assemble { .. } => "assemble",
            ActionKind::Glow { .. } => "glow",
            ActionKind::Highlight { .. } => "highlight",
            ActionKind::Reset { .. } => "reset",
            ActionKind::Camera { .. } => "camera",
            ActionKind::Focus { .. } => "focus",
            ActionKind::Label { .. } => "label",
            ActionKind::Unlabel { .. } => "unlabel",
        }
    }

    pub fn target(&self) -> Option<&str> {
        match self {
            ActionKind::Camera { .. } => None,
            ActionKind::Show { target, .. }
            | ActionKind::Hide { target, .. }
            | ActionKind::Move { target, .. }
            | ActionKind::Rotate { target, .. }
            | ActionKind::Spin { target, .. }
            | ActionKind::Stop { target }
            | ActionKind::Explode { target, .. }
            | ActionKind::Assemble { target }
            | ActionKind::Glow { target, .. }
            | ActionKind::Highlight { target }
            | ActionKind::Reset { target }
            | ActionKind::Focus { target, .. }
            | ActionKind::Label { target, .. }
            | ActionKind::Unlabel { target } => Some(target),
        }
    }
}

impl<'de> Deserialize<'de> for Action {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let mut map = Map::<String, Value>::deserialize(d)?;
        let delay = take(&mut map, "delay")?.unwrap_or(0.0);
        let kind = ActionKind::deserialize(Value::Object(map)).map_err(de::Error::custom)?;
        Ok(Action { delay, kind })
    }
}

fn take<T: DeserializeOwned, E: de::Error>(map: &mut Map<String, Value>, key: &str) -> Result<Option<T>, E> {
    match map.remove(key) {
        None => Ok(None),
        Some(v) => serde_json::from_value(v).map(Some).map_err(|e| E::custom(format!("{key}: {e}"))),
    }
}

// --------------------------------------------------------------- colours

/// `#rrggbb` to linear RGB, 0 to 1.
pub fn hex(s: &str) -> Option<[f32; 3]> {
    let s = s.strip_prefix('#')?;
    if s.len() != 6 {
        return None;
    }
    let byte = |i: usize| u8::from_str_radix(&s[i..i + 2], 16).ok();
    let to_linear = |c: u8| {
        let c = c as f32 / 255.0;
        if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }
    };
    Some([to_linear(byte(0)?), to_linear(byte(2)?), to_linear(byte(4)?)])
}

/// A material with every value filled in, linear colours.
#[derive(Debug, Clone, PartialEq)]
pub struct Material {
    pub name: String,
    pub base: [f32; 3],
    pub metallic: f32,
    pub roughness: f32,
    pub emission: [f32; 3],
    pub strength: f32,
    pub transmission: f32,
    pub ior: f32,
    pub opacity: f32,
}

impl MaterialSpec {
    pub fn resolve(&self, name: &str) -> Material {
        // Measured base colours of real metals (linear), and sensible
        // defaults for the rest.
        let (base, metallic, roughness) = match self.preset {
            Preset::Steel => ([0.56, 0.57, 0.58], 1.0, 0.32),
            Preset::BrushedSteel => ([0.56, 0.57, 0.58], 1.0, 0.45),
            Preset::Aluminium => ([0.91, 0.92, 0.92], 1.0, 0.3),
            Preset::Copper => ([0.955, 0.638, 0.538], 1.0, 0.25),
            Preset::Brass => ([0.91, 0.78, 0.42], 1.0, 0.25),
            Preset::Gold => ([1.0, 0.766, 0.336], 1.0, 0.18),
            Preset::Chrome => ([0.55, 0.556, 0.554], 1.0, 0.05),
            Preset::Titanium => ([0.542, 0.497, 0.449], 1.0, 0.3),
            Preset::Plastic => ([0.2, 0.2, 0.22], 0.0, 0.4),
            Preset::Rubber => ([0.02, 0.02, 0.02], 0.0, 0.85),
            Preset::Ceramic => ([0.8, 0.8, 0.78], 0.0, 0.2),
            Preset::Paint => ([0.5, 0.05, 0.05], 0.0, 0.35),
            Preset::Glass => ([1.0, 1.0, 1.0], 0.0, 0.02),
            Preset::Emissive => ([0.02, 0.02, 0.02], 0.0, 0.5),
        };
        let base = self.color.as_deref().and_then(hex).unwrap_or(base);
        let (emission, strength) = match (self.preset, &self.emission) {
            (_, Some(c)) => (hex(c).unwrap_or([1.0; 3]), self.strength.unwrap_or(10.0)),
            (Preset::Emissive, None) => (self.color.as_deref().and_then(hex).unwrap_or([1.0, 0.5, 0.9]), self.strength.unwrap_or(20.0)),
            _ => ([0.0; 3], 0.0),
        };
        Material {
            name: name.to_string(),
            base,
            metallic: self.metallic.unwrap_or(metallic),
            roughness: self.roughness.unwrap_or(roughness),
            emission,
            strength,
            transmission: self.transmission.unwrap_or(if self.preset == Preset::Glass { 1.0 } else { 0.0 }),
            ior: self.ior.unwrap_or(1.5),
            opacity: self.opacity.unwrap_or(1.0),
        }
    }
}

// ------------------------------------------------------------- validation

#[derive(Debug, Clone, serde::Serialize)]
pub struct Problem {
    pub path: String,
    pub message: String,
}

fn problem(out: &mut Vec<Problem>, path: impl Into<String>, message: impl Into<String>) {
    out.push(Problem { path: path.into(), message: message.into() });
}

fn valid_id(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
}

/// A target names a part (`coil`) or one copy of an array (`coil[3]`).
pub fn split_target(t: &str) -> (&str, Option<usize>) {
    if let Some(open) = t.find('[') {
        if let Some(index) = t[open + 1..].strip_suffix(']').and_then(|n| n.parse().ok()) {
            return (&t[..open], Some(index));
        }
    }
    (t, None)
}

impl Scene {
    /// Everything that can be checked without rendering: ids, references,
    /// shapes, colours, targets.
    pub fn check(&self) -> Vec<Problem> {
        let mut out = vec![];
        if self.version != SUPPORTED_VERSION {
            problem(&mut out, "version", format!("version {} is not supported; use {SUPPORTED_VERSION}", self.version));
        }
        let c = &self.canvas;
        if c.width < 16 || c.height < 16 || c.width > 7680 || c.height > 4320 || !c.width.is_multiple_of(2) || !c.height.is_multiple_of(2) {
            problem(&mut out, "canvas", "width and height must be even numbers between 16 and 7680 x 4320");
        }
        if !(1..=120).contains(&c.fps) {
            problem(&mut out, "canvas.fps", "fps must be between 1 and 120");
        }
        if !(1..=4096).contains(&c.samples) {
            problem(&mut out, "canvas.samples", "samples must be between 1 and 4096");
        }
        if let Some(b) = &self.environment.background {
            if hex(b).is_none() {
                problem(&mut out, "environment.background", format!("`{b}` is not a colour such as #10131c"));
            }
        }
        for (name, m) in &self.materials {
            let path = format!("materials.{name}");
            if !valid_id(name) {
                problem(&mut out, &path, "material names use only letters, digits and `_`");
            }
            for (field, value) in [("color", &m.color), ("emission", &m.emission)] {
                if let Some(v) = value {
                    if hex(v).is_none() {
                        problem(&mut out, format!("{path}.{field}"), format!("`{v}` is not a colour such as #ff8800"));
                    }
                }
            }
            for (field, value, lo, hi) in [
                ("metallic", m.metallic, 0.0, 1.0),
                ("roughness", m.roughness, 0.0, 1.0),
                ("transmission", m.transmission, 0.0, 1.0),
                ("opacity", m.opacity, 0.0, 1.0),
                ("ior", m.ior, 1.0, 3.0),
                ("strength", m.strength, 0.0, 1000.0),
            ] {
                if let Some(v) = value {
                    if !(lo..=hi).contains(&v) {
                        problem(&mut out, format!("{path}.{field}"), format!("`{field}` must be between {lo} and {hi}, not {v}"));
                    }
                }
            }
        }

        let mut seen: Vec<&str> = vec![];
        for (i, part) in self.parts.iter().enumerate() {
            let path = format!("parts[{i}]");
            if !valid_id(&part.id) {
                problem(&mut out, format!("{path}.id"), format!("`{}` is not a valid id; use letters, digits and `_`", part.id));
            } else if seen.contains(&part.id.as_str()) {
                problem(&mut out, format!("{path}.id"), format!("duplicate id `{}`", part.id));
            }
            match (&part.shape, &part.material) {
                (Some(shape), material) => {
                    for (field, message) in shape.check() {
                        problem(&mut out, format!("{path}.shape.{field}"), message);
                    }
                    match material {
                        None => problem(&mut out, format!("{path}.material"), "a part with a shape needs a `material`"),
                        Some(m) if !self.materials.contains_key(m) => {
                            let known: Vec<&str> = self.materials.keys().map(String::as_str).collect();
                            problem(&mut out, format!("{path}.material"), format!("unknown material `{m}`; the materials are: {}", known.join(", ")));
                        }
                        _ => {}
                    }
                }
                (None, Some(_)) => problem(&mut out, format!("{path}.material"), "a group (a part without a shape) takes no material"),
                (None, None) => {}
            }
            if let Some(parent) = &part.parent {
                if !seen.contains(&parent.as_str()) {
                    problem(&mut out, format!("{path}.parent"), format!("`{parent}` is not a part declared before `{}`", part.id));
                }
            }
            if let Some(array) = &part.array {
                if array.count() < 1 || array.count() > 512 {
                    problem(&mut out, format!("{path}.array.count"), "an array has between 1 and 512 copies");
                }
            }
            let finite = |v: V3| v.iter().all(|x| x.is_finite());
            if !finite(part.at) || !finite(part.rotate) || !finite(part.scale.vector()) {
                problem(&mut out, &path, "`at`, `rotate` and `scale` must be finite numbers");
            }
            seen.push(&part.id);
        }
        if self.parts.is_empty() {
            problem(&mut out, "parts", "a scene needs at least one part");
        }

        for (i, light) in self.lights.iter().enumerate() {
            let path = format!("lights[{i}]");
            if !(light.power.is_finite() && light.power > 0.0) {
                problem(&mut out, format!("{path}.power"), "power must be a positive number of watts");
            }
            if let Some(c) = &light.color {
                if hex(c).is_none() {
                    problem(&mut out, format!("{path}.color"), format!("`{c}` is not a colour such as #ffffff"));
                }
            }
        }
        let cam = &self.camera;
        if !(5.0..=120.0).contains(&cam.fov) || cam.distance <= 0.0 {
            problem(&mut out, "camera", "`fov` is in degrees between 5 and 120, and `distance` must be positive");
        }

        let target_ok = |t: &str| -> Result<(), String> {
            let (id, index) = split_target(t);
            let Some(part) = self.parts.iter().find(|p| p.id == id) else {
                return Err(format!("unknown part `{id}`; the parts are: {}", self.parts.iter().map(|p| p.id.as_str()).collect::<Vec<_>>().join(", ")));
            };
            match (index, &part.array) {
                (None, _) => Ok(()),
                (Some(_), None) => Err(format!("`{t}` names a copy, but `{id}` is not an array; use `{id}`")),
                (Some(k), Some(a)) if k as u32 >= a.count() => Err(format!("`{id}` has copies 0 to {}, not {k}", a.count() - 1)),
                _ => Ok(()),
            }
        };
        if self.scenes.is_empty() {
            problem(&mut out, "scenes", "a scene needs at least one section of steps");
        }
        let mut section_ids: Vec<&str> = vec![];
        for (s, section) in self.scenes.iter().enumerate() {
            if section_ids.contains(&section.id.as_str()) {
                problem(&mut out, format!("scenes[{s}].id"), format!("duplicate id `{}`", section.id));
            }
            section_ids.push(&section.id);
            for (k, step) in section.steps.iter().enumerate() {
                let path = format!("scenes[{s}].steps[{k}]");
                if !step.say.contains_key("en") {
                    problem(&mut out, format!("{path}.say"), "every step needs English narration in `en`");
                }
                for (a, action) in step.actions.iter().enumerate() {
                    let apath = format!("{path}.do[{a}]");
                    if !(0.0..1.0).contains(&action.delay) {
                        problem(&mut out, format!("{apath}.delay"), "`delay` is a fraction of the step, from 0 up to (not including) 1");
                    }
                    if let Some(t) = action.kind.target() {
                        if let Err(message) = target_ok(t) {
                            problem(&mut out, format!("{apath}.target"), message);
                        }
                    }
                    match &action.kind {
                        ActionKind::Move { to, by, .. } | ActionKind::Rotate { to, by, .. } if to.is_some() == by.is_some() => {
                            problem(&mut out, &apath, format!("`{}` needs `to` or `by`, not both", action.kind.name()));
                        }
                        ActionKind::Glow { color: Some(c), .. } if hex(c).is_none() => {
                            problem(&mut out, format!("{apath}.color"), format!("`{c}` is not a colour such as #ff8800"));
                        }
                        ActionKind::Spin { rpm, .. } if !rpm.is_finite() => problem(&mut out, format!("{apath}.rpm"), "rpm must be a number"),
                        ActionKind::Camera { azimuth: None, elevation: None, distance: None, target: None, fov: None } => {
                            problem(&mut out, &apath, "`camera` needs at least one of azimuth, elevation, distance, target, fov");
                        }
                        ActionKind::Label { target, text: None } => {
                            let (id, _) = split_target(target);
                            if self.parts.iter().find(|p| p.id == id).is_some_and(|p| p.label.is_none()) {
                                problem(&mut out, &apath, format!("`label` needs `text`, or a `label` on part `{id}`"));
                            }
                        }
                        _ => {}
                    }
                }
            }
        }
        out
    }
}
