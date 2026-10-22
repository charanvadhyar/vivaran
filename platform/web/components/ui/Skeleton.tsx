import styles from "./Skeleton.module.css";

/** A grey block the shape of content that is still loading. */
export function Skeleton({ width = "100%", height = 16, radius }: { width?: number | string; height?: number | string; radius?: number }) {
  return <div className={styles.skeleton} style={{ width, height, borderRadius: radius }} aria-hidden />;
}
