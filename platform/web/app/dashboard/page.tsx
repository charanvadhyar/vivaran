import { redirect } from "next/navigation";
import { claimSubscribed, joinCreator, newConnectorAddress } from "../actions";
import { CreditsCard } from "@/components/credits/CreditsCard";
import { EarnCard } from "@/components/credits/EarnCard";
import { LedgerList } from "@/components/credits/LedgerList";
import { isAdmin } from "@/lib/admin";
import { account, getPlans, ledgerOf } from "@/lib/credits";
import { CREATOR_PAY } from "@/lib/mode";
import { Container } from "@/components/layout/Container";
import { PageHeader } from "@/components/layout/PageHeader";
import { Section } from "@/components/layout/Section";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Stat, StatGroup } from "@/components/ui/Stat";
import { ConnectorCard } from "@/components/video/ConnectorCard";
import { GnaniKeyCard } from "@/components/video/GnaniKeyCard";
import { HowTo } from "@/components/video/HowTo";
import { VideoGrid } from "@/components/video/VideoGrid";
import { currentUser } from "@/lib/auth";
import { gnaniKeyStatus } from "@/lib/users";
import { videosOf } from "@/lib/videos";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const metadata = { title: "My videos" };

export default async function Dashboard() {
  const user = await currentUser();
  if (!user) redirect("/login");
  const videos = await videosOf(user.id);
  const site = (process.env.SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
  const address = `${site}/u/${user.connector_token}/mcp`;
  const local = /^http:\/\/(localhost|127\.0\.0\.1)/.test(site);
  const shown = videos.filter((v) => v.is_public);
  const views = shown.reduce((sum, v) => sum + v.views, 0);
  const [keyStatus, acct, plans, ledger, admin] = await Promise.all([
    gnaniKeyStatus(user.id), account(user.id), getPlans(), ledgerOf(user.id), isAdmin(user)]);

  return (
    <Container main>
      <PageHeader title="My videos"
        lead={<>{user.name} · public page <a href={`/u/${user.handle}`} style={{ color: "var(--fg-link)" }}>/u/{user.handle}</a>
          {admin ? <> · <a href="/admin" style={{ color: "var(--fg-link)" }}>Admin</a></> : null}</>}
        aside={<StatGroup><Stat value={videos.length} label="made" /><Stat value={shown.length} label="public" /><Stat value={views} label="views" /></StatGroup>} />
      <div className={styles.split}>
        <ConnectorCard address={address} local={local} regenerate={newConnectorAddress} />
        <HowTo />
      </div>
      <Section title="Credits">
        <div className={styles.split}>
          <CreditsCard account={acct} plans={plans} ownKey={keyStatus.set} />
          <EarnCard account={acct} plans={plans} referralLink={`${site}/r/${user.handle}`} join={joinCreator}
            claimSubscribed={claimSubscribed} termsHref={CREATOR_PAY ? "/creator-terms" : null} />
        </div>
      </Section>
      <Section title="Your own voice key">
        <GnaniKeyCard initial={keyStatus} />
      </Section>
      <Section title="Credit history">
        <LedgerList rows={ledger} />
      </Section>
      <Section title="Videos">
        {videos.length ? <VideoGrid videos={videos} own /> : (
          <EmptyState title="Nothing yet" text="Videos you make through the connector are saved here, private until you publish them." />
        )}
      </Section>
    </Container>
  );
}
