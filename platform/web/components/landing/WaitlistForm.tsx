"use client";

import { useActionState } from "react";
import { joinWaitlist, type WaitlistResult } from "@/app/actions";
import { Button } from "../ui/Button";
import { Icon } from "../ui/Icon";
import { cx } from "../ui/cx";
import styles from "./WaitlistForm.module.css";

const ROLES = [
  { value: "creator", label: "I want to make videos" },
  { value: "teacher", label: "I teach" },
  { value: "learner", label: "I want to watch" },
];

/** Leave an email. `compact` is the hero version for students: one line, and
    we write when new videos for their exams go up. The full version is the
    creator waitlist: who they are and what they would explain. */
export function WaitlistForm({ compact = false, source = "hero" }: { compact?: boolean; source?: string }) {
  const [result, act, pending] = useActionState<WaitlistResult, FormData>(joinWaitlist, null);

  if (result?.ok) {
    return (
      <div className={cx(styles.done, compact && styles.compact)} role="status">
        <Icon name="check" className={styles.tick} size={20} />
        <div>
          <strong>{result.already ? "You are already on the list." : compact ? "You are on the list." : `You are number ${result.position} on the creator list.`}</strong>
          <span>{compact ? "We write when new videos for your exams go up. Nothing else." : "Connector addresses go out in batches. We write when yours is ready."}</span>
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
          {compact ? "Get new videos" : "Join the creator list"}
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
      <p className={styles.fine}>No spam, and you can tell us to forget you any time.</p>
    </form>
  );
}
