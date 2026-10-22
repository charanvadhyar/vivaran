//! The validator replays a script step by step through the same [`World`]
//! the renderer uses, so an action that is impossible at that moment (an
//! index past the end, a `swap` on a text, a pointer left on a removed cell)
//! is caught before anything is drawn.
//!
//! Every diagnostic carries the exact JSON path and a reason written so that
//! the script's author, usually Claude, can fix it without help.

use crate::families::{Body, Problem};
use crate::script::{Script, Step, SUPPORTED_VERSION};
use crate::state::World;
use crate::target::is_valid_id;
use serde::Serialize;
use std::collections::BTreeMap;
use std::fmt;

/// Sarvam `bulbul:v3` accepts at most this many characters per request.
const MAX_SAY_CHARS: usize = 2500;
/// One step is meant to be one sentence. Longer than this earns a warning.
const LONG_SAY_CHARS: usize = 300;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Error,
    Warning,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Diagnostic {
    pub severity: Severity,
    pub path: String,
    pub message: String,
}

impl fmt::Display for Diagnostic {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let label = match self.severity {
            Severity::Error => "error",
            Severity::Warning => "warning",
        };
        write!(f, "{label}: {}: {}", self.path, self.message)
    }
}

pub fn validate(script: &Script) -> Vec<Diagnostic> {
    let mut v = Validator { diags: vec![] };
    v.header(script);
    let mut world = v.objects(script);
    v.scenes(script, &mut world);
    v.unused(&world);
    v.diags
}

struct Validator {
    diags: Vec<Diagnostic>,
}

impl Validator {
    fn error(&mut self, path: impl Into<String>, message: impl Into<String>) {
        self.diags.push(Diagnostic { severity: Severity::Error, path: path.into(), message: message.into() });
    }

    fn warn(&mut self, path: impl Into<String>, message: impl Into<String>) {
        self.diags.push(Diagnostic { severity: Severity::Warning, path: path.into(), message: message.into() });
    }

    /// Report a family's problems under `path`.
    fn report(&mut self, path: &str, problems: Vec<Problem>) {
        for p in problems {
            let full = match p.field.as_str() {
                "" => path.to_string(),
                field => format!("{path}.{field}"),
            };
            let severity = if p.warning { Severity::Warning } else { Severity::Error };
            self.diags.push(Diagnostic { severity, path: full, message: p.message });
        }
    }

    fn header(&mut self, s: &Script) {
        if s.version != SUPPORTED_VERSION {
            self.error("version", format!("version {} is not supported; use {SUPPORTED_VERSION}", s.version));
        }
        if s.title.trim().is_empty() {
            self.error("title", "the title is empty");
        }
        for (name, value) in [("width", s.canvas.width), ("height", s.canvas.height)] {
            if !(16..=7680).contains(&value) {
                self.error(format!("canvas.{name}"), format!("{value} is outside the supported range 16 to 7680"));
            } else if value % 2 != 0 {
                self.error(format!("canvas.{name}"), format!("{value} is odd; H.264 video needs an even {name}"));
            }
        }
        if !(1..=120).contains(&s.canvas.fps) {
            self.error("canvas.fps", format!("{} is outside the supported range 1 to 120", s.canvas.fps));
        }
    }

    fn objects(&mut self, script: &Script) -> World {
        let mut first: BTreeMap<&str, usize> = BTreeMap::new();
        for (i, o) in script.objects.iter().enumerate() {
            let path = format!("objects[{i}]");
            let kind = o.kind.kind();

            if !is_valid_id(&o.id) {
                self.error(
                    format!("{path}.id"),
                    format!(
                        "`{}` is not a valid id; start with a lowercase letter or `_` and use only lowercase letters, digits and `_`",
                        o.id
                    ),
                );
            } else if let Some(earlier) = first.get(o.id.as_str()) {
                self.error(format!("{path}.id"), format!("duplicate id `{}`; it is already used by objects[{earlier}]", o.id));
            } else {
                first.insert(&o.id, i);
            }

            match (kind.is_placed(), o.region) {
                (true, None) => self.error(
                    &path,
                    format!("{} `{}` needs a `region`: title, center, left, right or bottom", kind.name(), o.id),
                ),
                (false, Some(_)) => self.error(
                    format!("{path}.region"),
                    format!("{} `{}` attaches to other objects and takes no `region`", kind.name(), o.id),
                ),
                _ => {}
            }
            self.report(&path, o.kind.check());
        }

        // With every object known, check what pointers and arrows attach to.
        let world = World::new(script);
        for (i, item) in world.items.iter().enumerate() {
            let mut problems = vec![];
            match &item.body {
                Body::Pointer(p) => {
                    world.attachment(&p.target, "target", "a pointer", &mut problems);
                }
                Body::Arrow(a) => {
                    world.attachment(&a.from, "from", "an arrow", &mut problems);
                    world.attachment(&a.to, "to", "an arrow", &mut problems);
                }
                _ => {}
            }
            self.report(&format!("objects[{i}]"), problems);
        }
        world
    }

    fn scenes(&mut self, s: &Script, world: &mut World) {
        if s.scenes.is_empty() {
            self.error("scenes", "a script needs at least one scene");
        }
        let mut seen: BTreeMap<&str, usize> = BTreeMap::new();
        for (i, scene) in s.scenes.iter().enumerate() {
            let path = format!("scenes[{i}]");
            if !is_valid_id(&scene.id.replace('-', "_")) {
                self.error(
                    format!("{path}.id"),
                    format!("`{}` is not a valid scene id; use lowercase letters, digits, `_` and `-`", scene.id),
                );
            } else if let Some(first) = seen.insert(&scene.id, i) {
                self.error(format!("{path}.id"), format!("duplicate scene id `{}`; it is already used by scenes[{first}]", scene.id));
            }
            if scene.steps.is_empty() {
                self.error(format!("{path}.steps"), "a scene needs at least one step");
            }
            for (j, step) in scene.steps.iter().enumerate() {
                self.step(step, &format!("{path}.steps[{j}]"), world);
            }
        }
    }

    fn step(&mut self, step: &Step, path: &str, world: &mut World) {
        if !step.say.contains_key("en") {
            self.error(
                format!("{path}.say"),
                "missing `en` narration; every step needs English text, which other languages are translated from",
            );
        }
        for (lang, text) in &step.say {
            let p = format!("{path}.say.{lang}");
            let ok_code = (2..=8).contains(&lang.len()) && lang.chars().all(|c| c.is_ascii_alphabetic() || c == '-');
            if !ok_code {
                self.error(&p, format!("`{lang}` is not a language code such as `en`, `te` or `hi-IN`"));
            }
            let chars = text.chars().count();
            if text.trim().is_empty() {
                self.error(&p, "the narration is empty; every step must say something");
            } else if chars > MAX_SAY_CHARS {
                self.error(
                    &p,
                    format!("{chars} characters is over the {MAX_SAY_CHARS} the voice service accepts per request; split the step"),
                );
            } else if chars > LONG_SAY_CHARS {
                self.warn(&p, format!("{chars} characters is long for one step; one step should be one sentence"));
            }
        }
        for (k, action) in step.actions.iter().enumerate() {
            let p = format!("{path}.do[{k}]");
            if !(0.0..=1.0).contains(&action.delay) {
                self.error(
                    format!("{p}.delay"),
                    format!("{} is outside 0 to 1; `delay` is a fraction of the step", action.delay),
                );
            }
            let problems = world.apply(&action.kind);
            self.report(&p, problems);
        }
    }

    fn unused(&mut self, world: &World) {
        for (i, item) in world.items.iter().enumerate() {
            if !item.seen {
                self.warn(
                    format!("objects[{i}]"),
                    format!("`{}` is never shown; objects start hidden, so add a `show` or set `visible: true`", item.id),
                );
            }
        }
    }
}
