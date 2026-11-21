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

## Credits, plans and the channel

A render costs credits, counted in videos: one credit is one video of up to
ten minutes voiced with the platform's voice; a silent video, or one voiced on
the creator's own Gnani key, costs a quarter. A failed render gives its credits
back. Free accounts get 3 credits each month (refilled, not piled up); Pro gets
more, longer videos and no watermark. Bonus credits come from the creator
program (joining, subscribing to the channel, the first video on the channel,
invited friends, view milestones on YouTube) and never expire. One render at a
time per account, and never longer than `CEVG_MAX_MINUTES`.

Every script is checked by a reviewer agent before it renders (`review` tool,
`shell/cevg_shell/review.py`, on the Claude API with `ANTHROPIC_API_KEY`; the
model is `CEVG_REVIEW_MODEL`, or the figure model). It reads the script with a
drawn frame of each scene and the guide's teaching rules, recomputes the
working, and lists blocking and minor issues; the assistant fixes them and
asks again. `render` refuses a script whose exact text (its hash) has not
passed, except after three failed rounds when the user chooses to render
anyway. Each plan has `reviews_per_month` (free 3, Pro 150); past it, or
without an API key, scripts render unreviewed.

The contact page (`/contact`) takes sales enquiries, grievances, support requests
and anything else. Each message is saved in `contact_messages` with a reference
(`VIV-00012`) and shows on /admin under Messages, where you reply by email and set
its status. Grievances are promised an acknowledgement within 24 hours and a
resolution within 15 days; the overview counts any that are late. Public video
pages link to it to report a video, and one network may send 5 messages a day.

Sign-ups are counted per network. The site keeps a keyed hash of the IP address
each account signed up from (never the address; the key is `AUTH_SECRET`). Once a
network has made `signups_per_network_per_day` accounts in a day (plans, default
3; 0 turns it off), later accounts from it still work but get no free credits:
no monthly credits and no rewards for joining or subscribing. They show as "on
hold" on /admin, which releases them (or holds any other account). A college or
mobile network puts many real people behind one address, which is why accounts
are held rather than refused.

The rules are SQL functions in `schema.sql` (`vivaran_spend`, `vivaran_refund`,
`vivaran_balance`, ...), shared by the site and the render server; the numbers
are the `plans` row of the `settings` table, edited on `/admin`. Until online
payment is set up, credits packs and Pro are granted by hand on `/admin`.

Creators send public videos to the Vivaran YouTube channel from the video's
page (Pro gets the title, description and tags written by the Claude API); an
admin approves each one, and the render server uploads it.

Every free video carries `CEVG_WATERMARK` (default "Vivaran") and the creator's
handle; the channel copy of a Pro video gets it added at upload.

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
