//! Three-dimensional scenes: the geometry a `space` object hands to a
//! rendering backend, and the camera that looks at it.
//!
//! The family (`families::space`) turns its state into plain geometry here:
//! meshes, segments and points in scene coordinates, with `z` up. A
//! [`SpaceBackend`] rasterises that into a transparent viewport image, which
//! the 2D compositor places like any other image. Labels are not part of the
//! geometry: the compositor projects them with the same camera and draws
//! them on top with the ordinary text machinery, so they stay sharp and are
//! never hidden behind a surface.
//!
//! The software backend in `soft` is the reference; `cevg-gpu` implements
//! the same trait on Vulkan.

use crate::render::Rgb;
use std::sync::Arc;
use tiny_skia::Pixmap;

pub type Vec3 = [f32; 3];

pub fn sub(a: Vec3, b: Vec3) -> Vec3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn add(a: Vec3, b: Vec3) -> Vec3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
pub fn scale(a: Vec3, s: f32) -> Vec3 {
    [a[0] * s, a[1] * s, a[2] * s]
}
pub fn dot(a: Vec3, b: Vec3) -> f32 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross(a: Vec3, b: Vec3) -> Vec3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
pub fn length(a: Vec3) -> f32 {
    dot(a, a).sqrt()
}
pub fn normalize(a: Vec3) -> Vec3 {
    let l = length(a);
    if l > 1e-12 { scale(a, 1.0 / l) } else { [0.0, 0.0, 0.0] }
}

/// An orbiting camera: it looks at `target` from a distance, at an azimuth
/// (degrees, from +x toward +y) and an elevation (degrees above the xy
/// plane). `z` is up. `fov` is the vertical field of view in degrees.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Camera {
    pub azimuth: f32,
    pub elevation: f32,
    pub distance: f32,
    pub target: Vec3,
    pub fov: f32,
}

impl Default for Camera {
    fn default() -> Self {
        Camera { azimuth: 35.0, elevation: 24.0, distance: 3.6, target: [0.0, 0.0, 0.0], fov: 36.0 }
    }
}

/// The camera as numbers, in the order the display list interpolates them.
pub const CAMERA_NUMBERS: usize = 7;

impl Camera {
    pub fn numbers(&self) -> [f32; CAMERA_NUMBERS] {
        [self.azimuth, self.elevation, self.distance, self.target[0], self.target[1], self.target[2], self.fov]
    }

    pub fn from_numbers(n: &[f32]) -> Camera {
        Camera { azimuth: n[0], elevation: n[1], distance: n[2].max(0.05), target: [n[3], n[4], n[5]], fov: n[6].clamp(5.0, 120.0) }
    }

    /// Where the eye is.
    pub fn eye(&self) -> Vec3 {
        let (az, el) = (self.azimuth.to_radians(), self.elevation.to_radians());
        let dir = [el.cos() * az.cos(), el.cos() * az.sin(), el.sin()];
        add(self.target, scale(dir, self.distance))
    }

    /// The view transform: scene coordinates to eye coordinates, where the
    /// eye is at the origin, looks down -z, and y is up on the screen.
    pub fn view(&self) -> View {
        let eye = self.eye();
        let forward = normalize(sub(self.target, eye));
        // Looking straight down would leave no "up"; lean a little.
        let world_up = if forward[2].abs() > 0.999 { [0.0, 1.0, 0.0] } else { [0.0, 0.0, 1.0] };
        let right = normalize(cross(forward, world_up));
        let up = cross(right, forward);
        View { eye, right, up, forward }
    }
}

/// An orthonormal frame at the eye.
#[derive(Debug, Clone, Copy)]
pub struct View {
    pub eye: Vec3,
    pub right: Vec3,
    pub up: Vec3,
    pub forward: Vec3,
}

impl View {
    /// Eye coordinates: x right, y up, z toward the viewer (so points in
    /// front of the camera have negative z).
    pub fn to_eye(&self, p: Vec3) -> Vec3 {
        let d = sub(p, self.eye);
        [dot(d, self.right), dot(d, self.up), -dot(d, self.forward)]
    }
}

/// The projection onto a viewport of `width` x `height` pixels.
#[derive(Debug, Clone, Copy)]
pub struct Projection {
    pub view: View,
    /// Pixels per eye-unit at a depth of one.
    pub focal: f32,
    pub width: f32,
    pub height: f32,
    pub near: f32,
}

impl Projection {
    pub fn new(camera: &Camera, width: f32, height: f32) -> Projection {
        let focal = (height / 2.0) / (camera.fov.to_radians() / 2.0).tan();
        Projection { view: camera.view(), focal, width, height, near: 0.05 }
    }

    /// Screen position (pixels, y down) and depth (eye-space distance along
    /// the viewing direction) of a point. Points behind the camera give
    /// `None`; segments are clipped before they get here.
    pub fn project(&self, p: Vec3) -> Option<((f32, f32), f32)> {
        let e = self.view.to_eye(p);
        let depth = -e[2];
        if depth < self.near {
            return None;
        }
        let x = self.width / 2.0 + e[0] * self.focal / depth;
        let y = self.height / 2.0 - e[1] * self.focal / depth;
        Some(((x, y), depth))
    }

    /// A point in eye coordinates, for the rasteriser.
    pub fn to_eye(&self, p: Vec3) -> Vec3 {
        self.view.to_eye(p)
    }

    /// Screen position of an eye-space point in front of the near plane.
    pub fn screen(&self, e: Vec3) -> (f32, f32) {
        let depth = (-e[2]).max(self.near);
        (self.width / 2.0 + e[0] * self.focal / depth, self.height / 2.0 - e[1] * self.focal / depth)
    }
}

/// What a solid is, apart from where its vertices are. Two solids with the
/// same `Content` can morph into each other by interpolating vertices.
#[derive(Debug, Clone, PartialEq)]
pub enum Content {
    /// Discs of `radius` pixels at each vertex.
    Points { radius: f32 },
    /// Straight runs between consecutive vertices. `head` puts an arrowhead
    /// at the last vertex. `width` is in pixels.
    Segments { width: f32, head: bool },
    /// Triangles over the vertices. Shaded when `lit`.
    Mesh { triangles: Vec<[u32; 3]>, lit: bool },
}

/// One drawable thing: content plus the numbers the display list animates.
#[derive(Debug, Clone)]
pub struct Solid {
    pub content: Arc<Content>,
    pub vertices: Vec<Vec3>,
    pub color: Rgb,
    /// For segments: how much of the run is drawn, 0 to 1.
    pub drawn: f32,
    pub opacity: f32,
}

/// Everything a backend needs for one viewport.
pub struct Scene<'a> {
    pub camera: Camera,
    pub width: u32,
    pub height: u32,
    pub background: Rgb,
    pub solids: &'a [Solid],
}

/// A rasteriser for [`Scene`]s. Shared between frame threads, so it must be
/// `Sync`; a GPU backend guards its device behind a lock.
pub trait SpaceBackend: Send + Sync {
    fn name(&self) -> &'static str;
    /// A premultiplied RGBA image, transparent where nothing was drawn.
    fn render(&self, scene: &Scene) -> Pixmap;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_target_projects_to_the_centre_and_z_is_up() {
        let camera = Camera::default();
        let proj = Projection::new(&camera, 800.0, 600.0);
        let ((x, y), depth) = proj.project(camera.target).unwrap();
        assert!((x - 400.0).abs() < 1e-3 && (y - 300.0).abs() < 1e-3);
        assert!((depth - camera.distance).abs() < 1e-4);
        let ((_, above), _) = proj.project([0.0, 0.0, 0.5]).unwrap();
        assert!(above < 300.0, "a point above the target is higher on screen");
        let ((right, _), _) = proj.project([0.0, 1.0, 0.0]).unwrap();
        assert!(right > 400.0, "with azimuth 35 from +x, +y is to the right of +x");
    }

    #[test]
    fn points_behind_the_camera_are_rejected() {
        let camera = Camera { distance: 1.0, ..Camera::default() };
        let proj = Projection::new(&camera, 100.0, 100.0);
        assert!(proj.project(scale(camera.eye(), 2.0)).is_none());
    }
}
