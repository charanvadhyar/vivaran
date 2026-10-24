use cevg_core::soft::SoftBackend;
use cevg_core::space3d::{Camera, Content, Scene, Solid, SpaceBackend};
use std::sync::Arc;
fn main() {
    let gpu = cevg_gpu::VulkanBackend::new().unwrap();
    println!("device: {}", gpu.device_name());
    let solids = vec![
        Solid { content: Arc::new(Content::Mesh { triangles: vec![[0, 1, 2], [0, 2, 3]], lit: true }), vertices: vec![[-0.8, -0.8, 0.0], [0.8, -0.8, 0.0], [0.8, 0.8, 0.0], [-0.8, 0.8, 0.0]], color: [60, 140, 220], drawn: 1.0, opacity: 0.9 },
        Solid { content: Arc::new(Content::Segments { width: 4.0, head: true }), vertices: vec![[0.0, 0.0, 0.0], [0.5, 0.5, 0.7]], color: [245, 184, 61], drawn: 1.0, opacity: 1.0 },
        Solid { content: Arc::new(Content::Points { radius: 9.0 }), vertices: vec![[-0.4, 0.3, 0.2]], color: [255, 138, 168], drawn: 1.0, opacity: 1.0 },
    ];
    let scene = Scene { camera: Camera::default(), width: 480, height: 360, background: [15, 18, 26], solids: &solids };
    gpu.render(&scene).save_png("/tmp/gpu/vulkan.png").unwrap();
    SoftBackend.render(&scene).save_png("/tmp/gpu/soft.png").unwrap();
}
