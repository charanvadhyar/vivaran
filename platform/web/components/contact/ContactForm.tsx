"use client";

import Link from "next/link";
import { useActionState, useState } from "react";
import { sendContact, type ContactResult } from "@/app/actions";
import { GRIEVANCE_ACK_HOURS, GRIEVANCE_RESOLVE_DAYS, KINDS, LIMITS, LIMIT_TOPIC, type Kind, type LimitName } from "@/lib/contactKinds";
import { Button } from "../ui/Button";
import { Icon } from "../ui/Icon";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import styles from "./ContactForm.module.css";

const KIND_OPTIONS = (Object.keys(KINDS) as Kind[]).map((k) => ({ value: k, label: KINDS[k].label }));

/** Write to us: sales, a grievance, help, or anything else. */
export function ContactForm({ kind: initial, topic: initialTopic = "", limit = "", signedIn = false, name = "", email = "", about = "" }:
  { kind: Kind; topic?: string; limit?: LimitName | ""; signedIn?: boolean; name?: string; email?: string; about?: string }) {
  const [result, act, pending] = useActionState<ContactResult, FormData>(sendContact, null);
  const [kind, setKind] = useState<Kind>(initial);
  const topics: readonly string[] = KINDS[kind].topics;
  const [topic, setTopic] = useState(topics.includes(initialTopic) ? initialTopic : "");

  if (result?.ok) {
    return (
      <div className={styles.done} role="status">
        <Icon name="check" className={styles.tick} size={20} />
        <div>
          <strong>Sent. Your reference is {result.ticket}.</strong>
          <span>
            {result.kind === "grievance"
              ? `We acknowledge grievances within ${GRIEVANCE_ACK_HOURS} hours and aim to resolve them within ${GRIEVANCE_RESOLVE_DAYS} days. We reply to the email you gave; quote ${result.ticket} if you write again.`
              : `We reply to the email you gave, usually within two working days. Quote ${result.ticket} if you write again.`}
          </span>
        </div>
      </div>
    );
  }

  return (
    <form action={act} className={styles.form}>
      {/* Not shown to people; a bot that fills every field fills this one. */}
      <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden className={styles.trap} />
      <label className={styles.label} htmlFor="contact-kind">What is it about?</label>
      <Select id="contact-kind" name="kind" options={KIND_OPTIONS} value={kind} onChange={(e) => { setKind(e.target.value as Kind); setTopic(""); }} />
      {topics.length ? (
        <>
          <label className={styles.label} htmlFor="contact-topic">Topic</label>
          <Select id="contact-topic" name="topic" required placeholder="Choose one…" value={topic} onChange={(e) => setTopic(e.target.value)}
            options={topics.map((t) => ({ value: t, label: t }))} />
        </>
      ) : null}
      {topic === LIMIT_TOPIC ? (
        <>
          <label className={styles.label} htmlFor="contact-limit">Which limit?</label>
          <Select id="contact-limit" name="limit" required placeholder="Choose one…" defaultValue={limit}
            options={(Object.keys(LIMITS) as LimitName[]).map((l) => ({ value: l, label: LIMITS[l] }))} />
          <p className={styles.fine}>
            {signedIn
              ? "We look at your account, and reply with what we can do. Say what you are making and how much more you need."
              : "Sign in first if you can, so we know which account it is; otherwise use the email address on your account."}
          </p>
        </>
      ) : null}
      <div className={styles.pair}>
        <Input label="Your name" name="name" required maxLength={100} defaultValue={name} autoComplete="name" />
        <Input label="Email" name="email" type="email" required maxLength={254} defaultValue={email} autoComplete="email"
          hint="We reply here." />
      </div>
      {kind === "sales" ? (
        <div className={styles.pair}>
          <Input label="College, centre or company (optional)" name="organisation" maxLength={120} autoComplete="organization" />
          <Input label="Phone (optional)" name="phone" type="tel" maxLength={20} autoComplete="tel" inputMode="tel" />
        </div>
      ) : null}
      {kind === "grievance" ? (
        <Input label="Link to the video or page (if there is one)" name="about_url" type="url" maxLength={500} defaultValue={about}
          placeholder="https://vivaran.tech/v/…" />
      ) : null}
      <label className={styles.label} htmlFor="contact-message">Message</label>
      <textarea id="contact-message" name="message" required minLength={20} maxLength={5000} rows={7} className={styles.message}
        placeholder={topic === LIMIT_TOPIC ? "What you are making, and how much more you need (for example: a 15-minute video, or 20 downloads for a class)."
          : kind === "sales" ? "How many students or creators, which subjects, and what you have in mind."
          : kind === "grievance" ? "What is wrong, and what you would like us to do. For a video, say which step or time."
          : "What happened, and what you expected."} />
      {result && !result.ok ? <p className={styles.error} role="alert">{result.error}</p> : null}
      <div><Button type="submit" variant="primary" loading={pending} icon={<Icon name="arrowRight" />}>Send</Button></div>
      <p className={styles.fine}>We use what you send only to reply and to deal with your request. See the <Link href="/privacy">privacy policy</Link>.</p>
    </form>
  );
}
