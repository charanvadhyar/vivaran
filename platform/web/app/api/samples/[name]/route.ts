import path from "node:path";
import { sendFile } from "@/lib/files";
import { storage } from "@/lib/videos";

// Short voice samples made by the `voice_sample` tool. They hold no user content.
export async function GET(request: Request, { params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  if (!/^voice-[A-Za-z]+-[a-z]{2}-[0-9.]+\.wav$/.test(name)) return new Response("not found", { status: 404 });
  return sendFile(request, path.join(storage(), "samples", name), "audio/wav", "public, max-age=86400");
}
