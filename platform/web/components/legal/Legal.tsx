import type { ReactNode } from "react";
import { Container } from "../layout/Container";
import { PageHeader } from "../layout/PageHeader";
import styles from "./Legal.module.css";

/** A plain legal page: a title, the date it last changed, and numbered sections. */
export function Legal({ title, lead, updated, children }: { title: string; lead: ReactNode; updated: string; children: ReactNode }) {
  return (
    <Container main narrow>
      <PageHeader title={title} lead={lead} />
      <article className={styles.doc}>
        <p className={styles.updated}>Last updated {updated}</p>
        {children}
      </article>
    </Container>
  );
}

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
