import { NextResponse, type NextRequest } from "next/server";
import { closedInWaitlist } from "@/lib/mode";

/** Before launch, the doors that need an account send people to the waitlist. */
export function proxy(request: NextRequest) {
  if (closedInWaitlist(request.nextUrl.pathname)) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.search = "";
    url.hash = "waitlist";
    return NextResponse.redirect(url, 307);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/login", "/dashboard/:path*", "/design", "/api/auth/:path*"] };
