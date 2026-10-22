import { useId, type InputHTMLAttributes } from "react";
import { cx } from "./cx";
import styles from "./Input.module.css";

/** A text input with an optional label, hint and error. */
export function Input({ label, hint, error, className, id, ...rest }:
  { label?: string; hint?: string; error?: string } & InputHTMLAttributes<HTMLInputElement>) {
  const auto = useId();
  const inputId = id ?? auto;
  return (
    <div className={cx(styles.field, className)}>
      {label ? <label className={styles.label} htmlFor={inputId}>{label}</label> : null}
      <input id={inputId} className={styles.input} aria-invalid={error ? true : undefined}
        aria-describedby={hint || error ? `${inputId}-note` : undefined} {...rest} />
      {error ? <span id={`${inputId}-note`} className={styles.error}>{error}</span>
        : hint ? <span id={`${inputId}-note`} className={styles.hint}>{hint}</span> : null}
    </div>
  );
}
