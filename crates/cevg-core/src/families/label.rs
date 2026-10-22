//! Text: titles, labels and captions. Script type `text`.

use super::{ActError, ActResult, Changed, Emphasis, Geometry, Placed};
use crate::render::{Cx, Rect};
use crate::script::{ActionKind, Region};
use crate::text::{Face, HAlign};
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    pub text: String,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub text: String,
}

/// Size and face by region: titles are large and bold, captions smaller.
fn style(region: Region, u: f32) -> (f32, Face) {
    match region {
        Region::Title => (68.0 * u, Face::SansBold),
        Region::Bottom => (46.0 * u, Face::Sans),
        _ => (50.0 * u, Face::Sans),
    }
}

impl State {
    pub fn new(spec: &Spec) -> State {
        State { text: spec.text.clone() }
    }

    pub fn act(&mut self, _id: &str, action: &ActionKind) -> ActResult {
        match action {
            // `write` types the text onto the screen; the world shows it.
            ActionKind::Write { .. } => {}
            ActionKind::Replace { text, .. } => self.text = text.clone(),
            ActionKind::Set { value, .. } => self.text = value.to_string(),
            _ => return Err(ActError::Unsupported),
        }
        Ok(Changed::Content)
    }

    pub fn layout(&self, slot: Rect, region: Region, cx: &mut Cx) -> Placed {
        let (size, face) = style(region, cx.u);
        let (w, h) = cx.fonts.measure(&self.text, size, face, Some(slot.w));
        Placed {
            bounds: Rect { x: slot.cx() - w / 2.0, y: slot.cy() - h / 2.0, w, h },
            skirt: 8.0 * cx.u,
            scale: 1.0,
            geometry: Geometry::None,
        }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, region: Region, cx: &mut Cx) {
        let (size, face) = style(region, cx.u);
        let tone = cx.tone(Emphasis::Normal, whole);
        // Text that wrapped during layout must wrap the same way here.
        let (one_line, _) = cx.fonts.measure(&self.text, size, face, None);
        let max_w = (one_line > placed.bounds.w + 1.0).then_some(placed.bounds.w + 1.0);
        cx.text(&self.text, size, face, tone.ink, tone.ink_opacity, placed.bounds.cx(), placed.bounds.cy(), HAlign::Center, max_w);
    }
}
