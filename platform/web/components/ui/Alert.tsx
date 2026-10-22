import type { ReactNode } from "react";
import { cx } from "./cx";
import { Icon } from "./Icon";
import styles from "./Alert.module.css";

/** A sentence the reader must not miss: a caution, a fact, or an error. */
export function Alert({ tone = "note", children, className }: { tone?: "note" | "info" | "danger"; children: ReactNode; className?: string }) {
  return (
    <div role={tone === "danger" ? "alert" : "note"} className={cx(styles.alert, styles[tone], className)}>
      <Icon name={tone === "danger" ? "warning" : "info"} />
      <div>{children}</div>
    </div>
  );
}
