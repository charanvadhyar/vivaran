"use server";

import { revalidatePath } from "next/cache";
import { notFound } from "next/navigation";
import { grant, isAdmin, setAdmin, setPro } from "@/lib/admin";
import { currentUser } from "@/lib/auth";
import { logEvent } from "@/lib/credits";
import { db, one } from "@/lib/db";
import { renderServer } from "@/lib/render";
import { accessToken, disconnect } from "@/lib/youtube";

async function requireAdmin() {
  const user = await currentUser();
  if (!user || !(await isAdmin(user))) notFound();
  return user;
}

const back = () => revalidatePath("/admin");

export async function grantCredits(form: FormData) {
  const admin = await requireAdmin();
  const amount = Number(form.get("amount"));
  const kind = String(form.get("kind")) as "admin_grant" | "pack" | "admin_take";
  const inr = form.get("inr") ? Number(form.get("inr")) : null;
  if (!Number.isFinite(amount) || amount <= 0 || amount > 1000 || !["admin_grant", "pack", "admin_take"].includes(kind)) return;
  await grant(admin.id, String(form.get("user")), amount, kind, String(form.get("note") ?? ""), inr && Number.isFinite(inr) ? inr : null);
  back();
}

export async function setProUntil(form: FormData) {
  const admin = await requireAdmin();
  const raw = String(form.get("until") ?? "");
  const until = raw ? new Date(`${raw}T23:59:59+05:30`) : null;
  const inr = form.get("inr") ? Number(form.get("inr")) : null;
  if (until && Number.isNaN(until.getTime())) return;
  await setPro(admin.id, String(form.get("user")), until, inr && Number.isFinite(inr) ? inr : null);
  back();
}

export async function toggleAdmin(form: FormData) {
  const admin = await requireAdmin();
  const target = String(form.get("user"));
  if (target === admin.id) return; // never lock yourself out
  await setAdmin(target, form.get("admin") === "1");
  back();
}

/** Approve a video for the channel and start uploading it. */
export async function approveUpload(form: FormData): Promise<void> {
  const admin = await requireAdmin();
  const id = String(form.get("id"));
  const title = String(form.get("title") ?? "").trim().slice(0, 100);
  const description = String(form.get("description") ?? "").trim().slice(0, 4900);
  const tags = String(form.get("tags") ?? "").split(",").map((t) => t.trim()).filter(Boolean).slice(0, 25);
  await db.query(`update youtube_uploads set status = 'approved', title = coalesce(nullif($2, ''), title),
                   description = coalesce(nullif($3, ''), description), tags = $4, reviewed_at = now(), error = null
                   where id = $1::bigint and status in ('pending', 'failed')`, [id, title, description, tags]);
  await logEvent("youtube_approved", admin.id, null, { upload: id });
  try {
    await renderServer("youtube-upload", { upload_id: Number(id), access_token: await accessToken() });
  } catch (e) {
    await db.query(`update youtube_uploads set status = 'failed', error = $2 where id = $1::bigint`, [id, (e as Error).message.slice(0, 1000)]);
  }
  back();
}

export async function rejectUpload(form: FormData) {
  const admin = await requireAdmin();
  const note = String(form.get("note") ?? "").trim() || "This video was not approved for the channel.";
  await db.query(`update youtube_uploads set status = 'rejected', review_note = $2, reviewed_at = now() where id = $1::bigint`,
    [String(form.get("id")), note]);
  await logEvent("youtube_rejected", admin.id, null, { upload: String(form.get("id")) });
  back();
}

export async function syncYouTube(): Promise<void> {
  await requireAdmin();
  try {
    await renderServer("youtube-sync", { access_token: await accessToken() });
  } catch (e) {
    await one(`insert into settings (key, value) values ('youtube_sync_error', to_jsonb($1::text))
               on conflict (key) do update set value = excluded.value, updated_at = now() returning key`, [(e as Error).message]);
  }
  back();
}

export async function disconnectYouTube() {
  await requireAdmin();
  await disconnect();
  back();
}

/** Save the plans: the whole JSON, checked for the parts the code reads. */
export async function savePlans(form: FormData): Promise<{ ok: boolean; message: string }> {
  await requireAdmin();
  let value: Record<string, unknown>;
  try {
    value = JSON.parse(String(form.get("plans") ?? ""));
  } catch (e) {
    return { ok: false, message: `Not valid JSON: ${(e as Error).message}` };
  }
  for (const key of ["free", "pro", "cost", "rewards", "packs", "downloads_per_day", "cost_model"]) {
    if (!(key in value)) return { ok: false, message: `The plans need "${key}".` };
  }
  await db.query(`update settings set value = $1::jsonb, updated_at = now() where key = 'plans'`, [JSON.stringify(value)]);
  back();
  return { ok: true, message: "Saved. New prices and rewards apply from now." };
}

export async function savePlaylists(form: FormData): Promise<{ ok: boolean; message: string }> {
  await requireAdmin();
  try {
    const value = JSON.parse(String(form.get("playlists") || "{}"));
    await db.query(`insert into settings (key, value) values ('youtube_playlists', $1::jsonb)
                    on conflict (key) do update set value = excluded.value, updated_at = now()`, [JSON.stringify(value)]);
  } catch (e) {
    return { ok: false, message: `Not valid JSON: ${(e as Error).message}` };
  }
  back();
  return { ok: true, message: "Saved." };
}
