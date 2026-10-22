//! Timeline family: lanes over a shared time axis. Script type `timeline`.
//!
//! Blocks sit in a lane from a start time to an end time: a CPU scheduling
//! chart, the stages of a pipeline, who holds a lock. Messages are arrows
//! from one lane to another: a protocol handshake. A cursor marks "now".
//!
//! Parts: `t.name` for a block, a message or a lane. Actions: `add_block`,
//! `add_message`, `advance` (moves the cursor), `set` (a label), `remove`.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{Cx, Rect};
use crate::script::ActionKind;
use crate::target::{is_valid_name, Part};
use crate::text::{Face, HAlign};
use serde::Deserialize;

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BlockSpec {
    pub id: String,
    pub lane: String,
    pub start: f64,
    pub end: f64,
    /// Shown inside the block. Defaults to nothing.
    #[serde(default)]
    pub label: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MessageSpec {
    pub id: String,
    pub from: String,
    pub to: String,
    /// When it leaves `from`.
    pub at: f64,
    /// When it reaches `to`. Defaults to `at`.
    #[serde(default)]
    pub arrive: Option<f64>,
    #[serde(default)]
    pub label: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    pub lanes: Vec<String>,
    /// The right edge of the time axis. Defaults to the latest time used;
    /// giving it keeps the axis still while blocks are added.
    #[serde(default)]
    pub end: Option<f64>,
    /// Written under the axis: "ms", "clock cycle".
    #[serde(default)]
    pub unit: Option<String>,
    #[serde(default)]
    pub blocks: Vec<BlockSpec>,
    #[serde(default)]
    pub messages: Vec<MessageSpec>,
    /// Where the "now" cursor starts. Without it there is no cursor until
    /// an `advance`.
    #[serde(default)]
    pub now: Option<f64>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub lanes: Vec<(String, Emphasis)>,
    pub end: Option<f64>,
    pub unit: Option<String>,
    pub blocks: Vec<(BlockSpec, Emphasis)>,
    pub messages: Vec<(MessageSpec, Emphasis)>,
    pub now: Option<f64>,
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    if spec.lanes.is_empty() {
        out.push(Problem::error("lanes", "a timeline needs at least one lane"));
    }
    for (i, lane) in spec.lanes.iter().enumerate() {
        if spec.lanes[..i].contains(lane) {
            out.push(Problem::error(format!("lanes[{i}]"), format!("duplicate lane `{lane}`")));
        }
    }
    if spec.end.is_some_and(|e| e <= 0.0) {
        out.push(Problem::error("end", "`end` must be above 0"));
    }
    // Replay through the same checks the add actions use.
    let mut state = State::new(&Spec { blocks: vec![], messages: vec![], ..spec.clone() });
    for (i, block) in spec.blocks.iter().enumerate() {
        match state.block_problem(block) {
            Some((field, message)) => out.push(Problem::error(format!("blocks[{i}]{field}"), message)),
            None => state.blocks.push((block.clone(), Emphasis::Normal)),
        }
    }
    for (i, message) in spec.messages.iter().enumerate() {
        match state.message_problem(message) {
            Some((field, text)) => out.push(Problem::error(format!("messages[{i}]{field}"), text)),
            None => state.messages.push((message.clone(), Emphasis::Normal)),
        }
    }
    out
}

/// Tick step at a round number, about eight across the axis.
fn tick_step(end: f64) -> f64 {
    let rough = end / 8.0;
    let power = 10f64.powf(rough.log10().floor());
    [1.0, 2.0, 5.0, 10.0].iter().map(|m| m * power).find(|s| *s >= rough).unwrap_or(power * 10.0)
}

fn number(t: f64) -> String {
    if (t - t.round()).abs() < 1e-9 {
        format!("{}", t.round() as i64)
    } else {
        format!("{t:.2}").trim_end_matches('0').trim_end_matches('.').to_string()
    }
}

impl State {
    pub fn new(spec: &Spec) -> State {
        let fresh = Emphasis::Normal;
        State {
            lanes: spec.lanes.iter().map(|l| (l.clone(), fresh)).collect(),
            end: spec.end,
            unit: spec.unit.clone(),
            blocks: spec.blocks.iter().map(|b| (b.clone(), fresh)).collect(),
            messages: spec.messages.iter().map(|m| (m.clone(), fresh)).collect(),
            now: spec.now,
        }
    }

    fn lane(&self, name: &str) -> Option<usize> {
        self.lanes.iter().position(|(l, _)| l == name)
    }

    fn id_taken(&self, id: &str) -> bool {
        self.blocks.iter().any(|(b, _)| b.id == id) || self.messages.iter().any(|(m, _)| m.id == id)
    }

    fn id_problem(&self, id: &str) -> Option<(&'static str, String)> {
        if !is_valid_name(id) {
            return Some((".id", format!("`{id}` is not a valid id; use only letters, digits and `_`")));
        }
        if self.id_taken(id) {
            return Some((".id", format!("duplicate id `{id}`; blocks and messages share one set of ids")));
        }
        None
    }

    fn lane_problem(&self, lane: &str, field: &'static str) -> Option<(&'static str, String)> {
        if self.lane(lane).is_some() {
            return None;
        }
        let lanes: Vec<&str> = self.lanes.iter().map(|(l, _)| l.as_str()).collect();
        Some((field, format!("no lane `{lane}`; the lanes are: {}", lanes.join(", "))))
    }

    fn block_problem(&self, b: &BlockSpec) -> Option<(&'static str, String)> {
        self.id_problem(&b.id).or_else(|| self.lane_problem(&b.lane, ".lane")).or_else(|| {
            if !(b.start >= 0.0 && b.end > b.start && b.end.is_finite()) {
                return Some(("", format!("a block needs 0 <= start < end, but got start {} and end {}", b.start, b.end)));
            }
            let clash = self.blocks.iter().find(|(o, _)| o.lane == b.lane && o.start < b.end && b.start < o.end);
            clash.map(|(o, _)| ("", format!("this overlaps block `{}` in lane `{}` ({} to {})", o.id, o.lane, number(o.start), number(o.end))))
        })
    }

    fn message_problem(&self, m: &MessageSpec) -> Option<(&'static str, String)> {
        self.id_problem(&m.id)
            .or_else(|| self.lane_problem(&m.from, ".from"))
            .or_else(|| self.lane_problem(&m.to, ".to"))
            .or_else(|| {
                if m.from == m.to {
                    return Some(("", format!("a message goes between two lanes, but both ends are `{}`", m.from)));
                }
                let arrive = m.arrive.unwrap_or(m.at);
                if !(m.at >= 0.0 && arrive >= m.at && arrive.is_finite()) {
                    return Some(("", format!("a message needs 0 <= at <= arrive, but got at {} and arrive {arrive}", m.at)));
                }
                None
            })
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        match part {
            Part::Name(name) if self.id_taken(name) || self.lane(name).is_some() => Ok(()),
            Part::Name(name) => Err(format!("`{id}` has no block, message or lane named `{name}`")),
            _ => Err(format!("`{id}{part}` is not a part of a timeline; use `{id}.name` for a block, a message or a lane")),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        let Part::Name(name) = part else { return };
        if let Some((_, e)) = self.blocks.iter_mut().find(|(b, _)| b.id == *name) {
            *e = emphasis;
        } else if let Some((_, e)) = self.messages.iter_mut().find(|(m, _)| m.id == *name) {
            *e = emphasis;
        } else if let Some((_, e)) = self.lanes.iter_mut().find(|(l, _)| l == name) {
            *e = emphasis;
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.blocks.iter_mut().for_each(|b| f(&mut b.1));
        self.messages.iter_mut().for_each(|m| f(&mut m.1));
        self.lanes.iter_mut().for_each(|l| f(&mut l.1));
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        let whole = |target: &crate::target::Target, name: &str| {
            if target.is_whole() {
                Ok(())
            } else {
                at("target", format!("`{name}` takes the whole timeline; use `{id}`"))
            }
        };
        match action {
            ActionKind::AddBlock { target, id: block_id, lane, start, end, label } => {
                whole(target, "add_block")?;
                let block = BlockSpec { id: block_id.clone(), lane: lane.clone(), start: *start, end: *end, label: label.clone() };
                if let Some((field, message)) = self.block_problem(&block) {
                    return at(field.trim_start_matches('.'), message);
                }
                self.blocks.push((block, Emphasis::Normal));
                Ok(Changed::Structure)
            }
            ActionKind::AddMessage { target, id: message_id, from, to, at: leave, arrive, label } => {
                whole(target, "add_message")?;
                let message = MessageSpec {
                    id: message_id.clone(),
                    from: from.clone(),
                    to: to.clone(),
                    at: *leave,
                    arrive: *arrive,
                    label: label.clone(),
                };
                if let Some((field, text)) = self.message_problem(&message) {
                    return at(field.trim_start_matches('.'), text);
                }
                self.messages.push((message, Emphasis::Normal));
                Ok(Changed::Structure)
            }
            ActionKind::Advance { target, to } => {
                whole(target, "advance")?;
                if !(*to >= 0.0 && to.is_finite()) {
                    return at("to", format!("{to} is not a time on the axis; it must be 0 or more"));
                }
                self.now = Some(*to);
                Ok(Changed::Content)
            }
            ActionKind::Set { target, value } => {
                let Part::Name(name) = &target.part else {
                    return at("target", format!("`set` on a timeline needs a block or a message such as `{id}.name`"));
                };
                if let Some((b, _)) = self.blocks.iter_mut().find(|(b, _)| b.id == *name) {
                    b.label = Some(value.to_string());
                } else if let Some((m, _)) = self.messages.iter_mut().find(|(m, _)| m.id == *name) {
                    m.label = Some(value.to_string());
                } else {
                    return at("target", format!("`{id}` has no block or message `{name}` to set"));
                }
                Ok(Changed::Content)
            }
            ActionKind::Remove { target } => {
                let Part::Name(name) = &target.part else {
                    return at("target", format!("`remove` on a timeline takes a block or a message such as `{id}.name`"));
                };
                if !self.id_taken(name) {
                    return at("target", format!("`{id}` has no block or message `{name}` to remove"));
                }
                self.blocks.retain(|(b, _)| b.id != *name);
                self.messages.retain(|(m, _)| m.id != *name);
                Ok(Changed::Structure)
            }
            _ => Err(ActError::Unsupported),
        }
    }

    /// The right edge of the axis: the given `end`, stretched if something
    /// reaches past it.
    fn span(&self) -> f64 {
        let used = self
            .blocks
            .iter()
            .map(|(b, _)| b.end)
            .chain(self.messages.iter().map(|(m, _)| m.arrive.unwrap_or(m.at)))
            .chain(self.now)
            .fold(0.0f64, f64::max);
        let end = self.end.unwrap_or(0.0).max(used);
        if end > 0.0 { end } else { 1.0 }
    }

    /// The chart area (right of the lane names, above the axis) and the
    /// height of one lane.
    fn frame(&self, slot: Rect, cx: &mut Cx) -> (Rect, f32) {
        let u = cx.u;
        let names = self.lanes.iter().map(|(l, _)| cx.fonts.measure(l, 34.0 * u, Face::SansBold, None).0).fold(0.0f32, f32::max);
        let left = names + 40.0 * u;
        // Room under the lanes for the axis, and above them for the cursor's
        // label.
        let (top, bottom) = (56.0 * u, 96.0 * u);
        let lane_h = ((slot.h - top - bottom) / self.lanes.len().max(1) as f32).min(170.0 * u);
        let h = lane_h * self.lanes.len().max(1) as f32;
        let w = slot.w - left - 30.0 * u;
        let y = slot.cy() - (top + h + bottom) / 2.0 + top;
        (Rect { x: slot.x + left, y, w, h }, lane_h)
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let (area, lane_h) = self.frame(slot, cx);
        let span = self.span();
        let x = |t: f64| area.x + (t / span) as f32 * area.w;
        let lane_y = |name: &str| area.y + self.lane(name).unwrap_or(0) as f32 * lane_h;
        let mut nodes = vec![];
        for (b, _) in &self.blocks {
            let pad = lane_h * 0.16;
            nodes.push((b.id.clone(), Rect { x: x(b.start), y: lane_y(&b.lane) + pad, w: x(b.end) - x(b.start), h: lane_h - 2.0 * pad }));
        }
        for (m, _) in &self.messages {
            let (x0, x1) = (x(m.at), x(m.arrive.unwrap_or(m.at)));
            let (y0, y1) = (lane_y(&m.from) + lane_h / 2.0, lane_y(&m.to) + lane_h / 2.0);
            nodes.push((m.id.clone(), Rect { x: (x0 + x1) / 2.0 - 6.0, y: (y0 + y1) / 2.0 - 6.0, w: 12.0, h: 12.0 }));
        }
        for (i, (name, _)) in self.lanes.iter().enumerate() {
            nodes.push((name.clone(), Rect { x: area.x, y: area.y + i as f32 * lane_h, w: area.w, h: lane_h }));
        }
        Placed { bounds: area, skirt: 8.0 * cx.u, scale: (lane_h / (120.0 * cx.u)).min(1.0), geometry: Geometry::Nodes(nodes) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let Geometry::Nodes(rects) = &placed.geometry else { return };
        let (pal, u, area) = (cx.pal, cx.u, placed.bounds);
        let frame = cx.tone(Emphasis::Normal, whole);
        let lane_h = area.h / self.lanes.len().max(1) as f32;
        let span = self.span();
        let x = |t: f64| area.x + (t / span) as f32 * area.w;
        let rect_of = |id: &str| rects.iter().find(|(n, _)| n == id).map(|(_, r)| *r);
        let small = 26.0 * u;

        // Lanes: a faint band each, with the name to the left.
        for (i, (name, emphasis)) in self.lanes.iter().enumerate() {
            cx.at(format!("lane {name}"));
            let tone = cx.tone(*emphasis, whole);
            let band = Rect { x: area.x, y: area.y + i as f32 * lane_h, w: area.w, h: lane_h };
            let shade = if tone.heavy { tone.fill } else { pal.surface };
            let strength = if tone.heavy { 1.0 } else if i % 2 == 0 { 0.7 } else { 0.35 };
            cx.fill_rect(band, shade, tone.box_opacity * strength);
            let face = Face::SansBold;
            cx.text(name, 34.0 * u * placed.scale.max(0.7), face, tone.ink, tone.ink_opacity, area.x - 20.0 * u, band.cy(), HAlign::Right, None);
        }

        // Time axis. Ticks are named by their time, so they slide if the
        // axis stretches.
        let step = tick_step(span);
        let mut t = 0.0;
        while t <= span + 1e-9 {
            cx.at(format!("tick {t:.6}"));
            cx.line((x(t), area.y), (x(t), area.bottom() + 10.0 * u), pal.border, 1.5 * u, frame.box_opacity * 0.6);
            cx.text(&number(t), small, Face::Sans, pal.muted, frame.ink_opacity, x(t), area.bottom() + small * 1.2, HAlign::Center, None);
            t += step;
        }
        cx.at("axis");
        cx.line((area.x, area.bottom()), (area.x + area.w, area.bottom()), pal.muted, 3.0 * u, frame.box_opacity);
        let unit = self.unit.as_deref().unwrap_or("");
        cx.text(unit, 28.0 * u, Face::SansBold, pal.text, frame.ink_opacity, area.cx(), area.bottom() + small * 1.2 + 44.0 * u, HAlign::Center, None);

        // Blocks, coloured by lane.
        for (b, emphasis) in &self.blocks {
            let Some(rect) = rect_of(&b.id) else { continue };
            cx.at(format!("block {}", b.id));
            let tone = cx.tone(*emphasis, whole);
            let lane = self.lane(&b.lane).unwrap_or(0);
            let color = if tone.heavy { tone.border } else { pal.pointers[lane % pal.pointers.len()] };
            let radius = 10.0 * u;
            cx.fill_round_rect(rect, radius, pal.background, tone.box_opacity);
            cx.fill_round_rect(rect, radius, color, tone.box_opacity * 0.3);
            let width = if tone.heavy { 5.0 * u } else { 3.0 * u };
            cx.stroke_round_rect(rect.inset(width / 2.0), radius, color, width, tone.box_opacity);
            let label = b.label.as_deref().unwrap_or("");
            let size = cx.fit(label, (rect.h * 0.5).min(34.0 * u), Face::SansBold, (rect.w * 0.86).max(1.0));
            let ink = if tone.heavy { tone.ink } else { pal.text };
            cx.text(label, size, Face::SansBold, ink, tone.ink_opacity, rect.cx(), rect.cy(), HAlign::Center, None);
        }

        // Messages: an arrow from one lane to another. Labels sit on a
        // patch of background beside the middle of the arrow, alternately
        // above and below it, so that neighbours do not run into each other.
        for (i, (m, emphasis)) in self.messages.iter().enumerate() {
            cx.at(format!("message {}", m.id));
            let tone = cx.tone(*emphasis, whole);
            let color = if tone.heavy { tone.border } else { pal.text };
            let lane_mid = |name: &str| area.y + (self.lane(name).unwrap_or(0) as f32 + 0.5) * lane_h;
            let (from, to) = ((x(m.at), lane_mid(&m.from)), (x(m.arrive.unwrap_or(m.at)), lane_mid(&m.to)));
            cx.arrow(from, to, color, if tone.heavy { 5.5 * u } else { 4.0 * u }, tone.ink_opacity);
            let label = m.label.as_deref().unwrap_or("");
            let size = 28.0 * u;
            let (w, _) = cx.fonts.measure(label, size, Face::SansBold, None);
            let side = if i % 2 == 0 { -1.0 } else { 1.0 };
            let (mx, my) = ((from.0 + to.0) / 2.0, (from.1 + to.1) / 2.0 + side * size * 1.1);
            let patch = Rect { x: mx - w / 2.0 - size * 0.4, y: my - size * 0.75, w: w + size * 0.8, h: size * 1.5 };
            cx.fill_round_rect(patch, size * 0.4, pal.background, if label.is_empty() { 0.0 } else { tone.ink_opacity * 0.9 });
            cx.text(label, size, Face::SansBold, color, tone.ink_opacity, mx, my, HAlign::Center, None);
        }

        // The cursor, on top.
        if let Some(now) = self.now {
            cx.at("now");
            let nx = x(now);
            cx.line((nx, area.y - 14.0 * u), (nx, area.bottom()), pal.accent, 4.0 * u, frame.box_opacity);
            cx.text(&format!("t = {}", number(now)), small, Face::SansBold, pal.accent, frame.ink_opacity, nx, area.y - 34.0 * u, HAlign::Center, None);
        }
    }
}
