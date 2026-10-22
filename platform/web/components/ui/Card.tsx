import type { HTMLAttributes, ReactNode } from "react";
import { cx } from "./cx";
import styles from "./Card.module.css";

/** A raised surface. `title` and `subtitle` give it a standard head. */
export function Card({ title, subtitle, aside, flush, accent, interactive, className, children, ...rest }:
  { title?: ReactNode; subtitle?: ReactNode; aside?: ReactNode; flush?: boolean; accent?: boolean; interactive?: boolean; children?: ReactNode }
  & HTMLAttributes<HTMLElement>) {
  return (
    <section className={cx(styles.card, flush && styles.flush, accent && styles.accent, interactive && styles.interactive, className)} {...rest}>
      {title ? (
        <div className={styles.title}>
          <h2>{title}</h2>
          {aside}
        </div>
      ) : null}
      {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
      {children}
    </section>
  );
}
