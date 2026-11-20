/** Which doors are open.
    Waitlist mode (WAITLIST=1) is the site before launch: every page that explains
    Vivaran is up, the demo videos play, and people leave an email. Sign-in, the
    dashboard, connector addresses and rendering are closed. */
export const WAITLIST = process.env.WAITLIST === "1";

/** Whether the creator pay terms are shown (CREATOR_PAY=1). Off at launch:
    the Earn section, the terms page and links to it are hidden until payouts
    are ready. */
export const CREATOR_PAY = process.env.CREATOR_PAY === "1";

/** Paths that need an account or the render server; closed in waitlist mode. */
export const CLOSED_IN_WAITLIST = ["/login", "/dashboard", "/design", "/api/auth", "/admin", "/api/admin", "/r"];

export function closedInWaitlist(pathname: string): boolean {
  return WAITLIST && CLOSED_IN_WAITLIST.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}
