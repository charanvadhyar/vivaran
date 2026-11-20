import Link from "next/link";
import { BRAND } from "@/lib/brand";
import { CREATOR_PAY, WAITLIST } from "@/lib/mode";
import { Container } from "./Container";
import styles from "./Footer.module.css";

export function Footer() {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.inner}>
          <span>{BRAND.name} · {BRAND.native}</span>
          <nav className={styles.links} aria-label="Footer">
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
            <Link href="/contact">Contact</Link>
            <Link href="/contact?kind=grievance">Grievances</Link>
            {CREATOR_PAY ? <Link href="/creator-terms">Creator terms</Link> : null}
            {WAITLIST ? null : <Link href="/design">Design</Link>}
          </nav>
          <span>Videos are made by their creators with AI assistance. Check anything important against your textbook.</span>
        </div>
      </Container>
    </footer>
  );
}
