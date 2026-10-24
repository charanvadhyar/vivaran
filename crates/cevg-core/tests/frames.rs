//! Milestone 2: the world replays correctly and frames are drawn, the same
//! way every time.

use cevg_core::families::{Body, Emphasis};
use cevg_core::{frame_png, parse, Position, Renderer, World};

fn example(name: &str) -> String {
    let path = format!("{}/../../examples/{name}", env!("CARGO_MANIFEST_DIR"));
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"))
}

#[test]
fn world_follows_the_script() {
    let script = parse(&example("binary_search.json")).unwrap();

    let start = World::new(&script);
    assert!(start.items.iter().all(|i| !i.visible), "objects start hidden");

    let pos = Position::locate(&script, Some("first-check"), Some(1)).unwrap();
    let world = World::at(&script, pos);
    let Body::Pointer(lo) = &world.get("lo").unwrap().body else { panic!() };
    assert_eq!(lo.target.to_string(), "arr[4]");
    let Body::Array(arr) = &world.get("arr").unwrap().body else { panic!() };
    let dimmed: Vec<bool> = arr.cells.iter().map(|c| c.emphasis == Emphasis::Dim).collect();
    assert_eq!(dimmed, [true, true, true, true, false, false, false]);
    assert!(!world.get("note").unwrap().visible);

    let end = World::at(&script, Position::locate(&script, None, None).unwrap());
    let Body::Array(arr) = &end.get("arr").unwrap().body else { panic!() };
    assert_eq!(arr.cells[5].emphasis, Emphasis::Highlight);
    let Body::Text(note) = &end.get("note").unwrap().body else { panic!() };
    assert_eq!(note.text, "About log n checks");
}

#[test]
fn locate_explains_bad_positions() {
    let script = parse(&example("binary_search.json")).unwrap();
    assert!(Position::locate(&script, Some("nope"), None).unwrap_err().contains("setup, first-check"));
    assert!(Position::locate(&script, Some("setup"), Some(2)).unwrap_err().contains("steps 0 to 1"));
}

#[test]
fn frames_are_drawn_and_reproducible() {
    let script = parse(&example("binary_search.json")).unwrap();
    let world = World::at(&script, Position::locate(&script, None, None).unwrap());

    let a = Renderer::new().render(&script, &world);
    let b = Renderer::new().render(&script, &world);
    assert_eq!((a.width(), a.height()), (1920, 1080));
    assert!(a.data() == b.data(), "the same world must give the same pixels");

    // Something other than background was painted.
    let background = &a.data()[..4];
    assert!(a.data().chunks(4).any(|px| px != background));

    // A different step gives a different picture.
    let earlier = World::at(&script, Position::locate(&script, Some("setup"), Some(0)).unwrap());
    assert!(Renderer::new().render(&script, &earlier).data() != a.data());
}

#[test]
fn telugu_and_hindi_use_their_own_glyphs() {
    // If shaping fell back to missing-glyph boxes, the two scripts would
    // paint the same shapes. Different pictures show real glyphs were found.
    let frame = |text: &str| {
        let json = format!(
            r#"{{ "version": 1, "title": "t",
                 "canvas": {{ "width": 640, "height": 360 }},
                 "objects": [ {{ "id": "t", "type": "text", "region": "center", "text": "{text}", "visible": true }} ],
                 "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Hi." }} }} ] }} ] }}"#
        );
        frame_png(&json, None, None, None, None).expect("valid script")
    };
    let (te, hi, blank) = (frame("తెలుగు"), frame("हिन्दी"), frame(" "));
    assert!(te != blank && hi != blank && te != hi);
}

#[test]
fn invalid_scripts_are_not_drawn() {
    let report = frame_png(&example("broken/index_out_of_range.json"), None, None, None, None).unwrap_err();
    assert!(!report.ok);
    assert!(report.diagnostics[0].message.contains("out of range"));
}

#[test]
fn hidden_objects_take_no_room() {
    use cevg_core::draw::Shape;
    // Two texts share the centre. With one hidden, the other has the whole
    // region and sits in its middle; with both shown, they share it.
    let script = |second_visible: bool| {
        parse(&format!(
            r#"{{ "version": 1, "title": "t",
                 "objects": [
                   {{ "id": "a", "type": "text", "region": "center", "text": "first", "visible": true }},
                   {{ "id": "b", "type": "text", "region": "center", "text": "second", "visible": {second_visible} }}
                 ],
                 "scenes": [ {{ "id": "s", "steps": [ {{ "say": {{ "en": "Hi." }} }} ] }} ] }}"#
        ))
        .unwrap()
    };
    let y_of_first = |script: &cevg_core::Script| {
        let list = Renderer::new().display_list(script, &World::new(script));
        list.iter()
            .find_map(|c| match &c.shape {
                Shape::Text { text, y, .. } if text == "first" => Some(*y),
                _ => None,
            })
            .unwrap()
    };
    let (alone, shared) = (y_of_first(&script(false)), y_of_first(&script(true)));
    assert!((alone - 540.0).abs() < 1.0, "alone it is centred, at {alone}");
    assert!(shared < alone - 100.0, "sharing, it moves up to {shared}");
}

#[test]
fn the_guide_covers_every_object_type_and_action() {
    // The names are read from the source, so a new action cannot be added
    // without the guide (which is what Claude reads) mentioning it.
    let source = include_str!("../src/script.rs");
    let names: Vec<&str> = source
        .lines()
        .filter(|l| l.trim_start().starts_with("ActionKind::") && l.contains("{ .. } => \"") && l.trim_end().ends_with("\","))
        .filter_map(|l| l.split('"').nth(1))
        .filter(|name| !name.contains(' '))
        .collect();
    assert!(names.len() >= 36, "found only {} action names", names.len());
    for name in names {
        assert!(cevg_core::GUIDE.contains(&format!("`{name}`")), "the guide does not mention the action `{name}`");
    }
    for kind in ["text", "array", "pointer", "arrow", "code", "diagram", "table", "math", "plot", "timeline", "space"] {
        assert!(cevg_core::GUIDE.contains(&format!("\"type\": \"{kind}\"")), "the guide has no example of type `{kind}`");
    }
}
