"use client";

import { useActionState } from "react";
import { joinWaitlist, type WaitlistResult } from "@/app/actions";
import { Button } from "../ui/Button";
import { Icon } from "../ui/Icon";
import { cx } from "../ui/cx";
import styles from "./WaitlistForm.module.css";

const ROLES = [
  { value: "learner", label: "I want to watch" },
  { value: "creator", label: "I want to make videos" },
  { value: "teacher", label: "I teach" },
];

/** The one thing a visitor can do before launch: leave an email.
    `compact` is the hero version (email and button on one line); the full version adds who they are and a note. */
export function WaitlistForm({ compact = false, source = "hero" }: { compact?: boolean; source?: string }) {
  const [result, act, pending] = useActionState<WaitlistResult, FormData>(joinWaitlist, null);

  if (result?.ok) {
    return (
      <div className={cx(styles.done, compact && styles.compact)} role="status">
        <Icon name="check" className={styles.tick} size={20} />
        <div>
          <strong>{result.already ? "You are already on the list." : `You are number ${result.position} on the list.`}</strong>
          <span>We open after Sunday. One email when the doors open, nothing else.</span>
        </div>
      </div>
    );
  }

  return (
    <form action={act} className={cx(styles.form, compact && styles.compact)}>
      <input type="hidden" name="source" value={source} />
      {/* Not shown to people; a bot that fills every field fills this one. */}
      <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden className={styles.trap} />
      <div className={styles.row}>
        <input
          type="email" name="email" required placeholder="you@college.edu" autoComplete="email" inputMode="email"
          className={styles.email} aria-label="Email address" aria-invalid={result && !result.ok ? true : undefined}
        />
        <Button type="submit" variant="primary" size={compact ? "lg" : "md"} loading={pending} icon={<Icon name="spark" />}>
          Join the waitlist
        </Button>
      </div>
      {compact ? (
        <input type="hidden" name="role" value="learner" />
      ) : (
        <>
          <fieldset className={styles.roles}>
            <legend>Who are you?</legend>
            {ROLES.map((role, i) => (
              <label key={role.value} className={styles.role}>
                <input type="radio" name="role" value={role.value} defaultChecked={i === 0} />
                <span>{role.label}</span>
              </label>
            ))}
          </fieldset>
          <textarea name="note" rows={2} maxLength={500} className={styles.note}
            placeholder="Optional: a topic you would make or want explained (“Dijkstra in Telugu”, “Bayes’ theorem with a worked example”)" />
        </>
      )}
      {result && !result.ok ? <p className={styles.error} role="alert">{result.error}</p> : null}
      <p className={styles.fine}>No spam. One email at launch, and you can tell us to forget you any time.</p>
    </form>
  );
}
