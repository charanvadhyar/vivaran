import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import styles from "./EmptyState.module.css";

/** What a list shows when there is nothing in it: say why, and what to do next. */
export function EmptyState({ icon = "spark", title, text, action }: { icon?: IconName; title: string; text?: string; action?: ReactNode }) {
  return (
    <div className={styles.empty}>
      <Icon name={icon} size={24} className={styles.icon} />
      <div className={styles.title}>{title}</div>
      {text ? <p className={styles.text}>{text}</p> : null}
      {action ? <div className={styles.action}>{action}</div> : null}
    </div>
  );
}
