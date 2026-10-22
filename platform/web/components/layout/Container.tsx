import type { ReactNode } from "react";
import { cx } from "../ui/cx";
import styles from "./Container.module.css";

/** Centres content at the page width. `main` adds the page's vertical padding. */
export function Container({ children, narrow, main, className }: { children: ReactNode; narrow?: boolean; main?: boolean; className?: string }) {
  const Tag = main ? "main" : "div";
  return <Tag className={cx(styles.container, narrow && styles.narrow, main && styles.main, className)}>{children}</Tag>;
}
