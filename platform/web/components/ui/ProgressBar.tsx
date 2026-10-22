import styles from "./ProgressBar.module.css";

/** Progress from 0 to 1, or an indeterminate sweep when `value` is unknown. */
export function ProgressBar({ value, label, detail }: { value?: number; label?: string; detail?: string }) {
  const percent = value === undefined ? undefined : Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent} aria-label={label}>
      {label || detail ? (
        <div className={styles.label}><span>{label}</span><span>{detail ?? (percent !== undefined ? `${percent}%` : "")}</span></div>
      ) : null}
      <div className={styles.bar}>
        <div className={percent === undefined ? `${styles.fill} ${styles.busy}` : styles.fill} style={percent === undefined ? undefined : { width: `${percent}%` }} />
      </div>
    </div>
  );
}
