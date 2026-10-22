import styles from "./SectionLabel.module.css";

/** The small editorial label above a landing section: "[ 02 / 04 ] · Make". */
export function SectionLabel({ index, total, text }: { index: number; total: number; text: string }) {
  return (
    <div className={styles.label} aria-hidden>
      <span className={styles.index}>{String(index).padStart(2, "0")}</span>
      <span>{text}</span>
    </div>
  );
}
