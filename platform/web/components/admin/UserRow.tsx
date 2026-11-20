import type { AdminUser } from "@/lib/admin";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import styles from "./UserRow.module.css";

const day = (d: Date | null) => (d ? new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "2-digit", timeZone: "Asia/Kolkata" }) : "never");

/** One account in the admin list, with its tools folded under it. */
export function UserRow({ u, grant, setPro, toggleAdmin, toggleHeld }:
  { u: AdminUser; grant: (f: FormData) => Promise<void>; setPro: (f: FormData) => Promise<void>; toggleAdmin: (f: FormData) => Promise<void>;
    toggleHeld: (f: FormData) => Promise<void> }) {
  return (
    <details className={styles.row}>
      <summary className={styles.summary}>
        <span className={styles.who}><strong>{u.name}</strong> <a href={`/u/${u.handle}`}>@{u.handle}</a> <span className={styles.email}>{u.email}</span></span>
        <span className={styles.badges}>
          <Badge tone={u.tier === "pro" ? "accent" : "neutral"}>{u.tier}</Badge>
          {u.creator_since ? <Badge tone="info">creator</Badge> : null}
          {u.is_admin ? <Badge tone="solid">admin</Badge> : null}
          {u.free_held ? <Badge tone="negative">on hold</Badge> : null}
        </span>
        <span className={styles.num}>{Number(u.credits).toString()} cr</span>
        <span className={styles.num}>{u.videos} videos · {u.minutes} min</span>
        <span className={styles.muted}>seen {day(u.last_seen_at)}</span>
      </summary>
      <div className={styles.tools}>
        <p className={styles.muted}>Joined {day(u.created_at)}{u.referred_by ? ` · invited by @${u.referred_by}` : ""}{u.pro_until ? ` · Pro until ${day(u.pro_until)}` : ""}{u.same_network ? ` · ${u.same_network} other account${u.same_network === 1 ? "" : "s"} signed up from the same network` : ""}</p>
        <form action={toggleHeld} className={styles.form}>
          <input type="hidden" name="user" value={u.id} />
          <input type="hidden" name="held" value={u.free_held ? "0" : "1"} />
          <Button type="submit" size="sm" variant={u.free_held ? "primary" : "ghost"}>{u.free_held ? "Release free credits" : "Hold free credits"}</Button>
          <span className={styles.muted}>{u.free_held ? "Made after too many sign-ups from one network: no monthly credits or joining and subscribing rewards until released." : "Stops this account's monthly credits and the joining and subscribing rewards."}</span>
        </form>
        <form action={grant} className={styles.form}>
          <input type="hidden" name="user" value={u.id} />
          <select name="kind" defaultValue="admin_grant" aria-label="What">
            <option value="admin_grant">Give credits</option>
            <option value="pack">Pack bought</option>
            <option value="admin_take">Take credits</option>
          </select>
          <input name="amount" type="number" min="0.25" step="0.25" max="1000" placeholder="Credits" required aria-label="Credits" />
          <input name="inr" type="number" min="0" step="1" placeholder="₹ received" aria-label="Rupees received" />
          <input name="note" placeholder="Note (shown in their history)" aria-label="Note" />
          <Button type="submit" size="sm">Apply</Button>
        </form>
        <form action={setPro} className={styles.form}>
          <input type="hidden" name="user" value={u.id} />
          <label className={styles.muted}>Pro until <input name="until" type="date" defaultValue={u.pro_until ? new Date(u.pro_until).toISOString().slice(0, 10) : ""} /></label>
          <input name="inr" type="number" min="0" step="1" placeholder="₹ received" aria-label="Rupees received" />
          <Button type="submit" size="sm">Set Pro</Button>
          <span className={styles.muted}>Leave the date empty to end Pro.</span>
        </form>
        {u.fixed_admin ? (
          <p className={styles.muted}>Admin through ADMIN_HANDLES on the server; remove the handle there to change it.</p>
        ) : (
          <form action={toggleAdmin} className={styles.form}>
            <input type="hidden" name="user" value={u.id} />
            <input type="hidden" name="admin" value={u.is_admin ? "0" : "1"} />
            <Button type="submit" size="sm" variant={u.is_admin ? "danger" : "ghost"}>{u.is_admin ? "Remove admin" : "Make admin"}</Button>
          </form>
        )}
      </div>
    </details>
  );
}
