"use server";

import { unlink } from "node:fs/promises";
import path from "node:path";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { currentUser, signIn, signOut } from "@/lib/auth";
import { SUBJECTS } from "@/lib/brand";
import { db } from "@/lib/db";
import { regenerateToken } from "@/lib/users";
import { storage } from "@/lib/videos";
import { WAITLIST } from "@/lib/mode";
import { join, ROLES, validEmail, type Role } from "@/lib/waitlist";

async function requireUser() {
  const user = await currentUser();
  if (!user) redirect("/login");
  return user;
}

export async function signInWithGoogle() {
  await signIn("google", { redirectTo: "/dashboard" });
}

export async function signInForDevelopment(form: FormData) {
  await signIn("dev", { name: String(form.get("name") ?? ""), redirectTo: "/dashboard" });
}

export async function signOutNow() {
  await signOut({ redirectTo: "/" });
}

/** Make a video public or private. Only its creator can, and only once it has rendered. */
export async function setPublic(form: FormData) {
  const user = await requireUser();
  const id = String(form.get("id"));
  const makePublic = form.get("public") === "1";
  // A video is filed under a subject when it is published.
  const subject = String(form.get("subject") ?? "");
  if (makePublic && !SUBJECTS.some((s) => s.id === subject)) return;
  await db.query(
    `update videos set is_public = $3,
       subject = case when $3 then $4 else subject end,
       published_at = case when $3 then coalesce(published_at, now()) else published_at end
     where id = $1 and user_id::text = $2 and status = 'done'`,
    [id, user.id, makePublic, subject || null],
  );
  revalidatePath(`/v/${id}`);
  revalidatePath("/dashboard");
  revalidatePath("/");
}

export async function deleteVideo(form: FormData) {
  const user = await requireUser();
  const id = String(form.get("id"));
  if (!/^[a-f0-9]{12}$/.test(id)) return;
  const { rowCount } = await db.query(
    `delete from videos where id = $1 and user_id::text = $2 and status in ('done', 'failed')`,
    [id, user.id],
  );
  if (rowCount) {
    for (const ending of ["mp4", "png", "srt"]) {
      await unlink(path.join(storage(), "videos", `${id}.${ending}`)).catch(() => {});
    }
  }
  revalidatePath("/dashboard");
  revalidatePath("/");
  redirect("/dashboard");
}

/** Replace the connector address. The old one stops working at once. */
export async function newConnectorAddress() {
  const user = await requireUser();
  await regenerateToken(user.id);
  revalidatePath("/dashboard");
}

export type WaitlistResult = { ok: true; position: number; already: boolean } | { ok: false; error: string } | null;

/** Join the waitlist. Works without an account; the only thing kept is what the form sends. */
export async function joinWaitlist(_previous: WaitlistResult, form: FormData): Promise<WaitlistResult> {
  if (!WAITLIST) return { ok: false, error: "The waitlist is closed; sign in instead." };
  // A field people cannot see. Anything in it is a bot filling every box.
  if (String(form.get("website") ?? "")) return { ok: true, position: 0, already: true };
  const email = String(form.get("email") ?? "").trim();
  if (!validEmail(email)) return { ok: false, error: "That does not look like an email address." };
  const role = String(form.get("role") ?? "learner");
  if (!(ROLES as readonly string[]).includes(role)) return { ok: false, error: "Pick who you are." };
  const note = String(form.get("note") ?? "").trim().slice(0, 500) || null;
  const source = String(form.get("source") ?? "").trim().slice(0, 40) || null;
  try {
    const result = await join(email, role as Role, note, source);
    return { ok: true, ...result };
  } catch (error) {
    console.error("waitlist:", error);
    return { ok: false, error: "Something went wrong on our side. Try again in a minute." };
  }
}

// --- Credits and the creator program --------------------------------------------

export async function joinCreator() {
  const user = await requireUser();
  const { joinCreatorProgram } = await import("@/lib/credits");
  await joinCreatorProgram(user.id);
  revalidatePath("/dashboard");
}

export async function claimSubscribed() {
  const user = await requireUser();
  const { claimSubscribe } = await import("@/lib/credits");
  await claimSubscribe(user.id);
  revalidatePath("/dashboard");
}

// --- The Vivaran YouTube channel ----------------------------------------------------

export type SeoDraft = { title: string; description: string; tags: string[] };

/** Pro only: title, description and tags for the channel, written by the Claude API. */
export async function writeSeo(videoId: string): Promise<SeoDraft | { error: string }> {
  const user = await requireUser();
  const { account } = await import("@/lib/credits");
  if ((await account(user.id)).tier !== "pro") return { error: "Writing the SEO for you is part of Pro." };
  const own = await db.query(`select 1 from videos where id = $1 and user_id::text = $2 and status = 'done'`, [videoId, user.id]);
  if (!own.rowCount) return { error: "No such video." };
  try {
    const { renderServer } = await import("@/lib/render");
    return await renderServer<SeoDraft>("seo", { video_id: videoId });
  } catch (e) {
    return { error: `Could not write it just now: ${(e as Error).message}` };
  }
}

/** Send a public video to the channel's review queue. */
export async function submitToYouTube(form: FormData): Promise<{ ok: boolean; message: string }> {
  const user = await requireUser();
  const id = String(form.get("id") ?? "");
  const title = String(form.get("title") ?? "").trim();
  const description = String(form.get("description") ?? "").trim();
  const tags = String(form.get("tags") ?? "").split(",").map((t) => t.trim()).filter(Boolean).slice(0, 25);
  const byAi = form.get("seo_by_ai") === "1";
  if (!/^[a-f0-9]{12}$/.test(id)) return { ok: false, message: "No such video." };
  if (title.length < 10 || title.length > 100) return { ok: false, message: "The title must be 10 to 100 characters." };
  if (description.length < 100 || description.length > 4900) return { ok: false, message: "The description must be 100 to 4,900 characters." };
  if (tags.join(",").length > 480) return { ok: false, message: "The tags are too long together (480 characters at most)." };
  if (/[<>]/.test(title + description)) return { ok: false, message: "YouTube does not allow < or > in titles and descriptions." };
  const video = await db.query(`select 1 from videos where id = $1 and user_id::text = $2 and status = 'done' and is_public`, [id, user.id]);
  if (!video.rowCount) return { ok: false, message: "Make the video public on Vivaran first." };
  const site = (process.env.SITE_URL ?? "").replace(/\/$/, "");
  const credit = `Made by ${user.name} (@${user.handle})`;
  const full = description.includes(`@${user.handle}`) ? description : `${description}\n\n${credit} with Vivaran: ${site}/v/${id}`;
  const { rowCount } = await db.query(
    `insert into youtube_uploads (video_id, user_id, title, description, tags, seo_by_ai)
     values ($1, $2::uuid, $3, $4, $5, $6)
     on conflict (video_id) do update set title = excluded.title, description = excluded.description, tags = excluded.tags,
       seo_by_ai = excluded.seo_by_ai, status = 'pending', review_note = null, error = null, created_at = now()
     where youtube_uploads.status in ('pending', 'rejected', 'failed')`,
    [id, user.id, title, full, tags, byAi]);
  if (!rowCount) return { ok: false, message: "This video is already approved or on the channel." };
  const { logEvent } = await import("@/lib/credits");
  await logEvent("youtube_submitted", user.id, id, { by_ai: byAi });
  revalidatePath(`/v/${id}`);
  return { ok: true, message: "Sent for review. It goes on the channel once it is approved." };
}
