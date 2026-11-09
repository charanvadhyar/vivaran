import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { Readable } from "node:stream";

/** Send a file, honouring a Range header so the player can seek. When the
    render server keeps the files (CEVG_FILES_URL, e.g. on Railway while the
    site runs on Vercel), the request is passed on to it with the internal
    token; the caller has already checked who may see the file. */
export async function sendFile(request: Request, file: string, type: string, cache: string): Promise<Response> {
  const remote = process.env.CEVG_FILES_URL;
  if (remote) return fromRenderServer(request, remote, file, type, cache);
  let size: number;
  try {
    size = (await stat(file)).size;
  } catch {
    return new Response("not found", { status: 404 });
  }
  const headers: Record<string, string> = { "content-type": type, "accept-ranges": "bytes", "cache-control": cache };
  const range = /^bytes=(\d*)-(\d*)$/.exec(request.headers.get("range") ?? "");
  if (range && (range[1] || range[2])) {
    let start = range[1] ? Number(range[1]) : size - Number(range[2]);
    let end = range[1] && range[2] ? Number(range[2]) : size - 1;
    start = Math.max(0, start);
    end = Math.min(end, size - 1);
    if (start > end) return new Response(null, { status: 416, headers: { "content-range": `bytes */${size}` } });
    const body = Readable.toWeb(createReadStream(file, { start, end })) as ReadableStream;
    return new Response(body, {
      status: 206,
      headers: { ...headers, "content-range": `bytes ${start}-${end}/${size}`, "content-length": String(end - start + 1) },
    });
  }
  const body = Readable.toWeb(createReadStream(file)) as ReadableStream;
  return new Response(body, { headers: { ...headers, "content-length": String(size) } });
}

async function fromRenderServer(request: Request, base: string, file: string, type: string, cache: string): Promise<Response> {
  const parts = file.split(/[\\/]/);
  const kind = parts[parts.length - 2];
  const name = parts[parts.length - 1];
  const headers: Record<string, string> = { "x-cevg-internal": process.env.CEVG_INTERNAL_TOKEN ?? "" };
  const range = request.headers.get("range");
  if (range) headers.range = range;
  const upstream = await fetch(`${base.replace(/\/$/, "")}/files/${kind}/${encodeURIComponent(name)}`, { headers, cache: "no-store" });
  if (upstream.status !== 200 && upstream.status !== 206 && upstream.status !== 416) return new Response("not found", { status: 404 });
  const out: Record<string, string> = { "content-type": type, "accept-ranges": "bytes", "cache-control": cache };
  for (const h of ["content-length", "content-range"]) {
    const v = upstream.headers.get(h);
    if (v) out[h] = v;
  }
  return new Response(upstream.body, { status: upstream.status, headers: out });
}
