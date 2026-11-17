import { randomBytes } from "node:crypto";
import { one } from "./db";

export type User = {
  id: string;
  email: string;
  name: string;
  image: string | null;
  handle: string;
  connector_token: string;
};

const COLUMNS = "id::text as id, email, name, image, handle, connector_token";

export function newToken(): string {
  return randomBytes(24).toString("base64url");
}

function slug(name: string): string {
  const base = name
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 24);
  return base || "creator";
}

/** The account for a Google identity, created the first time it signs in. */
export async function upsertUser(profile: { sub: string; email: string; name: string; image?: string | null; verified?: boolean }): Promise<User> {
  const existing = await one<User>(
    `update users set email = $2, name = $3, image = $4 where google_sub = $1 returning ${COLUMNS}`,
    [profile.sub, profile.email, profile.name, profile.image ?? null],
  );
  if (existing) return existing;

  // An account made before its owner could sign in (google_sub "pending:…", such as the
  // founder's, which owns the demo videos) is claimed by the first sign-in whose
  // Google-verified email matches it; its connector address stays the same.
  if (profile.verified && profile.email) {
    const claimed = await one<User>(
      `update users set google_sub = $1, name = $3, image = $4
        where google_sub like 'pending:%' and lower(email) = lower($2) returning ${COLUMNS}`,
      [profile.sub, profile.email, profile.name, profile.image ?? null],
    );
    if (claimed) return claimed;
  }

  // A handle must be unique; add a short suffix until it is.
  for (let attempt = 0; attempt < 6; attempt++) {
    const handle = attempt === 0 ? slug(profile.name) : `${slug(profile.name)}-${randomBytes(2).toString("hex")}`;
    const created = await one<User>(
      `insert into users (google_sub, email, name, image, handle, connector_token)
       values ($1, $2, $3, $4, $5, $6)
       on conflict do nothing returning ${COLUMNS}`,
      [profile.sub, profile.email, profile.name, profile.image ?? null, handle, newToken()],
    );
    if (created) return created;
    const raced = await one<User>(`select ${COLUMNS} from users where google_sub = $1`, [profile.sub]);
    if (raced) return raced;
  }
  throw new Error("could not create the account");
}

export function userById(id: string): Promise<User | null> {
  return one<User>(`select ${COLUMNS} from users where id::text = $1`, [id]);
}

export function userByHandle(handle: string): Promise<Pick<User, "id" | "name" | "image" | "handle"> | null> {
  return one(`select id::text as id, name, image, handle from users where handle = $1`, [handle]);
}

export function regenerateToken(id: string): Promise<User | null> {
  return one<User>(`update users set connector_token = $2 where id::text = $1 returning ${COLUMNS}`, [id, newToken()]);
}

// --- Bring-your-own Gnani key ------------------------------------------------
// The key is stored encrypted at rest with pgcrypto (pgp_sym_encrypt), using the
// shared passphrase CEVG_KEY_SECRET. The render server decrypts it with the same
// passphrase when that user renders, so their videos run on their own Gnani
// credits. We never keep the plaintext and never return it to the browser.

export type GnaniKeyStatus = { set: boolean; setAt: string | null };

function keySecret(): string {
  const secret = process.env.CEVG_KEY_SECRET;
  if (!secret) throw new Error("CEVG_KEY_SECRET is not set");
  return secret;
}

export async function setGnaniKey(id: string, key: string): Promise<void> {
  await one(
    `update users set gnani_key_enc = pgp_sym_encrypt($2, $3), gnani_key_set_at = now()
       where id::text = $1 returning id`,
    [id, key, keySecret()],
  );
}

export async function clearGnaniKey(id: string): Promise<void> {
  await one(
    `update users set gnani_key_enc = null, gnani_key_set_at = null where id::text = $1 returning id`,
    [id],
  );
}

export async function gnaniKeyStatus(id: string): Promise<GnaniKeyStatus> {
  const row = await one<{ has_key: boolean; set_at: Date | null }>(
    `select (gnani_key_enc is not null) as has_key, gnani_key_set_at as set_at from users where id::text = $1`,
    [id],
  );
  return { set: row?.has_key ?? false, setAt: row?.set_at ? new Date(row.set_at).toISOString() : null };
}
