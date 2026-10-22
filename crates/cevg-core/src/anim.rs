//! Animation and video.
//!
//! A [`Movie`] holds, for every step, the display list before the step and
//! after each of its actions. The picture at any time is a blend of those
//! lists, so a frame depends on nothing but its own time: frames render in
//! parallel, and any one frame can be previewed alone.
//!
//! Timing follows the narration. A step lasts as long as its speech plus a
//! short hold. Every action starts at its `delay` (a fraction of the speech)
//! and stretches to the end of the speech, so the picture finishes changing
//! exactly as the sentence ends.

use crate::draw::{blend, raster, Cmd, Shape};
use crate::render::{palette, Rect, Renderer, Rgb};
use crate::text::{Face, HAlign};
use crate::script::Script;
use crate::state::{Position, World};
use crate::text::Fonts;
use rayon::prelude::*;
use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};
use tiny_skia::Pixmap;

/// Seconds the finished picture rests after the speech, before the next step.
pub const HOLD: f32 = 0.35;

/// A guess at how long each step's narration takes to say, for silent video
/// and previews. Real videos pass measured audio lengths instead.
pub fn estimate_speech(script: &Script) -> Vec<f32> {
    script
        .scenes
        .iter()
        .flat_map(|s| &s.steps)
        .map(|step| {
            let words = step.say.get("en").map_or(0, |t| t.split_whitespace().count());
            (words as f32 / 2.6).max(1.5)
        })
        .collect()
}

/// The number of a step counted across all scenes.
pub fn flat_index(script: &Script, pos: Position) -> usize {
    script.scenes[..pos.scene].iter().map(|s| s.steps.len()).sum::<usize>() + pos.step
}

struct Clip {
    start: f32,
    speech: f32,
    /// `lists[0]` is the picture before the step; `lists[i]` after action `i`.
    lists: Vec<Vec<Cmd>>,
    delays: Vec<f32>,
}

/// Height of the caption band, as a fraction of the canvas height.
const CAPTION_BAND: f32 = 0.14;

/// The narration, shown under the picture for checking a script by eye.
struct Captions {
    /// One caption per step.
    lines: Vec<String>,
    band: Rgb,
    ink: Rgb,
}

pub struct Movie {
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    pub seconds: f32,
    background: Rgb,
    clips: Vec<Clip>,
    captions: Option<Captions>,
    /// A short line shown in the top right corner of every frame.
    watermark: Option<(String, Rgb)>,
}

/// Slow at both ends, so that motion starts and stops gently.
fn ease(p: f32) -> f32 {
    let p = p.clamp(0.0, 1.0);
    if p < 0.5 {
        4.0 * p * p * p
    } else {
        1.0 - (-2.0 * p + 2.0).powi(3) / 2.0
    }
}

impl Movie {
    /// Prepare a script for rendering. `speech` gives the length in seconds
    /// of each step's narration, in order across all scenes.
    pub fn new(script: &Script, speech: &[f32]) -> Result<Movie, String> {
        Self::build(script, speech, None)
    }

    /// The same, with each step's narration in `language` shown in a band
    /// under the picture. A step without that language shows its English.
    pub fn with_captions(script: &Script, speech: &[f32], language: &str) -> Result<Movie, String> {
        Self::build(script, speech, Some(language))
    }

    fn build(script: &Script, speech: &[f32], captions: Option<&str>) -> Result<Movie, String> {
        let steps: Vec<_> = script.scenes.iter().flat_map(|s| &s.steps).collect();
        if speech.len() != steps.len() {
            return Err(format!("{} durations were given, but the script has {} steps", speech.len(), steps.len()));
        }
        if let Some(bad) = speech.iter().find(|s| !(**s > 0.0 && **s <= 600.0)) {
            return Err(format!("a step duration of {bad} seconds is not usable; each must be above 0 and at most 600"));
        }

        let mut renderer = Renderer::new();
        let mut world = World::new(script);
        // With captions the picture is laid out in the space above the band.
        let scale = if captions.is_some() { 1.0 - CAPTION_BAND } else { 1.0 };
        let mut before = renderer.display_list_scaled(script, &world, scale);
        let mut start = 0.0;
        let mut clips = Vec::with_capacity(steps.len());
        for (step, speech) in steps.iter().zip(speech) {
            let mut lists = vec![before];
            for action in &step.actions {
                world.apply(&action.kind);
                lists.push(renderer.display_list_scaled(script, &world, scale));
            }
            before = lists.last().expect("at least the first list").clone();
            let delays = step.actions.iter().map(|a| a.delay.clamp(0.0, 1.0) as f32).collect();
            clips.push(Clip { start, speech: *speech, lists, delays });
            start += speech + HOLD;
        }
        Ok(Movie {
            width: script.canvas.width,
            height: script.canvas.height,
            fps: script.canvas.fps,
            seconds: start,
            background: palette(script.canvas.theme).background,
            clips,
            watermark: None,
            captions: captions.map(|language| {
                let pal = palette(script.canvas.theme);
                let line = |step: &&crate::script::Step| {
                    step.say.get(language).or(step.say.get("en")).cloned().unwrap_or_default()
                };
                Captions { lines: steps.iter().map(line).collect(), band: pal.surface, ink: pal.text }
            }),
        })
    }

    /// Show `text` faintly in the top right corner of every frame.
    pub fn with_watermark(mut self, script: &Script, text: &str) -> Movie {
        let text = text.trim();
        if !text.is_empty() {
            self.watermark = Some((text.chars().take(60).collect(), palette(script.canvas.theme).muted));
        }
        self
    }

    pub fn frame_count(&self) -> usize {
        (self.seconds * self.fps as f32).ceil() as usize
    }

    /// The time at which a step is `at` of the way through its speech
    /// (0 = before anything has moved, 1 = everything has finished).
    pub fn time_of(&self, step: usize, at: f32) -> f32 {
        let clip = &self.clips[step];
        clip.start + clip.speech * at.clamp(0.0, 1.0)
    }

    fn clip_at(&self, time: f32) -> Option<usize> {
        self.clips.iter().rposition(|c| c.start <= time).or(if self.clips.is_empty() { None } else { Some(0) })
    }

    /// The picture of a step with its first `done` actions complete and the rest
    /// not started: an exact state, with nothing half-faded. `done` past the
    /// number of actions means the end of the step.
    pub fn cmds_after(&self, step: usize, done: usize) -> Vec<Cmd> {
        let clip = &self.clips[step];
        let progress: Vec<f32> = (0..clip.delays.len()).map(|i| if i < done { 1.0 } else { 0.0 }).collect();
        let mut cmds = blend(&clip.lists, &progress);
        self.decorate(&mut cmds, step, 1.0);
        cmds
    }

    /// The number of actions in a step.
    pub fn actions_in(&self, step: usize) -> usize {
        self.clips[step].delays.len()
    }

    /// The display list at a moment in time.
    pub fn cmds_at(&self, time: f32) -> Vec<Cmd> {
        let Some(index) = self.clip_at(time) else { return vec![] };
        let clip = &self.clips[index];
        let local = time - clip.start;
        let progress: Vec<f32> = clip
            .delays
            .iter()
            .map(|delay| {
                let begin = delay * clip.speech;
                let span = clip.speech - begin;
                if span < 1e-3 {
                    // An action with delay 1 happens all at once at the end.
                    return if local >= begin { 1.0 } else { 0.0 };
                }
                ease((local - begin) / span)
            })
            .collect();
        let mut cmds = blend(&clip.lists, &progress);
        self.decorate(&mut cmds, index, local);
        cmds
    }

    /// Add the watermark and the caption band for step `index`, `local` seconds into it.
    fn decorate(&self, cmds: &mut Vec<Cmd>, index: usize, local: f32) {
        if let Some((text, ink)) = &self.watermark {
            let (w, h) = (self.width as f32, self.height as f32);
            cmds.push(Cmd {
                key: "watermark".into(),
                shape: Shape::Text {
                    text: text.clone(),
                    face: Face::Sans,
                    align: HAlign::Right,
                    max_w: Some(w * 0.4),
                    x: w - h * 0.03,
                    y: h * 0.04,
                    size: h * 0.024,
                    color: *ink,
                    opacity: 0.7,
                },
            });
        }

        if let Some(captions) = &self.captions {
            let (w, h) = (self.width as f32, self.height as f32);
            let band = Rect { x: 0.0, y: h * (1.0 - CAPTION_BAND), w, h: h * CAPTION_BAND };
            cmds.push(Cmd { key: "caption|band".into(), shape: Shape::Fill { rect: band, radius: 0.0, color: captions.band, opacity: 1.0 } });
            cmds.push(Cmd {
                key: "caption|text".into(),
                shape: Shape::Text {
                    text: captions.lines[index].clone(),
                    face: Face::Sans,
                    align: HAlign::Center,
                    max_w: Some(w * 0.9),
                    x: w / 2.0,
                    y: band.y + band.h / 2.0,
                    size: h * 0.036,
                    color: captions.ink,
                    // A quick fade in, so a new sentence is noticed.
                    opacity: (local / 0.25).clamp(0.0, 1.0),
                },
            });
        }
    }

    /// The captions as a SubRip (.srt) file, timed to the steps.
    pub fn srt(&self) -> Option<String> {
        let captions = self.captions.as_ref()?;
        let stamp = |t: f32| {
            let ms = (t * 1000.0).round() as u64;
            format!("{:02}:{:02}:{:02},{:03}", ms / 3_600_000, ms / 60_000 % 60, ms / 1000 % 60, ms % 1000)
        };
        let mut out = String::new();
        for (i, (clip, line)) in self.clips.iter().zip(&captions.lines).enumerate() {
            let end = self.clips.get(i + 1).map_or(self.seconds, |next| next.start);
            out.push_str(&format!("{}\n{} --> {}\n{}\n\n", i + 1, stamp(clip.start), stamp(end), line));
        }
        Some(out)
    }

    pub fn frame_at(&self, time: f32, fonts: &mut Fonts) -> Pixmap {
        raster(&self.cmds_at(time), self.width, self.height, self.background, fonts)
    }

    /// The picture of a step after its first `done` actions; see [`Movie::cmds_after`].
    pub fn frame_after(&self, step: usize, done: usize, fonts: &mut Fonts) -> Pixmap {
        raster(&self.cmds_after(step, done), self.width, self.height, self.background, fonts)
    }

    /// Render every frame and encode an H.264 MP4 with `ffmpeg`.
    /// `progress` is called with (frames done, frames in total).
    pub fn encode(&self, out: &Path, mut progress: impl FnMut(usize, usize)) -> Result<(), String> {
        let mut ffmpeg = Command::new("ffmpeg")
            .args(["-hide_banner", "-loglevel", "error", "-y"])
            .args(["-f", "rawvideo", "-pix_fmt", "rgba"])
            .args(["-s", &format!("{}x{}", self.width, self.height)])
            .args(["-r", &self.fps.to_string(), "-i", "-", "-an"])
            .args(["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"])
            .args(["-movflags", "+faststart"])
            .arg(out)
            .stdin(Stdio::piped())
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("could not start ffmpeg ({e}); it must be installed and on the PATH"))?;
        let mut pipe = ffmpeg.stdin.take().expect("piped stdin");

        // Frames are rendered a batch at a time on all cores and written in
        // order. A batch is small enough to hold in memory at 1080p.
        let total = self.frame_count();
        let batch = rayon::current_num_threads() * 4;
        let mut written = Ok(());
        'frames: for first in (0..total).step_by(batch) {
            let last = (first + batch).min(total);
            let frames: Vec<Pixmap> = (first..last)
                .into_par_iter()
                .map_init(Fonts::new, |fonts, i| self.frame_at(i as f32 / self.fps as f32, fonts))
                .collect();
            for frame in &frames {
                // The canvas is opaque, so premultiplied RGBA is plain RGBA.
                if let Err(e) = pipe.write_all(frame.data()) {
                    written = Err(e);
                    break 'frames;
                }
            }
            progress(last, total);
        }
        drop(pipe);

        let output = ffmpeg.wait_with_output().map_err(|e| format!("ffmpeg did not finish: {e}"))?;
        if !output.status.success() || written.is_err() {
            let reason = String::from_utf8_lossy(&output.stderr);
            return Err(format!("ffmpeg failed: {}", reason.trim()));
        }
        Ok(())
    }
}
