import { Avatar } from "../ui/Avatar";
import styles from "./CreatorHeader.module.css";

/** A creator's name and picture at the top of their public page. */
export function CreatorHeader({ name, image, meta }: { name: string; image?: string | null; meta: string }) {
  return (
    <div className={styles.head}>
      <Avatar name={name} src={image} size={64} />
      <div className={styles.text}>
        <h1>{name}</h1>
        <span className={styles.meta}>{meta}</span>
      </div>
    </div>
  );
}
