import type { InputHTMLAttributes } from "react";
import styles from "./Switch.module.css";

/** An on/off control. It is a checkbox underneath, so it works in forms. */
export function Switch({ label, ...rest }: { label: string } & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className={styles.switch}>
      <input type="checkbox" role="switch" className={styles.input} {...rest} />
      <span className={styles.track} aria-hidden><span className={styles.thumb} /></span>
      <span>{label}</span>
    </label>
  );
}
