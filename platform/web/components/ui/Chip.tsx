import Link from "next/link";
import type { ReactNode } from "react";
import { cx } from "./cx";
import styles from "./Chip.module.css";

/** A pill for choosing one of several things (a filter, a tab-like switch). */
export function Chip({ href, on, children, onClick }: { href?: string; on?: boolean; children: ReactNode; onClick?: () => void }) {
  const className = cx(styles.chip, on && styles.on);
  if (href) return <Link href={href} className={className} aria-current={on ? "page" : undefined}>{children}</Link>;
  return <button type="button" className={className} aria-pressed={on} onClick={onClick}>{children}</button>;
}
