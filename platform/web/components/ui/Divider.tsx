import styles from "./Divider.module.css";

/** A line between sections, with an optional word on it. */
export function Divider({ label }: { label?: string }) {
  if (label) return <div className={styles.labelled} role="separator">{label}</div>;
  return <hr className={styles.divider} />;
}
