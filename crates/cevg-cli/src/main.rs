//! `cevg`: the command-line face of the core.
//!
//!   cevg validate <script.json> [--json]
//!   cevg frame <script.json> [--scene <id>] [--step <n>] [--at <0..1>] [--captions [lang]] [--watermark <text>] [--after <n>] [-o <out.png>]
//!   cevg render <script.json> [--speech <s1,s2,...>] [--captions [lang]] [--watermark <text>] [-o <out.mp4>]
//!   cevg guide
//!   cevg gpu
//!
//! `--gpu auto|vulkan|soft` on frame and render chooses how 3D scenes are
//! drawn: the GPU through Vulkan, or the software rasteriser. `auto` (the
//! default) takes Vulkan when a device is found.
//!
//! Exit codes: 0 = success, 1 = the script has errors, 2 = bad usage or I/O.

use cevg_core::Report;
use std::process::ExitCode;

const USAGE: &str = "usage:
  cevg validate <script.json> [--json]
  cevg frame <script.json> [--scene <id>] [--step <n>] [--at <0..1>] [--captions [lang]] [--watermark <text>] [--after <n>] [-o <out.png>]
  cevg render <script.json> [--speech <s1,s2,...>] [--captions [lang]] [--watermark <text>] [-o <out.mp4>]
  cevg guide
  cevg gpu

guide prints the reference for writing scene scripts.

gpu reports which Vulkan device would draw 3D scenes, if any. --gpu
auto|vulkan|soft on frame and render chooses between the GPU and the
software rasteriser; auto (the default) takes the GPU when there is one.

frame draws one moment. Without --scene it uses the last scene; without
--step, the last step of that scene. Steps count from 0. --at says how far
through the step: 0 is before anything moves, 1 (the default) is the end.

render makes an MP4 with ffmpeg. --speech gives the narration length of
every step in seconds, in order; without it lengths are estimated from the
English text.

--after <n> draws a step with its first n actions complete and the rest not
started (an exact state, nothing half-faded); with --json it also prints how
many actions the step has.

--captions shows each step's narration under the picture, in English or in
the language named after it (--captions te), and render also writes an .srt
file next to the video.";

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match run(&args) {
        Ok(code) => code,
        Err(message) => {
            eprintln!("cevg: {message}\n\n{USAGE}");
            ExitCode::from(2)
        }
    }
}

/// Pick the 3D backend for this run. `auto` falls back quietly.
fn choose_gpu(choice: &str) -> Result<(), String> {
    match choice {
        "soft" => Ok(()),
        "vulkan" => {
            let backend = cevg_gpu::VulkanBackend::new().map_err(|e| format!("--gpu vulkan: {e}"))?;
            cevg_core::set_space_backend(Box::new(backend)).map_err(|e| e.to_string())
        }
        _ => {
            if let Ok(backend) = cevg_gpu::VulkanBackend::new() {
                let _ = cevg_core::set_space_backend(Box::new(backend));
            }
            Ok(())
        }
    }
}

fn run(args: &[String]) -> Result<ExitCode, String> {
    let mut positional = Vec::new();
    let (mut json, mut scene, mut step, mut out) = (false, None, None, None);
    let (mut at, mut speech): (Option<f32>, Option<Vec<f32>>) = (None, None);
    let mut captions: Option<String> = None;
    let mut watermark: Option<String> = None;
    let mut after: Option<usize> = None;
    let mut gpu = "auto".to_string();

    let mut it = args.iter().peekable();
    while let Some(arg) = it.next() {
        // An optional language may follow --captions; a script file or
        // another option does not count as one.
        if arg == "--captions" {
            let language = it.next_if(|next| !next.starts_with('-') && !next.contains('.')).cloned();
            captions = Some(language.unwrap_or_else(|| "en".to_string()));
            continue;
        }
        let mut value = |name: &str| it.next().cloned().ok_or(format!("{name} needs a value"));
        match arg.as_str() {
            "--json" => json = true,
            "--scene" => scene = Some(value("--scene")?),
            "--step" => {
                let v = value("--step")?;
                step = Some(v.parse::<usize>().map_err(|_| format!("--step `{v}` is not a whole number"))?);
            }
            "--at" => {
                let v = value("--at")?;
                at = Some(v.parse::<f32>().map_err(|_| format!("--at `{v}` is not a number"))?);
            }
            "--speech" => {
                let v = value("--speech")?;
                let parsed: Result<Vec<f32>, _> = v.split(',').map(|s| s.trim().parse::<f32>()).collect();
                speech = Some(parsed.map_err(|_| format!("--speech `{v}` is not a list of numbers such as 2.5,3,4"))?);
            }
            "--watermark" => watermark = Some(value("--watermark")?),
            "--after" => {
                let v = value("--after")?;
                after = Some(v.parse::<usize>().map_err(|_| format!("--after `{v}` is not a whole number"))?);
            }
            "--gpu" => {
                gpu = value("--gpu")?;
                if !["auto", "vulkan", "soft"].contains(&gpu.as_str()) {
                    return Err(format!("--gpu `{gpu}` is not one of auto, vulkan, soft"));
                }
            }
            "-o" | "--out" => out = Some(value("-o")?),
            flag if flag.starts_with('-') => return Err(format!("unknown option `{flag}`")),
            _ => positional.push(arg.as_str()),
        }
    }

    if matches!(positional.first(), Some(&"frame") | Some(&"render")) {
        choose_gpu(&gpu)?;
    }

    match positional.as_slice() {
        ["guide"] => {
            print!("{}", cevg_core::GUIDE);
            Ok(ExitCode::SUCCESS)
        }
        ["gpu"] => {
            match cevg_gpu::VulkanBackend::new() {
                Ok(backend) => println!("vulkan: {}", backend.device_name()),
                Err(e) => println!("no vulkan ({e}); 3D scenes use the software rasteriser"),
            }
            Ok(ExitCode::SUCCESS)
        }
        ["validate", file] => {
            let report = cevg_core::check(&read(file)?);
            print_report(&report, json);
            Ok(exit(report.ok))
        }
        ["frame", file] => {
            let out = out.unwrap_or_else(|| "frame.png".to_string());
            let json_text = read(file)?;
            let drawn = match after {
                Some(done) => cevg_core::frame_png_after(&json_text, scene.as_deref(), step, done, captions.as_deref(), watermark.as_deref())
                    .map(|(png, actions)| {
                        if json {
                            println!("{}", serde_json::json!({ "after": done, "actions": actions }));
                        }
                        png
                    }),
                None => cevg_core::frame_png_marked(&json_text, scene.as_deref(), step, at, captions.as_deref(), watermark.as_deref()),
            };
            match drawn {
                Ok(png) => {
                    std::fs::write(&out, png).map_err(|e| format!("cannot write {out}: {e}"))?;
                    println!("wrote {out}");
                    Ok(ExitCode::SUCCESS)
                }
                Err(report) => {
                    print_report(&report, json);
                    Ok(ExitCode::from(1))
                }
            }
        }
        ["render", file] => {
            let out = out.unwrap_or_else(|| "video.mp4".to_string());
            let show = |done: usize, total: usize| eprint!("\rframe {done} of {total}");
            match cevg_core::render_video_marked(
                &read(file)?,
                speech.as_deref(),
                captions.as_deref(),
                watermark.as_deref(),
                out.as_ref(),
                show,
            ) {
                Ok(info) => {
                    eprintln!();
                    if json {
                        println!("{}", serde_json::to_string_pretty(&info).expect("info serializes"));
                    } else {
                        println!(
                            "wrote {out}: {:.1} seconds, {} frames at {}x{}, {} fps",
                            info.seconds, info.frames, info.width, info.height, info.fps
                        );
                    }
                    Ok(ExitCode::SUCCESS)
                }
                Err(report) => {
                    eprintln!();
                    print_report(&report, json);
                    Ok(ExitCode::from(1))
                }
            }
        }
        _ => Err("expected a command and a script file".to_string()),
    }
}

fn read(file: &str) -> Result<String, String> {
    std::fs::read_to_string(file).map_err(|e| format!("cannot read {file}: {e}"))
}

fn exit(ok: bool) -> ExitCode {
    if ok {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(1)
    }
}

fn print_report(report: &Report, json: bool) {
    if json {
        println!("{}", serde_json::to_string_pretty(report).expect("report serializes"));
        return;
    }
    for d in &report.diagnostics {
        println!("{d}");
    }
    match (&report.summary, report.ok) {
        (Some(s), true) => println!(
            "ok: \"{}\" has {} objects, {} scenes and {} steps ({} warning(s))",
            s.title, s.objects, s.scenes, s.steps, report.warnings
        ),
        _ => println!("invalid: {} error(s), {} warning(s)", report.errors, report.warnings),
    }
}
