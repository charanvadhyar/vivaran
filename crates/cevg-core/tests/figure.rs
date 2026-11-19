//! The figure family: SVG pictures whose top-level groups are parts.

use cevg_core::{check, frame_png, Severity};

const SVG: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="50 50 400 300">
  <defs><marker id="m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#fff"/></marker></defs>
  <rect x="60" y="60" width="380" height="20" fill="#333"/>
  <g id="top"><rect x="100" y="100" width="120" height="50" fill="#456"/><text x="160" y="130" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#fff">Top</text></g>
  <g id="link"><line x1="160" y1="150" x2="160" y2="240" stroke="#fff" stroke-width="2" marker-end="url(#m)"/></g>
  <g id="bottom"><rect x="100" y="250" width="120" height="50" fill="#654"/></g>
</svg>"##;

fn script(build: bool, actions: &str) -> String {
    let obj = serde_json::json!({ "id": "fig", "type": "figure", "region": "center", "visible": true, "svg": SVG, "build": build });
    format!(
        r#"{{ "version": 1, "title": "t", "objects": [ {obj} ],
  "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Go." }}, "do": [ {actions} ] }} ] }} ] }}"#
    )
}

fn errors(json: &str) -> Vec<String> {
    check(json).diagnostics.into_iter().filter(|d| d.severity == Severity::Error).map(|d| format!("{}: {}", d.path, d.message)).collect()
}

#[test]
fn parts_are_the_top_level_groups() {
    assert_eq!(cevg_core::families::figure::part_names(SVG).unwrap(), ["top", "link", "bottom"]);
}

#[test]
fn reveal_highlight_and_unknown_parts() {
    let ok = script(true, r#"{ "action": "reveal", "target": "fig.top" }, { "action": "highlight", "target": "fig.top" }, { "action": "reveal", "target": "fig" }"#);
    assert!(errors(&ok).is_empty(), "{:#?}", errors(&ok));
    let bad = errors(&script(true, r#"{ "action": "reveal", "target": "fig.middle" }"#));
    assert_eq!(bad.len(), 1, "{bad:#?}");
    assert!(bad[0].contains("has no part `middle`") && bad[0].contains("`fig.top`"), "{}", bad[0]);
}

#[test]
fn a_figure_without_svg_needs_a_prompt() {
    let json = r#"{ "version": 1, "title": "t", "objects": [ { "id": "fig", "type": "figure", "region": "center" } ],
      "scenes": [ { "id": "s", "steps": [ { "say": { "en": "Go." }, "do": [ { "action": "show", "target": "fig" } ] } ] } ] }"#;
    assert!(errors(json).iter().any(|e| e.contains("needs `svg`")));
    let broken = script(false, r#"{ "action": "show", "target": "fig" }"#).replace("<svg xmlns", "<svgx xmlns");
    assert!(!errors(&broken).is_empty());
}

#[test]
fn layers_add_up_to_the_whole_picture() {
    // Base plus every part, laid over each other, should match the whole SVG.
    let whole = cevg_core::families::figure::rasterize(SVG, 800).unwrap();
    let layers = cevg_core::families::figure::layers(SVG, 800).unwrap();
    let mut sum = tiny_skia::Pixmap::new(whole.width(), whole.height()).unwrap();
    for (_, b, img) in &layers {
        sum.draw_pixmap(b[0] as i32, b[1] as i32, img.as_ref(), &tiny_skia::PixmapPaint::default(), tiny_skia::Transform::identity(), None);
    }
    let diff: u64 = whole.data().iter().zip(sum.data()).map(|(a, b)| (*a as i64 - *b as i64).unsigned_abs()).sum();
    let mean = diff as f64 / whole.data().len() as f64;
    assert!(mean < 1.0, "layers differ from the whole picture by {mean:.2} per channel");
}

#[test]
fn a_built_figure_draws_more_as_parts_are_revealed() {
    let before = frame_png(&script(true, r#"{ "action": "reveal", "target": "fig.top" }"#), None, None, Some(0.0), None).unwrap();
    let after = frame_png(&script(true, r#"{ "action": "reveal", "target": "fig.top" }"#), None, None, Some(1.0), None).unwrap();
    assert_ne!(before, after);
}
