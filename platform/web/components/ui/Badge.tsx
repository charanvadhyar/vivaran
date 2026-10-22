import type { ReactNode } from "react";
import { cx } from "./cx";
import styles from "./Badge.module.css";

export type BadgeTone = "neutral" | "positive" | "negative" | "accent" | "info" | "solid";

/** A small status label. Tone says what it means, not what colour it is. */
export function Badge({ tone = "neutral", children, className }: { tone?: BadgeTone; children: ReactNode; className?: string }) {
  return <span className={cx(styles.badge, tone !== "neutral" && styles[tone], className)}>{children}</span>;
}
