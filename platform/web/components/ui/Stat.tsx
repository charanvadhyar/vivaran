import type { ReactNode } from "react";
import styles from "./Stat.module.css";

/** One number with its label. Put several in a StatGroup. */
export function Stat({ value, label }: { value: ReactNode; label: string }) {
  return (
    <div className={styles.stat}>
      <div className={styles.value}>{value}</div>
      <div className={styles.label}>{label}</div>
    </div>
  );
}

export function StatGroup({ children }: { children: ReactNode }) {
  return <div className={styles.group}>{children}</div>;
}
