import type { NextConfig } from "next";
import { existsSync, readdirSync } from "node:fs";
import path from "node:path";

// One settings file for the site and the MCP server: platform/.env
const env = path.resolve(process.cwd(), "../.env");
if (existsSync(env)) process.loadEnvFile(env);

const mcp = process.env.MCP_INTERNAL_URL ?? "http://127.0.0.1:8765";
const waitlist = process.env.WAITLIST === "1";

// The demo videos ship with the site, in public/demo, under the URLs the
// players use. They stay there after launch; everything else comes from the
// render server.
const demoDir = path.resolve(process.cwd(), "public/demo");
const demos = existsSync(demoDir)
  ? [...new Set(readdirSync(demoDir).filter((f) => /^[a-f0-9]{12}\.mp4$/.test(f)).map((f) => f.slice(0, 12)))]
  : [];

const config: NextConfig = {
  async rewrites() {
    const demoFiles = waitlist
      ? [
          { source: "/api/videos/:id/file", destination: "/demo/:id.mp4" },
          { source: "/api/videos/:id/thumb", destination: "/demo/:id.png" },
        ]
      : demos.flatMap((id) => [
          { source: `/api/videos/${id}/file`, destination: `/demo/${id}.mp4` },
          { source: `/api/videos/${id}/thumb`, destination: `/demo/${id}.png` },
        ]);
    // The connector lives at the same public address as the site: a request
    // to /u/<token>/mcp is passed to the Python MCP server (MCP_INTERNAL_URL,
    // the render server on Railway; locally, this machine).
    const connector = waitlist ? [] : [{ source: "/u/:token/mcp", destination: `${mcp}/u/:token/mcp` }];
    return { beforeFiles: demoFiles, afterFiles: connector, fallback: [] };
  },
};

export default config;
