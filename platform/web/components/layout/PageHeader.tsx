import type { ReactNode } from "react";
import styles from "./PageHeader.module.css";

/** The title block at the top of a page, with room for actions or stats on the right. */
export function PageHeader({ title, lead, aside }: { title: ReactNode; lead?: ReactNode; aside?: ReactNode }) {
  return (
    <div className={styles.head}>
      <div className={styles.text}>
        <h1>{title}</h1>
        {lead ? <p className={styles.lead}>{lead}</p> : null}
      </div>
      {aside}
    </div>
  );
}
