import { ContactForm } from "@/components/contact/ContactForm";
import { Container } from "@/components/layout/Container";
import { PageHeader } from "@/components/layout/PageHeader";
import { currentUser } from "@/lib/auth";
import { BRAND } from "@/lib/brand";
import { GRIEVANCE_ACK_HOURS, GRIEVANCE_RESOLVE_DAYS, LIMIT_TOPIC, isKind, isLimit } from "@/lib/contactKinds";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Contact",
  description: `Write to ${BRAND.name}: Pro and credit packs, ${BRAND.name} for a college or team, help with your account, or a grievance.`,
};

export default async function Contact({ searchParams }: { searchParams: Promise<{ kind?: string; about?: string; topic?: string; limit?: string }> }) {
  const sp = await searchParams;
  const kind = isKind(sp.kind ?? "") ? (sp.kind as "sales" | "grievance" | "support" | "other") : "sales";
  const about = /^https?:\/\/\S+$/.test(sp.about ?? "") ? sp.about! : "";
  // `?topic=limit&limit=downloads` opens the form at "A limit on my account".
  const topic = sp.topic === "limit" ? LIMIT_TOPIC : "";
  const limit = isLimit(sp.limit ?? "") ? (sp.limit as "held") : "";
  const user = await currentUser();
  const mail = <a href={`mailto:${BRAND.contact}`}>{BRAND.contact}</a>;
  return (
    <Container main>
      <PageHeader title="Contact us" lead="Pro and credit packs, Vivaran for your college or team, help with your account, or a complaint. Every message gets a reference number and a reply by email." />
      <div className={styles.grid}>
        <ContactForm kind={kind} topic={topic} limit={limit} signedIn={!!user} name={user?.name ?? ""} email={user?.email ?? ""} about={about} />
        <aside className={styles.side}>
          <section>
            <h2>Sales</h2>
            <p>Pro for yourself, credit packs, or accounts for a class, a department or a coaching centre. Tell us how many people and which subjects, and we will send a quote.</p>
          </section>
          <section>
            <h2>Limits on your account</h2>
            <p>Need longer videos, more downloads, more figures, or your free credits released? Choose “Help with my account or a video”, then “{LIMIT_TOPIC}”. Tell us what you are making; we reply with what we can do.</p>
          </section>
          <section>
            <h2>Grievances</h2>
            <p>
              For a video that is wrong, uses your work or is unlawful, or a problem with your account or your data, choose
              “A grievance or complaint”. We acknowledge it within {GRIEVANCE_ACK_HOURS} hours and aim to resolve it within {GRIEVANCE_RESOLVE_DAYS} days.
            </p>
            <p>Grievance officer: {BRAND.owner}, {mail}.</p>
          </section>
          <section>
            <h2>Email</h2>
            <p>If the form does not work for you, write to {mail}.</p>
          </section>
        </aside>
      </div>
    </Container>
  );
}
