//! Animation and video: timing follows the speech, frames at the ends of a
//! step match the still frames, and the encoder writes what it says.

use cevg_core::anim::{estimate_speech, HOLD};
use cevg_core::text::Fonts;
use cevg_core::{parse, render_video, Movie, Position, Renderer, World};

fn example(name: &str) -> String {
    let path = format!("{}/../../examples/{name}", env!("CARGO_MANIFEST_DIR"));
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"))
}

/// A small canvas keeps these tests quick.
fn small(json: &str) -> String {
    json.replace(r#""width": 1920, "height": 1080"#, r#""width": 480, "height": 270"#)
}

#[test]
fn timing_follows_the_speech() {
    let script = parse(&example("binary_search.json")).unwrap();
    let speech = vec![2.0; 7];
    let movie = Movie::new(&script, &speech).unwrap();
    assert!((movie.seconds - 7.0 * (2.0 + HOLD)).abs() < 1e-4);
    assert_eq!(movie.frame_count(), (movie.seconds * 30.0).ceil() as usize);
    assert!((movie.time_of(3, 0.5) - (3.0 * (2.0 + HOLD) + 1.0)).abs() < 1e-4);

    assert!(Movie::new(&script, &[2.0; 6]).err().unwrap().contains("6 durations were given, but the script has 7 steps"));
    assert!(Movie::new(&script, &[0.0; 7]).err().unwrap().contains("not usable"));
    assert_eq!(estimate_speech(&script).len(), 7);
}

#[test]
fn a_step_starts_and_ends_on_the_still_frames() {
    let json = small(&example("binary_search.json"));
    let script = parse(&json).unwrap();
    let movie = Movie::new(&script, &[2.0; 7]).unwrap();
    let mut fonts = Fonts::new();
    let still = |scene: &str, step: usize| {
        let pos = Position::locate(&script, Some(scene), Some(step)).unwrap();
        Renderer::new().render(&script, &World::at(&script, pos))
    };

    // Step 3 is first-check step 1: `lo` moves from cell 0 to cell 4.
    let before = movie.frame_at(movie.time_of(3, 0.0), &mut fonts);
    let middle = movie.frame_at(movie.time_of(3, 0.75), &mut fonts);
    let after = movie.frame_at(movie.time_of(3, 1.0), &mut fonts);
    let held = movie.frame_at(movie.time_of(3, 1.0) + HOLD * 0.5, &mut fonts);

    assert!(before.data() == still("first-check", 0).data(), "a step starts where the last one ended");
    assert!(after.data() == still("first-check", 1).data(), "a step ends on its still frame");
    assert!(held.data() == after.data(), "the picture rests during the hold");
    assert!(middle.data() != before.data() && middle.data() != after.data(), "in between it is in motion");
}

#[test]
fn frames_do_not_depend_on_each_other() {
    let json = small(&example("subjects/dsa_bfs.json"));
    let script = parse(&json).unwrap();
    let movie = Movie::new(&script, &estimate_speech(&script)).unwrap();
    let time = movie.time_of(1, 0.6);
    let a = movie.frame_at(time, &mut Fonts::new());
    // Render other frames first, on another font cache, then the same one.
    let mut fonts = Fonts::new();
    movie.frame_at(0.0, &mut fonts);
    movie.frame_at(movie.seconds, &mut fonts);
    let b = movie.frame_at(time, &mut fonts);
    assert!(a.data() == b.data());
}

#[test]
fn encodes_a_video_when_ffmpeg_is_present() {
    if std::process::Command::new("ffmpeg").arg("-version").output().is_err() {
        eprintln!("skipped: ffmpeg is not installed");
        return;
    }
    let json = small(&example("binary_search.json"));
    let out = std::env::temp_dir().join(format!("cevg-test-{}.mp4", std::process::id()));
    let mut seen = (0, 0);
    let info = render_video(&json, Some(&[0.5; 7]), None, &out, |done, total| seen = (done, total)).unwrap();
    assert_eq!(info.frames, ((0.5 + HOLD) * 7.0 * 30.0_f32).ceil() as usize);
    assert_eq!(seen, (info.frames, info.frames));
    assert_eq!(info.step_starts.len(), 7);
    let size = std::fs::metadata(&out).unwrap().len();
    std::fs::remove_file(&out).ok();
    assert!(size > 5_000, "the file is only {size} bytes");

    let report = render_video(&json, Some(&[0.5; 3]), None, &out, |_, _| {}).unwrap_err();
    assert!(report.diagnostics.last().unwrap().message.contains("3 durations were given"));
}

#[test]
fn captions_show_the_narration_of_the_current_step() {
    use cevg_core::draw::Shape;
    let json = small(&example("binary_search.json"));
    let script = parse(&json).unwrap();
    let plain = Movie::new(&script, &[2.0; 7]).unwrap();
    let movie = Movie::with_captions(&script, &[2.0; 7], "en").unwrap();

    let caption = |time: f32| {
        movie.cmds_at(time).into_iter().rev().find_map(|c| match c.shape {
            Shape::Text { text, .. } if c.key == "caption|text" => Some(text),
            _ => None,
        })
    };
    assert_eq!(caption(movie.time_of(0, 0.5)).unwrap(), "We are looking for 23 in this sorted array.");
    assert_eq!(caption(movie.time_of(3, 0.5)).unwrap(), "12 is smaller than 23, so the left half cannot hold the answer.");
    assert!(plain.cmds_at(1.0).iter().all(|c| !c.key.starts_with("caption")));

    // A language the script does not have falls back to English.
    let tamil = Movie::with_captions(&script, &[2.0; 7], "ta").unwrap();
    assert!(tamil.srt().unwrap().contains("We are looking for 23"));
    // A language it does have is shown.
    let telugu = Movie::with_captions(&script, &[2.0; 7], "te").unwrap();
    assert!(telugu.srt().unwrap().contains("search చేస్తున్నాం"));

    let srt = movie.srt().unwrap();
    assert!(srt.starts_with("1\n00:00:00,000 --> 00:00:02,350\nWe are looking for 23 in this sorted array.\n\n2\n00:00:02,350 --> "), "{srt}");
    assert_eq!(srt.matches(" --> ").count(), 7);
    assert!(plain.srt().is_none());
}
