import { randomBytes } from "node:crypto";
import { NextResponse } from "next/server";
import { isAdmin } from "@/lib/admin";
import { currentUser } from "@/lib/auth";
import { connectUrl } from "@/lib/youtube";

/** Start connecting the Vivaran YouTube channel (admins only). */
export async function GET() {
  if (!(await isAdmin(await currentUser()))) return new Response("not found", { status: 404 });
  const state = randomBytes(16).toString("hex");
  const response = NextResponse.redirect(connectUrl(state));
  response.cookies.set("yt_oauth_state", state, { maxAge: 600, httpOnly: true, sameSite: "lax", path: "/" });
  return response;
}
