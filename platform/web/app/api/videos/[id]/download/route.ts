import path from "node:path";
import { currentUser } from "@/lib/auth";
import { downloadsLeft, logEvent } from "@/lib/credits";
import { sendFile } from "@/lib/files";
import { storage, videoById } from "@/lib/videos";

/** A creator downloads their own video: signed in, own videos only, a few a day. */
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[a-f0-9]{12}$/.test(id)) return new Response("not found", { status: 404 });
  const [video, user] = await Promise.all([videoById(id), currentUser()]);
  if (!video || !user || video.user_id !== user.id || video.status !== "done") return new Response("not found", { status: 404 });
  // A Range request is the browser resuming the same download; count only the first.
  const resuming = !!request.headers.get("range");
  if (!resuming) {
    if ((await downloadsLeft(user.id)) <= 0) {
      const site = (process.env.SITE_URL ?? new URL(request.url).origin).replace(/\/$/, "");
      return new Response(
        `You have reached today's download limit. Try again tomorrow, or ask for more at ${site}/contact?kind=support&topic=limit&limit=downloads`,
        { status: 429, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
    await logEvent("download", user.id, id);
  }
  const response = await sendFile(request, path.join(storage(), "videos", `${id}.mp4`), "video/mp4", "private, no-store");
  const name = `${video.title.replace(/[^\p{L}\p{N} ._-]+/gu, "").slice(0, 80) || "video"} (Vivaran @${video.creator_handle}).mp4`;
  response.headers.set("content-disposition", `attachment; filename*=UTF-8''${encodeURIComponent(name)}`);
  return response;
}
