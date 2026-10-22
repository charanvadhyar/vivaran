//! Node-link family: nodes joined by edges, laid out automatically.
//! Script type `diagram`.
//!
//! One family covers trees, graphs, neural networks, state machines, block
//! diagrams of architectures, pipelines and query plans. The script never
//! gives coordinates; it picks a `layout`:
//!
//! * `layers`  columns (or rows) by distance from the sources; a node may pin
//!   its own `layer`. Neural networks, pipelines, flowcharts.
//! * `tree`    children under their parent. Search trees, heaps, parse trees.
//! * `ring`    nodes on a circle. State machines, small graphs with cycles.
//! * `grid`    every node says its cell with `at: [column, row]`. Block
//!   diagrams where placement carries meaning.
//!
//! Parts: `g.node` and `g.from->to`. Actions: `set` a label, `remove` a node
//! or edge, `add_node`, `add_edge`.

use super::{at, ActError, ActResult, Changed, Emphasis, Geometry, Placed, Problem};
use crate::render::{edge_point, Cx, Rect};
use crate::script::ActionKind;
use crate::target::{is_valid_name, Part};
use crate::text::{Face, HAlign};
use serde::Deserialize;
use std::collections::BTreeSet;

const MAX_COMFORTABLE_NODES: usize = 24;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Layout {
    #[default]
    Layers,
    Tree,
    Ring,
    Grid,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Direction {
    Right,
    Down,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Shape {
    #[default]
    Box,
    Circle,
    Pill,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    #[serde(default)]
    pub layout: Layout,
    /// Which way the layers or tree levels run. Default: `right` for layers,
    /// `down` for trees.
    #[serde(default)]
    pub direction: Option<Direction>,
    /// The shape of every node that does not set its own.
    #[serde(default)]
    pub shape: Shape,
    /// Whether edges have arrowheads. Default true.
    #[serde(default = "yes")]
    pub directed: bool,
    pub nodes: Vec<NodeSpec>,
    #[serde(default)]
    pub edges: Vec<EdgeSpec>,
    /// Labelled boxes drawn around sets of nodes: "CPU", "hidden layer".
    #[serde(default)]
    pub groups: Vec<GroupSpec>,
}

fn yes() -> bool {
    true
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NodeSpec {
    pub id: String,
    /// Shown inside the node. Defaults to the id.
    #[serde(default)]
    pub label: Option<String>,
    #[serde(default)]
    pub shape: Option<Shape>,
    /// `layers` layout only: pin the node to this layer, counted from 0.
    #[serde(default)]
    pub layer: Option<usize>,
    /// `grid` layout only: `[column, row]`, counted from 0.
    #[serde(default)]
    pub at: Option<[usize; 2]>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EdgeSpec {
    pub from: String,
    pub to: String,
    #[serde(default)]
    pub label: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GroupSpec {
    pub label: String,
    pub nodes: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Node {
    pub spec: NodeSpec,
    pub emphasis: Emphasis,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Edge {
    pub spec: EdgeSpec,
    pub emphasis: Emphasis,
}

#[derive(Debug, Clone, PartialEq)]
pub struct State {
    pub layout: Layout,
    pub direction: Direction,
    pub shape: Shape,
    pub directed: bool,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub groups: Vec<GroupSpec>,
}

pub fn check(spec: &Spec) -> Vec<Problem> {
    let mut out = vec![];
    if spec.nodes.is_empty() {
        out.push(Problem::error("nodes", "a diagram needs at least one node"));
    }
    // Replay the nodes and edges through the same checks that `add_node` and
    // `add_edge` use, so that a spec and an action can never disagree.
    let mut state = State::new(&Spec { nodes: vec![], edges: vec![], groups: vec![], ..spec.clone() });
    for (i, node) in spec.nodes.iter().enumerate() {
        match state.node_problem(node) {
            Some((field, message)) => out.push(Problem::error(format!("nodes[{i}]{field}"), message)),
            None => state.nodes.push(Node { spec: node.clone(), emphasis: Emphasis::Normal }),
        }
        if spec.layout != Layout::Grid && node.at.is_some() {
            out.push(Problem::warn(format!("nodes[{i}].at"), "`at` only has an effect with `\"layout\": \"grid\"`"));
        }
        if spec.layout != Layout::Layers && node.layer.is_some() {
            out.push(Problem::warn(format!("nodes[{i}].layer"), "`layer` only has an effect with `\"layout\": \"layers\"`"));
        }
    }
    for (i, edge) in spec.edges.iter().enumerate() {
        match state.edge_problem(edge) {
            Some((field, message)) => out.push(Problem::error(format!("edges[{i}]{field}"), message)),
            None => state.edges.push(Edge { spec: edge.clone(), emphasis: Emphasis::Normal }),
        }
    }
    for (i, group) in spec.groups.iter().enumerate() {
        for (j, id) in group.nodes.iter().enumerate() {
            if state.node(id).is_none() {
                out.push(Problem::error(format!("groups[{i}].nodes[{j}]"), format!("no node `{id}` in this diagram")));
            }
        }
    }
    if spec.nodes.len() > MAX_COMFORTABLE_NODES {
        out.push(Problem::warn(
            "nodes",
            format!(
                "{} nodes may not fit the region at a readable size; {MAX_COMFORTABLE_NODES} or fewer is safe",
                spec.nodes.len()
            ),
        ));
    }
    out
}

impl State {
    pub fn new(spec: &Spec) -> State {
        let fresh = Emphasis::Normal;
        State {
            layout: spec.layout,
            direction: spec.direction.unwrap_or(match spec.layout {
                Layout::Tree => Direction::Down,
                _ => Direction::Right,
            }),
            shape: spec.shape,
            directed: spec.directed,
            nodes: spec.nodes.iter().map(|n| Node { spec: n.clone(), emphasis: fresh }).collect(),
            edges: spec.edges.iter().map(|e| Edge { spec: e.clone(), emphasis: fresh }).collect(),
            groups: spec.groups.clone(),
        }
    }

    fn node(&self, id: &str) -> Option<usize> {
        self.nodes.iter().position(|n| n.spec.id == id)
    }

    /// Undirected diagrams accept an edge written either way round.
    fn edge(&self, from: &str, to: &str) -> Option<usize> {
        self.edges.iter().position(|e| {
            (e.spec.from == from && e.spec.to == to) || (!self.directed && e.spec.from == to && e.spec.to == from)
        })
    }

    /// Why this node cannot be added, as (field suffix, message).
    fn node_problem(&self, node: &NodeSpec) -> Option<(&'static str, String)> {
        if !is_valid_name(&node.id) {
            return Some((".id", format!("`{}` is not a valid node id; use only letters, digits and `_`", node.id)));
        }
        if self.node(&node.id).is_some() {
            return Some((".id", format!("duplicate node id `{}`", node.id)));
        }
        if self.layout == Layout::Grid {
            let Some(cell) = node.at else {
                return Some(("", format!("node `{}` needs `at: [column, row]` because the layout is `grid`", node.id)));
            };
            if let Some(other) = self.nodes.iter().find(|n| n.spec.at == Some(cell)) {
                return Some((".at", format!("cell [{}, {}] is already taken by node `{}`", cell[0], cell[1], other.spec.id)));
            }
        }
        None
    }

    fn edge_problem(&self, edge: &EdgeSpec) -> Option<(&'static str, String)> {
        for (field, id) in [(".from", &edge.from), (".to", &edge.to)] {
            if self.node(id).is_none() {
                return Some((field, format!("no node `{id}` in this diagram; its nodes are: {}", self.node_list())));
            }
        }
        if edge.from == edge.to {
            return Some(("", format!("an edge from `{}` to itself is not supported yet", edge.from)));
        }
        if self.edge(&edge.from, &edge.to).is_some() {
            return Some(("", format!("there is already an edge from `{}` to `{}`", edge.from, edge.to)));
        }
        None
    }

    fn node_list(&self) -> String {
        let ids: Vec<&str> = self.nodes.iter().take(16).map(|n| n.spec.id.as_str()).collect();
        let more = if self.nodes.len() > 16 { ", ..." } else { "" };
        format!("{}{more}", ids.join(", "))
    }

    pub fn check_part(&self, id: &str, part: &Part) -> Result<(), String> {
        match part {
            Part::Name(name) if self.node(name).is_some() => Ok(()),
            Part::Name(name) => Err(format!("`{id}` has no node `{name}`; its nodes are: {}", self.node_list())),
            Part::Edge { from, to } if self.edge(from, to).is_some() => Ok(()),
            Part::Edge { from, to } => Err(format!("`{id}` has no edge from `{from}` to `{to}`")),
            _ => Err(format!(
                "`{id}{part}` is not a part of a diagram; use `{id}.node` for a node or `{id}.from->to` for an edge"
            )),
        }
    }

    pub fn emphasize(&mut self, part: &Part, emphasis: Emphasis) {
        match part {
            Part::Name(name) => {
                if let Some(i) = self.node(name) {
                    self.nodes[i].emphasis = emphasis;
                }
            }
            Part::Edge { from, to } => {
                if let Some(i) = self.edge(from, to) {
                    self.edges[i].emphasis = emphasis;
                }
            }
            _ => {}
        }
    }

    pub fn each_emphasis(&mut self, mut f: impl FnMut(&mut Emphasis)) {
        self.nodes.iter_mut().for_each(|n| f(&mut n.emphasis));
        self.edges.iter_mut().for_each(|e| f(&mut e.emphasis));
    }

    pub fn act(&mut self, id: &str, action: &ActionKind) -> ActResult {
        match action {
            ActionKind::Set { target, value } => {
                if let Err(message) = self.check_part(id, &target.part) {
                    return at("target", message);
                }
                match &target.part {
                    Part::Name(name) => {
                        let i = self.node(name).expect("checked");
                        self.nodes[i].spec.label = Some(value.to_string());
                    }
                    Part::Edge { from, to } => {
                        let i = self.edge(from, to).expect("checked");
                        self.edges[i].spec.label = Some(value.to_string());
                    }
                    _ => return at("target", format!("`set` on a diagram needs a node or an edge, not the whole of `{id}`")),
                }
                Ok(Changed::Content)
            }
            ActionKind::Remove { target } => {
                if let Err(message) = self.check_part(id, &target.part) {
                    return at("target", message);
                }
                match &target.part {
                    Part::Name(name) => {
                        self.nodes.retain(|n| n.spec.id != *name);
                        self.edges.retain(|e| e.spec.from != *name && e.spec.to != *name);
                        self.groups.iter_mut().for_each(|g| g.nodes.retain(|n| n != name));
                    }
                    Part::Edge { from, to } => {
                        let i = self.edge(from, to).expect("checked");
                        self.edges.remove(i);
                    }
                    _ => return at("target", format!("`remove` on a diagram takes a node or an edge, not the whole of `{id}`")),
                }
                Ok(Changed::Structure)
            }
            ActionKind::AddNode { target, id: node_id, label, shape, layer, at: cell } => {
                if !target.is_whole() {
                    return at("target", format!("`add_node` takes the whole diagram; use `{id}`"));
                }
                let node = NodeSpec { id: node_id.clone(), label: label.clone(), shape: *shape, layer: *layer, at: *cell };
                if let Some((field, message)) = self.node_problem(&node) {
                    return at(field.trim_start_matches('.'), message);
                }
                self.nodes.push(Node { spec: node, emphasis: Emphasis::Normal });
                Ok(Changed::Structure)
            }
            ActionKind::AddEdge { target, from, to, label } => {
                if !target.is_whole() {
                    return at("target", format!("`add_edge` takes the whole diagram; use `{id}`"));
                }
                let edge = EdgeSpec { from: from.clone(), to: to.clone(), label: label.clone() };
                if let Some((field, message)) = self.edge_problem(&edge) {
                    return at(field.trim_start_matches('.'), message);
                }
                self.edges.push(Edge { spec: edge, emphasis: Emphasis::Normal });
                Ok(Changed::Structure)
            }
            _ => Err(ActError::Unsupported),
        }
    }

    // ------------------------------------------------------------ layout

    fn edge_indices(&self) -> Vec<(usize, usize)> {
        self.edges.iter().filter_map(|e| Some((self.node(&e.spec.from)?, self.node(&e.spec.to)?))).collect()
    }

    /// Layered layout: (layer, place in layer) per node, plus the number of
    /// layers and the size of the fullest one.
    fn layers(&self) -> (Vec<(f32, f32)>, usize, usize) {
        let n = self.nodes.len();
        let edges = self.edge_indices();

        // Edges that close a cycle are ignored when assigning layers.
        let mut back = BTreeSet::new();
        let mut colour = vec![0u8; n];
        fn dfs(u: usize, edges: &[(usize, usize)], colour: &mut [u8], back: &mut BTreeSet<(usize, usize)>) {
            colour[u] = 1;
            for &(a, b) in edges.iter().filter(|e| e.0 == u) {
                match colour[b] {
                    0 => dfs(b, edges, colour, back),
                    1 => {
                        back.insert((a, b));
                    }
                    _ => {}
                }
            }
            colour[u] = 2;
        }
        for u in 0..n {
            if colour[u] == 0 {
                dfs(u, &edges, &mut colour, &mut back);
            }
        }

        // Longest path from the sources, except where a node pins its layer.
        let mut layer: Vec<usize> = self.nodes.iter().map(|n| n.spec.layer.unwrap_or(0)).collect();
        for _ in 0..n {
            let mut changed = false;
            for &(a, b) in edges.iter().filter(|e| !back.contains(e)) {
                if self.nodes[b].spec.layer.is_none() && layer[b] < layer[a] + 1 {
                    layer[b] = layer[a] + 1;
                    changed = true;
                }
            }
            if !changed {
                break;
            }
        }

        let count = layer.iter().max().map_or(1, |m| m + 1);
        let mut rows: Vec<Vec<usize>> = vec![vec![]; count];
        for (i, l) in layer.iter().enumerate() {
            rows[*l].push(i);
        }

        // Fewer crossings: order each layer by the average place of each
        // node's neighbours in the layer beside it, sweeping both ways.
        let mut place = vec![0.0f32; n];
        let settle = |rows: &Vec<Vec<usize>>, place: &mut Vec<f32>| {
            for row in rows {
                for (k, &i) in row.iter().enumerate() {
                    place[i] = k as f32;
                }
            }
        };
        settle(&rows, &mut place);
        for sweep in 0..4 {
            let order: Vec<usize> = if sweep % 2 == 0 { (1..count).collect() } else { (0..count.saturating_sub(1)).rev().collect() };
            for l in order {
                let beside = if sweep % 2 == 0 { l - 1 } else { l + 1 };
                let key = |i: usize| {
                    let near: Vec<f32> = edges
                        .iter()
                        .filter_map(|&(a, b)| match (a == i, b == i) {
                            (true, _) if layer[b] == beside => Some(place[b]),
                            (_, true) if layer[a] == beside => Some(place[a]),
                            _ => None,
                        })
                        .collect();
                    if near.is_empty() { place[i] } else { near.iter().sum::<f32>() / near.len() as f32 }
                };
                let mut keyed: Vec<(f32, usize)> = rows[l].iter().map(|&i| (key(i), i)).collect();
                keyed.sort_by(|a, b| a.0.total_cmp(&b.0));
                rows[l] = keyed.into_iter().map(|(_, i)| i).collect();
                settle(&rows, &mut place);
            }
        }

        let widest = rows.iter().map(Vec::len).max().unwrap_or(1).max(1);
        let mut out = vec![(0.0, 0.0); n];
        for (l, row) in rows.iter().enumerate() {
            let offset = (widest - row.len()) as f32 / 2.0;
            for (k, &i) in row.iter().enumerate() {
                out[i] = (l as f32, offset + k as f32);
            }
        }
        (out, count, widest)
    }

    /// Tree layout: leaves take consecutive places, a parent sits over the
    /// middle of its children.
    fn tree(&self) -> (Vec<(f32, f32)>, usize, usize) {
        let n = self.nodes.len();
        let edges = self.edge_indices();
        let mut out = vec![(0.0, 0.0); n];
        let mut seen = vec![false; n];
        let (mut next_leaf, mut depth_max) = (0.0f32, 0usize);

        fn place(
            u: usize,
            depth: usize,
            edges: &[(usize, usize)],
            seen: &mut [bool],
            out: &mut [(f32, f32)],
            next_leaf: &mut f32,
            depth_max: &mut usize,
        ) -> f32 {
            seen[u] = true;
            *depth_max = (*depth_max).max(depth);
            let children: Vec<usize> = edges.iter().filter(|e| e.0 == u).map(|e| e.1).collect();
            let mut xs = vec![];
            for child in children {
                if !seen[child] {
                    xs.push(place(child, depth + 1, edges, seen, out, next_leaf, depth_max));
                }
            }
            let x = if xs.is_empty() {
                *next_leaf += 1.0;
                *next_leaf - 1.0
            } else {
                (xs[0] + xs[xs.len() - 1]) / 2.0
            };
            out[u] = (depth as f32, x);
            x
        }

        let has_parent: BTreeSet<usize> = edges.iter().map(|e| e.1).collect();
        let roots: Vec<usize> = (0..n).filter(|i| !has_parent.contains(i)).collect();
        for u in roots.into_iter().chain(0..n) {
            if !seen[u] {
                place(u, 0, &edges, &mut seen, &mut out, &mut next_leaf, &mut depth_max);
            }
        }
        (out, depth_max + 1, (next_leaf as usize).max(1))
    }

    /// The centre of every node and the size of the cell it may fill.
    fn centres(&self, slot: Rect, u: f32) -> (Vec<(f32, f32)>, f32, f32) {
        let n = self.nodes.len();
        if self.layout == Layout::Ring {
            // An ellipse that uses the width of the slot, so that edge labels
            // have room between the nodes.
            let ry = (slot.h / 2.0 - 60.0 * u).max(60.0 * u);
            let rx = (slot.w / 2.0 - 140.0 * u).clamp(ry, ry * 2.0);
            let step = std::f32::consts::TAU / n.max(1) as f32;
            let at = |i: usize| {
                let angle = step * i as f32 - std::f32::consts::FRAC_PI_2;
                (slot.cx() + rx * angle.cos(), slot.cy() + ry * angle.sin())
            };
            if n <= 1 {
                return (vec![(slot.cx(), slot.cy()); n], 2.0 * rx, 2.0 * ry);
            }
            // Size nodes by the tightest gap between neighbours.
            let gap = (0..n)
                .map(|i| {
                    let (a, b) = (at(i), at((i + 1) % n));
                    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
                })
                .fold(f32::INFINITY, f32::min);
            return ((0..n).map(at).collect(), gap * 0.95, gap * 0.6);
        }

        // Every other layout puts nodes in a grid of columns and rows.
        let (cells, cols, rows): (Vec<(f32, f32)>, usize, usize) = match self.layout {
            Layout::Grid => {
                let at = |n: &Node| n.spec.at.unwrap_or([0, 0]);
                let cols = self.nodes.iter().map(|n| at(n)[0]).max().unwrap_or(0) + 1;
                let rows = self.nodes.iter().map(|n| at(n)[1]).max().unwrap_or(0) + 1;
                (self.nodes.iter().map(|n| (at(n)[0] as f32, at(n)[1] as f32)).collect(), cols, rows)
            }
            _ => {
                let (places, along, across) = if self.layout == Layout::Tree { self.tree() } else { self.layers() };
                match self.direction {
                    Direction::Right => (places, along, across),
                    Direction::Down => (places.into_iter().map(|(a, b)| (b, a)).collect(), across, along),
                }
            }
        };
        // Cells are capped so that a small diagram does not sprawl.
        let cell_w = (slot.w / cols as f32).min(380.0 * u);
        let cell_h = (slot.h / rows as f32).min(230.0 * u);
        let x0 = slot.cx() - cell_w * cols as f32 / 2.0;
        let y0 = slot.cy() - cell_h * rows as f32 / 2.0;
        let centres = cells.iter().map(|(c, r)| (x0 + (c + 0.5) * cell_w, y0 + (r + 0.5) * cell_h)).collect();
        (centres, cell_w, cell_h)
    }

    fn shape_of(&self, node: &Node) -> Shape {
        node.spec.shape.unwrap_or(self.shape)
    }

    pub fn layout(&self, slot: Rect, cx: &mut Cx) -> Placed {
        let u = cx.u;
        // Leave room for group frames and their labels.
        let inner = if self.groups.is_empty() { slot } else { Rect { y: slot.y + 30.0 * u, h: slot.h - 30.0 * u, ..slot }.inset(26.0 * u) };
        let (centres, cell_w, cell_h) = self.centres(inner, u);
        let box_w = (cell_w * 0.64).min(250.0 * u);
        let box_h = (cell_h * 0.56).min(104.0 * u);
        let round = (cell_w * 0.62).min(cell_h * 0.62).min(120.0 * u);

        let nodes: Vec<(String, Rect)> = self
            .nodes
            .iter()
            .zip(&centres)
            .map(|(node, (x, y))| {
                let (w, h) = if self.shape_of(node) == Shape::Circle { (round, round) } else { (box_w, box_h) };
                (node.spec.id.clone(), Rect { x: x - w / 2.0, y: y - h / 2.0, w, h })
            })
            .collect();
        let bounds = nodes.iter().map(|(_, r)| *r).reduce(|a, b| a.union(&b)).unwrap_or(slot);
        Placed { bounds, skirt: 8.0 * u, scale: box_h / (104.0 * u), geometry: Geometry::Nodes(nodes) }
    }

    pub fn paint(&self, placed: &Placed, whole: Emphasis, cx: &mut Cx) {
        let Geometry::Nodes(rects) = &placed.geometry else { return };
        let (pal, u) = (cx.pal, cx.u);
        let rect_of = |id: &str| rects.iter().find(|(n, _)| n == id).map(|(_, r)| *r);
        let frame = cx.tone(Emphasis::Normal, whole);

        // Groups, behind everything.
        for (i, group) in self.groups.iter().enumerate() {
            cx.at(format!("group{i}"));
            let Some(around) = group.nodes.iter().filter_map(|n| rect_of(n)).reduce(|a, b| a.union(&b)) else { continue };
            let pad = 22.0 * u;
            let area = Rect { x: around.x - pad, y: around.y - pad - 34.0 * u, w: around.w + 2.0 * pad, h: around.h + 2.0 * pad + 34.0 * u };
            cx.fill_round_rect(area, 18.0 * u, pal.surface, frame.box_opacity * 0.55);
            cx.stroke_round_rect(area, 18.0 * u, pal.border, 2.0 * u, frame.box_opacity);
            cx.text(&group.label, 26.0 * u, Face::SansBold, pal.muted, frame.ink_opacity, area.x + 18.0 * u, area.y + 26.0 * u, HAlign::Left, None);
        }

        // Edges, under the nodes.
        for edge in &self.edges {
            let (Some(a), Some(b)) = (rect_of(&edge.spec.from), rect_of(&edge.spec.to)) else { continue };
            cx.at(format!("edge {}->{}", edge.spec.from, edge.spec.to));
            let tone = cx.tone(edge.emphasis, whole);
            let color = if tone.heavy { tone.border } else { pal.muted };
            let width = if tone.heavy { 5.5 * u } else { 3.5 * u };
            let round = |id: &str| self.node(id).is_some_and(|i| self.shape_of(&self.nodes[i]) == Shape::Circle);
            let mut start = leave(a, round(&edge.spec.from), (b.cx(), b.cy()), 7.0 * u);
            let mut end = leave(b, round(&edge.spec.to), (a.cx(), a.cy()), 7.0 * u);

            // Unit normal of the edge, pointing up (or left for a vertical one).
            let (dx, dy) = (end.0 - start.0, end.1 - start.1);
            let len = (dx * dx + dy * dy).sqrt().max(1.0);
            let mut normal = (dy / len, -dx / len);
            if normal.1 > 0.0 || (normal.1 == 0.0 && normal.0 > 0.0) {
                normal = (-normal.0, -normal.1);
            }
            // A pair of opposite edges is drawn side by side, each with its
            // label on its own outer side.
            let mut label_side = 1.0;
            if self.directed && self.edge(&edge.spec.to, &edge.spec.from).is_some() {
                label_side = if edge.spec.from < edge.spec.to { 1.0 } else { -1.0 };
                let shift = 9.0 * u * label_side;
                start = (start.0 + normal.0 * shift, start.1 + normal.1 * shift);
                end = (end.0 + normal.0 * shift, end.1 + normal.1 * shift);
            }
            if self.directed {
                cx.arrow(start, end, color, width, tone.ink_opacity);
            } else {
                cx.line(start, end, color, width, tone.ink_opacity);
            }
            if let Some(label) = &edge.spec.label {
                let (mx, my) = ((start.0 + end.0) / 2.0, (start.1 + end.1) / 2.0);
                let size = 26.0 * u;
                let (w, _) = cx.fonts.measure(label, size, Face::Sans, None);
                // Push the label off the line: by its height above, or by
                // half its width to the side when the line is steep.
                let off = (22.0 * u + normal.0.abs() * w / 2.0) * label_side;
                let ink = if tone.heavy { tone.border } else { pal.text };
                cx.text(label, size, Face::Sans, ink, tone.ink_opacity, mx + normal.0 * off, my + normal.1 * off, HAlign::Center, None);
            }
        }

        // Nodes.
        for (node, (_, rect)) in self.nodes.iter().zip(rects) {
            cx.at(format!("node {}", node.spec.id));
            let tone = cx.tone(node.emphasis, whole);
            let width = if tone.heavy { 5.0 * u } else { 3.0 * u };
            let radius = match self.shape_of(node) {
                Shape::Box => 14.0 * u,
                Shape::Circle | Shape::Pill => rect.h / 2.0,
            };
            cx.fill_round_rect(*rect, radius, tone.fill, tone.box_opacity);
            cx.stroke_round_rect(rect.inset(width / 2.0), radius, tone.border, width, tone.box_opacity);
            let label = node.spec.label.as_deref().unwrap_or(&node.spec.id);
            let size = cx.fit(label, (rect.h * 0.4).min(36.0 * u), Face::SansBold, rect.w * 0.82);
            cx.text(label, size, Face::SansBold, tone.ink, tone.ink_opacity, rect.cx(), rect.cy(), HAlign::Center, None);
        }
    }
}

/// Where a line from the centre of a node toward `toward` leaves the node.
fn leave(rect: Rect, round: bool, toward: (f32, f32), gap: f32) -> (f32, f32) {
    if !round {
        return edge_point(rect, toward, gap);
    }
    let (dx, dy) = (toward.0 - rect.cx(), toward.1 - rect.cy());
    let len = (dx * dx + dy * dy).sqrt().max(1.0);
    let r = rect.w / 2.0 + gap;
    (rect.cx() + dx / len * r, rect.cy() + dy / len * r)
}
