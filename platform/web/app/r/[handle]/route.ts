import { NextResponse } from "next/server";
import { userByHandle } from "@/lib/users";

/** An invitation link: remember who invited, then go to sign-in. */
export async function GET(request: Request, { params }: { params: Promise<{ handle: string }> }) {
  const { handle } = await params;
  const site = (process.env.SITE_URL ?? new URL(request.url).origin).replace(/\/$/, "");
  const response = NextResponse.redirect(`${site}/login`);
  if (/^[a-z0-9-]{1,40}$/.test(handle) && (await userByHandle(handle))) {
    response.cookies.set("vivaran_ref", handle, { maxAge: 60 * 60 * 24 * 30, httpOnly: true, sameSite: "lax", path: "/" });
  }
  return response;
}
