/** Admin: who is an admin, the analytics, and the account tools. */
import { many, one } from "./db";
import type { User } from "./users";

/** An admin is marked in the database, or named by handle in ADMIN_HANDLES (comma-separated). */
export async function isAdmin(user: User | null): Promise<boolean> {
  if (!user) return false;
  const handles = (process.env.ADMIN_HANDLES ?? "").split(",").map((h) => h.trim()).filter(Boolean);
  if (handles.includes(user.handle)) return true;
  const row = await one<{ is_admin: boolean }>(`select is_admin from users where id::text = $1`, [user.id]);
  return !!row?.is_admin;
}

export type Day = { day: string; [series: string]: number | string };

const num = (v: unknown) => Number(v ?? 0);

export async function overview(days: number) {
  const since = `now() - make_interval(days => ${Math.max(1, Math.min(365, Math.floor(days)))})`;
  const k = await one<Record<string, unknown>>(`
    with p as (select (value->'cost_model'->>'gnani_inr_per_1k_chars')::numeric as gnani,
                      (value->'cost_model'->>'server_inr_per_video_minute')::numeric as server
                 from settings where key = 'plans')
    select
      (select count(*) from users) as users_total,
      (select count(*) from users where created_at > ${since}) as users_new,
      (select count(distinct user_id) from videos where created_at > ${since}) as users_rendering,
      (select count(*) from users where last_seen_at > ${since}) as users_seen,
      (select count(*) from users where creator_since is not null) as creators,
      (select count(*) from users where pro_until > now()) as pro,
      (select count(*) from videos where status = 'done' and created_at > ${since}) as videos_done,
      (select count(*) from videos where status = 'failed' and created_at > ${since}) as videos_failed,
      (select coalesce(sum(seconds), 0) / 60.0 from videos where status = 'done' and created_at > ${since}) as minutes,
      (select coalesce(sum(characters), 0) from videos where status = 'done' and created_at > ${since}) as characters,
      (select coalesce(avg(extract(epoch from finished_at - created_at) / nullif(seconds / 60.0, 0)), 0)
         from videos where status = 'done' and voiced and finished_at > created_at and created_at > ${since}) as render_s_per_min,
      (select coalesce(sum(v.characters) filter (where v.voiced and not coalesce((e.meta->>'own_key')::boolean, false)), 0) / 1000.0 * max(p.gnani)
            + coalesce(sum(v.seconds), 0) / 60.0 * max(p.server)
         from videos v left join events e on e.video_id = v.id and e.type = 'render_done' cross join p
        where v.status = 'done' and v.created_at > ${since}) as cost_inr,
      (select coalesce(sum(delta), 0) from credit_ledger where delta > 0 and kind not in ('render_refund') and created_at > ${since}) as credits_given,
      (select coalesce(-sum(delta), 0) from credit_ledger where kind in ('render', 'render_refund') and created_at > ${since}) as credits_spent,
      (select coalesce(sum(amount_inr), 0) from credit_ledger where created_at > ${since}) as revenue_inr,
      (select count(*) from users where pro_until > now()) * coalesce((select (value->'pro'->>'price_inr')::numeric from settings where key = 'plans'), 0) as mrr_inr,
      (select count(*) from events where type = 'view' and created_at > ${since}) as site_views,
      (select coalesce(sum(views), 0) from videos) as site_views_total,
      (select count(*) from videos where is_public and status = 'done') as public_videos,
      (select count(*) from events where type = 'download' and created_at > ${since}) as downloads,
      (select count(*) from youtube_uploads where status = 'published') as yt_published,
      (select count(*) from youtube_uploads where status = 'pending') as yt_pending,
      (select coalesce(sum(yt_views), 0) from youtube_uploads) as yt_views,
      (select value from settings where key = 'youtube_channel') as yt_channel,
      (select count(*) from events where type = 'figure' and created_at > ${since}) as figures,
      (select count(*) from events where type = 'seo_ai' and created_at > ${since}) as seo_ai
  `);
  const kpi = Object.fromEntries(Object.entries(k ?? {}).map(([key, v]) => [key, key === "yt_channel" ? v : num(v)])) as Record<string, number> & { yt_channel: { subscribers?: number; views?: number; title?: string } | null };

  const daily = await many<Record<string, unknown>>(`
    with d as (select generate_series(date_trunc('day', ${since}), date_trunc('day', now()), interval '1 day')::date as day),
    p as (select value from settings where key = 'plans')
    select to_char(d.day, 'YYYY-MM-DD') as day,
      (select count(*) from users u where u.created_at::date = d.day) as signups,
      (select count(*) from videos v where v.status = 'done' and v.created_at::date = d.day) as renders,
      (select count(*) from videos v where v.status = 'failed' and v.created_at::date = d.day) as failures,
      (select coalesce(sum(v.seconds), 0) / 60.0 from videos v where v.status = 'done' and v.created_at::date = d.day) as minutes,
      (select coalesce(sum(v.characters), 0) / 1000.0 * (p.value->'cost_model'->>'gnani_inr_per_1k_chars')::numeric
            + coalesce(sum(v.seconds), 0) / 60.0 * (p.value->'cost_model'->>'server_inr_per_video_minute')::numeric
         from videos v where v.status = 'done' and v.created_at::date = d.day) as cost,
      (select count(*) from events e where e.type = 'view' and e.created_at::date = d.day) as views,
      (select count(*) from events e where e.type = 'download' and e.created_at::date = d.day) as downloads,
      (select coalesce(-sum(delta), 0) from credit_ledger c where c.kind in ('render', 'render_refund') and c.created_at::date = d.day) as credits_spent,
      (select count(distinct v.user_id) from videos v where v.created_at::date = d.day) as active
    from d, p order by d.day`);
  const series = daily.map((r) => Object.fromEntries(Object.entries(r).map(([key, v]) => [key, key === "day" ? v : num(v)]))) as Day[];

  const by = async (column: string) => many<{ key: string; videos: string; minutes: string }>(`
    select coalesce(${column}::text, '(none)') as key, count(*)::text as videos, round(coalesce(sum(seconds), 0)::numeric / 60, 1)::text as minutes
      from videos where status = 'done' and created_at > ${since} group by 1 order by sum(seconds) desc nulls last`);
  const [byLanguage, bySubject, byVoice] = await Promise.all([by("language"), by("subject"), by("case when voiced then 'voiced' else 'silent' end")]);

  const funnel = await one<Record<string, string>>(`
    select count(*)::text as signed_up,
      count(*) filter (where last_seen_at is not null or exists (select 1 from videos v where v.user_id = u.id))::text as connected,
      count(*) filter (where exists (select 1 from videos v where v.user_id = u.id and v.status = 'done'))::text as rendered,
      count(*) filter (where exists (select 1 from videos v where v.user_id = u.id and v.is_public))::text as published,
      count(*) filter (where exists (select 1 from youtube_uploads y where y.user_id = u.id))::text as submitted,
      count(*) filter (where exists (select 1 from youtube_uploads y where y.user_id = u.id and y.status = 'published'))::text as on_youtube
    from users u where u.created_at > ${since}`);

  const topVideos = await many<{ id: string; title: string; handle: string; views: number; yt_views: string | null; minutes: string }>(`
    select v.id, v.title, u.handle, v.views, y.yt_views::text, round((v.seconds / 60)::numeric, 1)::text as minutes
      from videos v join users u on u.id = v.user_id left join youtube_uploads y on y.video_id = v.id
     where v.status = 'done' and v.is_public order by v.views + coalesce(y.yt_views, 0) desc limit 10`);
  const topCreators = await many<{ handle: string; name: string; videos: string; minutes: string; views: string }>(`
    select u.handle, u.name, count(v.*)::text as videos, round(coalesce(sum(v.seconds), 0)::numeric / 60, 1)::text as minutes,
           coalesce(sum(v.views), 0)::text as views
      from users u join videos v on v.user_id = u.id and v.status = 'done'
     group by u.id order by sum(v.seconds) desc limit 10`);
  const failures = await many<{ id: string; title: string; handle: string; error: string; created_at: Date }>(`
    select v.id, v.title, u.handle, left(coalesce(v.error, ''), 160) as error, v.created_at
      from videos v join users u on u.id = v.user_id where v.status = 'failed' and v.created_at > ${since}
     order by v.created_at desc limit 10`);
  const rewards = await many<{ kind: string; times: string; credits: string }>(`
    select kind, count(*)::text as times, sum(delta)::text as credits from credit_ledger
     where delta > 0 and kind not in ('render_refund', 'monthly', 'monthly_topup') and created_at > ${since}
     group by kind order by sum(delta) desc`);

  return { kpi, series, byLanguage, bySubject, byVoice, funnel: funnel ?? {}, topVideos, topCreators, failures, rewards };
}

export type AdminUser = {
  id: string; name: string; handle: string; email: string; tier: string; pro_until: Date | null; is_admin: boolean;
  creator_since: Date | null; credits: string; videos: string; minutes: string; last_seen_at: Date | null; created_at: Date;
  referred_by: string | null;
};

export function users(q: string, limit = 100) {
  const like = `%${q.replace(/[\\%_]/g, "\\$&")}%`;
  return many<AdminUser>(`
    select u.id::text, u.name, u.handle, u.email, vivaran_tier(u.id) as tier, u.pro_until, u.is_admin, u.creator_since,
           (b.monthly + b.bonus)::text as credits,
           (select count(*) from videos v where v.user_id = u.id and v.status = 'done')::text as videos,
           (select round(coalesce(sum(seconds), 0)::numeric / 60, 1) from videos v where v.user_id = u.id and v.status = 'done')::text as minutes,
           greatest(u.last_seen_at, (select max(created_at) from videos v where v.user_id = u.id)) as last_seen_at, u.created_at,
           (select handle from users r where r.id = u.referred_by) as referred_by
      from users u, vivaran_balance(u.id) b
     where $1 = '' or u.name ilike $2 or u.handle ilike $2 or u.email ilike $2
     order by u.created_at desc limit $3`, [q, like, limit]);
}

export async function grant(adminId: string, userId: string, amount: number, kind: "admin_grant" | "pack" | "admin_take", note: string, amountInr: number | null) {
  await one(`insert into credit_ledger (user_id, bucket, delta, kind, note, amount_inr, granted_by)
             values ($1::uuid, 'bonus', $2, $3, $4, $5, $6::uuid) returning id`,
    [userId, kind === "admin_take" ? -Math.abs(amount) : Math.abs(amount), kind, note || null, amountInr, adminId]);
}

export async function setPro(adminId: string, userId: string, until: Date | null, amountInr: number | null) {
  await one(`update users set pro_until = $2 where id::text = $1 returning id`, [userId, until]);
  // Record the payment (and the change) in the ledger, with no credits attached.
  await one(`insert into credit_ledger (user_id, bucket, delta, kind, note, amount_inr, granted_by)
             values ($1::uuid, 'bonus', 0, 'pro_change', $2, $3, $4::uuid) returning id`,
    [userId, until ? `Pro until ${until.toISOString().slice(0, 10)}` : "Pro ended", amountInr, adminId]);
  if (until && until > new Date()) await one(`select vivaran_ensure_monthly($1::uuid)`, [userId]);
}

export async function setAdmin(userId: string, admin: boolean) {
  await one(`update users set is_admin = $2 where id::text = $1 returning id`, [userId, admin]);
}

export type Upload = {
  id: string; video_id: string; title: string; description: string; tags: string[]; seo_by_ai: boolean; status: string;
  review_note: string | null; youtube_id: string | null; error: string | null; yt_views: string; created_at: Date;
  handle: string; name: string; video_title: string; minutes: string; tier: string;
};

export const uploads = (status: string[]) => many<Upload>(`
  select y.id::text, y.video_id, y.title, y.description, y.tags, y.seo_by_ai, y.status, y.review_note, y.youtube_id, y.error,
         y.yt_views::text, y.created_at, u.handle, u.name, v.title as video_title, round((v.seconds / 60)::numeric, 1)::text as minutes,
         vivaran_tier(u.id) as tier
    from youtube_uploads y join users u on u.id = y.user_id join videos v on v.id = y.video_id
   where y.status = any($1) order by y.created_at desc limit 100`, [status]);
