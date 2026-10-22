import Link from "next/link";
import { BRAND } from "@/lib/brand";
import { WAITLIST } from "@/lib/mode";
import { Container } from "./Container";
import styles from "./Footer.module.css";

export function Footer() {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.inner}>
          <span>{BRAND.name} · {BRAND.native}</span>
          <nav className={styles.links} aria-label="Footer">
            <Link href="/terms">Creator terms</Link>
            {WAITLIST ? null : <Link href="/design">Design</Link>}
          </nav>
          <span>Videos are made by their creators with AI assistance. Check anything important against your textbook.</span>
        </div>
      </Container>
    </footer>
  );
}
