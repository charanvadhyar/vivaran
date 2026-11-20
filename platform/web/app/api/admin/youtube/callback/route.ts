import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { isAdmin } from "@/lib/admin";
import { currentUser } from "@/lib/auth";
import { saveFromCode } from "@/lib/youtube";

export async function GET(request: Request) {
  if (!(await isAdmin(await currentUser()))) return new Response("not found", { status: 404 });
  const url = new URL(request.url);
  const site = (process.env.SITE_URL ?? url.origin).replace(/\/$/, "");
  const expected = (await cookies()).get("yt_oauth_state")?.value;
  const code = url.searchParams.get("code");
  if (!code || !expected || url.searchParams.get("state") !== expected) {
    return NextResponse.redirect(`${site}/admin?tab=youtube&yt=${encodeURIComponent(url.searchParams.get("error") ?? "refused")}`);
  }
  try {
    await saveFromCode(code);
  } catch (e) {
    return NextResponse.redirect(`${site}/admin?tab=youtube&yt=${encodeURIComponent((e as Error).message.slice(0, 200))}`);
  }
  return NextResponse.redirect(`${site}/admin?tab=youtube&yt=connected`);
}
