import type { NextConfig } from "next";
import { existsSync } from "node:fs";
import path from "node:path";

// One settings file for the site and the MCP server: platform/.env
const env = path.resolve(process.cwd(), "../.env");
if (existsSync(env)) process.loadEnvFile(env);

const mcp = process.env.MCP_INTERNAL_URL ?? "http://127.0.0.1:8765";
const waitlist = process.env.WAITLIST === "1";

const config: NextConfig = {
  async rewrites() {
    if (waitlist) {
      // Before launch there is no render server and no video store: the demo
      // videos ship with the site itself, in public/demo, under the same URLs
      // the players use, so nothing else changes at launch.
      return {
        beforeFiles: [
          { source: "/api/videos/:id/file", destination: "/demo/:id.mp4" },
          { source: "/api/videos/:id/thumb", destination: "/demo/:id.png" },
        ],
        afterFiles: [],
        fallback: [],
      };
    }
    // The connector lives at the same public address as the site: a request
    // to /u/<token>/mcp is passed to the Python MCP server on this machine.
    return [{ source: "/u/:token/mcp", destination: `${mcp}/u/:token/mcp` }];
  },
};

export default config;
