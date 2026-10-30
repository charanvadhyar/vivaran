//! Vivaran Studio: film-quality 3D explainers.
//!
//! The assistant writes a studio scene (see `scene`): parametric parts
//! with real materials, lights, a camera, and narrated steps of actions.
//! This crate checks it, builds the meshes (`mesh`), turns it into a node
//! rig (`rig`), plays it out in time (`timeline`), and exports the two
//! files every renderer reads (`export`): `scene.glb` and `timeline.json`.
//!
//! Two renderers read those files. Blender's Cycles (`studio/blender/
//! render.py`) is the production path; our own Vulkan path tracer is built
//! against it, using Cycles frames as the reference. Callouts, captions
//! and the watermark are drawn afterwards by `finish`, the same for both.

pub mod export;
pub mod finish;
pub mod mesh;
pub mod rig;
pub mod scene;
pub mod timeline;

use scene::{Problem, Scene};
use serde::Serialize;
use std::path::Path;

/// The guide the assistant reads before writing a studio scene.
pub const GUIDE: &str = include_str!("guide.md");

#[derive(Debug, Clone, Serialize)]
pub struct Report {
    pub ok: bool,
    pub problems: Vec<Problem>,
    pub summary: Option<Summary>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Summary {
    pub title: String,
    pub parts: usize,
    pub nodes: usize,
    pub triangles: usize,
    pub steps: usize,
    pub seconds: f32,
    pub frames: usize,
}

pub fn parse(json: &str) -> Result<Scene, Problem> {
    let de = &mut serde_json::Deserializer::from_str(json);
    serde_path_to_error::deserialize(de).map_err(|e| {
        let path = e.path().to_string();
        Problem { path: if path == "." { "(root)".into() } else { path }, message: e.into_inner().to_string() }
    })
}

/// Parse and check a scene, and if it is sound, measure it.
pub fn check(json: &str) -> Report {
    let scene = match parse(json) {
        Ok(s) => s,
        Err(p) => return Report { ok: false, problems: vec![p], summary: None },
    };
    let problems = scene.check();
    if !problems.is_empty() {
        return Report { ok: false, problems, summary: None };
    }
    let rig = rig::Rig::build(&scene);
    let summary = match timeline::Timeline::build(&scene, &rig, None) {
        Ok(tl) => Some(Summary {
            title: scene.title.clone(),
            parts: scene.parts.len(),
            nodes: rig.nodes.len(),
            triangles: rig.meshes.iter().map(|(_, m)| m.triangles()).sum::<usize>(),
            steps: tl.steps.len(),
            seconds: tl.seconds,
            frames: tl.frames,
        }),
        Err(e) => return Report { ok: false, problems: vec![Problem { path: "scenes".into(), message: e }], summary: None },
    };
    Report { ok: true, problems: vec![], summary }
}

#[derive(Debug, Clone, Serialize)]
pub struct Built {
    pub glb: String,
    pub timeline: String,
    pub summary: Summary,
}

/// Write `scene.glb` and `timeline.json` into `dir`. `speech` gives each
/// step's narration length in seconds; without it lengths are estimated.
pub fn build(json: &str, dir: &Path, speech: Option<&[f32]>) -> Result<Built, String> {
    let scene = parse(json).map_err(|p| format!("{}: {}", p.path, p.message))?;
    let problems = scene.check();
    if let Some(p) = problems.first() {
        return Err(format!("{}: {} ({} problem(s) in all; run validate)", p.path, p.message, problems.len()));
    }
    let rig = rig::Rig::build(&scene);
    let tl = timeline::Timeline::build(&scene, &rig, speech)?;
    let (tracks, camera, nodes) = export::bake(&rig, &tl);
    let glb = export::glb(&scene, &rig, &tl, &tracks, &camera, &nodes);
    let file = export::timeline_file(&scene, &rig, &tl, tracks, camera, nodes);
    std::fs::create_dir_all(dir).map_err(|e| format!("{}: {e}", dir.display()))?;
    let glb_path = dir.join("scene.glb");
    let tl_path = dir.join("timeline.json");
    std::fs::write(&glb_path, glb).map_err(|e| format!("{}: {e}", glb_path.display()))?;
    std::fs::write(&tl_path, serde_json::to_vec(&file).expect("json")).map_err(|e| format!("{}: {e}", tl_path.display()))?;
    Ok(Built {
        glb: glb_path.display().to_string(),
        timeline: tl_path.display().to_string(),
        summary: Summary {
            title: scene.title.clone(),
            parts: scene.parts.len(),
            nodes: rig.nodes.len(),
            triangles: rig.meshes.iter().map(|(_, m)| m.triangles()).sum(),
            steps: tl.steps.len(),
            seconds: tl.seconds,
            frames: tl.frames,
        },
    })
}
