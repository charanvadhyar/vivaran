import { Pool } from "pg";

// One pool for the whole server, kept across hot reloads in development.
const holder = globalThis as unknown as { cevgPool?: Pool };

export const db: Pool =
  holder.cevgPool ?? (holder.cevgPool = makePool());

function makePool(): Pool {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 10 });
  // A dropped idle connection must not crash the server; the next query reconnects.
  pool.on("error", (error) => console.error("database connection lost:", error.message));
  return pool;
}

export async function one<T>(sql: string, params: unknown[] = []): Promise<T | null> {
  const { rows } = await db.query(sql, params);
  return (rows[0] as T) ?? null;
}

export async function many<T>(sql: string, params: unknown[] = []): Promise<T[]> {
  const { rows } = await db.query(sql, params);
  return rows as T[];
}
