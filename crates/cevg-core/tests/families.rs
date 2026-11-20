//! The diagram, table and math families: their parts, their actions and the
//! errors they report.

use cevg_core::families::{Body, Emphasis};
use cevg_core::{check, frame_png, parse, Position, Severity, World};

const SUBJECTS: [&str; 11] = [
    "ml_network", "coa_cpu", "db_join", "math_gradient", "os_states", "dsa_bfs", "ml_descent", "ml_loss", "os_round_robin",
    "net_handshake", "ml_pca",
];

fn example(name: &str) -> String {
    let path = format!("{}/../../examples/subjects/{name}.json", env!("CARGO_MANIFEST_DIR"));
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"))
}

/// A script with a diagram `g`, a table `t`, a math object `eq` and a pointer
/// `p` on node `b`, all visible, plus the given actions in one step.
fn script(actions: &str) -> String {
    format!(
        r#"{{
  "version": 1, "title": "t",
  "objects": [
    {{ "id": "g", "type": "diagram", "region": "left", "visible": true,
      "nodes": [ {{ "id": "a" }}, {{ "id": "b" }}, {{ "id": "c" }} ],
      "edges": [ {{ "from": "a", "to": "b" }}, {{ "from": "b", "to": "c" }} ] }},
    {{ "id": "t", "type": "table", "region": "right", "visible": true,
      "columns": ["id", "name"], "rows": [ [1, "x"], [2, "y"] ] }},
    {{ "id": "eq", "type": "math", "region": "bottom", "visible": true,
      "lines": ["a^2 + b^2 = c^2", "c = sqrt(a^2 + b^2)"] }},
    {{ "id": "p", "type": "pointer", "label": "p", "target": "g.b", "visible": true }}
  ],
  "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Go." }}, "do": [ {actions} ] }} ] }} ]
}}"#
    )
}

fn errors(json: &str) -> Vec<String> {
    check(json)
        .diagnostics
        .into_iter()
        .filter(|d| d.severity == Severity::Error)
        .map(|d| format!("{}: {}", d.path, d.message))
        .collect()
}

fn ok(actions: &str) {
    let found = errors(&script(actions));
    assert!(found.is_empty(), "{found:#?}");
}

fn one_error(actions: &str, needle: &str) {
    let found = errors(&script(actions));
    assert_eq!(found.len(), 1, "{found:#?}");
    assert!(found[0].contains(needle), "`{}` should mention `{needle}`", found[0]);
}

fn world_after(actions: &str) -> World {
    let script = parse(&script(actions)).unwrap();
    World::at(&script, Position::locate(&script, None, None).unwrap())
}

#[test]
fn subject_examples_are_clean_and_draw() {
    for name in SUBJECTS {
        let json = example(name);
        let report = check(&json);
        assert!(report.diagnostics.is_empty(), "{name}: {:#?}", report.diagnostics);
        let png = frame_png(&json, None, None, None, None).unwrap_or_else(|r| panic!("{name}: {:#?}", r.diagnostics));
        assert!(png.len() > 10_000, "{name}: the frame looks empty");
    }
}

#[test]
fn every_part_form_is_accepted() {
    ok(r#"{ "action": "highlight", "target": "g.a" }"#);
    ok(r#"{ "action": "mark", "target": "g.a->b" }"#);
    ok(r#"{ "action": "dim", "target": "t[1]" }"#);
    ok(r#"{ "action": "highlight", "target": "t[0..2]" }"#);
    ok(r#"{ "action": "highlight", "target": "t[1][0]" }"#);
    ok(r#"{ "action": "mark", "target": "t.name" }"#);
    ok(r#"{ "action": "highlight", "target": "eq[1]" }"#);
    ok(r#"{ "action": "reset", "target": "g" }"#);
    ok(r#"{ "action": "point", "target": "p", "to": "t[1][1]" }"#);
    ok(r#"{ "action": "point", "target": "p", "to": "eq[0]" }"#);
}

#[test]
fn diagram_actions() {
    ok(r#"{ "action": "set", "target": "g.a", "value": "start" }"#);
    ok(r#"{ "action": "set", "target": "g.a->b", "value": 5 }"#);
    ok(r#"{ "action": "add_node", "target": "g", "id": "d", "label": "new" },
          { "action": "add_edge", "target": "g", "from": "c", "to": "d", "label": "next" },
          { "action": "highlight", "target": "g.c->d" }"#);
    ok(r#"{ "action": "remove", "target": "g.a->b" }"#);

    one_error(r#"{ "action": "highlight", "target": "g.z" }"#, "`g` has no node `z`; its nodes are: a, b, c");
    one_error(r#"{ "action": "highlight", "target": "g.c->a" }"#, "no edge from `c` to `a`");
    one_error(r#"{ "action": "highlight", "target": "g[0]" }"#, "is not a part of a diagram");
    one_error(r#"{ "action": "add_node", "target": "g", "id": "a" }"#, "duplicate node id `a`");
    one_error(r#"{ "action": "add_edge", "target": "g", "from": "a", "to": "z" }"#, "no node `z`");
    one_error(r#"{ "action": "add_edge", "target": "g", "from": "a", "to": "b" }"#, "already an edge");
    // Removing a node takes its edges with it and strands the pointer on it.
    one_error(r#"{ "action": "remove", "target": "g.b" }"#, "leaves pointer `p` on g.b");

    let world = world_after(r#"{ "action": "point", "target": "p", "to": "g.a" }, { "action": "remove", "target": "g.b" }"#);
    let Body::Diagram(g) = &world.get("g").unwrap().body else { panic!() };
    assert_eq!((g.nodes.len(), g.edges.len()), (2, 0));
}

#[test]
fn diagram_self_loops() {
    // An edge from a node to itself is an ordinary edge: it can be added, lit,
    // labelled, pointed at and removed, but only once.
    ok(r#"{ "action": "add_edge", "target": "g", "from": "a", "to": "a", "label": "0" },
          { "action": "highlight", "target": "g.a->a" },
          { "action": "set", "target": "g.a->a", "value": "0, 1" },
          { "action": "point", "target": "p", "to": "g.a->a" }"#);
    one_error(
        r#"{ "action": "add_edge", "target": "g", "from": "b", "to": "b" }, { "action": "add_edge", "target": "g", "from": "b", "to": "b" }"#,
        "already an edge from `b` to `b`",
    );

    // The loop sits outside its node, away from the node's other edges.
    let world = world_after(r#"{ "action": "add_edge", "target": "g", "from": "a", "to": "a" }"#);
    let Body::Diagram(g) = &world.get("g").unwrap().body else { panic!() };
    let rect = |x: f32| cevg_core::render::Rect { x, y: 0.0, w: 200.0, h: 100.0 };
    let rects = vec![("a".to_string(), rect(0.0)), ("b".to_string(), rect(400.0)), ("c".to_string(), rect(800.0))];
    let l = g.self_loop("a", &rects).expect("a loop");
    assert!(l.dir.0 < 0.5, "the loop should not point at b: {:?}", l.dir);
    assert!(l.points.len() > 10);
    for (x, y) in &l.points {
        assert!(!(*x > 0.0 && *x < 200.0 && *y > 0.0 && *y < 100.0), "({x}, {y}) is inside the node");
    }
    let png = frame_png(&script(r#"{ "action": "add_edge", "target": "g", "from": "c", "to": "c", "label": "x" }"#), None, None, None, None)
        .unwrap_or_else(|r| panic!("{:#?}", r.diagnostics));
    assert!(png.len() > 10_000);
}

#[test]
fn diagram_specs() {
    let with = |nodes: &str, extra: &str| {
        script("").replace(
            r#""nodes": [ { "id": "a" }, { "id": "b" }, { "id": "c" } ],"#,
            &format!(r#""nodes": [ {nodes} ], {extra}"#),
        )
    };
    let found = errors(&with(r#"{ "id": "a" }, { "id": "b" }, { "id": "c" }, { "id": "a" }"#, ""));
    assert!(found[0].contains("objects[0].nodes[3].id: duplicate node id `a`"), "{found:#?}");

    let found = errors(&with(r#"{ "id": "a", "at": [0, 0] }, { "id": "b" }, { "id": "c", "at": [0, 0] }"#, r#""layout": "grid","#));
    assert!(found.iter().any(|e| e.contains("node `b` needs `at: [column, row]`")), "{found:#?}");
    assert!(found.iter().any(|e| e.contains("cell [0, 0] is already taken by node `a`")), "{found:#?}");

    let found = errors(&with(r#"{ "id": "a" }, { "id": "c" }"#, ""));
    assert!(found.iter().any(|e| e.contains("objects[0].edges[0].to: no node `b`")), "{found:#?}");
}

#[test]
fn table_actions() {
    ok(r#"{ "action": "set", "target": "t[0][1]", "value": "z" }"#);
    ok(r#"{ "action": "add_row", "target": "t", "values": [3, "w"] }, { "action": "highlight", "target": "t[2]" }"#);
    ok(r#"{ "action": "add_row", "target": "t", "values": [0, "first"], "index": 0 }"#);
    ok(r#"{ "action": "remove", "target": "t[0]" }"#);

    one_error(r#"{ "action": "highlight", "target": "t[2]" }"#, "t[2] is out of range, t has 2 rows");
    one_error(r#"{ "action": "highlight", "target": "t[0][2]" }"#, "t has 2 columns");
    one_error(r#"{ "action": "highlight", "target": "t.age" }"#, "no column `age`; its columns are: id, name (or by position, c0 to c1)");
    ok(r#"{ "action": "highlight", "target": "t.c1" }"#);
    one_error(r#"{ "action": "highlight", "target": "t.c2" }"#, "no column `c2`");
    one_error(r#"{ "action": "add_row", "target": "t", "values": [3] }"#, "1 values, but `t` has 2 columns");
    one_error(r#"{ "action": "set", "target": "t[0]", "value": 1 }"#, "needs one cell");
    one_error(r#"{ "action": "remove", "target": "t[0]" }, { "action": "highlight", "target": "t[1]" }"#, "t has 1 row");

    let ragged = script("").replace(r#"[2, "y"]"#, r#"[2, "y", "extra"]"#);
    assert!(errors(&ragged)[0].contains("objects[1].rows[1]: this row has 3 values, but the table has 2 columns"));

    let world = world_after(r#"{ "action": "add_row", "target": "t", "values": [3, "w"] }"#);
    let Body::Table(t) = &world.get("t").unwrap().body else { panic!() };
    assert_eq!(t.rows.len(), 3);
}

#[test]
fn math_actions() {
    ok(r#"{ "action": "reveal", "target": "eq[1]" }"#);
    ok(r#"{ "action": "set", "target": "eq[1]", "value": "c = 5" }"#);

    one_error(r#"{ "action": "reveal", "target": "eq[2]" }"#, "eq[2] is out of range, eq has 2 lines");
    one_error(r#"{ "action": "reveal", "target": "eq" }"#, "needs one line");
    one_error(r#"{ "action": "set", "target": "eq[0]", "value": 5 }"#, "must be a string");
    one_error(r#"{ "action": "set", "target": "eq[0]", "value": "c = sqroot(a)" }"#, "not valid Typst math: unknown variable: sqroot");
    one_error(r#"{ "action": "set", "target": "eq[0]", "value": "$x$" }"#, "`$` is not allowed");

    let broken = script("").replace("c = sqrt(a^2 + b^2)", "c = squareroot(a^2 + b^2)");
    assert!(errors(&broken)[0].starts_with("objects[2].lines[1]: not valid Typst math"), "{:#?}", errors(&broken));

    let world = world_after(r#"{ "action": "reveal", "target": "eq[1]" }"#);
    let Body::Math(eq) = &world.get("eq").unwrap().body else { panic!() };
    assert_eq!(eq.shown, 2);
}

#[test]
fn highlight_moves_but_mark_stays() {
    let world = world_after(
        r#"{ "action": "mark", "target": "g.a" },
           { "action": "highlight", "target": "g.b" },
           { "action": "highlight", "target": "g.c" }"#,
    );
    let Body::Diagram(g) = &world.get("g").unwrap().body else { panic!() };
    let emphasis: Vec<Emphasis> = g.nodes.iter().map(|n| n.emphasis).collect();
    assert_eq!(emphasis, [Emphasis::Mark, Emphasis::Normal, Emphasis::Highlight]);

    let world = world_after(r#"{ "action": "mark", "target": "t.id" }, { "action": "reset", "target": "t" }"#);
    let Body::Table(t) = &world.get("t").unwrap().body else { panic!() };
    assert!(t.rows.iter().flatten().all(|c| c.1 == Emphasis::Normal));
}

#[test]
fn actions_on_the_wrong_family_say_where_they_work() {
    one_error(r#"{ "action": "add_row", "target": "g", "values": [1] }"#, "`add_row` works on table objects, but `g` is a diagram");
    one_error(r#"{ "action": "reveal", "target": "t[0]" }"#, "`reveal` works on math and figure objects, but `t` is a table");
    one_error(r#"{ "action": "add_node", "target": "eq", "id": "x" }"#, "`add_node` works on diagram objects");
}

/// A script with a plot `p` and a timeline `tl`, both visible.
fn charts(actions: &str) -> String {
    format!(
        r#"{{
  "version": 1, "title": "t",
  "objects": [
    {{ "id": "p", "type": "plot", "region": "left", "visible": true,
      "x": {{ "min": 0, "max": 4 }},
      "curves": [ {{ "id": "f", "fn": "x^2" }}, {{ "id": "data", "points": [[0, 1], [4, 3]], "visible": false }} ],
      "points": [ {{ "id": "a", "at": [1, 1] }} ] }},
    {{ "id": "tl", "type": "timeline", "region": "right", "visible": true,
      "lanes": ["P1", "P2"], "end": 10,
      "blocks": [ {{ "id": "b1", "lane": "P1", "start": 0, "end": 4 }} ] }}
  ],
  "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Go." }}, "do": [ {actions} ] }} ] }} ]
}}"#
    )
}

fn chart_ok(actions: &str) {
    let found = errors(&charts(actions));
    assert!(found.is_empty(), "{found:#?}");
}

fn chart_error(actions: &str, needle: &str) {
    let found = errors(&charts(actions));
    assert_eq!(found.len(), 1, "{found:#?}");
    assert!(found[0].contains(needle), "`{}` should mention `{needle}`", found[0]);
}

#[test]
fn plot_actions() {
    chart_ok(r#"{ "action": "trace", "target": "p.data" }"#);
    chart_ok(r#"{ "action": "move_to", "target": "p.a", "at": [2, 4] }"#);
    chart_ok(r#"{ "action": "add_point", "target": "p", "id": "b", "at": [3, 9], "label": "new" }, { "action": "mark", "target": "p.b" }"#);
    chart_ok(r#"{ "action": "set", "target": "p.f", "value": "2x + 1" }"#);
    chart_ok(r#"{ "action": "set", "target": "p.a", "value": "start" }"#);
    chart_ok(r#"{ "action": "highlight", "target": "p.f" }, { "action": "remove", "target": "p.a" }"#);

    chart_error(r#"{ "action": "trace", "target": "p.a" }"#, "`a` is a point");
    chart_error(r#"{ "action": "move_to", "target": "p.f", "at": [1, 1] }"#, "`f` is a curve");
    chart_error(r#"{ "action": "highlight", "target": "p.z" }"#, "no curve or point `z`; it has: f, data, a");
    chart_error(r#"{ "action": "add_point", "target": "p", "id": "f", "at": [1, 1] }"#, "duplicate id `f`");
    chart_error(r#"{ "action": "set", "target": "p.f", "value": "x +" }"#, "ends too early");
    chart_error(r#"{ "action": "set", "target": "p.data", "value": "x" }"#, "data curve");
    chart_error(r#"{ "action": "trace", "target": "tl" }"#, "`trace` works on plot and space objects, but `tl` is a timeline");

    let bad = charts("").replace(r#""fn": "x^2""#, r#""fn": "y^2""#);
    assert!(errors(&bad)[0].contains("objects[0].curves[0].fn: unknown name `y`"), "{:#?}", errors(&bad));
    let bad = charts("").replace(r#""x": { "min": 0, "max": 4 },"#, "");
    assert!(errors(&bad)[0].contains("needs `x.min` and `x.max`"), "{:#?}", errors(&bad));
}

#[test]
fn timeline_actions() {
    chart_ok(r#"{ "action": "add_block", "target": "tl", "id": "b2", "lane": "P2", "start": 4, "end": 6, "label": "P2" }"#);
    chart_ok(r#"{ "action": "add_message", "target": "tl", "id": "m", "from": "P1", "to": "P2", "at": 1, "arrive": 2 }"#);
    chart_ok(r#"{ "action": "advance", "target": "tl", "to": 4 }"#);
    chart_ok(r#"{ "action": "highlight", "target": "tl.b1" }, { "action": "mark", "target": "tl.P2" }"#);
    chart_ok(r#"{ "action": "set", "target": "tl.b1", "value": "run" }, { "action": "remove", "target": "tl.b1" }"#);

    chart_error(
        r#"{ "action": "add_block", "target": "tl", "id": "b2", "lane": "P1", "start": 3, "end": 5 }"#,
        "overlaps block `b1` in lane `P1` (0 to 4)",
    );
    chart_error(r#"{ "action": "add_block", "target": "tl", "id": "b2", "lane": "P9", "start": 4, "end": 5 }"#, "no lane `P9`; the lanes are: P1, P2");
    chart_error(r#"{ "action": "add_block", "target": "tl", "id": "b2", "lane": "P2", "start": 5, "end": 5 }"#, "0 <= start < end");
    chart_error(r#"{ "action": "add_block", "target": "tl", "id": "b1", "lane": "P2", "start": 5, "end": 6 }"#, "duplicate id `b1`");
    chart_error(r#"{ "action": "add_message", "target": "tl", "id": "m", "from": "P1", "to": "P1", "at": 1 }"#, "both ends are `P1`");
    chart_error(r#"{ "action": "advance", "target": "tl", "to": -1 }"#, "not a time on the axis");
    chart_error(r#"{ "action": "highlight", "target": "tl.nope" }"#, "no block, message or lane named `nope`");
    chart_error(r#"{ "action": "advance", "target": "p", "to": 1 }"#, "`advance` works on timeline objects, but `p` is a plot");
}
