import styles from "./Kbd.module.css";

/** A key on the keyboard. */
export function Kbd({ children }: { children: string }) {
  return <kbd className={styles.kbd}>{children}</kbd>;
}
