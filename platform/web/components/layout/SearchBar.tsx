import { Icon } from "../ui/Icon";
import styles from "./SearchBar.module.css";

/** The site search. A plain form, so it works before any script loads. */
export function SearchBar({ defaultValue = "", placeholder = "Search a topic" }: { defaultValue?: string; placeholder?: string }) {
  return (
    <form className={styles.search} action="/explore" role="search">
      <Icon name="search" className={styles.icon} />
      <input type="search" name="q" className={styles.input} placeholder={placeholder} defaultValue={defaultValue} aria-label="Search videos" />
    </form>
  );
}
