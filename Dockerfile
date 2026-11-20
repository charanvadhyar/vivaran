# The Vivaran render server for Railway: the cevg renderer (Rust) and the
# multi-user MCP server (Python) in one image. Fonts are compiled into cevg,
# so the runtime needs only ffmpeg.
#
# Build settings come from the environment (see platform/.env.example):
#   DATABASE_URL, SITE_URL, CEVG_STORAGE=/data (a Railway volume), GNANI_API_KEY,
#   CEVG_INTERNAL_TOKEN (shared with the site, which fetches videos from /files),
#   CEVG_WATERMARK, CEVG_MAX_MINUTES, ANTHROPIC_API_KEY. PORT is set by Railway.
# Plans, credits and rewards live in the database (`settings` table).

FROM rust:1.92-bookworm AS renderer
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY crates ./crates
# The Studio commands embed the Blender script, so it is part of the build.
COPY studio ./studio
RUN cargo build --release -p cevg-cli && strip target/release/cevg

FROM python:3.12-slim-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*
COPY --from=renderer /src/target/release/cevg /usr/local/bin/cevg
WORKDIR /app
COPY shell ./shell
COPY examples ./examples
# The schema is applied at start-up; the font marks the channel copy of Pro videos.
COPY platform/schema.sql /app/platform/schema.sql
COPY crates/cevg-core/assets/fonts/NotoSans-SemiBold.ttf /app/fonts/NotoSans-SemiBold.ttf
RUN pip install --no-cache-dir "mcp>=2.3" "psycopg[binary]>=3.2"
ENV PYTHONPATH=/app/shell \
    PYTHONUNBUFFERED=1 \
    CEVG_BIN=/usr/local/bin/cevg \
    CEVG_PLATFORM_DIR=/app/platform \
    CEVG_STORAGE=/data
RUN mkdir -p /data
EXPOSE 8765
CMD ["sh", "-c", "python -m cevg_shell serve-platform --host 0.0.0.0 --port ${PORT:-8765}"]
