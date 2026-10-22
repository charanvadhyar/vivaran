import type { ReactNode } from "react";
import { Button } from "../ui/Button";
import { Icon } from "../ui/Icon";
import styles from "./Hero.module.css";

/** The opening of the landing page: the promise on the left, the product working on the right. */
export function Hero({ demo, cta }: { demo: ReactNode; cta?: ReactNode }) {
  return (
    <section className={styles.hero}>
      <div className={styles.copy}>
        <h1>Ask for a video.<br />Get every step, <span className={styles.mark}>shown</span>.</h1>
        <p className={styles.lead}>
          Tell Claude or ChatGPT what you need to understand. Vivaran turns the explanation into an animated video that shows
          where every number comes from, narrated in English, Telugu or Hindi, so you can redo it in the exam.
        </p>
        {cta ?? (
          <div className={styles.actions}>
            <Button href="/login" variant="primary" size="lg" icon={<Icon name="spark" />}>Make a video, free</Button>
            <Button href="/explore" variant="ghost" size="lg">Watch what others made</Button>
          </div>
        )}
        <p className={styles.apps}>Works inside <strong>Claude</strong> and <strong>ChatGPT</strong>. Nothing to install.</p>
      </div>
      {demo}
    </section>
  );
}
