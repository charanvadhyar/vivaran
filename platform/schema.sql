-- CEVG platform, version 1. Safe to run again: it only creates what is missing.

create table if not exists users (
  id              uuid primary key default gen_random_uuid(),
  google_sub      text unique not null,          -- Google's id for the account
  email           text not null,
  name            text not null,
  image           text,
  handle          text unique not null,          -- shown on public pages
  connector_token text unique not null,          -- the secret part of the user's MCP address
  created_at      timestamptz not null default now()
);

create table if not exists videos (
  id           text primary key,
  user_id      uuid not null references users(id) on delete cascade,
  title        text not null,
  language     text not null,
  speaker      text,
  voiced       boolean not null,
  captions     boolean not null default false,
  status       text not null check (status in ('queued', 'running', 'done', 'failed')),
  progress     text not null default '',
  error        text,
  seconds      real,
  steps        integer,
  characters   integer not null default 0,       -- characters sent to the voice service
  is_public    boolean not null default false,
  script       jsonb not null,
  outline      jsonb,
  views        integer not null default 0,
  created_at   timestamptz not null default now(),
  finished_at  timestamptz,
  published_at timestamptz
);

create index if not exists videos_by_user on videos (user_id, created_at desc);
create index if not exists videos_public on videos (published_at desc) where is_public and status = 'done';

-- Added with the subject pages: what a video is about.
alter table videos add column if not exists subject text;
create index if not exists videos_public_subject on videos (subject, published_at desc) where is_public and status = 'done';

-- Before launch: people who asked to be told when the doors open.
create table if not exists waitlist (
  id         bigserial primary key,
  email      text not null,
  role       text not null default 'learner' check (role in ('learner', 'creator', 'teacher')),
  note       text,                                 -- what they would make or want to watch
  source     text,                                 -- where the sign-up came from (hero, footer, ...)
  created_at timestamptz not null default now()
);
create unique index if not exists waitlist_email on waitlist (lower(email));

-- ---------------------------------------------------------------- accounts and credits (Nov 2026)

create extension if not exists pgcrypto;

-- Bring-your-own Gnani key (pgp_sym_encrypt with CEVG_KEY_SECRET); added by hand before, recorded here.
alter table users add column if not exists gnani_key_enc    bytea;
alter table users add column if not exists gnani_key_set_at timestamptz;

alter table users add column if not exists tier          text not null default 'free';
alter table users add column if not exists pro_until     timestamptz;          -- Pro ends after this (null: no Pro)
alter table users add column if not exists is_admin      boolean not null default false;
alter table users add column if not exists creator_since timestamptz;          -- joined the creator program
alter table users add column if not exists referred_by   uuid references users(id) on delete set null;
alter table users add column if not exists last_seen_at  timestamptz;          -- last use of the site or connector

-- Plans, prices and rewards, editable from the admin page. Both the site and the
-- render server read them from here, so there is one source of truth.
create table if not exists settings (
  key        text primary key,
  value      jsonb not null,
  updated_at timestamptz not null default now()
);
insert into settings (key, value) values ('plans', '{
  "free": {"monthly_credits": 3, "max_minutes": 10, "watermark": true,  "figures_per_month": 5},
  "pro":  {"monthly_credits": 6, "max_minutes": 20, "watermark": false, "figures_per_month": 60, "price_inr": 299},
  "cost": {"minutes_per_credit": 10, "voiced": 1, "silent_or_own_key": 0.25},
  "rewards": {"creator_join": 2, "first_publish": 1, "subscribe": 1, "referral": 1, "views_1k": 2, "views_10k": 5},
  "packs": [{"credits": 3, "price_inr": 199}, {"credits": 7, "price_inr": 449}, {"credits": 15, "price_inr": 799}],
  "downloads_per_day": 10,
  "youtube_channel_url": "",
  "cost_model": {"gnani_inr_per_1k_chars": 2.65, "server_inr_per_video_minute": 0.76, "inr_per_usd": 93.3}
}'::jsonb) on conflict (key) do nothing;

-- Every change to a balance, as a row. Credits are counted in videos (one credit is
-- one video of up to `minutes_per_credit` minutes). The monthly bucket is refilled
-- each calendar month and does not pile up; the bonus bucket never expires.
create table if not exists credit_ledger (
  id         bigserial primary key,
  user_id    uuid not null references users(id) on delete cascade,
  bucket     text not null check (bucket in ('monthly', 'bonus')),
  period     text,                               -- 'YYYY-MM' for the monthly bucket
  delta      numeric(10, 2) not null,
  kind       text not null,                      -- monthly, creator_join, subscribe, render_hold, ...
  video_id   text,
  note       text,
  amount_inr numeric(10, 2),                     -- money received, for hand grants of packs and Pro
  granted_by uuid references users(id) on delete set null,
  created_at timestamptz not null default now()
);
create index if not exists credit_ledger_user on credit_ledger (user_id, created_at desc);
create index if not exists credit_ledger_video on credit_ledger (video_id) where video_id is not null;
-- Rewards that are given once per account, once per video, or once per referred friend.
create unique index if not exists credit_once_per_account on credit_ledger (user_id, kind)
  where kind in ('creator_join', 'first_publish', 'subscribe');
create unique index if not exists credit_once_per_video on credit_ledger (user_id, kind, video_id)
  where kind in ('views_1k', 'views_10k');
create unique index if not exists credit_once_per_friend on credit_ledger (user_id, kind, note)
  where kind = 'referral';
create unique index if not exists credit_monthly_once on credit_ledger (user_id, period)
  where kind = 'monthly';

-- Things that happened, for the admin analytics.
create table if not exists events (
  id         bigserial primary key,
  type       text not null,                      -- signup, render_done, render_failed, download, view, ...
  user_id    uuid references users(id) on delete set null,
  video_id   text,
  meta       jsonb,
  created_at timestamptz not null default now()
);
create index if not exists events_by_type on events (type, created_at desc);
create index if not exists events_by_time on events (created_at desc);

-- Videos sent to the Vivaran YouTube channel: submitted by the creator, approved by an admin.
create table if not exists youtube_uploads (
  id           bigserial primary key,
  video_id     text not null unique references videos(id) on delete cascade,
  user_id      uuid not null references users(id) on delete cascade,
  title        text not null,
  description  text not null,
  tags         text[] not null default '{}',
  seo_by_ai    boolean not null default false,
  status       text not null default 'pending'
               check (status in ('pending', 'approved', 'uploading', 'published', 'rejected', 'failed')),
  review_note  text,
  youtube_id   text,
  error        text,
  yt_views     bigint not null default 0,
  yt_likes     bigint not null default 0,
  stats_at     timestamptz,
  created_at   timestamptz not null default now(),
  reviewed_at  timestamptz,
  published_at timestamptz
);
create index if not exists youtube_uploads_status on youtube_uploads (status, created_at);

-- ---------------------------------------------------------------- credit functions (shared by site and render server)

-- The account's tier today: Pro while pro_until is in the future.
create or replace function vivaran_tier(uid uuid) returns text language sql stable as $$
  select case when pro_until is not null and pro_until > now() then 'pro' else 'free' end from users where id = uid
$$;

-- Give this month's allowance if it has not been given yet; a Pro upgrade mid-month tops it up.
create or replace function vivaran_ensure_monthly(uid uuid) returns void language plpgsql as $$
declare
  p text := to_char(now() at time zone 'Asia/Kolkata', 'YYYY-MM');
  plans jsonb := (select value from settings where key = 'plans');
  want numeric := (plans -> vivaran_tier(uid) ->> 'monthly_credits')::numeric;
  given numeric;
begin
  insert into credit_ledger (user_id, bucket, period, delta, kind, note)
    values (uid, 'monthly', p, want, 'monthly', vivaran_tier(uid))
    on conflict do nothing;
  select coalesce(sum(delta), 0) into given from credit_ledger
    where user_id = uid and bucket = 'monthly' and period = p and kind in ('monthly', 'monthly_topup');
  if given < want then
    insert into credit_ledger (user_id, bucket, period, delta, kind, note)
      values (uid, 'monthly', p, want - given, 'monthly_topup', 'pro');
  end if;
end $$;

-- What the account can spend now: this month's credits and bonus credits.
create or replace function vivaran_balance(uid uuid, out monthly numeric, out bonus numeric) language sql stable as $$
  select
    coalesce(sum(delta) filter (where bucket = 'monthly' and period = to_char(now() at time zone 'Asia/Kolkata', 'YYYY-MM')), 0),
    coalesce(sum(delta) filter (where bucket = 'bonus'), 0)
  from credit_ledger where user_id = uid
$$;

-- Take credits for a render, monthly first. Returns false (and takes nothing) if there are not enough.
create or replace function vivaran_spend(uid uuid, amount numeric, vid text, why text) returns boolean language plpgsql as $$
declare
  b record;
  p text := to_char(now() at time zone 'Asia/Kolkata', 'YYYY-MM');
  from_monthly numeric;
begin
  perform pg_advisory_xact_lock(hashtext(uid::text));
  perform vivaran_ensure_monthly(uid);
  select * into b from vivaran_balance(uid);
  if b.monthly + b.bonus < amount then
    return false;
  end if;
  from_monthly := least(greatest(b.monthly, 0), amount);
  if from_monthly > 0 then
    insert into credit_ledger (user_id, bucket, period, delta, kind, video_id) values (uid, 'monthly', p, -from_monthly, why, vid);
  end if;
  if amount - from_monthly > 0 then
    insert into credit_ledger (user_id, bucket, delta, kind, video_id) values (uid, 'bonus', -(amount - from_monthly), why, vid);
  end if;
  return true;
end $$;

-- Give back what a render took (it failed), into the buckets it came from.
create or replace function vivaran_refund(vid text) returns numeric language plpgsql as $$
declare
  r record;
  total numeric := 0;
begin
  for r in select user_id, bucket, period, -sum(delta) as back from credit_ledger
             where video_id = vid and kind in ('render', 'render_adjust', 'render_refund')
             group by user_id, bucket, period having -sum(delta) > 0 loop
    insert into credit_ledger (user_id, bucket, period, delta, kind, video_id) values (r.user_id, r.bucket, r.period, r.back, 'render_refund', vid);
    total := total + r.back;
  end loop;
  return total;
end $$;

-- Secrets the site keeps for itself (the YouTube channel's refresh token), encrypted with CEVG_KEY_SECRET.
create table if not exists secrets (
  key        text primary key,
  value      bytea not null,
  updated_at timestamptz not null default now()
);
