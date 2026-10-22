import { currentUser } from "@/lib/auth";
import { videoById } from "@/lib/videos";

/** The state of a render, for the watch page to poll. Only the creator may ask. */
export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [video, viewer] = await Promise.all([videoById(id), currentUser()]);
  if (!video || video.user_id !== viewer?.id) return Response.json({ state: "unknown" }, { status: 404 });
  return Response.json({ state: video.status, progress: video.progress, error: video.error }, { headers: { "cache-control": "no-store" } });
}
