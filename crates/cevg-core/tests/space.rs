//! The space family: scripts validate, frames draw, and the camera and
//! paths animate between exact states.

use cevg_core::draw::Shape;
use cevg_core::space3d::Content;
use cevg_core::{check, parse, Movie, Position, Renderer, World};

fn example(name: &str) -> String {
    let path = format!("{}/../../examples/{name}", env!("CARGO_MANIFEST_DIR"));
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"))
}

#[test]
fn the_3d_examples_are_valid() {
    for name in ["space_saddle.json", "subjects/ml_pca_3d.json"] {
        let report = check(&example(name));
        assert!(report.ok, "{name}: {:#?}", report.diagnostics);
    }
}

#[test]
fn a_space_frame_is_drawn_and_reproducible() {
    let script = parse(&example("space_saddle.json")).unwrap();
    let world = World::at(&script, Position::locate(&script, Some("two-ways"), Some(1)).unwrap());
    let a = Renderer::new().render(&script, &world);
    let b = Renderer::new().render(&script, &world);
    assert_eq!(a.data(), b.data(), "the same world must give the same pixels");
    // The viewport sits in the centre region; something blue-ish (the
    // surface) was painted there.
    let px = |x: u32, y: u32| {
        let i = ((y * a.width() + x) * 4) as usize;
        &a.data()[i..i + 4]
    };
    let painted = (400..1500).step_by(10).flat_map(|x| (260..840).step_by(10).map(move |y| (x, y))).filter(|(x, y)| px(*x, *y) != px(2, 2)).count();
    assert!(painted > 200, "only {painted} samples differ from the background");
}

/// The display list's viewport, as (azimuth, elevation).
fn camera_of(cmds: &[cevg_core::draw::Cmd]) -> (f32, f32) {
    cmds.iter()
        .find_map(|c| match &c.shape {
            Shape::Viewport { camera, .. } => Some((camera[0], camera[1])),
            _ => None,
        })
        .expect("a viewport")
}

#[test]
fn orbit_moves_the_camera_through_exact_states_and_paths_trace() {
    let script = parse(&example("space_saddle.json")).unwrap();
    let speech = vec![2.0; 6];
    let movie = Movie::new(&script, &speech).unwrap();
    // Step 5 (flat index) orbits from azimuth 40 to 130.
    let before = camera_of(&movie.cmds_after(5, 0));
    let after = camera_of(&movie.cmds_after(5, 1));
    assert_eq!((before.0.round(), after.0.round()), (40.0, 130.0));
    let mid = camera_of(&movie.cmds_at(movie.time_of(5, 0.5)));
    assert!(mid.0 > 45.0 && mid.0 < 125.0, "half way through, the azimuth is between: {}", mid.0);

    // Step 3 traces the path along x: part way through, the run is partly drawn.
    let drawn_of = |cmds: &[cevg_core::draw::Cmd]| -> Option<f32> {
        cmds.iter().find_map(|c| match &c.shape {
            Shape::Solid { content, drawn, .. } if c.key.contains("part along_x") && matches!(**content, Content::Segments { .. }) => Some(*drawn),
            _ => None,
        })
    };
    assert_eq!(drawn_of(&movie.cmds_after(3, 0)), None, "hidden before the step");
    assert_eq!(drawn_of(&movie.cmds_after(3, 1)), Some(1.0));
    let part = drawn_of(&movie.cmds_at(movie.time_of(3, 0.5))).expect("drawing");
    assert!(part > 0.05 && part < 0.95, "part way: {part}");
}
