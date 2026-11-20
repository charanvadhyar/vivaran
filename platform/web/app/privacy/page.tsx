import Link from "next/link";
import { Legal, Section } from "@/components/legal/Legal";
import { BRAND } from "@/lib/brand";

export const metadata = { title: "Privacy policy", description: `What ${BRAND.name} collects, why, who it is shared with, and how to have it deleted.` };

const mail = <a href={`mailto:${BRAND.contact}`}>{BRAND.contact}</a>;

export default function Privacy() {
  return (
    <Legal title="Privacy policy" updated="20 November 2026"
      lead={`${BRAND.name} turns explanations into step-by-step videos. This page says exactly what we collect to do that, why, and what you can ask us to do with it.`}>
      <Section title="Who we are">
        <p>{BRAND.name} ({BRAND.native}) is run by {BRAND.owner}, an individual in India. Write to {mail} about anything on this page.</p>
      </Section>

      <Section title="If you only watch videos">
        <p>You can watch public videos without an account. We do not ask who you are, and we keep no record of which videos you watch. Each video keeps a plain view count that is not linked to anyone.</p>
        <p>Our hosting providers keep ordinary server logs (such as IP address, browser and time of request) for a short time to keep the site running and secure.</p>
      </Section>

      <Section title="What we collect, and why">
        <ul>
          <li><strong>Your Google account details, when you sign in:</strong> your name, email address, profile picture and Google's account id. We use them to create your account, show your name on videos you publish, and contact you about your account. We never see your Google password.</li>
          <li><strong>Your connector address:</strong> a secret link we create for you, so your AI assistant can make videos in your account. Treat it like a password.</li>
          <li><strong>The videos you make:</strong> the scene script your assistant writes (narration, pictures, steps), the finished video, its thumbnail and its settings (language, voice, subject). They are private until you choose to publish them.</li>
          <li><strong>Waitlist sign-ups:</strong> your email, whether you want to watch, make videos or teach, and any note you leave. We use them only to tell you when the site opens and what is new.</li>
          <li><strong>A code for the network you signed up from:</strong> worked out from your IP address with a secret key, so that the address itself cannot be read back. We use it only to notice many accounts being made from one network in a day, to stop free credits being farmed.</li>
          <li><strong>Messages you send through the contact form:</strong> your name, email, the message, and anything else you choose to add (a phone number, your organisation, a link). We use them only to reply and to deal with your request, and keep them for as long as that takes and a year after, so that we can look back at a complaint if it comes up again. To limit spam we also keep a code worked out from your network address, from which the address itself cannot be read back.</li>
          <li><strong>A sign-in cookie</strong> that keeps you signed in, and a setting in your browser that remembers light or dark mode. We use no advertising or tracking cookies.</li>
        </ul>
      </Section>

      <Section title="Who else handles your data">
        <p>We do not sell your data or show you ads. We share it only with the services that run {BRAND.name}, and only what each needs:</p>
        <ul>
          <li><strong>Google</strong>, to sign you in.</li>
          <li><strong>Railway</strong>, which hosts this website, the server that draws videos, and the database and storage that keep accounts and videos (in Singapore).</li>
          <li><strong>Anthropic</strong> (the Claude API), when a figure is drawn for a video or a Pro creator asks us to write a video&apos;s YouTube title and description. It receives the video&apos;s title, narration and outline, and for the description your name and handle.</li>
          <li><strong>YouTube</strong>, when you send a video to the Vivaran channel and we approve it: the video, its title, description and tags, with your name and handle in the description.</li>
          <li><strong>Gnani AI</strong>, which turns each line of narration into speech and listens back to check it. It receives the narration text and the spoken audio, not your name or email.</li>
        </ul>
        <p>The AI assistant you connect, such as Claude or ChatGPT, is your own service. What you type to it is covered by that company&apos;s privacy policy, not this one; we receive only the scripts it sends to make your videos.</p>
        <p>These providers may process data outside India. We may also disclose data if the law requires it.</p>
      </Section>

      <Section title="What is public">
        <p>When you publish a video, anyone can see it with your name, your profile picture and your public page, which lists your published videos. Your email address and connector address are never shown. You can make a video private again or delete it from your dashboard at any time.</p>
      </Section>

      <Section title="How long we keep it">
        <ul>
          <li>Your account and videos, until you delete them or ask us to delete your account.</li>
          <li>Waitlist sign-ups, until the waitlist closes or you ask us to remove you.</li>
          <li>A video you delete is removed from your account at once.</li>
        </ul>
      </Section>

      <Section title="Your choices and rights">
        <p>You can ask us to show you the personal data we hold about you, correct it, or delete your account and everything in it. Write to {mail} from the email address on your account, and we will reply within 30 days. You can also remove {BRAND.name}&apos;s access in your Google account settings at any time.</p>
        <p>If you are unhappy with our reply, you may complain to the Data Protection Board of India.</p>
      </Section>

      <Section title="Age">
        <p>Anyone can watch. To create an account you must be 18 or older.</p>
      </Section>

      <Section title="Security">
        <p>Connections to {BRAND.name} are encrypted, connector addresses are long random secrets, and only the services above can reach the database. No system is perfectly secure: if your connector address leaks, tell us and we will issue a new one.</p>
      </Section>

      <Section title="Changes">
        <p>If we change this policy we will update the date at the top, and tell account holders by email about any important change. See also our <Link href="/terms">terms of use</Link>.</p>
      </Section>
    </Legal>
  );
}
