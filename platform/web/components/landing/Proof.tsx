import styles from "./Proof.module.css";

/** Numbers that say what the thing does, not how big it is. */
export function Proof({ items }: { items: { big: string; label: string }[] }) {
  return (
    <div className={styles.row}>
      {items.map((item) => (
        <div key={item.label} className={styles.cell}>
          <div className={styles.big} dangerouslySetInnerHTML={{ __html: item.big }} />
          <div className={styles.label}>{item.label}</div>
        </div>
      ))}
    </div>
  );
}
