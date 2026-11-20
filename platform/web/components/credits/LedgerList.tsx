import { KIND_LABELS, type LedgerRow } from "@/lib/credits";
import { Card } from "../ui/Card";
import styles from "./LedgerList.module.css";

/** Every change to the balance, newest first. */
export function LedgerList({ rows }: { rows: LedgerRow[] }) {
  const shown = rows.filter((r) => Number(r.delta) !== 0);
  return (
    <Card title="History">
      {shown.length ? (
        <table className={styles.table}>
          <tbody>
            {shown.map((r) => {
              const d = Number(r.delta);
              return (
                <tr key={r.id}>
                  <td className={styles.when}>{new Date(r.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", timeZone: "Asia/Kolkata" })}</td>
                  <td>{KIND_LABELS[r.kind] ?? r.kind}{r.video_id ? <a href={`/v/${r.video_id}`} className={styles.video}> · video</a> : null}</td>
                  <td className={d > 0 ? styles.plus : styles.minus}>{d > 0 ? "+" : "−"}{Math.abs(d).toString().replace(/\.00$/, "")}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : <p className={styles.empty}>No credits used yet.</p>}
    </Card>
  );
}
