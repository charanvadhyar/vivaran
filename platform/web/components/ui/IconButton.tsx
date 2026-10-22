import type { ButtonHTMLAttributes } from "react";
import { cx } from "./cx";
import { Icon, type IconName } from "./Icon";
import styles from "./IconButton.module.css";

/** A button that is only an icon. `label` is required: it is what screen readers and the tooltip say. */
export function IconButton({ icon, label, outlined, size = "md", className, ...rest }:
  { icon: IconName; label: string; outlined?: boolean; size?: "sm" | "md" } & ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button type="button" aria-label={label} title={label}
      className={cx(styles.iconButton, outlined && styles.outlined, size === "sm" && styles.sm, className)} {...rest}>
      <Icon name={icon} />
    </button>
  );
}
