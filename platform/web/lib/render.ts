/** Calls from the site to the render server's internal endpoints, with the shared token. */
export async function renderServer<T>(name: "seo" | "youtube-upload" | "youtube-sync", body: Record<string, unknown>): Promise<T> {
  const base = process.env.CEVG_FILES_URL;
  if (!base) throw new Error("CEVG_FILES_URL is not set, so the site cannot reach the render server");
  const res = await fetch(`${base.replace(/\/$/, "")}/internal/${name}`, {
    method: "POST",
    headers: { "content-type": "application/json", "x-cevg-internal": process.env.CEVG_INTERNAL_TOKEN ?? "" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const data = (await res.json().catch(() => ({}))) as T & { error?: string };
  if (!res.ok) throw new Error(data.error ?? `the render server answered ${res.status}`);
  return data;
}
