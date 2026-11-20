import styles from "./KpiGrid.module.css";

export type Kpi = { label: string; value: string; sub?: string; tone?: "good" | "bad" };

/** The headline numbers, as tiles. */
export function KpiGrid({ items }: { items: Kpi[] }) {
  return (
    <div className={styles.grid}>
      {items.map((k) => (
        <div key={k.label} className={styles.tile}>
          <div className={styles.label}>{k.label}</div>
          <div className={`${styles.value} ${k.tone ? styles[k.tone] : ""}`}>{k.value}</div>
          {k.sub ? <div className={styles.sub}>{k.sub}</div> : null}
        </div>
      ))}
    </div>
  );
}
