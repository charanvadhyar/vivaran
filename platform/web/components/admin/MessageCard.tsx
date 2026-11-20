import type { Message } from "@/lib/contact";
import { GRIEVANCE_ACK_HOURS, GRIEVANCE_RESOLVE_DAYS, KINDS, LIMITS, isLimit, ticket } from "@/lib/contactKinds";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import styles from "./MessageCard.module.css";

const STATUSES = [["new", "New"], ["acknowledged", "Acknowledged"], ["resolved", "Resolved"], ["closed", "Closed (no action)"]] as const;
const when = (d: Date) => new Date(d).toLocaleString("en-IN", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata" });

/** One message from the contact page: who, what, how long it has waited, and its status. */
export function MessageCard({ m, update }: { m: Message; update: (f: FormData) => Promise<void> }) {
  const open = m.status === "new" || m.status === "acknowledged";
  const late = open && m.kind === "grievance" && m.age_hours > GRIEVANCE_RESOLVE_DAYS * 24;
  const unanswered = m.status === "new" && m.age_hours > GRIEVANCE_ACK_HOURS;
  const ref = ticket(m.id);
  const reply = `mailto:${m.email}?subject=${encodeURIComponent(`Re: ${ref}${m.topic ? ` · ${m.topic}` : ""}`)}`;
  const age = m.age_hours < 48 ? `${Math.round(m.age_hours)} h ago` : `${Math.round(m.age_hours / 24)} days ago`;
  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <div>
          <strong>{ref}</strong> · {m.kind === "other" ? "Other" : KINDS[m.kind].label.split(":")[0]}{m.topic ? ` · ${m.topic}` : ""}
          <div className={styles.muted}>
            {m.name} · <a href={reply}>{m.email}</a>{m.phone ? ` · ${m.phone}` : ""}{m.organisation ? ` · ${m.organisation}` : ""}
            {m.handle ? <> · <a href={`/u/${m.handle}`}>@{m.handle}</a></> : " · not signed in"} · {when(m.created_at)} ({age})
          </div>
        </div>
        <div className={styles.badges}>
          {late ? <Badge tone="negative">past {GRIEVANCE_RESOLVE_DAYS} days</Badge> : unanswered ? <Badge tone="negative">not acknowledged</Badge> : null}
          <Badge tone={m.kind === "grievance" ? "negative" : m.kind === "sales" ? "accent" : "neutral"}>{m.kind}</Badge>
          <Badge tone={open ? "neutral" : "positive"}>{m.status}</Badge>
        </div>
      </div>
      {m.limit_name ? (
        <p className={styles.muted}>
          Asks about: <strong>{isLimit(m.limit_name) ? LIMITS[m.limit_name] : m.limit_name}</strong> ·{" "}
          <a href={`/admin?tab=users&q=${encodeURIComponent(m.handle ?? m.email)}`}>open the account</a>
        </p>
      ) : null}
      {m.about_url ? <p className={styles.muted}>About: <a href={m.about_url} target="_blank" rel="noreferrer">{m.about_url}</a></p> : null}
      <p className={styles.message}>{m.message}</p>
      <form action={update} className={styles.form}>
        <input type="hidden" name="id" value={m.id} />
        <select name="status" defaultValue={m.status} aria-label="Status" className={styles.select}>
          {STATUSES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <input name="note" defaultValue={m.admin_note ?? ""} placeholder="Note for admins (not sent)" maxLength={1000} className={styles.input} aria-label="Note" />
        <Button type="submit" size="sm">Save</Button>
        <Button href={reply} size="sm" variant="ghost">Reply by email</Button>
      </form>
    </div>
  );
}
