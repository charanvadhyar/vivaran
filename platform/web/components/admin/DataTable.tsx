import type { ReactNode } from "react";
import styles from "./DataTable.module.css";

/** A small table of rows. Numeric columns are right-aligned. */
export function DataTable({ title, columns, rows, empty = "Nothing yet." }:
  { title: string; columns: { key: string; label: string; numeric?: boolean }[]; rows: Record<string, ReactNode>[]; empty?: string }) {
  return (
    <div className={styles.wrap}>
      <div className={styles.title}>{title}</div>
      {rows.length ? (
        <table className={styles.table}>
          <thead><tr>{columns.map((c) => <th key={c.key} className={c.numeric ? styles.num : undefined}>{c.label}</th>)}</tr></thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>{columns.map((c) => <td key={c.key} className={c.numeric ? styles.num : undefined}>{r[c.key]}</td>)}</tr>
            ))}
          </tbody>
        </table>
      ) : <p className={styles.empty}>{empty}</p>}
    </div>
  );
}
