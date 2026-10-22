//! Text: shaping, measuring and painting.
//!
//! The fonts are compiled into the library, so a frame looks the same on every
//! machine and never depends on what is installed. `cosmic-text` shapes the
//! text (which Telugu and Devanagari need) and falls back from the Latin face
//! to the Indic faces glyph by glyph.

use cosmic_text::{
    fontdb, Align, Attrs, Buffer, Color, Family, FeatureTag, FontFeatures, FontSystem, Metrics, Shaping, SwashCache, Weight,
};
use tiny_skia::Pixmap;

const FONT_FILES: &[&[u8]] = &[
    include_bytes!("../assets/fonts/NotoSans-Regular.ttf"),
    include_bytes!("../assets/fonts/NotoSans-SemiBold.ttf"),
    include_bytes!("../assets/fonts/NotoSansTelugu-Regular.ttf"),
    include_bytes!("../assets/fonts/NotoSansTelugu-SemiBold.ttf"),
    include_bytes!("../assets/fonts/NotoSansDevanagari-Regular.ttf"),
    include_bytes!("../assets/fonts/NotoSansDevanagari-SemiBold.ttf"),
    include_bytes!("../assets/fonts/JetBrainsMono-Regular.ttf"),
];

/// Line height as a multiple of font size. Indic scripts need the headroom
/// for marks above and below the line.
const LINE_HEIGHT: f32 = 1.4;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Face {
    Sans,
    SansBold,
    Mono,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HAlign {
    Left,
    Center,
    Right,
}

#[derive(Debug, Clone, Copy)]
pub struct Style {
    pub size: f32,
    pub face: Face,
    pub color: [u8; 3],
    pub opacity: f32,
}

pub struct Fonts {
    system: FontSystem,
    cache: SwashCache,
}

impl Default for Fonts {
    fn default() -> Self {
        Self::new()
    }
}

impl Fonts {
    pub fn new() -> Fonts {
        let mut db = fontdb::Database::new();
        for bytes in FONT_FILES {
            db.load_font_data(bytes.to_vec());
        }
        db.set_sans_serif_family("Noto Sans");
        db.set_monospace_family("JetBrains Mono");
        Fonts {
            system: FontSystem::new_with_locale_and_db("en-US".to_string(), db),
            cache: SwashCache::new(),
        }
    }

    fn layout(&mut self, text: &str, size: f32, face: Face, max_w: Option<f32>, center: bool) -> (Buffer, f32, f32) {
        let attrs = match face {
            Face::Sans => Attrs::new().family(Family::SansSerif),
            Face::SansBold => Attrs::new().family(Family::SansSerif).weight(Weight::SEMIBOLD),
            Face::Mono => {
                // No ligatures in code: `<=` must stay two characters.
                let mut features = FontFeatures::new();
                features.disable(FeatureTag::new(b"calt")).disable(FeatureTag::new(b"liga"));
                Attrs::new().family(Family::Monospace).font_features(features)
            }
        };
        let mut buffer = Buffer::new(&mut self.system, Metrics::new(size, size * LINE_HEIGHT));
        buffer.set_size(max_w, None);
        let align = (center && max_w.is_some()).then_some(Align::Center);
        buffer.set_text(text, &attrs, Shaping::Advanced, align);
        buffer.shape_until_scroll(&mut self.system, false);

        let (mut width, mut lines) = (0.0f32, 0usize);
        for run in buffer.layout_runs() {
            width = width.max(run.line_w);
            lines += 1;
        }
        (buffer, width, lines as f32 * size * LINE_HEIGHT)
    }

    /// Width and height of the text. With `max_w` the text wraps.
    pub fn measure(&mut self, text: &str, size: f32, face: Face, max_w: Option<f32>) -> (f32, f32) {
        let (_, w, h) = self.layout(text, size, face, max_w, false);
        (w, h)
    }

    /// Paint text. `x` is the left edge, centre or right edge according to
    /// `align`; `y` is always the vertical centre of the text block. With
    /// `max_w` the text wraps inside that width.
    #[allow(clippy::too_many_arguments)]
    pub fn draw(
        &mut self,
        pixmap: &mut Pixmap,
        text: &str,
        style: Style,
        x: f32,
        y: f32,
        align: HAlign,
        max_w: Option<f32>,
    ) {
        if text.is_empty() || style.opacity <= 0.0 {
            return;
        }
        let center = align == HAlign::Center;
        let (mut buffer, w, h) = self.layout(text, style.size, style.face, max_w, center);
        let left = match (align, max_w) {
            (HAlign::Left, _) => x,
            (HAlign::Center, Some(max_w)) => x - max_w / 2.0,
            (HAlign::Center, None) => x - w / 2.0,
            (HAlign::Right, _) => x - w,
        };
        let (ox, oy) = (left.round() as i32, (y - h / 2.0).round() as i32);

        let (pw, ph) = (pixmap.width() as i32, pixmap.height() as i32);
        let data = pixmap.data_mut();
        let [r, g, b] = style.color;
        let opacity = style.opacity.clamp(0.0, 1.0);

        buffer.draw(
            &mut self.system,
            &mut self.cache,
            Color::rgb(r, g, b),
            |gx, gy, gw, gh, color| {
                let alpha = (color.a() as f32 * opacity).round() as u32;
                if alpha == 0 {
                    return;
                }
                let src = [color.r() as u32, color.g() as u32, color.b() as u32];
                for py in (oy + gy).max(0)..(oy + gy + gh as i32).min(ph) {
                    for px in (ox + gx).max(0)..(ox + gx + gw as i32).min(pw) {
                        let i = ((py * pw + px) * 4) as usize;
                        // The canvas is opaque, so plain "over" blending on
                        // each channel is exact and alpha stays at 255.
                        for c in 0..3 {
                            let dst = data[i + c] as u32;
                            data[i + c] = ((src[c] * alpha + dst * (255 - alpha) + 127) / 255) as u8;
                        }
                    }
                }
            },
        );
    }
}
