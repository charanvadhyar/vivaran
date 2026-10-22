import { many, one } from "./db";

export const ROLES = ["learner", "creator", "teacher"] as const;
export type Role = (typeof ROLES)[number];

export type Signup = { id: number; email: string; role: Role; note: string | null; source: string | null; created_at: Date };

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function validEmail(text: string): boolean {
  return text.length <= 254 && EMAIL.test(text);
}

/** Add an email to the waitlist. Returns the person's position; joining twice keeps the first place. */
export async function join(email: string, role: Role, note: string | null, source: string | null): Promise<{ position: number; already: boolean }> {
  const inserted = await one<{ id: number }>(
    `insert into waitlist (email, role, note, source) values ($1, $2, $3, $4)
     on conflict (lower(email)) do nothing returning id`,
    [email, role, note, source],
  );
  const row = await one<{ id: number; position: number }>(
    `select id, (select count(*)::int from waitlist w2 where w2.id <= w.id) as position
     from waitlist w where lower(email) = lower($1)`,
    [email],
  );
  return { position: row?.position ?? 1, already: !inserted };
}

export const waitlistCount = async () => (await one<{ n: number }>("select count(*)::int as n from waitlist"))?.n ?? 0;

export const allSignups = () => many<Signup>("select * from waitlist order by id");
