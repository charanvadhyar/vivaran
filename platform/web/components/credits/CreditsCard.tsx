import type { Account, Plans } from "@/lib/credits";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import styles from "./CreditsCard.module.css";

const fmt = (n: number) => (Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0$/, ""));

/** The account's plan and credits, and what a video costs. */
export function CreditsCard({ account, plans, ownKey }: { account: Account; plans: Plans; ownKey: boolean }) {
  const plan = plans[account.tier];
  const c = plans.cost;
  return (
    <Card title="Your plan" aside={<Badge tone={account.tier === "pro" ? "accent" : "neutral"}>{account.isAdmin ? "Admin" : account.tier === "pro" ? "Pro" : "Free"}</Badge>}>
      <div className={styles.balance}>
        <span className={styles.big}>{fmt(account.total)}</span>
        <span className={styles.unit}>{account.total === 1 ? "video credit" : "video credits"}</span>
      </div>
      <p className={styles.split}>
        {fmt(account.monthly)} this month {account.held ? "(free credits on hold)" : `(refills to ${plan.monthly_credits} on ${account.refillsOn})`} · {fmt(account.bonus)} bonus (never expire)
      </p>
      <ul className={styles.rules}>
        <li>A video of up to {c.minutes_per_credit} minutes with Vivaran&apos;s voice costs {fmt(c.voiced)} credit.</li>
        <li>A silent video{ownKey ? ", or one voiced on your own Gnani key," : " (or one voiced on your own Gnani key)"} costs {fmt(c.silent_or_own_key)}.</li>
        <li>A failed render gives its credits back.</li>
        <li>Your plan allows videos of up to {plan.max_minutes} minutes{plan.watermark ? ", with the Vivaran mark" : ", without the Vivaran mark"}.</li>
      </ul>
      {account.held ? (
        <p className={styles.note}>
          Your free credits are on hold: several accounts were made from the same network today. Write to us and we will
          release them. Credits from a pack or Pro work as usual.
        </p>
      ) : null}
      {account.isAdmin ? (
        <p className={styles.note}>An admin account: your renders do not use credits, and Pro&apos;s limits apply.</p>
      ) : account.tier === "pro" && account.proUntil ? (
        <p className={styles.note}>Pro until {new Date(account.proUntil).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric", timeZone: "Asia/Kolkata" })}.</p>
      ) : (
        <div className={styles.pro}>
          <strong>Pro · ₹{plans.pro.price_inr}/month</strong>
          <span>{plans.pro.monthly_credits} credits a month, videos up to {plans.pro.max_minutes} minutes, no watermark on your copy, and the YouTube title and description written for you.</span>
          {plans.packs.length ? <span>Or a one-time pack: {plans.packs.map((p) => `${p.credits} credits for ₹${p.price_inr}`).join(" · ")}.</span> : null}
          <span className={styles.soon}>Online payment is coming. For now, write to us to get Pro or a pack.</span>
        </div>
      )}
    </Card>
  );
}
