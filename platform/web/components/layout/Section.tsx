import Link from "next/link";
import type { ReactNode } from "react";
import { cx } from "../ui/cx";
import { Icon } from "../ui/Icon";
import styles from "./Section.module.css";

/** A titled block on a page, such as a shelf of videos. */
export function Section({ title, aside, href, first, children }:
  { title: ReactNode; aside?: ReactNode; href?: string; first?: boolean; children: ReactNode }) {
  return (
    <section className={cx(styles.section, first && styles.first)}>
      <div className={styles.head}>
        <h2>{title}</h2>
        {href ? <Link href={href} className={styles.aside}>{aside}<Icon name="chevronRight" /></Link> : aside ? <span className={styles.aside}>{aside}</span> : null}
      </div>
      {children}
    </section>
  );
}
