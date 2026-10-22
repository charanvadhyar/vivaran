//! Milestone 1 acceptance: the binary search script passes cleanly, and each
//! deliberately broken script fails at the right place for the right reason.

use cevg_core::{check, Report, Severity};

fn run(name: &str) -> Report {
    let path = format!("{}/../../examples/{name}", env!("CARGO_MANIFEST_DIR"));
    let text = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
    check(&text)
}

/// The script must fail with exactly one error, at `path`, mentioning `needle`.
fn fails(name: &str, path: &str, needle: &str) {
    let report = run(&format!("broken/{name}.json"));
    assert!(!report.ok, "{name} should be invalid");
    let errors: Vec<_> = report
        .diagnostics
        .iter()
        .filter(|d| d.severity == Severity::Error)
        .collect();
    assert_eq!(errors.len(), 1, "{name}: {errors:#?}");
    assert_eq!(errors[0].path, path, "{name}");
    assert!(
        errors[0].message.contains(needle),
        "{name}: `{}` should mention `{needle}`",
        errors[0].message
    );
}

#[test]
fn binary_search_is_clean() {
    let report = run("binary_search.json");
    assert!(report.ok, "{:#?}", report.diagnostics);
    assert!(report.diagnostics.is_empty(), "{:#?}", report.diagnostics);
    let summary = report.summary.unwrap();
    assert_eq!((summary.objects, summary.scenes, summary.steps), (6, 3, 7));
    assert_eq!(summary.languages, ["en", "hi", "te"]);
}

#[test]
fn index_out_of_range() {
    fails(
        "index_out_of_range",
        "scenes[0].steps[1].do[0].target",
        "arr[9] is out of range, arr has 7 elements",
    );
}

#[test]
fn unknown_object() {
    fails("unknown_object", "scenes[0].steps[1].do[0].target", "unknown object `array`");
}

#[test]
fn wrong_kind() {
    fails("wrong_kind", "scenes[0].steps[1].do[0].b", "`note` is a text");
}

#[test]
fn misspelled_field() {
    fails("misspelled_field", "scenes[0].steps[1].do[0]", "unknown field `targett`");
}

#[test]
fn dangling_pointer() {
    fails("dangling_pointer", "scenes[0].steps[1].do[0]", "leaves pointer `hi` on arr[6]");
}

#[test]
fn missing_english() {
    fails("missing_english", "scenes[0].steps[1].say", "missing `en` narration");
}
