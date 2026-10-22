//! CEVG core: the scene script, the visual families, the validator and the
//! still-frame renderer.
//!
//! * [`parse`] turns JSON into a typed [`Script`], with the path of any error.
//! * [`validate`] replays a script and returns its problems.
//! * [`check`] does both and returns one [`Report`].
//! * [`frame_png`] draws one moment of a script.
//! * [`render_video`] renders the whole script to an MP4.

pub mod anim;
pub mod draw;
pub mod expr;
pub mod families;
pub mod render;
pub mod script;
pub mod state;
pub mod target;
pub mod text;
pub mod validate;

pub use anim::Movie;
pub use render::Renderer;
pub use script::Script;
pub use state::{Position, World};
pub use target::Target;
pub use validate::{validate, Diagnostic, Severity};

use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct Report {
    /// True when there are no errors. Warnings do not make a script invalid.
    pub ok: bool,
    pub errors: usize,
    pub warnings: usize,
    pub diagnostics: Vec<Diagnostic>,
    /// Present when the JSON could be parsed into a script.
    pub summary: Option<Summary>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Summary {
    pub title: String,
    pub objects: usize,
    pub scenes: usize,
    pub steps: usize,
    pub languages: Vec<String>,
}

/// Parse a scene script. On failure the diagnostic says where in the JSON the
/// problem is, for example `scenes[1].steps[0].do[2]`.
pub fn parse(json: &str) -> Result<Script, Diagnostic> {
    let de = &mut serde_json::Deserializer::from_str(json);
    serde_path_to_error::deserialize(de).map_err(|e| {
        let path = e.path().to_string();
        Diagnostic {
            severity: Severity::Error,
            path: if path == "." { "(root)".to_string() } else { path },
            message: e.into_inner().to_string(),
        }
    })
}

/// Parse and validate in one call.
pub fn check(json: &str) -> Report {
    let (diagnostics, summary) = match parse(json) {
        Err(d) => (vec![d], None),
        Ok(script) => {
            let mut languages: Vec<String> = script
                .scenes
                .iter()
                .flat_map(|s| &s.steps)
                .flat_map(|s| s.say.keys().cloned())
                .collect();
            languages.sort();
            languages.dedup();
            let summary = Summary {
                title: script.title.clone(),
                objects: script.objects.len(),
                scenes: script.scenes.len(),
                steps: script.scenes.iter().map(|s| s.steps.len()).sum(),
                languages,
            };
            (validate(&script), Some(summary))
        }
    };
    let errors = diagnostics.iter().filter(|d| d.severity == Severity::Error).count();
    Report {
        ok: errors == 0,
        errors,
        warnings: diagnostics.len() - errors,
        diagnostics,
        summary,
    }
}

fn movie(script: &Script, speech: &[f32], captions: Option<&str>, watermark: Option<&str>) -> Result<Movie, String> {
    let movie = match captions {
        Some(language) => Movie::with_captions(script, speech, language),
        None => Movie::new(script, speech),
    }?;
    Ok(match watermark {
        Some(text) => movie.with_watermark(script, text),
        None => movie,
    })
}

/// The reference a script author reads first: what can be drawn, how parts
/// are named, what each action does, and how to plan scenes from narration.
pub const GUIDE: &str = include_str!("guide.md");

/// A copy of a clean report with one error added to it.
fn failed(report: &Report, path: &str, message: String) -> Report {
    let mut report = report.clone();
    report.ok = false;
    report.errors += 1;
    report.diagnostics.push(Diagnostic { severity: Severity::Error, path: path.to_string(), message });
    report
}

/// Draw one moment of a script and return it as PNG bytes.
///
/// `scene` is a scene id (default: the last scene) and `step` a zero-based
/// step number inside it (default: the last step). `at` says how far through
/// that step, from 0 (nothing has moved yet) to 1 (the step has finished,
/// which is the default). A script with errors is not drawn; the report says
/// why. `captions` names a language whose narration is shown under the
/// picture.
pub fn frame_png(
    json: &str,
    scene: Option<&str>,
    step: Option<usize>,
    at: Option<f32>,
    captions: Option<&str>,
) -> Result<Vec<u8>, Report> {
    frame_png_marked(json, scene, step, at, captions, None)
}

/// One moment of a step as a PNG, with the first `done` actions complete and
/// the rest not started: an exact state, nothing half-faded. Also returns the
/// number of actions the step has.
pub fn frame_png_after(
    json: &str,
    scene: Option<&str>,
    step: Option<usize>,
    done: usize,
    captions: Option<&str>,
    watermark: Option<&str>,
) -> Result<(Vec<u8>, usize), Report> {
    let report = check(json);
    if !report.ok {
        return Err(report);
    }
    let script = parse(json).map_err(|_| report.clone())?;
    let pos = Position::locate(&script, scene, step).map_err(|m| failed(&report, "(frame)", m))?;
    let movie = movie(&script, &anim::estimate_speech(&script), captions, watermark).map_err(|m| failed(&report, "(frame)", m))?;
    let index = anim::flat_index(&script, pos);
    let png = movie
        .frame_after(index, done, &mut text::Fonts::new())
        .encode_png()
        .map_err(|e| failed(&report, "(frame)", format!("PNG encoding failed: {e}")))?;
    Ok((png, movie.actions_in(index)))
}

/// [`frame_png`], with a watermark in the top right corner.
pub fn frame_png_marked(
    json: &str,
    scene: Option<&str>,
    step: Option<usize>,
    at: Option<f32>,
    captions: Option<&str>,
    watermark: Option<&str>,
) -> Result<Vec<u8>, Report> {
    let report = check(json);
    if !report.ok {
        return Err(report);
    }
    let script = parse(json).map_err(|_| report.clone())?;
    let pos = Position::locate(&script, scene, step).map_err(|m| failed(&report, "(frame)", m))?;
    let movie =
        movie(&script, &anim::estimate_speech(&script), captions, watermark).map_err(|m| failed(&report, "(frame)", m))?;
    let time = movie.time_of(anim::flat_index(&script, pos), at.unwrap_or(1.0));
    movie
        .frame_at(time, &mut text::Fonts::new())
        .encode_png()
        .map_err(|e| failed(&report, "(frame)", format!("PNG encoding failed: {e}")))
}

#[derive(Debug, Clone, Serialize)]
pub struct VideoInfo {
    pub seconds: f32,
    pub frames: usize,
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    /// When each step starts, in seconds, in order across all scenes.
    pub step_starts: Vec<f32>,
}

/// Render a script to an MP4 file.
///
/// `speech` gives the length of each step's narration in seconds, in order
/// across all scenes; without it the lengths are estimated from the English
/// text. `captions` names a language whose narration is shown under the
/// picture and also written beside the video as an .srt file. `progress` is
/// called with (frames done, frames in total).
pub fn render_video(
    json: &str,
    speech: Option<&[f32]>,
    captions: Option<&str>,
    out: &std::path::Path,
    progress: impl FnMut(usize, usize),
) -> Result<VideoInfo, Report> {
    render_video_marked(json, speech, captions, None, out, progress)
}

/// [`render_video`], with a watermark in the top right corner of every frame.
pub fn render_video_marked(
    json: &str,
    speech: Option<&[f32]>,
    captions: Option<&str>,
    watermark: Option<&str>,
    out: &std::path::Path,
    progress: impl FnMut(usize, usize),
) -> Result<VideoInfo, Report> {
    let report = check(json);
    if !report.ok {
        return Err(report);
    }
    let script = parse(json).map_err(|_| report.clone())?;
    let estimated = anim::estimate_speech(&script);
    let speech = speech.unwrap_or(&estimated);
    let movie = movie(&script, speech, captions, watermark).map_err(|m| failed(&report, "(render)", m))?;
    movie.encode(out, progress).map_err(|m| failed(&report, "(render)", m))?;
    if let Some(srt) = movie.srt() {
        let path = out.with_extension("srt");
        std::fs::write(&path, srt).map_err(|e| failed(&report, "(render)", format!("cannot write {}: {e}", path.display())))?;
    }
    Ok(VideoInfo {
        seconds: movie.seconds,
        frames: movie.frame_count(),
        width: movie.width,
        height: movie.height,
        fps: movie.fps,
        step_starts: (0..speech.len()).map(|i| movie.time_of(i, 0.0)).collect(),
    })
}
