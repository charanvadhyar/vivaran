import Link from "next/link";
import { Legal, Section } from "@/components/legal/Legal";
import { BRAND } from "@/lib/brand";
import { CREATOR_PAY } from "@/lib/mode";

export const metadata = { title: "Terms of use", description: `The rules for watching and making videos on ${BRAND.name}.` };

const mail = <a href={`mailto:${BRAND.contact}`}>{BRAND.contact}</a>;

export default function Terms() {
  return (
    <Legal title="Terms of use" updated="20 November 2026"
      lead={`These terms are the agreement between you and ${BRAND.name} when you watch videos or make them here. Please read them; by using the site you accept them.`}>
      <Section title="The service">
        <p>{BRAND.name} turns an explanation, written by an AI assistant you connect, into an animated, narrated video. Watching public videos is free and needs no account. Making videos needs an account, which you create by signing in with Google. {BRAND.name} is run by {BRAND.owner} in India; write to {mail} with any question.</p>
      </Section>

      <Section title="Your account">
        <ul>
          <li>You must be 18 or older to create an account, and the details on it must be yours.</li>
          <li>Your connector address lets anyone who has it make videos in your account. Keep it secret, and tell us if it leaks so we can replace it.</li>
          <li>You are responsible for what is made through your account.</li>
          <li>Each account has a daily limit on narrated minutes, so the service stays available for everyone.</li>
        </ul>
      </Section>

      <Section title="Videos are study aids, not textbooks">
        <p>Videos are written with AI assistance and drawn and narrated automatically. They can contain mistakes, in the working, the numbers or the narration. Check anything important against your textbook, your notes or your teacher. {BRAND.name} is not responsible for marks lost, or any other result, from relying on a video.</p>
      </Section>

      <Section title="Your videos">
        <ul>
          <li>Videos you make are yours. Each is private until you publish it.</li>
          <li>When you publish a video, you allow {BRAND.name} to host it, show it on this site with your name, and let others share its link, for as long as it stays published. You can make it private again or delete it at any time.</li>
          <li>Before publishing, watch the video and check every step. You confirm that you have the right to publish what is in it.</li>
          {CREATOR_PAY ? <li>If you take part in the creator programme, the <Link href="/creator-terms">creator terms</Link> also apply.</li> : null}
        </ul>
      </Section>

      <Section title="What is not allowed">
        <ul>
          <li>Publishing content that is unlawful, hateful, sexual, violent, or that harasses or impersonates anyone.</li>
          <li>Copying someone else&apos;s copyrighted material into a video without the right to do so.</li>
          <li>Presenting a video as official exam or university material when it is not.</li>
          <li>Trying to get around limits, reach other people&apos;s accounts or videos, or disrupt the service.</li>
        </ul>
        <p>We may remove a video that breaks these rules or is clearly wrong, and suspend an account that keeps breaking them. Where we can, we will tell you why.</p>
      </Section>

      <Section title="Our part">
        <p>The software, design and name {BRAND.name} belong to us, even where the source code can be read on GitHub. We try to keep the site running and your videos safe, but we provide the service as it is, without promises that it will always be available, error-free or suitable for any particular purpose. To the extent the law allows, we are not liable for indirect losses, or for losses from relying on a video.</p>
        <p>We may change or stop parts of the service. If we close it, we will give account holders at least 30 days&apos; notice by email, so you can keep copies of your videos.</p>
      </Section>

      <Section title="Ending your account">
        <p>You can stop at any time and ask us to delete your account by writing to {mail}. We may close an account that seriously or repeatedly breaks these terms.</p>
      </Section>

      <Section title="Complaints and grievances">
        <p>
          To complain about a video (that it is wrong, uses your work or your likeness, or is unlawful), about your account, or about how
          we handle your data, use the <Link href="/contact?kind=grievance">contact form</Link> and choose “A grievance or complaint”,
          or write to our grievance officer, {BRAND.owner}, at {mail}. You get a reference number. We acknowledge a grievance within
          24 hours and aim to resolve it within 15 days. Every public video page also has a link to report it.
        </p>
      </Section>

      <Section title="Changes and law">
        <p>If we change these terms we will update the date at the top, and tell account holders by email about any important change; using the site after that means you accept the new terms. These terms are governed by the laws of India. How we handle your data is in our <Link href="/privacy">privacy policy</Link>.</p>
      </Section>
    </Legal>
  );
}
