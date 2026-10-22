import { Container } from "@/components/layout/Container";
import { ConnectBox } from "@/components/landing/ConnectBox";
import { DemoChat } from "@/components/landing/DemoChat";
import { Earn } from "@/components/landing/Earn";
import { Hero } from "@/components/landing/Hero";
import { Proof } from "@/components/landing/Proof";
import { SectionLabel } from "@/components/landing/SectionLabel";
import { WaitlistForm } from "@/components/landing/WaitlistForm";
import { Button } from "@/components/ui/Button";
import { VideoGrid } from "@/components/video/VideoGrid";
import { currentUser } from "@/lib/auth";
import { WAITLIST } from "@/lib/mode";
import { siteStats } from "@/lib/stats";
import { publicVideos } from "@/lib/videos";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";

/** The front door: what Vivaran is, shown working, then how to watch, make and earn. */
export default async function Home() {
  const [user, latest, stats] = await Promise.all([currentUser(), publicVideos({}, 8), siteStats()]);
  // The demo shows the richest recent video: voiced if there is one, with the most parts.
  const sample = [...latest].sort((a, b) => Number(b.voiced) - Number(a.voiced) || (b.outline?.length ?? 0) - (a.outline?.length ?? 0))[0] ?? null;
  const total = 4;
  // Before launch the numbers say what the thing is; a library of two demos is nothing to count.
  const proof = WAITLIST
    ? [
        { big: `${Math.round(stats.seconds / 60)} min`, label: "of worked examples to watch now, every step on screen" },
        { big: "3", label: "languages: English, and code-mixed Telugu and Hindi" },
        { big: "7", label: "kinds of picture: arrays, diagrams, tables, maths, code, plots, timelines" },
        { big: "0", label: "stock animations: every picture is drawn from the script's own objects" },
      ]
    : [
        { big: `<em>${stats.videos}</em>`, label: "public videos, each checked by its creator before publishing" },
        { big: `${Math.round(stats.seconds / 60)} min`, label: "of worked explanations to watch" },
        { big: "3", label: "languages: English, and code-mixed Telugu and Hindi" },
        { big: "7", label: "kinds of picture: arrays, diagrams, tables, maths, code, plots, timelines" },
      ];

  return (
    <Container main>
      <Hero demo={<DemoChat sample={sample} />} cta={WAITLIST ? <WaitlistForm compact source="hero" /> : undefined} />

      <section className={styles.section}>
        <SectionLabel index={1} total={total} text="Watch" />
        <div className={styles.head}>
          <h2>Explanations that show the working</h2>
          <p>Every video is built from a script that names each object and each change, so the picture moves exactly when the narration says it does. Nothing is a stock animation.</p>
        </div>
        <Proof items={proof} />
        {latest.length ? (
          <div className={styles.latest}>
            <VideoGrid videos={latest.slice(0, 4)} />
            <div className={styles.more}><Button href="/explore">{WAITLIST ? "Watch the demos" : "Explore by subject"}</Button></div>
          </div>
        ) : null}
      </section>

      <section className={styles.section}>
        <SectionLabel index={2} total={total} text="Make" />
        <div className={styles.head}>
          <h2>Connect your assistant in a minute</h2>
          <p>Vivaran is a connector, not another app to learn. Claude or ChatGPT writes the script to our teaching standard, checks it, shows you an outline and renders it.{WAITLIST ? " Connector addresses go out to the waitlist first." : ""}</p>
        </div>
        <ConnectBox signedIn={Boolean(user)} waitlist={WAITLIST} />
      </section>

      <section className={styles.section}>
        <SectionLabel index={3} total={total} text="Earn" />
        <div className={styles.head}>
          <h2>Free to make. Paid by views.</h2>
          <p>Creators keep their videos and are paid for the views they bring. The rates are introductory and written down in full.</p>
        </div>
        <Earn />
      </section>

      <section className={styles.section}>
        <SectionLabel index={4} total={total} text="Standard" />
        <div className={styles.head}>
          <h2>The exam standard</h2>
          <p>A video passes only if a student could redo the working in an exam from it alone: every term in a formula named, every number traced to where it came from, every decision said out loud. That rule is in the guide the assistant reads before it writes a single line.</p>
        </div>
        {WAITLIST ? (
          <div id="waitlist" className={styles.waitlist}>
            <h3>Be there when the doors open</h3>
            <p>We are finishing the hosting and the first creator terms. Leave an email and you get a connector address in the first batch.</p>
            <WaitlistForm source="footer" />
          </div>
        ) : (
          <div className={styles.cta}>
            <Button href={user ? "/dashboard" : "/login"} variant="primary" size="lg">{user ? "Make a video" : "Start for free"}</Button>
            <Button href="/explore" variant="ghost" size="lg">Watch first</Button>
          </div>
        )}
      </section>
    </Container>
  );
}
