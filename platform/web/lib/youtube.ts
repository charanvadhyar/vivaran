/** The Vivaran YouTube channel's sign-in. An admin connects the channel once; the
    refresh token is kept encrypted (pgcrypto, CEVG_KEY_SECRET) in the `secrets`
    table, and a short-lived access token is handed to the render server for each
    upload or statistics run. */
import { one } from "./db";

const SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/youtube"];

function site(): string {
  return (process.env.SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
}

export const redirectUri = () => `${site()}/api/admin/youtube/callback`;

export function connectUrl(state: string): string {
  const q = new URLSearchParams({
    client_id: process.env.AUTH_GOOGLE_ID ?? "", redirect_uri: redirectUri(), response_type: "code",
    scope: SCOPES.join(" "), access_type: "offline", prompt: "consent", include_granted_scopes: "true", state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${q}`;
}

function secret(): string {
  const s = process.env.CEVG_KEY_SECRET;
  if (!s) throw new Error("CEVG_KEY_SECRET is not set");
  return s;
}

export async function saveFromCode(code: string): Promise<void> {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ code, client_id: process.env.AUTH_GOOGLE_ID ?? "", client_secret: process.env.AUTH_GOOGLE_SECRET ?? "",
      redirect_uri: redirectUri(), grant_type: "authorization_code" }),
  });
  const data = (await res.json()) as { refresh_token?: string; error?: string; error_description?: string };
  if (!res.ok || !data.refresh_token) throw new Error(data.error_description ?? data.error ?? "Google did not return a refresh token");
  await one(`insert into secrets (key, value) values ('youtube_refresh', pgp_sym_encrypt($1, $2))
             on conflict (key) do update set value = excluded.value, updated_at = now() returning key`, [data.refresh_token, secret()]);
}

export async function connected(): Promise<boolean> {
  return !!(await one(`select 1 from secrets where key = 'youtube_refresh'`));
}

export async function disconnect(): Promise<void> {
  await one(`delete from secrets where key = 'youtube_refresh' returning key`);
}

/** A fresh access token for the channel, or an error saying to connect it. */
export async function accessToken(): Promise<string> {
  const row = await one<{ token: string }>(
    `select pgp_sym_decrypt(value, $1) as token from secrets where key = 'youtube_refresh'`, [secret()]);
  if (!row) throw new Error("the YouTube channel is not connected; connect it on the admin page");
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ refresh_token: row.token, client_id: process.env.AUTH_GOOGLE_ID ?? "",
      client_secret: process.env.AUTH_GOOGLE_SECRET ?? "", grant_type: "refresh_token" }),
  });
  const data = (await res.json()) as { access_token?: string; error?: string; error_description?: string };
  if (!res.ok || !data.access_token) throw new Error(`Google refused the channel token: ${data.error_description ?? data.error}; connect the channel again`);
  return data.access_token;
}
