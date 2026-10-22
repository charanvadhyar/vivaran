// Creates the tables, and loads any seed files it is given. Safe to run again.
//
//   npm run db:setup                      the schema only
//   npm run db:setup -- ../seed-demos.sql  the schema, then that seed
//
// On Vercel the build command is `node scripts/setup-db.mjs ../seed-demos.sql && next build`,
// so the database is ready by the time the site is up.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import pg from "pg";

const env = path.resolve(process.cwd(), "../.env");
if (existsSync(env)) process.loadEnvFile(env);
if (!process.env.DATABASE_URL) {
  console.error("DATABASE_URL is not set. Copy platform/.env.example to platform/.env and fill it in.");
  process.exit(1);
}

// The schema lives in the platform folder; a packaged deployment carries a copy in db/.
const schema = ["../schema.sql", "db/schema.sql"].map((p) => path.resolve(process.cwd(), p)).find(existsSync);
if (!schema) {
  console.error("schema.sql not found next to the web folder or in db/");
  process.exit(1);
}
const seeds = process.argv.slice(2).map((p) => path.resolve(process.cwd(), p));

const client = new pg.Client({ connectionString: process.env.DATABASE_URL });
await client.connect();
await client.query(readFileSync(schema, "utf8"));
for (const seed of seeds) {
  await client.query(readFileSync(seed, "utf8"));
  console.log(`loaded ${path.basename(seed)}`);
}
const { rows } = await client.query("select (select count(*) from users)::int as users, (select count(*) from videos)::int as videos");
console.log(`database ready (${rows[0].users} users, ${rows[0].videos} videos)`);
await client.end();
