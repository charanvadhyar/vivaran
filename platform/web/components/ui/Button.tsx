import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cx } from "./cx";
import styles from "./Button.module.css";

export type ButtonVariant = "default" | "primary" | "ghost" | "danger" | "knockout";
export type ButtonSize = "sm" | "md" | "lg";

type Common = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  block?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  children?: ReactNode;
  className?: string;
};

type AsButton = Common & ButtonHTMLAttributes<HTMLButtonElement> & { href?: undefined };
type AsLink = Common & { href: string; download?: string; target?: string; rel?: string };

/** The one button. Use `href` for a link that looks like a button. */
export function Button(props: AsButton | AsLink) {
  const { variant = "default", size = "md", block, loading, icon, children, className, ...rest } = props;
  const classes = cx(
    styles.button,
    variant !== "default" && styles[variant],
    size !== "md" && styles[size],
    block && styles.block,
    loading && styles.loading,
    className,
  );
  const inner = (
    <>
      {icon}
      {children}
    </>
  );
  if ("href" in rest && rest.href !== undefined) {
    const { href, ...linkRest } = rest as AsLink;
    return (
      <Link href={href} className={classes} {...linkRest}>
        {inner}
      </Link>
    );
  }
  const { type = "button", disabled, ...buttonRest } = rest as AsButton;
  return (
    <button type={type} className={classes} disabled={disabled || loading} aria-busy={loading || undefined} {...buttonRest}>
      {inner}
    </button>
  );
}
