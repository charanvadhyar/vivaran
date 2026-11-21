import { createHmac, timingSafeEqual } from "node:crypto";

/** Whether `?exp=&sig=` on a video file or thumbnail link is a valid signature from the render server,
    which signs short-lived links for the player in its MCP Apps panel (shown in a sandbox without the
    site's cookies). Both sides share CEVG_INTERNAL_TOKEN. */
export function signedOk(videoId: string, url: string): boolean {
  const key = process.env.CEVG_INTERNAL_TOKEN ?? "";
  const params = new URL(url).searchParams;
  const exp = Number(params.get("exp"));
  const sig = params.get("sig") ?? "";
  if (!key || !Number.isFinite(exp) || exp * 1000 < Date.now() || sig.length !== 32) return false;
  const want = createHmac("sha256", key).update(`${videoId}.${exp}`).digest("hex").slice(0, 32);
  return timingSafeEqual(Buffer.from(sig), Buffer.from(want));
}
