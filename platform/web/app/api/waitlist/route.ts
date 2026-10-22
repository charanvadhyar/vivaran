import { timingSafeEqual } from "node:crypto";
import { allSignups } from "@/lib/waitlist";

/** The waitlist as CSV, for whoever runs the launch. Needs the admin token:
      curl -H "Authorization: Bearer $WAITLIST_ADMIN_TOKEN" https://<site>/api/waitlist > waitlist.csv
    The token travels in a header, never in the address, so it does not land in logs. */
export async function GET(request: Request) {
  const expected = process.env.WAITLIST_ADMIN_TOKEN ?? "";
  const given = (request.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!expected || given.length !== expected.length || !timingSafeEqual(Buffer.from(given), Buffer.from(expected))) {
    return new Response("not found", { status: 404 });
  }
  const rows = await allSignups();
  const cell = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = ["position,email,role,note,source,joined_at",
    ...rows.map((r, i) => [i + 1, r.email, r.role, r.note, r.source, r.created_at.toISOString()].map(cell).join(","))].join("\n");
  return new Response(csv + "\n", {
    headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": "attachment; filename=waitlist.csv", "cache-control": "no-store" },
  });
}
