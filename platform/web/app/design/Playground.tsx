"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { Slider } from "@/components/ui/Slider";
import { Switch } from "@/components/ui/Switch";
import { useToast } from "@/components/ui/Toast";

/** The interactive pieces on the design page. */
export function Playground() {
  const [speed, setSpeed] = useState(1);
  const [on, setOn] = useState(true);
  const [open, setOpen] = useState(false);
  const toast = useToast();
  return (
    <div style={{ display: "grid", gap: 16 }}>
      <Slider label="Speed" value={speed} min={0.5} max={2} step={0.25} onChange={setSpeed} format={(v) => `${v}×`} />
      <Switch label="Show silent videos" checked={on} onChange={(e) => setOn(e.target.checked)} />
      <div style={{ display: "flex", gap: 10 }}>
        <Button onClick={() => toast("Saved", "check")}>Show a toast</Button>
        <Button onClick={() => setOpen(true)}>Open a dialog</Button>
      </div>
      <Dialog open={open} onClose={() => setOpen(false)} title="A dialog"
        actions={<><Button onClick={() => setOpen(false)}>Cancel</Button><Button variant="primary" onClick={() => setOpen(false)}>Confirm</Button></>}>
        <p>Built on the native dialog element: Escape closes it, focus stays inside.</p>
      </Dialog>
    </div>
  );
}
