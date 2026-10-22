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
