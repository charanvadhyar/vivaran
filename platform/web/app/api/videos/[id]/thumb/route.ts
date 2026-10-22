import path from "node:path";
import { currentUser } from "@/lib/auth";
import { sendFile } from "@/lib/files";
import { canWatch, storage, videoById } from "@/lib/videos";

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[a-f0-9]{12}$/.test(id)) return new Response("not found", { status: 404 });
  const video = await videoById(id);
  if (!video) return new Response("not found", { status: 404 });
  // A private video is only for its creator.
  const viewer = video.is_public ? null : await currentUser();
  if (!canWatch(video, viewer?.id)) return new Response("not found", { status: 404 });
  const cache = video.is_public ? "public, max-age=3600" : "private, no-store";
  return sendFile(request, path.join(storage(), "videos", `${id}.png`), "image/png", cache);
}
