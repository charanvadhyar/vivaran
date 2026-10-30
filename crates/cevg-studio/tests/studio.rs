//! End-to-end checks on the studio pipeline: the example scene, the files
//! `build` writes, and the guide the assistant reads.

use serde_json::Value;

const TOKAMAK: &str = include_str!("../../../examples/studio/tokamak.json");

fn scratch(name: &str) -> std::path::PathBuf {
    let dir = std::env::temp_dir().join(format!("cevg-studio-test-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    dir
}

#[test]
fn tokamak_validates() {
    let report = cevg_studio::check(TOKAMAK);
    assert!(report.ok, "problems: {:?}", report.problems);
    let s = report.summary.expect("summary");
    assert_eq!(s.parts, 16);
    assert_eq!(s.steps, 9);
    // 12 coil copies plus their group node on top of the 16 declared parts.
    assert!(s.nodes > s.parts, "arrays should add nodes: {}", s.nodes);
    assert!(s.triangles > 50_000, "too coarse: {} triangles", s.triangles);
    assert!(s.frames > 30 * 30, "about a minute expected, got {} frames", s.frames);
}

#[test]
fn build_writes_glb_and_timeline() {
    let dir = scratch("build");
    let built = cevg_studio::build(TOKAMAK, &dir, None).expect("build");

    let glb = std::fs::read(&built.glb).expect("glb");
    assert_eq!(&glb[0..4], b"glTF", "GLB magic");
    assert_eq!(u32::from_le_bytes(glb[4..8].try_into().unwrap()), 2, "glTF version");
    assert_eq!(u32::from_le_bytes(glb[8..12].try_into().unwrap()) as usize, glb.len(), "declared length");
    assert_eq!(glb.len() % 4, 0, "GLB is 4-byte aligned");
    // The JSON chunk parses and names our meshes and the camera.
    let json_len = u32::from_le_bytes(glb[12..16].try_into().unwrap()) as usize;
    assert_eq!(&glb[16..20], b"JSON");
    let gltf: Value = serde_json::from_slice(&glb[20..20 + json_len]).expect("gltf json");
    assert_eq!(gltf["asset"]["version"], "2.0");
    assert!(!gltf["meshes"].as_array().unwrap().is_empty());
    assert!(gltf["cameras"].as_array().is_some_and(|c| c.len() == 1));
    let names: Vec<&str> = gltf["nodes"].as_array().unwrap().iter().filter_map(|n| n["name"].as_str()).collect();
    for want in ["plasma", "tf_coil[0]", "tf_coil[11]", "cs_winding"] {
        assert!(names.contains(&want), "node {want} missing from {names:?}");
    }

    let tl: Value = serde_json::from_str(&std::fs::read_to_string(&built.timeline).unwrap()).expect("timeline json");
    assert_eq!(tl["format"], "vivaran-studio-timeline/1");
    assert_eq!(tl["frames"].as_u64().unwrap() as usize, built.summary.frames);
    assert_eq!(tl["steps"].as_array().unwrap().len(), 9);
    assert!(!tl["lights"].as_array().unwrap().is_empty(), "the preset adds lights");
    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn timeline_has_the_tracks_the_script_asks_for() {
    let dir = scratch("tracks");
    let built = cevg_studio::build(TOKAMAK, &dir, None).expect("build");
    let tl: Value = serde_json::from_str(&std::fs::read_to_string(&built.timeline).unwrap()).unwrap();
    let tracks = tl["tracks"].as_array().unwrap();
    let has = |node: &str, path: &str| tracks.iter().any(|t| t["node"] == node && t["path"] == path);
    assert!(has("plasma", "emission_strength"), "glow on the plasma");
    assert!(has("divertor", "emission_strength"), "highlight on the divertor");
    assert!(has("tf_coil[3]", "translation"), "explode moves the coil copies");
    assert!(has("cs", "translation"), "the solenoid is lifted out");
    for t in tracks {
        let frames = t["frames"].as_array().unwrap();
        assert_eq!(frames.len(), t["values"].as_array().unwrap().len(), "{} {}", t["node"], t["path"]);
        assert!(frames.windows(2).all(|w| w[0].as_u64() < w[1].as_u64()), "frames increase");
    }
    let cam = &tl["camera"];
    let n = cam["frames"].as_array().unwrap().len();
    assert!(n >= 2, "the camera moves");
    assert_eq!(cam["position"].as_array().unwrap().len(), n);
    assert_eq!(cam["rotation"].as_array().unwrap().len(), n);
    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn narration_lengths_set_the_timing() {
    let short = cevg_studio::build(TOKAMAK, &scratch("short"), Some(&[2.0; 9])).unwrap();
    let long = cevg_studio::build(TOKAMAK, &scratch("long"), Some(&[8.0; 9])).unwrap();
    assert!(long.summary.frames > short.summary.frames + 9 * 5 * 30);
}

#[test]
fn problems_name_their_path() {
    let bad = TOKAMAK.replace(r#""material": "copper", "at": [0, 0, 1.25]"#, r#""material": "bronze", "at": [0, 0, 1.25]"#);
    let report = cevg_studio::check(&bad);
    assert!(!report.ok);
    assert!(report.problems.iter().any(|p| p.path.contains("parts") && p.message.contains("bronze")), "{:?}", report.problems);

    let bad = TOKAMAK.replace(r#""target": "divertor" }, { "action": "label""#, r#""target": "divertr" }, { "action": "label""#);
    let report = cevg_studio::check(&bad);
    assert!(!report.ok);
    assert!(report.problems.iter().any(|p| p.message.contains("divertr")), "{:?}", report.problems);

    let report = cevg_studio::check(r#"{ "version": 1, "title": "x", "parts": [ { "id": "a", "shape": { "kind": "blob" } } ], "scenes": [] }"#);
    assert!(!report.ok);
    assert!(report.problems[0].path.starts_with("parts[0]"), "{:?}", report.problems);
}

#[test]
fn guide_covers_every_action_and_shape() {
    let guide = cevg_studio::GUIDE;
    let actions = [
        "show", "hide", "move", "rotate", "spin", "stop", "explode", "assemble", "glow", "highlight", "reset", "camera", "focus", "label",
        "unlabel",
    ];
    for a in actions {
        assert!(guide.contains(&format!("| `{a}` |")), "guide does not document action `{a}`");
    }
    let shapes = ["box", "cylinder", "tube", "cone", "sphere", "torus", "revolve", "extrude", "sweep", "gear"];
    for s in shapes {
        assert!(guide.contains(&format!("| `{s}` |")), "guide does not document shape `{s}`");
    }
    for p in ["helix", "circle", "arc", "d_shape", "points"] {
        assert!(guide.contains(&format!("| `{p}` |")), "guide does not document path `{p}`");
    }
    for m in [
        "steel", "brushed_steel", "aluminium", "titanium", "chrome", "copper", "brass", "gold", "plastic", "rubber", "ceramic", "paint", "glass", "emissive",
    ] {
        assert!(guide.contains(&format!("`{m}`")), "guide does not document material `{m}`");
    }
    // Every action the guide documents is one the parser accepts.
    for a in actions {
        let target = if a == "camera" { "" } else { r#", "target": "a""# };
        let extra = match a {
            "move" => r#", "by": [0, 0, 1]"#,
            "rotate" => r#", "by": [0, 0, 90]"#,
            "spin" => r#", "axis": "z", "rpm": 10"#,
            "explode" => r#", "distance": 1"#,
            "glow" => r#", "strength": 4"#,
            "camera" => r#", "azimuth": 10"#,
            _ => "",
        };
        let json = format!(
            r#"{{ "version": 1, "title": "t", "materials": {{ "m": {{ "preset": "steel" }} }},
                 "parts": [ {{ "id": "a", "shape": {{ "kind": "box", "size": [1, 1, 1] }}, "material": "m", "label": "Block" }} ],
                 "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "One." }}, "do": [ {{ "action": "{a}"{target}{extra} }} ] }} ] }} ] }}"#
        );
        let r = cevg_studio::check(&json);
        assert!(r.ok, "action `{a}` rejected: {:?}", r.problems);
    }
}
