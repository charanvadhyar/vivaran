//! Rule-by-rule checks on small inline scripts.

use cevg_core::{check, Severity};

/// Build a script around one list of extra objects and one list of actions.
/// `arr` (5 cells), pointer `p` on arr[4], text `t` and code `src` (3 lines)
/// are always present and already visible.
fn script(extra_objects: &str, actions: &str) -> String {
    format!(
        r#"{{
  "version": 1, "title": "t",
  "objects": [
    {{ "id": "arr", "type": "array", "region": "center", "values": [1, 2, 3, 4, 5], "visible": true }},
    {{ "id": "p", "type": "pointer", "label": "p", "target": "arr[4]", "visible": true }},
    {{ "id": "t", "type": "text", "region": "bottom", "text": "hi", "visible": true }},
    {{ "id": "src", "type": "code", "region": "left", "lines": ["a", "b", "c"], "visible": true }}
    {extra_objects}
  ],
  "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Go." }}, "do": [ {actions} ] }} ] }} ]
}}"#
    )
}

fn errors(extra_objects: &str, actions: &str) -> Vec<String> {
    check(&script(extra_objects, actions))
        .diagnostics
        .into_iter()
        .filter(|d| d.severity == Severity::Error)
        .map(|d| format!("{}: {}", d.path, d.message))
        .collect()
}

fn warnings(extra_objects: &str, actions: &str) -> Vec<String> {
    check(&script(extra_objects, actions))
        .diagnostics
        .into_iter()
        .filter(|d| d.severity == Severity::Warning)
        .map(|d| d.message)
        .collect()
}

fn ok(actions: &str) {
    let found = errors("", actions);
    assert!(found.is_empty(), "{found:#?}");
}

fn one_error(extra_objects: &str, actions: &str, needle: &str) {
    let found = errors(extra_objects, actions);
    assert_eq!(found.len(), 1, "{found:#?}");
    assert!(found[0].contains(needle), "`{}` should mention `{needle}`", found[0]);
}

#[test]
fn every_action_has_a_valid_form() {
    ok(r#"{ "action": "highlight", "target": "arr[0..=4]" }"#);
    ok(r#"{ "action": "dim", "target": "arr[0..5]" }"#);
    ok(r#"{ "action": "move", "target": "arr", "region": "left" }"#);
    ok(r#"{ "action": "write", "target": "t" }"#);
    ok(r#"{ "action": "replace", "target": "t", "text": "new" }"#);
    ok(r#"{ "action": "swap", "a": "arr[0]", "b": "arr[4]" }"#);
    ok(r#"{ "action": "compare", "a": "arr[1]", "b": "arr[2]" }"#);
    ok(r#"{ "action": "set", "target": "arr[2]", "value": "x" }"#);
    ok(r#"{ "action": "insert", "target": "arr", "index": 5, "value": 6 }"#);
    ok(r#"{ "action": "point", "target": "p", "to": "arr[0]" }"#);
    ok(r#"{ "action": "goto_line", "target": "src", "line": 3 }"#);
    ok(r#"{ "action": "mark_lines", "target": "src", "from": 1, "to": 3 }"#);
    ok(r#"{ "action": "hide", "target": "p" }"#);
}

#[test]
fn state_is_tracked_across_actions() {
    // After an insert the array has 6 cells, so index 5 exists.
    ok(r#"{ "action": "insert", "target": "arr", "index": 0, "value": 0 },
          { "action": "highlight", "target": "arr[5]" }"#);
    // Moving the pointer first makes the remove safe.
    ok(r#"{ "action": "point", "target": "p", "to": "arr[0]" },
          { "action": "remove", "target": "arr[4]" }"#);
    // After a remove the array has 4 cells, so index 4 is gone.
    one_error(
        "",
        r#"{ "action": "point", "target": "p", "to": "arr[0]" },
           { "action": "remove", "target": "arr[0]" },
           { "action": "highlight", "target": "arr[4]" }"#,
        "arr[4] is out of range, arr has 4 elements",
    );
}

#[test]
fn ranges_are_end_exclusive() {
    one_error("", r#"{ "action": "dim", "target": "arr[0..6]" }"#, "out of range");
    one_error("", r#"{ "action": "dim", "target": "arr[0..=5]" }"#, "out of range");
}

#[test]
fn kinds_are_enforced() {
    one_error("", r#"{ "action": "point", "target": "arr", "to": "arr[0]" }"#, "`point` works on pointer objects");
    one_error("", r#"{ "action": "point", "target": "p", "to": "p" }"#, "`p` is a pointer");
    one_error("", r#"{ "action": "replace", "target": "arr", "text": "x" }"#, "`arr` is an array");
    one_error("", r#"{ "action": "set", "target": "arr", "value": 1 }"#, "needs one array cell");
    one_error("", r#"{ "action": "highlight", "target": "t[0]" }"#, "has no parts that can be named");
    one_error("", r#"{ "action": "show", "target": "arr[1]" }"#, "takes a whole object");
    one_error("", r#"{ "action": "swap", "a": "arr[1]", "b": "arr[1]" }"#, "same cell");
}

#[test]
fn numbers_are_bounded() {
    one_error("", r#"{ "action": "insert", "target": "arr", "index": 6, "value": 1 }"#, "past the end");
    one_error("", r#"{ "action": "goto_line", "target": "src", "line": 0 }"#, "lines 1 to 3");
    one_error("", r#"{ "action": "goto_line", "target": "src", "line": 4 }"#, "lines 1 to 3");
    one_error("", r#"{ "action": "mark_lines", "target": "src", "from": 3, "to": 2 }"#, "is after");
    one_error("", r#"{ "action": "dim", "target": "arr", "delay": 1.5 }"#, "outside 0 to 1");
}

#[test]
fn arrows_attach_and_retarget() {
    let arrow = r#", { "id": "link", "type": "arrow", "from": "arr[0]", "to": "t" }"#;
    assert!(errors(arrow, r#"{ "action": "draw", "target": "link" },
                             { "action": "retarget", "target": "link", "to": "arr[4]" }"#).is_empty());
    one_error(arrow, r#"{ "action": "draw", "target": "link" },
                        { "action": "retarget", "target": "link" }"#, "needs `from`, `to` or both");
    // An arrow end is stranded just like a pointer.
    one_error(arrow, r#"{ "action": "draw", "target": "link" },
                        { "action": "retarget", "target": "link", "from": "arr[4]" },
                        { "action": "point", "target": "p", "to": "arr[0]" },
                        { "action": "remove", "target": "arr[4]" }"#, "leaves arrow `link` on arr[4]");
}

#[test]
fn object_rules() {
    one_error(r#", { "id": "arr", "type": "text", "region": "title", "text": "x", "visible": true }"#, "", "duplicate id `arr`");
    one_error(r#", { "id": "x", "type": "text", "text": "x", "visible": true }"#, "", "needs a `region`");
    one_error(r#", { "id": "q", "type": "pointer", "label": "q", "target": "arr[0]", "region": "left", "visible": true }"#, "", "takes no `region`");
    one_error(r#", { "id": "q", "type": "pointer", "label": "q", "target": "arr[5]", "visible": true }"#, "", "out of range");
    one_error(r#", { "id": "Bad", "type": "text", "region": "title", "text": "x" }"#, "", "not a valid id");
    one_error(r#", { "id": "x", "type": "blob", "region": "title" }"#, "", "unknown variant `blob`");
}

#[test]
fn warnings_do_not_fail_a_script() {
    let hidden = r#", { "id": "late", "type": "text", "region": "title", "text": "x" }"#;
    let report = check(&script(hidden, r#"{ "action": "replace", "target": "late", "text": "y" }"#));
    assert!(report.ok);
    assert_eq!(report.warnings, 2, "{:#?}", report.diagnostics);

    let w = warnings(hidden, "");
    assert!(w[0].contains("`late` is never shown"), "{w:#?}");
    let w = warnings("", r#"{ "action": "show", "target": "arr" }"#);
    assert!(w[0].contains("already visible"), "{w:#?}");
}

#[test]
fn header_rules() {
    let bad = script("", "").replace(r#""version": 1"#, r#""version": 2"#);
    assert!(check(&bad).diagnostics[0].message.contains("not supported"));
    let bad = script("", "").replace(r#""title": "t","#, r#""title": "t", "canvas": { "width": 1921 },"#);
    assert!(check(&bad).diagnostics[0].message.contains("odd"));
    let report = check("{ not json");
    assert!(!report.ok && report.summary.is_none());
}
