"use client";

import { useEffect, useState } from "react";
import { Alert } from "../ui/Alert";
import { Card } from "../ui/Card";
import { ProgressBar } from "../ui/ProgressBar";
import { useRouter } from "next/navigation";

type Status = { state: string; progress: string; error?: string | null };

/** Shown in place of the player while a video renders. Asks the server every few seconds and reloads when done. */
export function RenderStatus({ id, initial }: { id: string; initial: Status }) {
  const [status, setStatus] = useState(initial);
  const router = useRouter();
  useEffect(() => {
    if (status.state === "done" || status.state === "failed") return;
    const timer = setInterval(async () => {
      const r = await fetch(`/api/videos/${id}/status`, { cache: "no-store" });
      if (!r.ok) return;
      const next = (await r.json()) as Status;
      setStatus(next);
      if (next.state === "done" || next.state === "failed") router.refresh();
    }, 4000);
    return () => clearInterval(timer);
  }, [id, status.state, router]);

  if (status.state === "failed") {
    return <Alert tone="danger"><strong>This render failed.</strong><div style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>{status.error}</div></Alert>;
  }
  return (
    <Card style={{ aspectRatio: "16 / 9", display: "grid", alignContent: "center", gap: 12 }}>
      <h2>Rendering…</h2>
      <ProgressBar label={status.state === "queued" ? "Waiting for an earlier render" : status.progress} />
      <p style={{ color: "var(--fg-muted)", fontSize: "var(--text-sm)" }}>This page updates itself. A minute of video takes about a minute to render.</p>
    </Card>
  );
}
