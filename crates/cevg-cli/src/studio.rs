//! `cevg studio`: film-quality 3D explainers.
//!
//!   cevg studio guide
//!   cevg studio validate <scene.json> [--json]
//!   cevg studio build <scene.json> [-o <dir>] [--speech s1,s2,...]
//!   cevg studio finish <scene.json> --frames <dir> [-o out.mp4] [--captions [lang]] [--watermark text] [--speech ...]
//!   cevg studio render <scene.json> [-o out.mp4] [--preview] [--frames 1-90] [--blender <path>] [--device auto|cpu|gpu] [--captions [lang]] [--watermark text]
//!
//! `render` does all three: build, Cycles through Blender, finish.

use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode};

const RENDER_PY: &str = include_str!("../../../studio/blender/render.py");

pub const USAGE: &str = "studio usage:
  cevg studio guide
  cevg studio validate <scene.json> [--json]
  cevg studio build <scene.json> [-o <dir>] [--speech s1,s2,...]
  cevg studio finish <scene.json> --frames <dir> [-o out.mp4] [--captions [lang]] [--watermark <text>] [--speech ...]
  cevg studio still <scene.json> --frame <n> --image <frame.png> [-o out.png] [--captions [lang]] [--watermark <text>]
  cevg studio render <scene.json> [-o out.mp4] [--preview] [--frames 1-90] [--blender <path>] [--device auto|cpu|gpu]
                     [--captions [lang]] [--watermark <text>] [--speech ...]

build writes scene.glb (glTF 2.0) and timeline.json into a folder; both
renderers read those. finish draws callouts, captions and the watermark over
rendered frames and encodes the MP4. render runs build, Blender's Cycles and
finish in one go; --preview renders at half size with few samples, and
--frames limits it to some frames (as stills: no video is made). Blender is
found as --blender, $BLENDER, or `blender` on the PATH.";

struct Opts {
    positional: Vec<String>,
    json: bool,
    out: Option<String>,
    frames: Option<String>,
    speech: Option<Vec<f32>>,
    captions: Option<String>,
    watermark: Option<String>,
    blender: Option<String>,
    device: String,
    frame: Option<usize>,
    image: Option<String>,
    preview: bool,
}

fn parse(args: &[String]) -> Result<Opts, String> {
    let mut o = Opts {
        positional: vec![],
        json: false,
        out: None,
        frames: None,
        speech: None,
        captions: None,
        watermark: None,
        blender: None,
        device: "auto".into(),
        preview: false,
        frame: None,
        image: None,
    };
    let mut it = args.iter().peekable();
    while let Some(arg) = it.next() {
        if arg == "--captions" {
            let lang = it.next_if(|n| !n.starts_with('-') && !n.contains('.')).cloned();
            o.captions = Some(lang.unwrap_or_else(|| "en".into()));
            continue;
        }
        let mut value = |name: &str| it.next().cloned().ok_or(format!("{name} needs a value"));
        match arg.as_str() {
            "--json" => o.json = true,
            "--preview" => o.preview = true,
            "-o" | "--out" => o.out = Some(value("-o")?),
            "--frames" => o.frames = Some(value("--frames")?),
            "--watermark" => o.watermark = Some(value("--watermark")?),
            "--blender" => o.blender = Some(value("--blender")?),
            "--device" => o.device = value("--device")?,
            "--image" => o.image = Some(value("--image")?),
            "--frame" => {
                let v = value("--frame")?;
                o.frame = Some(v.parse().map_err(|_| format!("--frame `{v}` is not a whole number"))?);
            }
            "--speech" => {
                let v = value("--speech")?;
                let parsed: Result<Vec<f32>, _> = v.split(',').map(|s| s.trim().parse::<f32>()).collect();
                o.speech = Some(parsed.map_err(|_| format!("--speech `{v}` is not a list of numbers"))?);
            }
            flag if flag.starts_with('-') => return Err(format!("unknown option `{flag}`")),
            _ => o.positional.push(arg.clone()),
        }
    }
    Ok(o)
}

fn read(path: &str) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))
}

pub fn run(args: &[String]) -> Result<ExitCode, String> {
    let o = parse(args)?;
    match o.positional.iter().map(String::as_str).collect::<Vec<_>>().as_slice() {
        ["guide"] => {
            print!("{}", cevg_studio::GUIDE);
            Ok(ExitCode::SUCCESS)
        }
        ["validate", file] => {
            let report = cevg_studio::check(&read(file)?);
            if o.json {
                println!("{}", serde_json::to_string_pretty(&report).expect("json"));
            } else {
                for p in &report.problems {
                    println!("error: {}: {}", p.path, p.message);
                }
                match &report.summary {
                    Some(s) => println!(
                        "ok: {:?}: {} parts ({} nodes, {} triangles), {} steps, {:.1} s, {} frames",
                        s.title, s.parts, s.nodes, s.triangles, s.steps, s.seconds, s.frames
                    ),
                    None => println!("invalid: {} problem(s)", report.problems.len()),
                }
            }
            Ok(if report.ok { ExitCode::SUCCESS } else { ExitCode::from(1) })
        }
        ["build", file] => {
            let dir = PathBuf::from(o.out.clone().unwrap_or_else(|| default_dir(file)));
            let built = cevg_studio::build(&read(file)?, &dir, o.speech.as_deref())?;
            if o.json {
                println!("{}", serde_json::to_string_pretty(&built).expect("json"));
            } else {
                let s = &built.summary;
                println!("wrote {} and {}: {} nodes, {} triangles, {} frames", built.glb, built.timeline, s.nodes, s.triangles, s.frames);
            }
            Ok(ExitCode::SUCCESS)
        }
        ["finish", file] => {
            let frames = o.frames.clone().ok_or("finish needs --frames <dir>")?;
            let out = o.out.clone().unwrap_or_else(|| "studio.mp4".into());
            let opts = cevg_studio::finish::Options { captions: o.captions.clone(), watermark: o.watermark.clone(), speech: o.speech.clone() };
            cevg_studio::finish::finish(&read(file)?, Path::new(&frames), Path::new(&out), &opts, |d, t| eprint!("\rfinish: frame {d} of {t}"))?;
            eprintln!();
            println!("wrote {out}");
            Ok(ExitCode::SUCCESS)
        }
        ["still", file] => {
            let frame = o.frame.ok_or("still needs --frame <n>")?;
            let image = o.image.clone().ok_or("still needs --image <frame.png>")?;
            let out = o.out.clone().unwrap_or_else(|| format!("still_{frame:04}.png"));
            let opts = cevg_studio::finish::Options { captions: o.captions.clone(), watermark: o.watermark.clone(), speech: o.speech.clone() };
            cevg_studio::finish::still(&read(file)?, frame, Path::new(&image), Path::new(&out), &opts)?;
            println!("wrote {out}");
            Ok(ExitCode::SUCCESS)
        }
        ["render", file] => render(&o, file),
        _ => Err(format!("unknown studio command\n\n{USAGE}")),
    }
}

fn default_dir(file: &str) -> String {
    let stem = Path::new(file).file_stem().and_then(|s| s.to_str()).unwrap_or("scene");
    format!("{stem}.studio")
}

fn render(o: &Opts, file: &str) -> Result<ExitCode, String> {
    let json = read(file)?;
    let dir = PathBuf::from(default_dir(file));
    let built = cevg_studio::build(&json, &dir, o.speech.as_deref())?;
    println!("built {} frames into {}", built.summary.frames, dir.display());

    let script = dir.join("render.py");
    std::fs::write(&script, RENDER_PY).map_err(|e| format!("{}: {e}", script.display()))?;
    let blender = o.blender.clone().or_else(|| std::env::var("BLENDER").ok()).unwrap_or_else(|| "blender".into());
    let frames_dir = dir.join("frames");
    let mut cmd = Command::new(&blender);
    cmd.args(["-b", "--factory-startup", "-P"]).arg(&script).arg("--").arg(&dir).arg("--out").arg(&frames_dir).args(["--device", &o.device]);
    if o.preview {
        cmd.args(["--scale", "50", "--samples", "24"]);
    }
    if let Some(f) = &o.frames {
        cmd.args(["--frames", f]);
    }
    let status = cmd.status().map_err(|e| format!("could not run Blender (`{blender}`): {e}; install Blender 4 or pass --blender <path>"))?;
    if !status.success() {
        return Err(format!("Blender failed ({status})"));
    }
    if o.frames.is_some() {
        println!("frames are in {}", frames_dir.display());
        return Ok(ExitCode::SUCCESS);
    }
    if o.preview {
        // Half-size frames: finish works at the scene's size, so stop here.
        println!("preview frames are in {}", frames_dir.display());
        return Ok(ExitCode::SUCCESS);
    }
    let out = o.out.clone().unwrap_or_else(|| format!("{}.mp4", default_dir(file).trim_end_matches(".studio")));
    let opts = cevg_studio::finish::Options { captions: o.captions.clone(), watermark: o.watermark.clone(), speech: o.speech.clone() };
    cevg_studio::finish::finish(&json, &frames_dir, Path::new(&out), &opts, |d, t| eprint!("\rfinish: frame {d} of {t}"))?;
    eprintln!();
    println!("wrote {out}");
    Ok(ExitCode::SUCCESS)
}
