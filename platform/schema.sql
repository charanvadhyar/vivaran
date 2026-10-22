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
