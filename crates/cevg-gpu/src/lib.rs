//! The Vulkan backend for `space` scenes.
//!
//! Headless: no window, no swapchain. Each viewport is drawn into an
//! offscreen colour attachment (4x MSAA, resolved), read back into a
//! premultiplied RGBA image, and handed to the 2D compositor like any other
//! image. One shader draws everything (see `shaders/solid.vert`): meshes
//! arrive in scene space and are lit; lines, arrowheads and discs are
//! expanded on the CPU into screen-space triangles with a depth each, so
//! they look the same as the software backend's and need no wide-line
//! support from the driver.
//!
//! The device is shared between frame threads behind a mutex, so frames
//! are drawn one at a time; a frame is a few milliseconds, the readback
//! dominates, and the 2D work around it still runs in parallel.
//!
//! Shaders are GLSL compiled to SPIR-V with `glslangValidator` and committed
//! next to the sources, so building needs no Vulkan SDK.

use ash::vk;
use cevg_core::render::Rgb;
use cevg_core::space3d::{add, cross, length, normalize, scale, sub, Content, Projection, Scene, Solid, SpaceBackend, Vec3};
use std::ffi::CStr;
use std::sync::Mutex;
use tiny_skia::Pixmap;

const VERT: &[u8] = include_bytes!("../shaders/solid.vert.spv");
const FRAG: &[u8] = include_bytes!("../shaders/solid.frag.spv");
const SAMPLES: vk::SampleCountFlags = vk::SampleCountFlags::TYPE_4;
const FORMAT: vk::Format = vk::Format::R8G8B8A8_UNORM;
const DEPTH: vk::Format = vk::Format::D32_SFLOAT;
const NEAR: f32 = 0.05;
const FAR: f32 = 100.0;
/// Lines and points sit a little in front of the surfaces they touch.
const LIFT: f32 = 0.012;

#[repr(C)]
#[derive(Clone, Copy)]
struct Vertex {
    pos: [f32; 3],
    normal: [f32; 3],
    color: [f32; 4],
}

#[repr(C)]
#[derive(Clone, Copy)]
struct Push {
    view_proj: [f32; 16],
    light: [f32; 4],
    view: [[f32; 4]; 3],
}

/// A batch of triangles drawn with one pipeline and one mode.
struct Draw {
    first: u32,
    count: u32,
    lit: bool,
    translucent: bool,
}

struct Targets {
    width: u32,
    height: u32,
    color: (vk::Image, vk::DeviceMemory, vk::ImageView),
    depth: (vk::Image, vk::DeviceMemory, vk::ImageView),
    resolve: (vk::Image, vk::DeviceMemory, vk::ImageView),
    framebuffer: vk::Framebuffer,
    readback: (vk::Buffer, vk::DeviceMemory, u64),
}

struct Context {
    _entry: ash::Entry,
    instance: ash::Instance,
    physical: vk::PhysicalDevice,
    device: ash::Device,
    queue: vk::Queue,
    pool: vk::CommandPool,
    cmd: vk::CommandBuffer,
    fence: vk::Fence,
    render_pass: vk::RenderPass,
    layout: vk::PipelineLayout,
    opaque: vk::Pipeline,
    translucent: vk::Pipeline,
    memory: vk::PhysicalDeviceMemoryProperties,
    vertices: Option<(vk::Buffer, vk::DeviceMemory, u64)>,
    targets: Option<Targets>,
    name: String,
}

pub struct VulkanBackend {
    cx: Mutex<Context>,
}

// Vulkan handles are plain integers; the mutex is what makes sharing safe.
unsafe impl Send for Context {}
unsafe impl Sync for Context {}

fn err<T>(what: &str, e: impl std::fmt::Display) -> Result<T, String> {
    Err(format!("{what}: {e}"))
}

impl VulkanBackend {
    /// Open the first suitable device. A discrete GPU is preferred, then an
    /// integrated one, then a software device such as lavapipe.
    pub fn new() -> Result<VulkanBackend, String> {
        let cx = unsafe { Context::new()? };
        Ok(VulkanBackend { cx: Mutex::new(cx) })
    }

    /// The device in use, for `cevg gpu`.
    pub fn device_name(&self) -> String {
        self.cx.lock().expect("gpu lock").name.clone()
    }
}

impl SpaceBackend for VulkanBackend {
    fn name(&self) -> &'static str {
        "vulkan"
    }

    fn render(&self, scene: &Scene) -> Pixmap {
        let mut cx = self.cx.lock().expect("gpu lock");
        match unsafe { cx.render(scene) } {
            Ok(image) => image,
            Err(e) => {
                // A broken frame must not take the whole video down.
                eprintln!("cevg-gpu: {e}; this viewport is left empty");
                Pixmap::new(scene.width.max(1), scene.height.max(1)).expect("viewport size")
            }
        }
    }
}

// -------------------------------------------------------------- geometry

fn lin(c: Rgb) -> [f32; 3] {
    [c[0] as f32 / 255.0, c[1] as f32 / 255.0, c[2] as f32 / 255.0]
}

/// Depth in [0, 1] as the depth buffer sees it, for CPU-expanded geometry.
fn ndc_z(depth: f32) -> f32 {
    let (a, b) = (FAR / (FAR - NEAR), -FAR * NEAR / (FAR - NEAR));
    (a * depth + b) / depth
}

/// Column-major 4x4 product.
fn mul(a: &[f32; 16], b: &[f32; 16]) -> [f32; 16] {
    let mut out = [0.0; 16];
    for col in 0..4 {
        for row in 0..4 {
            out[col * 4 + row] = (0..4).map(|k| a[k * 4 + row] * b[col * 4 + k]).sum();
        }
    }
    out
}

/// Scene-to-clip matrix matching `Projection` pixel for pixel, with
/// Vulkan's y-down clip space.
fn view_proj(proj: &Projection) -> ([f32; 16], [[f32; 4]; 3]) {
    let v = &proj.view;
    let (r, u, f, e) = (v.right, v.up, v.forward, v.eye);
    // Rows of the rotation: right, up, -forward (eye z points at the viewer).
    let rows = [r, u, [-f[0], -f[1], -f[2]]];
    let t = [-(r[0] * e[0] + r[1] * e[1] + r[2] * e[2]), -(u[0] * e[0] + u[1] * e[1] + u[2] * e[2]), f[0] * e[0] + f[1] * e[1] + f[2] * e[2]];
    // Column-major: element (row i, col j) at j*4 + i.
    let mut view = [0.0f32; 16];
    for (i, row) in rows.iter().enumerate() {
        for j in 0..3 {
            view[j * 4 + i] = row[j];
        }
        view[12 + i] = t[i];
    }
    view[15] = 1.0;
    let (a, b) = (FAR / (FAR - NEAR), -FAR * NEAR / (FAR - NEAR));
    let mut p = [0.0f32; 16];
    p[0] = proj.focal / (proj.width / 2.0);
    p[5] = -proj.focal / (proj.height / 2.0);
    p[10] = -a;
    p[14] = b;
    p[11] = -1.0;
    let cols = [
        [rows[0][0], rows[1][0], rows[2][0], 0.0],
        [rows[0][1], rows[1][1], rows[2][1], 0.0],
        [rows[0][2], rows[1][2], rows[2][2], 0.0],
    ];
    (mul(&p, &view), cols)
}

/// Clip a segment in eye space against the near plane.
fn clip_near(a: Vec3, b: Vec3) -> Option<(Vec3, Vec3)> {
    let (da, db) = (-a[2] - NEAR, -b[2] - NEAR);
    match (da >= 0.0, db >= 0.0) {
        (true, true) => Some((a, b)),
        (false, false) => None,
        (true, false) => Some((a, add(a, scale(sub(b, a), da / (da - db))))),
        (false, true) => Some((add(a, scale(sub(b, a), da / (da - db))), b)),
    }
}

/// Builds the vertex list for one scene: lit triangles in scene space, and
/// flat triangles already in clip space.
struct Builder<'a> {
    proj: &'a Projection,
    vertices: Vec<Vertex>,
    draws: Vec<Draw>,
}

impl Builder<'_> {
    fn flat(&mut self, screen: (f32, f32), depth: f32, color: [f32; 4]) -> Vertex {
        let x = screen.0 / self.proj.width * 2.0 - 1.0;
        let y = screen.1 / self.proj.height * 2.0 - 1.0;
        Vertex { pos: [x, y, ndc_z(depth.max(NEAR))], normal: [0.0; 3], color }
    }

    fn tri(&mut self, a: Vertex, b: Vertex, c: Vertex) {
        self.vertices.extend([a, b, c]);
    }

    fn segment(&mut self, a: ((f32, f32), f32), b: ((f32, f32), f32), width: f32, color: [f32; 4]) {
        let ((ax, ay), za) = a;
        let ((bx, by), zb) = b;
        let (dx, dy) = (bx - ax, by - ay);
        let len = (dx * dx + dy * dy).sqrt();
        if len < 0.01 {
            return;
        }
        let (nx, ny) = (-dy / len * width / 2.0, dx / len * width / 2.0);
        let (ex, ey) = (dx / len * width / 2.0, dy / len * width / 2.0);
        let p0 = self.flat((ax - ex + nx, ay - ey + ny), za, color);
        let p1 = self.flat((ax - ex - nx, ay - ey - ny), za, color);
        let p2 = self.flat((bx + ex - nx, by + ey - ny), zb, color);
        let p3 = self.flat((bx + ex + nx, by + ey + ny), zb, color);
        self.tri(p0, p1, p2);
        self.tri(p0, p2, p3);
    }

    fn head(&mut self, from: (f32, f32), tip: ((f32, f32), f32), width: f32, color: [f32; 4]) {
        let ((tx, ty), z) = tip;
        let (dx, dy) = (tx - from.0, ty - from.1);
        let len = (dx * dx + dy * dy).sqrt();
        if len < 0.01 {
            return;
        }
        let (ux, uy) = (dx / len, dy / len);
        let size = (width * 4.0).min(len * 0.6);
        let base = (tx - ux * size, ty - uy * size);
        let half = size * 0.6;
        let t = self.flat((tx, ty), z, color);
        let l = self.flat((base.0 - uy * half, base.1 + ux * half), z, color);
        let r = self.flat((base.0 + uy * half, base.1 - ux * half), z, color);
        self.tri(t, l, r);
    }

    fn disc(&mut self, centre: (f32, f32), depth: f32, radius: f32, color: [f32; 4]) {
        const N: usize = 28;
        let c = self.flat(centre, depth, color);
        let rim: Vec<Vertex> = (0..N)
            .map(|i| {
                let t = i as f32 / N as f32 * std::f32::consts::TAU;
                self.flat((centre.0 + radius * t.cos(), centre.1 + radius * t.sin()), depth, color)
            })
            .collect();
        for i in 0..N {
            self.tri(c, rim[i], rim[(i + 1) % N]);
        }
    }

    fn solid(&mut self, solid: &Solid, background: Rgb) {
        let first = self.vertices.len() as u32;
        let rgb = lin(solid.color);
        let color = [rgb[0], rgb[1], rgb[2], solid.opacity];
        let translucent = solid.opacity < 0.995;
        let proj = self.proj;
        let eye: Vec<Vec3> = solid.vertices.iter().map(|v| proj.to_eye(*v)).collect();
        let lit = match &*solid.content {
            Content::Points { radius } => {
                let bg = lin(background);
                for e in &eye {
                    if -e[2] < NEAR {
                        continue;
                    }
                    let (x, y) = proj.screen(*e);
                    let z = -e[2] * (1.0 - LIFT);
                    self.disc((x, y), z, radius + 1.5, [bg[0], bg[1], bg[2], solid.opacity]);
                    self.disc((x, y), z - 0.002, *radius, color);
                }
                false
            }
            Content::Segments { width, head } => {
                let total: f32 = eye.windows(2).map(|p| length(sub(p[1], p[0]))).sum();
                let mut left = total * solid.drawn.clamp(0.0, 1.0);
                let mut last: Option<((f32, f32), (f32, f32))> = None;
                for pair in eye.windows(2) {
                    if left <= 0.0 {
                        break;
                    }
                    let step = length(sub(pair[1], pair[0]));
                    let end = if step <= left { pair[1] } else { add(pair[0], scale(sub(pair[1], pair[0]), left / step)) };
                    left -= step;
                    let Some((a, b)) = clip_near(pair[0], end) else { continue };
                    let (pa, pb) = (proj.screen(a), proj.screen(b));
                    self.segment((pa, -a[2] * (1.0 - LIFT)), (pb, -b[2] * (1.0 - LIFT)), *width, color);
                    last = Some((pa, pb));
                }
                if *head && solid.drawn >= 0.999 {
                    if let (Some((from, to)), Some(e)) = (last, eye.last()) {
                        self.head(from, (to, -e[2] * (1.0 - LIFT)), *width, color);
                    }
                }
                false
            }
            Content::Mesh { triangles, lit } => {
                for tri in triangles {
                    let (a, b, c) = (solid.vertices[tri[0] as usize], solid.vertices[tri[1] as usize], solid.vertices[tri[2] as usize]);
                    let (ea, eb, ec) = (eye[tri[0] as usize], eye[tri[1] as usize], eye[tri[2] as usize]);
                    if -ea[2] < NEAR || -eb[2] < NEAR || -ec[2] < NEAR {
                        continue;
                    }
                    let normal = if *lit { normalize(cross(sub(b, a), sub(c, a))) } else { [0.0, 0.0, 0.0] };
                    for p in [a, b, c] {
                        self.vertices.push(Vertex { pos: p, normal, color });
                    }
                }
                *lit
            }
        };
        let count = self.vertices.len() as u32 - first;
        if count > 0 {
            self.draws.push(Draw { first, count, lit, translucent });
        }
    }
}

// ---------------------------------------------------------------- vulkan

impl Context {
    unsafe fn new() -> Result<Context, String> {
        let entry = ash::Entry::load().map_err(|e| format!("no Vulkan loader found ({e}); install the GPU driver, or use --gpu soft"))?;
        let app = vk::ApplicationInfo::default().application_name(c"cevg").api_version(vk::make_api_version(0, 1, 1, 0));
        let mut layers: Vec<*const i8> = vec![];
        if std::env::var_os("CEVG_VK_VALIDATION").is_some() {
            let available = entry.enumerate_instance_layer_properties().unwrap_or_default();
            if available.iter().any(|l| CStr::from_ptr(l.layer_name.as_ptr()) == c"VK_LAYER_KHRONOS_validation") {
                layers.push(c"VK_LAYER_KHRONOS_validation".as_ptr());
            }
        }
        let instance = entry
            .create_instance(&vk::InstanceCreateInfo::default().application_info(&app).enabled_layer_names(&layers), None)
            .or_else(|e| err("could not create a Vulkan instance", e))?;

        // Pick a device with a graphics queue; discrete first.
        let devices = instance.enumerate_physical_devices().or_else(|e| err("no Vulkan devices", e))?;
        let rank = |d: &vk::PhysicalDevice| match instance.get_physical_device_properties(*d).device_type {
            vk::PhysicalDeviceType::DISCRETE_GPU => 0,
            vk::PhysicalDeviceType::INTEGRATED_GPU => 1,
            vk::PhysicalDeviceType::VIRTUAL_GPU => 2,
            vk::PhysicalDeviceType::CPU => 3,
            _ => 4,
        };
        let mut chosen = None;
        for d in devices.iter() {
            let families = instance.get_physical_device_queue_family_properties(*d);
            if let Some(q) = families.iter().position(|f| f.queue_flags.contains(vk::QueueFlags::GRAPHICS)) {
                if chosen.is_none_or(|(c, _)| rank(d) < rank(&c)) {
                    chosen = Some((*d, q as u32));
                }
            }
        }
        let Some((physical, family)) = chosen else {
            instance.destroy_instance(None);
            return Err("no Vulkan device with a graphics queue".to_string());
        };
        let props = instance.get_physical_device_properties(physical);
        let name = CStr::from_ptr(props.device_name.as_ptr()).to_string_lossy().into_owned();
        let memory = instance.get_physical_device_memory_properties(physical);

        let queue_info = [vk::DeviceQueueCreateInfo::default().queue_family_index(family).queue_priorities(&[1.0])];
        let device = instance
            .create_device(physical, &vk::DeviceCreateInfo::default().queue_create_infos(&queue_info), None)
            .or_else(|e| err("could not create the Vulkan device", e))?;
        let queue = device.get_device_queue(family, 0);
        let pool = device
            .create_command_pool(
                &vk::CommandPoolCreateInfo::default().queue_family_index(family).flags(vk::CommandPoolCreateFlags::RESET_COMMAND_BUFFER),
                None,
            )
            .or_else(|e| err("command pool", e))?;
        let cmd = device
            .allocate_command_buffers(&vk::CommandBufferAllocateInfo::default().command_pool(pool).level(vk::CommandBufferLevel::PRIMARY).command_buffer_count(1))
            .or_else(|e| err("command buffer", e))?[0];
        let fence = device.create_fence(&vk::FenceCreateInfo::default(), None).or_else(|e| err("fence", e))?;

        let render_pass = Self::render_pass(&device)?;
        let (layout, opaque, translucent) = Self::pipelines(&device, render_pass)?;

        Ok(Context {
            _entry: entry,
            instance,
            physical,
            device,
            queue,
            pool,
            cmd,
            fence,
            render_pass,
            layout,
            opaque,
            translucent,
            memory,
            vertices: None,
            targets: None,
            name,
        })
    }

    unsafe fn render_pass(device: &ash::Device) -> Result<vk::RenderPass, String> {
        let attachments = [
            vk::AttachmentDescription::default()
                .format(FORMAT)
                .samples(SAMPLES)
                .load_op(vk::AttachmentLoadOp::CLEAR)
                .store_op(vk::AttachmentStoreOp::DONT_CARE)
                .initial_layout(vk::ImageLayout::UNDEFINED)
                .final_layout(vk::ImageLayout::COLOR_ATTACHMENT_OPTIMAL),
            vk::AttachmentDescription::default()
                .format(DEPTH)
                .samples(SAMPLES)
                .load_op(vk::AttachmentLoadOp::CLEAR)
                .store_op(vk::AttachmentStoreOp::DONT_CARE)
                .initial_layout(vk::ImageLayout::UNDEFINED)
                .final_layout(vk::ImageLayout::DEPTH_STENCIL_ATTACHMENT_OPTIMAL),
            vk::AttachmentDescription::default()
                .format(FORMAT)
                .samples(vk::SampleCountFlags::TYPE_1)
                .load_op(vk::AttachmentLoadOp::DONT_CARE)
                .store_op(vk::AttachmentStoreOp::STORE)
                .initial_layout(vk::ImageLayout::UNDEFINED)
                .final_layout(vk::ImageLayout::TRANSFER_SRC_OPTIMAL),
        ];
        let color = [vk::AttachmentReference { attachment: 0, layout: vk::ImageLayout::COLOR_ATTACHMENT_OPTIMAL }];
        let depth = vk::AttachmentReference { attachment: 1, layout: vk::ImageLayout::DEPTH_STENCIL_ATTACHMENT_OPTIMAL };
        let resolve = [vk::AttachmentReference { attachment: 2, layout: vk::ImageLayout::COLOR_ATTACHMENT_OPTIMAL }];
        let subpass = [vk::SubpassDescription::default()
            .pipeline_bind_point(vk::PipelineBindPoint::GRAPHICS)
            .color_attachments(&color)
            .depth_stencil_attachment(&depth)
            .resolve_attachments(&resolve)];
        let dependency = [vk::SubpassDependency::default()
            .src_subpass(vk::SUBPASS_EXTERNAL)
            .dst_subpass(0)
            .src_stage_mask(vk::PipelineStageFlags::COLOR_ATTACHMENT_OUTPUT | vk::PipelineStageFlags::EARLY_FRAGMENT_TESTS)
            .dst_stage_mask(vk::PipelineStageFlags::COLOR_ATTACHMENT_OUTPUT | vk::PipelineStageFlags::EARLY_FRAGMENT_TESTS)
            .dst_access_mask(vk::AccessFlags::COLOR_ATTACHMENT_WRITE | vk::AccessFlags::DEPTH_STENCIL_ATTACHMENT_WRITE)];
        device
            .create_render_pass(
                &vk::RenderPassCreateInfo::default().attachments(&attachments).subpasses(&subpass).dependencies(&dependency),
                None,
            )
            .or_else(|e| err("render pass", e))
    }

    unsafe fn pipelines(device: &ash::Device, render_pass: vk::RenderPass) -> Result<(vk::PipelineLayout, vk::Pipeline, vk::Pipeline), String> {
        let module = |bytes: &[u8]| -> Result<vk::ShaderModule, String> {
            let words = ash::util::read_spv(&mut std::io::Cursor::new(bytes)).or_else(|e| err("shader", e))?;
            device.create_shader_module(&vk::ShaderModuleCreateInfo::default().code(&words), None).or_else(|e| err("shader module", e))
        };
        let (vert, frag) = (module(VERT)?, module(FRAG)?);
        let stages = [
            vk::PipelineShaderStageCreateInfo::default().stage(vk::ShaderStageFlags::VERTEX).module(vert).name(c"main"),
            vk::PipelineShaderStageCreateInfo::default().stage(vk::ShaderStageFlags::FRAGMENT).module(frag).name(c"main"),
        ];
        let binding = [vk::VertexInputBindingDescription { binding: 0, stride: std::mem::size_of::<Vertex>() as u32, input_rate: vk::VertexInputRate::VERTEX }];
        let attributes = [
            vk::VertexInputAttributeDescription { location: 0, binding: 0, format: vk::Format::R32G32B32_SFLOAT, offset: 0 },
            vk::VertexInputAttributeDescription { location: 1, binding: 0, format: vk::Format::R32G32B32_SFLOAT, offset: 12 },
            vk::VertexInputAttributeDescription { location: 2, binding: 0, format: vk::Format::R32G32B32A32_SFLOAT, offset: 24 },
        ];
        let vertex_input = vk::PipelineVertexInputStateCreateInfo::default().vertex_binding_descriptions(&binding).vertex_attribute_descriptions(&attributes);
        let assembly = vk::PipelineInputAssemblyStateCreateInfo::default().topology(vk::PrimitiveTopology::TRIANGLE_LIST);
        let viewport = vk::PipelineViewportStateCreateInfo::default().viewport_count(1).scissor_count(1);
        let raster = vk::PipelineRasterizationStateCreateInfo::default()
            .polygon_mode(vk::PolygonMode::FILL)
            .cull_mode(vk::CullModeFlags::NONE)
            .line_width(1.0);
        let multisample = vk::PipelineMultisampleStateCreateInfo::default().rasterization_samples(SAMPLES);
        let dynamic = [vk::DynamicState::VIEWPORT, vk::DynamicState::SCISSOR];
        let dynamic_state = vk::PipelineDynamicStateCreateInfo::default().dynamic_states(&dynamic);
        let push = [vk::PushConstantRange { stage_flags: vk::ShaderStageFlags::VERTEX, offset: 0, size: std::mem::size_of::<Push>() as u32 }];
        let layout = device
            .create_pipeline_layout(&vk::PipelineLayoutCreateInfo::default().push_constant_ranges(&push), None)
            .or_else(|e| err("pipeline layout", e))?;

        let make = |write_depth: bool, blend: bool| -> Result<vk::Pipeline, String> {
            let depth = vk::PipelineDepthStencilStateCreateInfo::default()
                .depth_test_enable(true)
                .depth_write_enable(write_depth)
                .depth_compare_op(vk::CompareOp::LESS_OR_EQUAL);
            let attachment = [vk::PipelineColorBlendAttachmentState::default()
                .color_write_mask(vk::ColorComponentFlags::RGBA)
                .blend_enable(blend)
                .src_color_blend_factor(vk::BlendFactor::ONE)
                .dst_color_blend_factor(vk::BlendFactor::ONE_MINUS_SRC_ALPHA)
                .color_blend_op(vk::BlendOp::ADD)
                .src_alpha_blend_factor(vk::BlendFactor::ONE)
                .dst_alpha_blend_factor(vk::BlendFactor::ONE_MINUS_SRC_ALPHA)
                .alpha_blend_op(vk::BlendOp::ADD)];
            let blending = vk::PipelineColorBlendStateCreateInfo::default().attachments(&attachment);
            let info = vk::GraphicsPipelineCreateInfo::default()
                .stages(&stages)
                .vertex_input_state(&vertex_input)
                .input_assembly_state(&assembly)
                .viewport_state(&viewport)
                .rasterization_state(&raster)
                .multisample_state(&multisample)
                .depth_stencil_state(&depth)
                .color_blend_state(&blending)
                .dynamic_state(&dynamic_state)
                .layout(layout)
                .render_pass(render_pass)
                .subpass(0);
            let pipelines = device.create_graphics_pipelines(vk::PipelineCache::null(), &[info], None).map_err(|(_, e)| format!("pipeline: {e}"))?;
            Ok(pipelines[0])
        };
        // Opaque solids blend too: the framebuffer starts transparent, and
        // premultiplied-over of an opaque colour is the colour itself.
        let opaque = make(true, true)?;
        let translucent = make(false, true)?;
        device.destroy_shader_module(vert, None);
        device.destroy_shader_module(frag, None);
        Ok((layout, opaque, translucent))
    }

    fn memory_type(&self, requirements: vk::MemoryRequirements, flags: vk::MemoryPropertyFlags) -> Result<u32, String> {
        (0..self.memory.memory_type_count)
            .find(|i| requirements.memory_type_bits & (1 << i) != 0 && self.memory.memory_types[*i as usize].property_flags.contains(flags))
            .ok_or_else(|| "no suitable memory type".to_string())
    }

    unsafe fn image(&self, width: u32, height: u32, format: vk::Format, samples: vk::SampleCountFlags, usage: vk::ImageUsageFlags, aspect: vk::ImageAspectFlags) -> Result<(vk::Image, vk::DeviceMemory, vk::ImageView), String> {
        let device = &self.device;
        let info = vk::ImageCreateInfo::default()
            .image_type(vk::ImageType::TYPE_2D)
            .format(format)
            .extent(vk::Extent3D { width, height, depth: 1 })
            .mip_levels(1)
            .array_layers(1)
            .samples(samples)
            .tiling(vk::ImageTiling::OPTIMAL)
            .usage(usage)
            .initial_layout(vk::ImageLayout::UNDEFINED);
        let image = device.create_image(&info, None).or_else(|e| err("image", e))?;
        let req = device.get_image_memory_requirements(image);
        let memory = device
            .allocate_memory(
                &vk::MemoryAllocateInfo::default().allocation_size(req.size).memory_type_index(self.memory_type(req, vk::MemoryPropertyFlags::DEVICE_LOCAL)?),
                None,
            )
            .or_else(|e| err("image memory", e))?;
        device.bind_image_memory(image, memory, 0).or_else(|e| err("bind image", e))?;
        let view = device
            .create_image_view(
                &vk::ImageViewCreateInfo::default()
                    .image(image)
                    .view_type(vk::ImageViewType::TYPE_2D)
                    .format(format)
                    .subresource_range(vk::ImageSubresourceRange { aspect_mask: aspect, base_mip_level: 0, level_count: 1, base_array_layer: 0, layer_count: 1 }),
                None,
            )
            .or_else(|e| err("image view", e))?;
        Ok((image, memory, view))
    }

    unsafe fn buffer(&self, size: u64, usage: vk::BufferUsageFlags) -> Result<(vk::Buffer, vk::DeviceMemory, u64), String> {
        let device = &self.device;
        let buffer = device.create_buffer(&vk::BufferCreateInfo::default().size(size).usage(usage), None).or_else(|e| err("buffer", e))?;
        let req = device.get_buffer_memory_requirements(buffer);
        let flags = vk::MemoryPropertyFlags::HOST_VISIBLE | vk::MemoryPropertyFlags::HOST_COHERENT;
        let memory = device
            .allocate_memory(&vk::MemoryAllocateInfo::default().allocation_size(req.size).memory_type_index(self.memory_type(req, flags)?), None)
            .or_else(|e| err("buffer memory", e))?;
        device.bind_buffer_memory(buffer, memory, 0).or_else(|e| err("bind buffer", e))?;
        Ok((buffer, memory, size))
    }

    unsafe fn drop_targets(&mut self) {
        if let Some(t) = self.targets.take() {
            let d = &self.device;
            d.destroy_framebuffer(t.framebuffer, None);
            for (image, memory, view) in [t.color, t.depth, t.resolve] {
                d.destroy_image_view(view, None);
                d.destroy_image(image, None);
                d.free_memory(memory, None);
            }
            d.destroy_buffer(t.readback.0, None);
            d.free_memory(t.readback.1, None);
        }
    }

    unsafe fn targets(&mut self, width: u32, height: u32) -> Result<(), String> {
        if self.targets.as_ref().is_some_and(|t| t.width == width && t.height == height) {
            return Ok(());
        }
        self.drop_targets();
        let color = self.image(width, height, FORMAT, SAMPLES, vk::ImageUsageFlags::COLOR_ATTACHMENT | vk::ImageUsageFlags::TRANSIENT_ATTACHMENT, vk::ImageAspectFlags::COLOR)?;
        let depth = self.image(width, height, DEPTH, SAMPLES, vk::ImageUsageFlags::DEPTH_STENCIL_ATTACHMENT | vk::ImageUsageFlags::TRANSIENT_ATTACHMENT, vk::ImageAspectFlags::DEPTH)?;
        let resolve = self.image(width, height, FORMAT, vk::SampleCountFlags::TYPE_1, vk::ImageUsageFlags::COLOR_ATTACHMENT | vk::ImageUsageFlags::TRANSFER_SRC, vk::ImageAspectFlags::COLOR)?;
        let views = [color.2, depth.2, resolve.2];
        let framebuffer = self
            .device
            .create_framebuffer(
                &vk::FramebufferCreateInfo::default().render_pass(self.render_pass).attachments(&views).width(width).height(height).layers(1),
                None,
            )
            .or_else(|e| err("framebuffer", e))?;
        let readback = self.buffer(u64::from(width) * u64::from(height) * 4, vk::BufferUsageFlags::TRANSFER_DST)?;
        self.targets = Some(Targets { width, height, color, depth, resolve, framebuffer, readback });
        Ok(())
    }

    unsafe fn upload(&mut self, vertices: &[Vertex]) -> Result<vk::Buffer, String> {
        let needed = (vertices.len().max(1) * std::mem::size_of::<Vertex>()) as u64;
        if self.vertices.is_none_or(|(_, _, size)| size < needed) {
            if let Some((b, m, _)) = self.vertices.take() {
                self.device.destroy_buffer(b, None);
                self.device.free_memory(m, None);
            }
            self.vertices = Some(self.buffer(needed.max(1 << 20), vk::BufferUsageFlags::VERTEX_BUFFER)?);
        }
        let (buffer, memory, size) = self.vertices.expect("just made");
        let ptr = self.device.map_memory(memory, 0, size, vk::MemoryMapFlags::empty()).or_else(|e| err("map vertices", e))?;
        std::ptr::copy_nonoverlapping(vertices.as_ptr() as *const u8, ptr as *mut u8, needed as usize);
        self.device.unmap_memory(memory);
        Ok(buffer)
    }

    unsafe fn render(&mut self, scene: &Scene) -> Result<Pixmap, String> {
        let (width, height) = (scene.width.max(1), scene.height.max(1));
        let proj = Projection::new(&scene.camera, width as f32, height as f32);

        // Opaque first, then translucent far to near, as the software backend does.
        let depth_of = |solid: &Solid| -> f32 {
            let n = solid.vertices.len().max(1) as f32;
            solid.vertices.iter().map(|v| -proj.to_eye(*v)[2]).sum::<f32>() / n
        };
        let mut order: Vec<(usize, bool, f32)> = scene.solids.iter().enumerate().map(|(i, s)| (i, s.opacity >= 0.995, depth_of(s))).collect();
        order.sort_by(|a, b| b.1.cmp(&a.1).then(b.2.partial_cmp(&a.2).unwrap_or(std::cmp::Ordering::Equal)));
        let mut builder = Builder { proj: &proj, vertices: vec![], draws: vec![] };
        for (i, _, _) in order {
            if scene.solids[i].opacity > 0.002 {
                builder.solid(&scene.solids[i], scene.background);
            }
        }
        let (view_proj, view) = view_proj(&proj);
        let light = normalize([-0.45, 0.6, 0.66]);

        self.targets(width, height)?;
        let vertex_buffer = self.upload(&builder.vertices)?;
        let d = &self.device;
        let t = self.targets.as_ref().expect("targets");

        d.reset_fences(&[self.fence]).or_else(|e| err("fence", e))?;
        d.reset_command_buffer(self.cmd, vk::CommandBufferResetFlags::empty()).or_else(|e| err("reset", e))?;
        d.begin_command_buffer(self.cmd, &vk::CommandBufferBeginInfo::default().flags(vk::CommandBufferUsageFlags::ONE_TIME_SUBMIT)).or_else(|e| err("begin", e))?;
        let clear = [
            vk::ClearValue { color: vk::ClearColorValue { float32: [0.0, 0.0, 0.0, 0.0] } },
            vk::ClearValue { depth_stencil: vk::ClearDepthStencilValue { depth: 1.0, stencil: 0 } },
            vk::ClearValue { color: vk::ClearColorValue { float32: [0.0, 0.0, 0.0, 0.0] } },
        ];
        let area = vk::Rect2D { offset: vk::Offset2D { x: 0, y: 0 }, extent: vk::Extent2D { width, height } };
        d.cmd_begin_render_pass(
            self.cmd,
            &vk::RenderPassBeginInfo::default().render_pass(self.render_pass).framebuffer(t.framebuffer).render_area(area).clear_values(&clear),
            vk::SubpassContents::INLINE,
        );
        d.cmd_set_viewport(self.cmd, 0, &[vk::Viewport { x: 0.0, y: 0.0, width: width as f32, height: height as f32, min_depth: 0.0, max_depth: 1.0 }]);
        d.cmd_set_scissor(self.cmd, 0, &[area]);
        d.cmd_bind_vertex_buffers(self.cmd, 0, &[vertex_buffer], &[0]);
        let mut bound: Option<bool> = None;
        for draw in &builder.draws {
            if bound != Some(draw.translucent) {
                d.cmd_bind_pipeline(self.cmd, vk::PipelineBindPoint::GRAPHICS, if draw.translucent { self.translucent } else { self.opaque });
                bound = Some(draw.translucent);
            }
            let push = Push { view_proj, light: [light[0], light[1], light[2], if draw.lit { 0.0 } else { 1.0 }], view };
            let bytes = std::slice::from_raw_parts(&push as *const Push as *const u8, std::mem::size_of::<Push>());
            d.cmd_push_constants(self.cmd, self.layout, vk::ShaderStageFlags::VERTEX, 0, bytes);
            d.cmd_draw(self.cmd, draw.count, 1, draw.first, 0);
        }
        d.cmd_end_render_pass(self.cmd);
        // The resolve image left the pass as TRANSFER_SRC; copy it out.
        let region = vk::BufferImageCopy::default()
            .image_subresource(vk::ImageSubresourceLayers { aspect_mask: vk::ImageAspectFlags::COLOR, mip_level: 0, base_array_layer: 0, layer_count: 1 })
            .image_extent(vk::Extent3D { width, height, depth: 1 });
        d.cmd_copy_image_to_buffer(self.cmd, t.resolve.0, vk::ImageLayout::TRANSFER_SRC_OPTIMAL, t.readback.0, &[region]);
        let barrier = vk::BufferMemoryBarrier::default()
            .src_access_mask(vk::AccessFlags::TRANSFER_WRITE)
            .dst_access_mask(vk::AccessFlags::HOST_READ)
            .src_queue_family_index(vk::QUEUE_FAMILY_IGNORED)
            .dst_queue_family_index(vk::QUEUE_FAMILY_IGNORED)
            .buffer(t.readback.0)
            .size(vk::WHOLE_SIZE);
        d.cmd_pipeline_barrier(self.cmd, vk::PipelineStageFlags::TRANSFER, vk::PipelineStageFlags::HOST, vk::DependencyFlags::empty(), &[], &[barrier], &[]);
        d.end_command_buffer(self.cmd).or_else(|e| err("end", e))?;

        let cmds = [self.cmd];
        d.queue_submit(self.queue, &[vk::SubmitInfo::default().command_buffers(&cmds)], self.fence).or_else(|e| err("submit", e))?;
        d.wait_for_fences(&[self.fence], true, u64::MAX).or_else(|e| err("wait", e))?;

        let mut out = Pixmap::new(width, height).expect("viewport size");
        let ptr = d.map_memory(t.readback.1, 0, t.readback.2, vk::MemoryMapFlags::empty()).or_else(|e| err("map readback", e))?;
        std::ptr::copy_nonoverlapping(ptr as *const u8, out.data_mut().as_mut_ptr(), (width * height * 4) as usize);
        d.unmap_memory(t.readback.1);
        Ok(out)
    }
}

impl Drop for Context {
    fn drop(&mut self) {
        unsafe {
            let _ = self.device.device_wait_idle();
            self.drop_targets();
            if let Some((b, m, _)) = self.vertices.take() {
                self.device.destroy_buffer(b, None);
                self.device.free_memory(m, None);
            }
            self.device.destroy_pipeline(self.opaque, None);
            self.device.destroy_pipeline(self.translucent, None);
            self.device.destroy_pipeline_layout(self.layout, None);
            self.device.destroy_render_pass(self.render_pass, None);
            self.device.destroy_fence(self.fence, None);
            self.device.destroy_command_pool(self.pool, None);
            self.device.destroy_device(None);
            self.instance.destroy_instance(None);
        }
        let _ = self.physical;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use cevg_core::soft::SoftBackend;
    use cevg_core::space3d::Camera;
    use std::sync::Arc;

    fn backend() -> Option<VulkanBackend> {
        match VulkanBackend::new() {
            Ok(b) => Some(b),
            Err(e) => {
                eprintln!("no Vulkan here, skipping: {e}");
                None
            }
        }
    }

    fn scene_solids() -> Vec<Solid> {
        vec![
            Solid {
                content: Arc::new(Content::Mesh { triangles: vec![[0, 1, 2], [0, 2, 3]], lit: true }),
                vertices: vec![[-0.8, -0.8, 0.0], [0.8, -0.8, 0.0], [0.8, 0.8, 0.0], [-0.8, 0.8, 0.0]],
                color: [60, 140, 220],
                drawn: 1.0,
                opacity: 0.9,
            },
            Solid {
                content: Arc::new(Content::Segments { width: 4.0, head: true }),
                vertices: vec![[0.0, 0.0, 0.0], [0.5, 0.5, 0.7]],
                color: [245, 184, 61],
                drawn: 1.0,
                opacity: 1.0,
            },
            Solid { content: Arc::new(Content::Points { radius: 9.0 }), vertices: vec![[-0.4, 0.3, 0.2]], color: [255, 138, 168], drawn: 1.0, opacity: 1.0 },
        ]
    }

    #[test]
    fn matches_the_software_backend_within_tolerance() {
        let Some(gpu) = backend() else { return };
        let solids = scene_solids();
        let scene = Scene { camera: Camera::default(), width: 320, height: 240, background: [15, 18, 26], solids: &solids };
        let (a, b) = (gpu.render(&scene), SoftBackend.render(&scene));
        assert_eq!(a.data().len(), b.data().len());
        // Edges differ by a pixel here and there; the bulk must agree.
        let far = a.data().chunks(4).zip(b.data().chunks(4)).filter(|(p, q)| p.iter().zip(*q).any(|(x, y)| (*x as i32 - *y as i32).abs() > 40)).count();
        let total = (scene.width * scene.height) as usize;
        assert!(far * 100 < total * 3, "{far} of {total} pixels differ a lot between vulkan and soft");
        assert!(a.data().chunks(4).any(|p| p[3] > 200), "the gpu drew something opaque");
    }

    #[test]
    fn the_same_scene_gives_the_same_pixels() {
        let Some(gpu) = backend() else { return };
        let solids = scene_solids();
        let scene = Scene { camera: Camera::default(), width: 200, height: 150, background: [0, 0, 0], solids: &solids };
        assert_eq!(gpu.render(&scene).data(), gpu.render(&scene).data());
    }
}
