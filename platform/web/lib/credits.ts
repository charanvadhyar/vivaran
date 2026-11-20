/** Credits, plans and rewards. The rules live in SQL (platform/schema.sql), shared
    with the render server, so the site and the server always agree. */
import { many, one } from "./db";

export type Plans = {
  free: { monthly_credits: number; max_minutes: number; watermark: boolean; figures_per_month: number };
  pro: { monthly_credits: number; max_minutes: number; watermark: boolean; figures_per_month: number; price_inr: number; seo_per_month?: number };
  cost: { minutes_per_credit: number; voiced: number; silent_or_own_key: number };
  rewards: { creator_join: number; first_publish: number; subscribe: number; referral: number; views_1k: number; views_10k: number };
  packs: { credits: number; price_inr: number }[];
  downloads_per_day: number;
  youtube_channel_url: string;
  cost_model: { gnani_inr_per_1k_chars: number; server_inr_per_video_minute: number; inr_per_usd: number };
};

/** The line every channel description ends with (the render server writes the same one). */
export function creditLine(name: string, handle: string, url: string): string {
  return name.trim().toLowerCase() === "vivaran" ? `Made with Vivaran: ${url}` : `Made by ${name} (@${handle}) with Vivaran: ${url}`;
}

export async function getPlans(): Promise<Plans> {
  const row = await one<{ value: Plans }>(`select value from settings where key = 'plans'`);
  if (!row) throw new Error("the plans are missing from the settings table; run the schema");
  return row.value;
}

export type Account = {
  tier: "free" | "pro";
  isAdmin: boolean;
  proUntil: Date | null;
  monthly: number;
  bonus: number;
  total: number;
  creatorSince: Date | null;
  claimed: { creator_join: boolean; subscribe: boolean; first_publish: boolean };
  refillsOn: string;
};

export async function account(userId: string): Promise<Account> {
  await one(`select vivaran_ensure_monthly($1::uuid)`, [userId]);
  const row = await one<{ tier: "free" | "pro"; is_admin: boolean; pro_until: Date | null; creator_since: Date | null; monthly: string; bonus: string }>(
    `select vivaran_tier(u.id) as tier, u.is_admin, u.pro_until, u.creator_since, b.monthly, b.bonus
       from users u, vivaran_balance(u.id) b where u.id::text = $1`, [userId]);
  const kinds = await many<{ kind: string }>(
    `select distinct kind from credit_ledger where user_id::text = $1 and kind in ('creator_join', 'subscribe', 'first_publish')`, [userId]);
  const has = (k: string) => kinds.some((r) => r.kind === k);
  const now = new Date();
  const next = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1));
  const monthly = Number(row?.monthly ?? 0);
  const bonus = Number(row?.bonus ?? 0);
  return {
    tier: row?.tier ?? "free", isAdmin: !!row?.is_admin, proUntil: row?.pro_until ?? null, monthly, bonus, total: monthly + bonus,
    creatorSince: row?.creator_since ?? null,
    claimed: { creator_join: has("creator_join"), subscribe: has("subscribe"), first_publish: has("first_publish") },
    refillsOn: next.toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
  };
}

export type LedgerRow = { id: string; delta: string; kind: string; video_id: string | null; note: string | null; created_at: Date };

export const ledgerOf = (userId: string, limit = 30) =>
  many<LedgerRow>(`select id::text, delta::text, kind, video_id, note, created_at from credit_ledger
                    where user_id::text = $1 order by id desc limit $2`, [userId, limit]);

/** What a ledger row means, in words. */
export const KIND_LABELS: Record<string, string> = {
  monthly: "Monthly credits", monthly_topup: "Pro monthly credits", render: "Video rendered", render_refund: "Render failed: refunded",
  creator_join: "Joined the creator program", subscribe: "Subscribed to the channel", first_publish: "First video on the channel",
  referral: "A friend you invited published", views_1k: "Video passed 1,000 views", views_10k: "Video passed 10,000 views",
  admin_grant: "Added by Vivaran", pack: "Credit pack", admin_take: "Removed by Vivaran",
};

/** Give a one-time bonus; false if it was already given. */
async function reward(userId: string, kind: string, amount: number, note?: string): Promise<boolean> {
  if (amount <= 0) return false;
  const done = await one<{ id: string }>(
    `insert into credit_ledger (user_id, bucket, delta, kind, note) values ($1::uuid, 'bonus', $2, $3, $4)
     on conflict do nothing returning id::text`, [userId, amount, kind, note ?? null]);
  if (done) await logEvent(`reward_${kind}`, userId, null, { credits: amount });
  return !!done;
}

export async function joinCreatorProgram(userId: string): Promise<boolean> {
  const plans = await getPlans();
  await one(`update users set creator_since = coalesce(creator_since, now()) where id::text = $1 returning id`, [userId]);
  return reward(userId, "creator_join", plans.rewards.creator_join);
}

/** Trusted, once per account: we do not check YouTube for it. */
export async function claimSubscribe(userId: string): Promise<boolean> {
  const plans = await getPlans();
  return reward(userId, "subscribe", plans.rewards.subscribe);
}

export async function logEvent(type: string, userId: string | null, videoId: string | null, meta?: Record<string, unknown>) {
  await one(`insert into events (type, user_id, video_id, meta) values ($1, $2::uuid, $3, $4::jsonb) returning id`,
    [type, userId, videoId, meta ? JSON.stringify(meta) : null]);
}

/** Downloads left today for an account. */
export async function downloadsLeft(userId: string): Promise<number> {
  const plans = await getPlans();
  const row = await one<{ n: string }>(
    `select count(*)::text as n from events where type = 'download' and user_id::text = $1 and created_at > now() - interval '24 hours'`, [userId]);
  return Math.max(0, plans.downloads_per_day - Number(row?.n ?? 0));
}

/** After every sign-in: a brand-new account records its sign-up and who invited it. */
export async function onSignIn(userId: string, refHandle: string | null) {
  const fresh = await one<{ fresh: boolean }>(
    `select created_at > now() - interval '10 minutes' as fresh from users where id::text = $1`, [userId]);
  // Accounts named in ADMIN_HANDLES are flagged in the database too, for the render server and the accounts list.
  const handles = (process.env.ADMIN_HANDLES ?? "").split(",").map((h) => h.trim()).filter(Boolean);
  if (handles.length) {
    await one(`update users set is_admin = true where id::text = $1 and handle = any($2::text[]) and not is_admin returning id`,
      [userId, handles]);
  }
  if (!fresh?.fresh) {
    await one(`update users set last_seen_at = now() where id::text = $1 returning id`, [userId]);
    return;
  }
  const logged = await one(`select 1 from events where type = 'signup' and user_id::text = $1`, [userId]);
  if (!logged) await logEvent("signup", userId, null, refHandle ? { ref: refHandle } : undefined);
  if (refHandle) {
    await one(`update users set referred_by = (select id from users where handle = $2 and id::text <> $1)
                where id::text = $1 and referred_by is null returning id`, [userId, refHandle]);
  }
  await one(`update users set last_seen_at = now() where id::text = $1 returning id`, [userId]);
}
