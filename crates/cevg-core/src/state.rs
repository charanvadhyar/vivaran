//! The world: what every object looks like at one moment of a script.
//!
//! A [`World`] starts from the script's `objects` and changes only through
//! [`World::apply`], which checks an action against the current state and
//! then carries it out. The validator and the renderer both replay scripts
//! through this one function, so what the validator accepts is exactly what
//! the renderer can draw.

use crate::families::{ActError, Body, Changed, Emphasis, Kind, Problem};
use crate::script::{ActionKind, Region, Script};
use crate::target::{Part, Target};

#[derive(Debug, Clone, PartialEq)]
pub struct Item {
    pub id: String,
    pub region: Option<Region>,
    pub visible: bool,
    /// Whether the object has been visible at any point so far.
    pub seen: bool,
    /// Emphasis of the object as a whole. Parts may carry their own.
    pub emphasis: Emphasis,
    pub body: Body,
}

#[derive(Debug, Clone, PartialEq)]
pub struct World {
    /// In declaration order, which is also the paint order.
    pub items: Vec<Item>,
}

/// A step in a script, by position.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Position {
    pub scene: usize,
    pub step: usize,
}

impl Position {
    /// Find a step by scene id and zero-based step number. With no scene the
    /// last scene is used; with no step, the last step of that scene.
    pub fn locate(script: &Script, scene: Option<&str>, step: Option<usize>) -> Result<Position, String> {
        let scene_index = match scene {
            None => script.scenes.len().checked_sub(1).ok_or("the script has no scenes")?,
            Some(id) => script.scenes.iter().position(|s| s.id == id).ok_or_else(|| {
                let ids: Vec<&str> = script.scenes.iter().map(|s| s.id.as_str()).collect();
                format!("no scene `{id}`; the scenes are: {}", ids.join(", "))
            })?,
        };
        let steps = script.scenes[scene_index].steps.len();
        let step_index = match step {
            None => steps.checked_sub(1).ok_or("the scene has no steps")?,
            Some(n) if n < steps => n,
            Some(n) => {
                return Err(format!(
                    "no step {n} in scene `{}`; it has steps 0 to {}",
                    script.scenes[scene_index].id,
                    steps.saturating_sub(1)
                ))
            }
        };
        Ok(Position { scene: scene_index, step: step_index })
    }
}

impl World {
    /// The world before any step has played.
    pub fn new(script: &Script) -> World {
        let items = script
            .objects
            .iter()
            .map(|o| Item {
                id: o.id.clone(),
                region: o.region,
                visible: o.visible,
                seen: o.visible,
                emphasis: Emphasis::Normal,
                body: Body::new(&o.kind),
            })
            .collect();
        World { items }
    }

    /// The world once the given step has finished.
    pub fn at(script: &Script, pos: Position) -> World {
        let mut world = World::new(script);
        for (i, scene) in script.scenes.iter().enumerate().take(pos.scene + 1) {
            let last = if i == pos.scene { pos.step + 1 } else { scene.steps.len() };
            for step in scene.steps.iter().take(last) {
                for action in &step.actions {
                    world.apply(&action.kind);
                }
            }
        }
        world
    }

    pub fn get(&self, id: &str) -> Option<&Item> {
        self.items.iter().find(|i| i.id == id)
    }

    fn index(&self, id: &str) -> Option<usize> {
        self.items.iter().position(|i| i.id == id)
    }

    /// Check an action against the current state and, if it is possible,
    /// carry it out. An action that cannot be carried out is skipped.
    pub fn apply(&mut self, action: &ActionKind) -> Vec<Problem> {
        let mut out = vec![];
        self.apply_into(action, &mut out);
        out
    }

    fn apply_into(&mut self, action: &ActionKind, out: &mut Vec<Problem>) -> Option<()> {
        let name = action.name();
        match action {
            ActionKind::Show { target } | ActionKind::Hide { target } => {
                let show = matches!(action, ActionKind::Show { .. });
                let i = self.whole(target, "target", name, out)?;
                let item = &mut self.items[i];
                if item.visible == show {
                    let state = if show { "visible" } else { "hidden" };
                    out.push(Problem::warn("target", format!("`{}` is already {state}, so `{name}` has no effect", item.id)));
                }
                item.visible = show;
                item.seen |= show;
            }
            ActionKind::Highlight { target } | ActionKind::Mark { target } | ActionKind::Dim { target } | ActionKind::Reset { target } => {
                let emphasis = match action {
                    ActionKind::Highlight { .. } => Emphasis::Highlight,
                    ActionKind::Mark { .. } => Emphasis::Mark,
                    ActionKind::Dim { .. } => Emphasis::Dim,
                    _ => Emphasis::Normal,
                };
                let i = self.part(target, "target", out)?;
                self.needs_visible(i, "target", name, out);
                let item = &mut self.items[i];
                if target.is_whole() {
                    item.emphasis = emphasis;
                    if emphasis == Emphasis::Normal {
                        item.body.repaint(None, Emphasis::Normal);
                    }
                } else {
                    // Highlight is the moving focus: it leaves the parts
                    // that were lit before.
                    if emphasis == Emphasis::Highlight {
                        item.body.repaint(Some(Emphasis::Highlight), Emphasis::Normal);
                    }
                    item.body.emphasize(&target.part, emphasis);
                }
            }
            ActionKind::Move { target, region } => {
                let i = self.whole(target, "target", name, out)?;
                let item = &mut self.items[i];
                if !item.body.kind().is_placed() {
                    out.push(Problem::error(
                        "target",
                        format!("`move` works on objects that sit in a region, but `{}` is {}", item.id, item.body.kind().a()),
                    ));
                    return None;
                }
                item.region = Some(*region);
                self.needs_visible(i, "target", name, out);
            }
            ActionKind::Swap { a, b } | ActionKind::Compare { a, b } => {
                let ia = self.cell(a, "a", name, out);
                let ib = self.cell(b, "b", name, out);
                let ((oa, ca), (ob, cb)) = (ia?, ib?);
                if a == b {
                    out.push(Problem::error("", format!("`{name}` uses the same cell `{a}` on both sides")));
                    return None;
                }
                if matches!(action, ActionKind::Swap { .. }) {
                    if oa == ob {
                        self.array(oa).swap(ca, cb);
                    } else {
                        let vb = self.array(ob).cells[cb].value.clone();
                        let va = self.array(oa).exchange(ca, vb);
                        self.array(ob).exchange(cb, va);
                    }
                } else {
                    // Both cells take the focus together.
                    for (o, c) in [(oa, None), (ob, None), (oa, Some(ca)), (ob, Some(cb))] {
                        match c {
                            None => self.items[o].body.repaint(Some(Emphasis::Highlight), Emphasis::Normal),
                            Some(c) => self.array(o).cells[c].emphasis = Emphasis::Highlight,
                        }
                    }
                }
            }
            ActionKind::Point { target, to } => {
                let i = self.whole_of(target, Kind::Pointer, action, out);
                let ok = self.attachment(to, "to", "a pointer", out);
                if let (Some(i), Some(())) = (i, ok) {
                    if let Body::Pointer(p) = &mut self.items[i].body {
                        p.target = to.clone();
                    }
                }
            }
            ActionKind::Draw { target } => {
                let i = self.whole_of(target, Kind::Arrow, action, out)?;
                self.items[i].visible = true;
                self.items[i].seen = true;
            }
            ActionKind::Retarget { target, from, to } => {
                let i = self.whole_of(target, Kind::Arrow, action, out);
                if from.is_none() && to.is_none() {
                    out.push(Problem::error("", "`retarget` needs `from`, `to` or both"));
                    return None;
                }
                let ok_from = from.as_ref().map_or(Some(()), |t| self.attachment(t, "from", "an arrow", out));
                let ok_to = to.as_ref().map_or(Some(()), |t| self.attachment(t, "to", "an arrow", out));
                if let (Some(i), Some(()), Some(())) = (i, ok_from, ok_to) {
                    if let Body::Arrow(arrow) = &mut self.items[i].body {
                        if let Some(from) = from {
                            arrow.from = from.clone();
                        }
                        if let Some(to) = to {
                            arrow.to = to.clone();
                        }
                    }
                }
            }
            // Everything else belongs to one family.
            _ => {
                let target = action.target()?;
                let i = self.find(target, "target", out)?;
                let item = &mut self.items[i];
                match item.body.act(&item.id, action) {
                    Ok(changed) => {
                        if matches!(action, ActionKind::Write { .. }) {
                            item.visible = true;
                            item.seen = true;
                        } else {
                            self.needs_visible(i, "target", name, out);
                        }
                        if changed == Changed::Structure {
                            self.stranded(out);
                        }
                    }
                    Err(ActError::Unsupported) => {
                        out.push(Problem::error(
                            "target",
                            format!("`{name}` works on {}, but `{}` is {}", action.works_on(), item.id, item.body.kind().a()),
                        ));
                        return None;
                    }
                    Err(ActError::At(field, message)) => {
                        out.push(Problem::error(field, message));
                        return None;
                    }
                }
            }
        }
        Some(())
    }

    // ----------------------------------------------------------- helpers

    fn array(&mut self, i: usize) -> &mut crate::families::array::State {
        match &mut self.items[i].body {
            Body::Array(a) => a,
            _ => unreachable!("checked by `cell`"),
        }
    }

    /// The object a target names.
    fn find(&self, t: &Target, field: &str, out: &mut Vec<Problem>) -> Option<usize> {
        let found = self.index(&t.object);
        if found.is_none() {
            let known: Vec<&str> = self.items.iter().map(|i| i.id.as_str()).collect();
            let known = if known.is_empty() { "(none)".to_string() } else { known.join(", ") };
            out.push(Problem::error(field, format!("unknown object `{}`; the defined objects are: {known}", t.object)));
        }
        found
    }

    /// The object a target names, with the part checked against its state.
    fn part(&self, t: &Target, field: &str, out: &mut Vec<Problem>) -> Option<usize> {
        let i = self.find(t, field, out)?;
        if let Err(message) = self.items[i].body.check_part(&t.object, &t.part) {
            out.push(Problem::error(field, message));
            return None;
        }
        Some(i)
    }

    /// The target must name a whole object.
    fn whole(&self, t: &Target, field: &str, action: &str, out: &mut Vec<Problem>) -> Option<usize> {
        let i = self.part(t, field, out)?;
        if !t.is_whole() {
            out.push(Problem::error(field, format!("`{action}` takes a whole object; use `{}` instead of `{t}`", t.object)));
            return None;
        }
        Some(i)
    }

    /// The target must name a whole object of one kind.
    fn whole_of(&self, t: &Target, kind: Kind, action: &ActionKind, out: &mut Vec<Problem>) -> Option<usize> {
        let i = self.find(t, "target", out)?;
        let item = &self.items[i];
        if item.body.kind() != kind {
            out.push(Problem::error(
                "target",
                format!("`{}` works on {}, but `{}` is {}", action.name(), action.works_on(), item.id, item.body.kind().a()),
            ));
            return None;
        }
        self.whole(t, "target", action.name(), out)
    }

    /// The target must be exactly one array cell: (object index, cell index).
    fn cell(&self, t: &Target, field: &str, action: &str, out: &mut Vec<Problem>) -> Option<(usize, usize)> {
        let i = self.find(t, field, out)?;
        let item = &self.items[i];
        let Body::Array(array) = &item.body else {
            out.push(Problem::error(
                field,
                format!("`{action}` needs an array cell, but `{}` is {}", item.id, item.body.kind().a()),
            ));
            return None;
        };
        match array.one_cell(&item.id, &t.part, action) {
            Ok(c) => {
                self.needs_visible(i, field, action, out);
                Some((i, c))
            }
            Err(message) => {
                out.push(Problem::error(field, message));
                None
            }
        }
    }

    /// A pointer or arrow end must sit on a part of a placed object.
    pub fn attachment(&self, t: &Target, field: &str, what: &str, out: &mut Vec<Problem>) -> Option<()> {
        let i = self.part(t, field, out)?;
        let kind = self.items[i].body.kind();
        if !kind.is_placed() {
            out.push(Problem::error(
                field,
                format!("{what} attaches to an object that sits in a region, but `{}` is {}", t.object, kind.a()),
            ));
            return None;
        }
        Some(())
    }

    fn needs_visible(&self, i: usize, field: &str, action: &str, out: &mut Vec<Problem>) {
        let item = &self.items[i];
        // Moving a hidden pointer into place before showing it is normal.
        if !item.visible && item.body.kind().is_placed() {
            out.push(Problem::warn(
                field,
                format!("`{}` is hidden at this point, so `{action}` will not be seen; add a `show` first", item.id),
            ));
        }
    }

    /// After parts were added or removed, nothing may be left attached to a
    /// part that no longer exists.
    fn stranded(&self, out: &mut Vec<Problem>) {
        for item in &self.items {
            let ends: Vec<&Target> = match &item.body {
                Body::Pointer(p) => vec![&p.target],
                Body::Arrow(a) => vec![&a.from, &a.to],
                _ => continue,
            };
            for end in ends {
                let gone = self.get(&end.object).is_some_and(|o| o.body.check_part(&end.object, &end.part).is_err());
                if gone && end.part != Part::Whole {
                    out.push(Problem::error(
                        "",
                        format!(
                            "this leaves {} `{}` on {end}, which no longer exists; move it first",
                            item.body.kind().name(),
                            item.id
                        ),
                    ));
                }
            }
        }
    }
}
