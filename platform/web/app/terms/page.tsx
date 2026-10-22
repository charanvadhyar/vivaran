import { WAITLIST } from "@/lib/mode";
import { Container } from "@/components/layout/Container";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { BRAND } from "@/lib/brand";
import styles from "./page.module.css";

export const metadata = { title: "Creator terms" };

export default function Terms() {
  return (
    <Container main narrow>
      <PageHeader title="How creators earn" lead={`${BRAND.name} is free to use. Videos you publish go on the ${BRAND.name} YouTube channel with your name on them, and you are paid for the views they get.`} />
      <div className={styles.stack}>
        <Card title="Making videos is free">
          <p>You pay nothing to make videos. A video renders silently first, with captions, so you can check every step. Voice is added when you publish it.</p>
        </Card>
        <Card title="You own your videos">
          <p>Each video stays yours. By publishing, you give {BRAND.name} an exclusive licence to show it on the {BRAND.name} YouTube channel for 12 months, and a non-exclusive licence to show it on this site. You can opt out of YouTube publication for any video, and you can download a copy at any time.</p>
        </Card>
        <Card title="Your name on every video">
          <p>Your name goes in the title or description, on the end card, and in the watermark in the corner. Your public page lists everything you have published.</p>
        </Card>
        <Card title="What you are paid" accent>
          <ul className={styles.list}>
            <li><strong>₹50 per 1,000 views</strong> on YouTube, counted 30 days after upload from YouTube's own figures, on videos where viewers watch at least 30% on average.</li>
            <li><strong>₹500 bonus</strong> when a video passes 10,000 views.</li>
            <li>Up to ₹1,000 per video. Paid monthly once your balance reaches ₹500.</li>
            <li>These are fixed amounts for reaching view milestones. There is no revenue share: what the channel earns from ads is not part of the deal.</li>
          </ul>
          <Alert tone="info">These are introductory rates and can change with 30 days' notice. Views that YouTube removes as invalid are not counted, and we may withhold payment on sudden, unexplained spikes.</Alert>
        </Card>
        <Card title="What we ask of you">
          <p>Watch your video through before publishing and check every step against the explanation you were given. Wrong working on the channel hurts every creator on it. We may take down a video that is wrong or that breaks YouTube's rules, and we will tell you why.</p>
        </Card>
      </div>
      <div style={{ marginTop: 32 }}><Button href={WAITLIST ? "/#waitlist" : "/dashboard"} variant="primary" size="lg">{WAITLIST ? "Join the waitlist" : "Start making videos"}</Button></div>
    </Container>
  );
}
