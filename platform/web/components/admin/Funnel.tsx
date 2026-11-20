import styles from "./Funnel.module.css";

/** How far new accounts get, step by step. */
export function Funnel({ steps }: { steps: { label: string; value: number }[] }) {
  const first = Math.max(1, steps[0]?.value ?? 1);
  return (
    <div className={styles.funnel}>
      <div className={styles.title}>From sign-up to YouTube</div>
      {steps.map((s) => (
        <div key={s.label} className={styles.row}>
          <span className={styles.label}>{s.label}</span>
          <span className={styles.track}><span className={styles.fill} style={{ width: `${(s.value / first) * 100}%` }} /></span>
          <span className={styles.value}>{s.value} <small>{Math.round((s.value / first) * 100)}%</small></span>
        </div>
      ))}
    </div>
  );
}
