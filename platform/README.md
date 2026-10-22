# Vivaran: the CEVG platform, version 1

A website where creators sign in, get a personal connector address for
Claude or ChatGPT, and every video they make through it is saved to their
account. Videos are private until the creator watches them and makes them
public.

## What runs

Two programs on one machine, sharing a Postgres database and a storage
folder:

| Part | What it is | Port |
| --- | --- | --- |
| `web/` | The site: Next.js. Sign-in, dashboard, watch pages, video files. | 3000 |
| `shell/cevg_shell/hosted.py` | The MCP server for many users, and the renderer. | 8765 |

The site passes `/u/<token>/mcp` on to the MCP server, so the connector and
the site share one public address. Only port 3000 needs to be reachable
from outside.

The token in a connector address says whose account a call belongs to.
A render becomes a row in `videos` and files in `storage/videos/`. One
video renders at a time; others wait.

## Run it on your computer

You need what the renderer needs (Rust build, Python 3.10+, ffmpeg), plus
Node 20.12 or later and Postgres 14 or later.

1. Postgres. Install it, or with Docker: `docker compose up -d` in this
   folder. Create a database called `cevg` if you installed it yourself.
2. Settings. Copy `.env.example` to `.env` in this folder and fill in
   `DATABASE_URL` and `AUTH_SECRET`. For a first run without Google, set
   `DEV_LOGIN=1`.
3. Packages.
   ```
   pip install "mcp>=2.3" "psycopg[binary]"
   cd web
   npm install
   npm run db:setup
   ```
4. Start both, each in its own terminal.
   ```
   cd shell
   python -m cevg_shell serve-platform
   ```
   ```
   cd platform/web
   npm run build
   npm run start
   ```
5. Open http://localhost:3000, sign in, and copy your connector address
   from "My videos".

Claude and ChatGPT connect to custom connectors from their own servers, not from your computer,
so a `localhost` address will not work for them. Test with a tunnel (below), or keep using the local
`serve` command for your own videos.

## Google sign-in

In Google Cloud Console, create an OAuth client of type "Web application".
Add `<SITE_URL>/api/auth/callback/google` as an authorised redirect URI.
Put the client id and secret in `.env` as `AUTH_GOOGLE_ID` and
`AUTH_GOOGLE_SECRET`, and set `DEV_LOGIN=0`.

## Reach it from ChatGPT and Claude

They need an https address. With a tunnel:

```
cloudflared tunnel --url http://localhost:3000
```

Put the https address it prints in `.env` as both `SITE_URL` and
`AUTH_URL`, add the redirect URI for it in Google, and restart both
programs. Connector addresses on the dashboard then start with that
address.

## Limits

Voice runs on the platform's Sarvam key (`SARVAM_API_KEY`), so each account
has a daily allowance: `CEVG_DAILY_VOICE_MINUTES` (default 10) voiced
minutes in any 24 hours, one render at a time, and no video longer than
`CEVG_MAX_MINUTES` (default 12). Silent videos with captions are not
counted. Without a key every video is silent.

Every video carries `CEVG_WATERMARK` (default "Vivaran") and the creator's handle in the top
right corner.

## Name and design

The platform is called Vivaran (వివరణ · विवरण, "explanation"). The name,
tagline and subject list live in `web/lib/brand.ts`; the look is one dark
"chalkboard" theme in `web/app/globals.css`, using the same slate and amber
as the videos.

The home page groups public videos by subject and has a search box. A
creator picks the subject when publishing; the assistant can also pass
`subject` to `render`.

## What version 1 leaves out

- Payments, credits and the bring-your-own-key tier.
- OAuth for the connector. The token in the address is the only lock, and
  it is stored as plain text in the database.
- Reports, moderation and taking down someone else's video.
- Search inside narration. Search matches titles and creator names only.
- Cloud storage. Files are on the local disk.
- More than one render at a time, and renders that survive a restart.
