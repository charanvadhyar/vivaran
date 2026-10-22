import { SUBJECTS } from "@/lib/brand";
import { Chip } from "../ui/Chip";
import styles from "./SubjectChips.module.css";

/** The subject filter on the home page. Keeps the search words when switching subject. */
export function SubjectChips({ chosen, query }: { chosen: string; query?: string }) {
  const link = (id: string) => {
    const params = new URLSearchParams();
    if (id) params.set("subject", id);
    if (query) params.set("q", query);
    const text = params.toString();
    return text ? `/explore?${text}` : "/explore";
  };
  return (
    <nav className={styles.row} aria-label="Subjects">
      <Chip href={link("")} on={!chosen}>All</Chip>
      {SUBJECTS.map((s) => <Chip key={s.id} href={link(s.id)} on={chosen === s.id}>{s.short}</Chip>)}
    </nav>
  );
}
