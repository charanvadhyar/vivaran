import Link from "next/link";
import styles from "./AdminNav.module.css";

const TABS = [["overview", "Analytics"], ["users", "Users & credits"], ["messages", "Messages"], ["youtube", "YouTube"], ["settings", "Plans & settings"]];

/** The admin page's sections, and the period the analytics cover. */
export function AdminNav({ tab, days }: { tab: string; days: number }) {
  return (
    <nav className={styles.nav}>
      <div className={styles.tabs}>
        {TABS.map(([id, label]) => (
          <Link key={id} href={`/admin?tab=${id}&days=${days}`} className={id === tab ? styles.active : styles.tab}>{label}</Link>
        ))}
      </div>
      {tab === "overview" ? (
        <div className={styles.days}>
          {[7, 30, 90, 365].map((d) => (
            <Link key={d} href={`/admin?tab=overview&days=${d}`} className={d === days ? styles.active : styles.tab}>{d === 365 ? "1 year" : `${d} days`}</Link>
          ))}
        </div>
      ) : null}
    </nav>
  );
}
