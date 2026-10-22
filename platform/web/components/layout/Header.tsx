import Link from "next/link";
import { BRAND } from "@/lib/brand";
import { WAITLIST } from "@/lib/mode";
import type { User } from "@/lib/users";
import { Avatar } from "../ui/Avatar";
import { Button } from "../ui/Button";
import { ThemeToggle } from "../ui/ThemeToggle";
import { Container } from "./Container";
import { SearchBar } from "./SearchBar";
import styles from "./Header.module.css";

/** The top bar: brand, search, and the account. */
export function Header({ user, signOut }: { user: User | null; signOut: () => Promise<void> }) {
  return (
    <header className={styles.header}>
      <Container>
        <div className={styles.inner}>
          <Link href="/" className={styles.brand} aria-label={`${BRAND.name} home`}>
            <span className={styles.mark} aria-hidden />
            <span>{BRAND.name}</span>
            <span className={styles.native} aria-hidden>{BRAND.native}</span>
          </Link>
          <div className={styles.search}><SearchBar /></div>
          <nav className={styles.nav} aria-label="Account">
            <Link href="/explore" className={`${styles.navLink} ${styles.wide}`}>Explore</Link>
            <ThemeToggle />
            {user ? (
              <>
                <Link href="/dashboard" className={styles.navLink}><Avatar name={user.name} src={user.image} size={24} />&nbsp;My videos</Link>
                <form action={signOut} className={styles.wide}><Button variant="ghost" type="submit">Sign out</Button></form>
              </>
            ) : WAITLIST ? (
              <Button href="/#waitlist" variant="primary">Join the waitlist</Button>
            ) : (
              <Button href="/login" variant="primary">Sign in</Button>
            )}
          </nav>
        </div>
      </Container>
    </header>
  );
}
