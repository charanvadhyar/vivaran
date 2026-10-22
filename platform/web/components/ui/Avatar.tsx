import styles from "./Avatar.module.css";

/** A person's picture, or their initials when there is none. */
export function Avatar({ name, src, size = 32 }: { name: string; src?: string | null; size?: 24 | 32 | 48 | 64 }) {
  const initials = name.split(/\s+/).map((part) => part[0]).filter(Boolean).slice(0, 2).join("").toUpperCase();
  return (
    <span className={styles.avatar} style={{ width: size, height: size, fontSize: size * 0.38 }} aria-hidden>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      {src ? <img src={src} alt="" referrerPolicy="no-referrer" /> : initials}
    </span>
  );
}
