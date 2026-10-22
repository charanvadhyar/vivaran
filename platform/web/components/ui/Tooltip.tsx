import type { ReactNode } from "react";
import styles from "./Tooltip.module.css";

/** A short label on hover or focus. For anything longer, put the text on the page. */
export function Tooltip({ text, children }: { text: string; children: ReactNode }) {
  return (
    <span className={styles.wrap}>
      {children}
      <span role="tooltip" className={styles.tip}>{text}</span>
    </span>
  );
}
