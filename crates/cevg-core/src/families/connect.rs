//! Pointers and arrows: marks that attach to parts of other objects.
//!
//! They take no region. Each frame they look up the box of whatever they
//! attach to, so they follow it wherever layout puts it.

use super::{Body, Emphasis};
use crate::render::{edge_point, Cx, Rect};
use crate::state::World;
use crate::target::Target;
use crate::text::{Face, HAlign};
use serde::Deserialize;
use std::collections::BTreeMap;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PointerSpec {
    pub label: String,
    pub target: Target,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ArrowSpec {
    pub from: Target,
    pub to: Target,
    #[serde(default)]
    pub label: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Pointer {
    pub label: String,
    pub target: Target,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Arrow {
    pub from: Target,
    pub to: Target,
    pub label: Option<String>,
}

impl Pointer {
    pub fn new(spec: &PointerSpec) -> Pointer {
        Pointer { label: spec.label.clone(), target: spec.target.clone() }
    }
}

impl Arrow {
    pub fn new(spec: &ArrowSpec) -> Arrow {
        Arrow { from: spec.from.clone(), to: spec.to.clone(), label: spec.label.clone() }
    }
}

/// Where a target is on screen.
pub struct Spot {
    pub rect: Rect,
    /// Room to leave under the target (index labels under array cells).
    pub skirt: f32,
    /// Other parts of the same object, which a pointer should not cover.
    pub neighbours: Vec<Rect>,
}

/// Finds a target on screen, if it is visible.
pub type Resolve<'a> = &'a dyn Fn(&Target) -> Option<Spot>;

fn overlaps(a: &Rect, b: &Rect) -> bool {
    a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h
}

/// A pointer is a short arrow aimed at its target with the label behind it.
/// It sits under the target unless a neighbouring part is in the way (the
/// child of a tree node, say); then it tries above, right and left.
/// Pointers that share a target stack their labels. Each pointer keeps one
/// colour for the whole video.
pub fn paint_pointers(world: &World, resolve: Resolve, cx: &mut Cx) {
    let u = cx.u;
    let (reach, size) = (52.0 * u, 36.0 * u);
    let mut stacked: BTreeMap<String, usize> = BTreeMap::new();
    let pointers = world.items.iter().filter(|i| matches!(i.body, Body::Pointer(_)));

    for (ordinal, item) in pointers.enumerate() {
        let Body::Pointer(pointer) = &item.body else { continue };
        if !item.visible {
            continue;
        }
        let Some(spot) = resolve(&pointer.target) else { continue };
        cx.object(&item.id);
        let rect = spot.rect;
        let slot = stacked.entry(pointer.target.to_string()).or_insert(0);
        let color = cx.pal.pointers[ordinal % cx.pal.pointers.len()];
        let opacity = cx.tone(Emphasis::Normal, item.emphasis).ink_opacity;
        let (label_w, _) = cx.fonts.measure(&pointer.label, size, Face::SansBold, None);

        // Direction from the target toward the label: down, up, right, left.
        let side = [(0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)]
            .into_iter()
            .find(|(dx, dy): &(f32, f32)| {
                let depth = if *dx == 0.0 { spot.skirt + reach + size * 1.6 } else { reach + label_w + size };
                let area = Rect {
                    x: if *dx < 0.0 { rect.x - depth } else if *dx > 0.0 { rect.x + rect.w } else { rect.cx() - label_w / 2.0 },
                    y: if *dy < 0.0 { rect.y - depth } else if *dy > 0.0 { rect.bottom() } else { rect.cy() - size / 2.0 },
                    w: if *dx == 0.0 { label_w } else { depth },
                    h: if *dy == 0.0 { size } else { depth },
                };
                !spot.neighbours.iter().any(|n| overlaps(&area, n))
            })
            .unwrap_or((0.0, 1.0));

        let (dx, dy) = side;
        let skirt = if dy > 0.0 { spot.skirt } else { 0.0 };
        let tip = (rect.cx() + dx * (rect.w / 2.0 + 10.0 * u), rect.cy() + dy * (rect.h / 2.0 + skirt + 10.0 * u));
        let tail = (tip.0 + dx * reach, tip.1 + dy * reach);
        // Stacked pointers share the first one's arrow; the others keep an
        // invisible one so that theirs fades in if they move away.
        cx.arrow(tail, tip, color, 5.0 * u, if *slot == 0 { opacity } else { 0.0 });
        let stack = *slot as f32 * size * 1.25;
        let (x, y, align) = if dx > 0.0 {
            (tail.0 + size * 0.3, tail.1 + stack, HAlign::Left)
        } else if dx < 0.0 {
            (tail.0 - size * 0.3, tail.1 + stack, HAlign::Right)
        } else {
            (tail.0, tail.1 + dy * (size * 0.8 + stack), HAlign::Center)
        };
        cx.text(&pointer.label, size, Face::SansBold, color, opacity, x, y, align, None);
        *slot += 1;
    }
}

pub fn paint_arrows(world: &World, resolve: Resolve, cx: &mut Cx) {
    let u = cx.u;
    for item in world.items.iter().filter(|i| i.visible) {
        let Body::Arrow(arrow) = &item.body else { continue };
        let (Some(a), Some(b)) = (resolve(&arrow.from), resolve(&arrow.to)) else { continue };
        let (a, b) = (a.rect, b.rect);
        cx.object(&item.id);
        let tone = cx.tone(Emphasis::Normal, item.emphasis);
        let color = if tone.heavy { tone.border } else { cx.pal.muted };
        let start = edge_point(a, (b.cx(), b.cy()), 10.0 * u);
        let end = edge_point(b, (a.cx(), a.cy()), 10.0 * u);
        cx.arrow(start, end, color, 4.0 * u, tone.ink_opacity);
        if let Some(label) = &arrow.label {
            let (x, y) = ((start.0 + end.0) / 2.0, (start.1 + end.1) / 2.0 - 26.0 * u);
            cx.text(label, 30.0 * u, Face::Sans, color, tone.ink_opacity, x, y, HAlign::Center, None);
        }
    }
}
