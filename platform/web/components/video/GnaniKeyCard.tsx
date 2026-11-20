"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";

type Status = { set: boolean; setAt: string | null };

const card: React.CSSProperties = {
  border: "1px solid var(--border-default)",
  background: "var(--bg-surface)",
  borderRadius: "var(--radius-lg)",
  padding: "1.25rem 1.5rem",
  display: "flex",
  flexDirection: "column",
  gap: "0.75rem",
};

function when(iso: string | null): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

export function GnaniKeyCard({ initial }: { initial: Status }) {
  const [status, setStatus] = useState<Status>(initial);
  const [key, setKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<{ ok: boolean; text: string } | null>(null);

  async function save() {
    if (!key.trim()) return;
    setBusy(true);
    setNote(null);
    try {
      const res = await fetch("/api/settings/gnani-key", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ key: key.trim() }),
      });
      const data = (await res.json()) as Status & { error?: string };
      if (!res.ok) {
        setNote({ ok: false, text: data.error ?? "Couldn't save the key." });
      } else {
        setStatus({ set: data.set, setAt: data.setAt });
        setKey("");
        setNote({ ok: true, text: "Saved. Your videos now render on your own Gnani credits." });
      }
    } catch {
      setNote({ ok: false, text: "Network error — please try again." });
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    setBusy(true);
    setNote(null);
    try {
      const res = await fetch("/api/settings/gnani-key", { method: "DELETE" });
      const data = (await res.json()) as Status;
      setStatus({ set: data.set, setAt: data.setAt });
      setNote({ ok: true, text: "Removed. Voiced videos now use Vivaran's voice and cost the full credit." });
    } catch {
      setNote({ ok: false, text: "Network error — please try again." });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={card}>
      <div>
        <strong style={{ fontSize: "1.05rem" }}>Your Gnani API key</strong>
        <p style={{ color: "var(--fg-muted)", margin: "0.35rem 0 0", lineHeight: "var(--leading-normal)" }}>
          Add your own Gnani key and your videos are voiced on <strong>your own Gnani credits</strong>, so each video
          costs only a quarter of a Vivaran credit. Without one, Vivaran&apos;s voice is used.{" "}
          <a href="https://app.gnani.ai/voice" target="_blank" rel="noreferrer" style={{ color: "var(--fg-link)" }}>
            Get a key →
          </a>
        </p>
      </div>

      {status.set && (
        <p style={{ margin: 0, color: "var(--positive, var(--fg-default))" }}>
          ✓ Your key is set{status.setAt ? ` (added ${when(status.setAt)})` : ""}. Renders use your key.
        </p>
      )}

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder={status.set ? "Paste a new key to replace it" : "Paste your Gnani API key"}
          autoComplete="off"
          spellCheck={false}
          style={{
            flex: "1 1 18rem",
            minWidth: 0,
            height: "var(--control-h)",
            padding: "0 0.75rem",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-default)",
            background: "var(--bg-raised)",
            color: "var(--fg-default)",
            fontFamily: "var(--font-mono)",
          }}
        />
        <Button variant="primary" onClick={save} loading={busy} disabled={busy || !key.trim()}>
          {status.set ? "Replace" : "Save"}
        </Button>
        {status.set && (
          <Button variant="danger" onClick={remove} disabled={busy}>
            Remove
          </Button>
        )}
      </div>

      {note && (
        <p style={{ margin: 0, color: note.ok ? "var(--positive, var(--fg-default))" : "var(--negative, var(--fg-default))" }}>
          {note.text}
        </p>
      )}

      <p style={{ margin: 0, color: "var(--fg-subtle)", fontSize: "0.85rem" }}>
        Stored encrypted; never shown again and never shared. You can replace or remove it any time.
      </p>
    </div>
  );
}
