import type { SelectHTMLAttributes } from "react";
import { cx } from "./cx";
import { Icon } from "./Icon";
import styles from "./Select.module.css";

/** A native select, styled. Keep it native: it works on every phone. */
export function Select({ options, placeholder, className, ...rest }:
  { options: { value: string; label: string }[]; placeholder?: string } & SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <span className={cx(styles.wrap, className)}>
      <select className={styles.select} {...rest}>
        {placeholder ? <option value="" disabled>{placeholder}</option> : null}
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      <Icon name="chevronDown" className={styles.chevron} />
    </span>
  );
}
