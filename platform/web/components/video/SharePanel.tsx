"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { useToast } from "@/components/ui/Toast";
import styles from "./SharePanel.module.css";

/** Share a public video: the phone's own share sheet where there is one,
    WhatsApp, LinkedIn, X, and a plain link. */
export function SharePanel({ url, title }: { url: string; title: string }) {
  const toast = useToast();
  const [native, setNative] = useState(false);
  useEffect(() => setNative(typeof navigator !== "undefined" && typeof navigator.share === "function"), []);
  const text = `${title}: every step, shown, on Vivaran`;
  const enc = encodeURIComponent;
  const targets = [
    { name: "WhatsApp", href: `https://wa.me/?text=${enc(`${text} ${url}`)}` },
    { name: "LinkedIn", href: `https://www.linkedin.com/sharing/share-offsite/?url=${enc(url)}` },
    { name: "X", href: `https://twitter.com/intent/tweet?text=${enc(text)}&url=${enc(url)}` },
  ];
  return (
    <div className={styles.panel} aria-label="Share this video">
      <span className={styles.label}><Icon name="share" /> Share with your batch</span>
      <div className={styles.row}>
        {native ? (
          <Button size="sm" variant="primary" icon={<Icon name="share" />}
            onClick={() => navigator.share({ title, text, url }).catch(() => undefined)}>Share</Button>
        ) : null}
        {targets.map((t) => (
          <Button key={t.name} size="sm" href={t.href} target="_blank" rel="noopener noreferrer">{t.name}</Button>
        ))}
        <Button size="sm" variant="ghost" icon={<Icon name="link" />} onClick={async () => {
          try {
            await navigator.clipboard.writeText(url);
            toast("Link copied", "check");
          } catch {
            toast(url);
          }
        }}>Copy link</Button>
      </div>
    </div>
  );
}
