import Link from "next/link";
import type { Account, Plans } from "@/lib/credits";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { CopyField } from "../ui/CopyField";
import styles from "./EarnCard.module.css";

/** Ways to earn more video credits through the creator program. */
export function EarnCard({ account, plans, referralLink, join, claimSubscribed, termsHref }:
  { account: Account; plans: Plans; referralLink: string; join: () => Promise<void>; claimSubscribed: () => Promise<void>; termsHref: string | null }) {
  const r = plans.rewards;
  const done = <Badge tone="positive">Done</Badge>;
  return (
    <Card title="Earn more credits" subtitle="Bonus credits never expire.">
      <ol className={styles.list}>
        <li className={styles.item}>
          <div>
            <strong>Join the creator program · +{r.creator_join}</strong>
            <p>Publish your videos on the Vivaran YouTube channel, with your name on them.{termsHref ? <> See the <Link href={termsHref}>creator terms</Link>.</> : null}</p>
          </div>
          {account.claimed.creator_join ? done : <form action={join}><Button type="submit" variant="primary">Join</Button></form>}
        </li>
        <li className={styles.item}>
          <div>
            <strong>Subscribe to the Vivaran channel · +{r.subscribe}</strong>
            <p>{plans.youtube_channel_url ? <a href={plans.youtube_channel_url} target="_blank" rel="noreferrer">Open the channel</a> : "The channel link is coming soon"}, subscribe, then claim. Once per account.</p>
          </div>
          {account.claimed.subscribe ? done : (
            <form action={claimSubscribed}><Button type="submit" disabled={!plans.youtube_channel_url}>I&apos;ve subscribed</Button></form>
          )}
        </li>
        <li className={styles.item}>
          <div>
            <strong>Your first video on the channel · +{r.first_publish}</strong>
            <p>Make a video public, then send it to the channel from its page.</p>
          </div>
          {account.claimed.first_publish ? done : <Badge>Waiting</Badge>}
        </li>
        <li className={styles.item}>
          <div>
            <strong>Invite friends · +{r.referral} each</strong>
            <p>When a friend signs up with your link and their first video goes on the channel.</p>
            <CopyField value={referralLink} label="Your invitation link" />
          </div>
        </li>
        <li className={styles.item}>
          <div>
            <strong>Views on the channel · +{r.views_1k} at 1,000 · +{r.views_10k} at 10,000</strong>
            <p>For each of your videos, counted from YouTube&apos;s own figures.</p>
          </div>
        </li>
      </ol>
    </Card>
  );
}
