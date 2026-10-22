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
export async function upsertUser(profile: { sub: string; email: string; name: string; image?: string | null }): Promise<User> {
  const existing = await one<User>(
    `update users set email = $2, name = $3, image = $4 where google_sub = $1 returning ${COLUMNS}`,
    [profile.sub, profile.email, profile.name, profile.image ?? null],
  );
  if (existing) return existing;

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
