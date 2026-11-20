import Link from "next/link";
import { notFound } from "next/navigation";
import { approveUpload, disconnectYouTube, grantCredits, rejectUpload, savePlans, savePlaylists, setProUntil, syncYouTube, toggleAdmin } from "./actions";
import { AdminNav } from "@/components/admin/AdminNav";
import { BarChart } from "@/components/admin/BarChart";
import { DataTable } from "@/components/admin/DataTable";
import { Funnel } from "@/components/admin/Funnel";
import { JsonForm } from "@/components/admin/JsonForm";
import { KpiGrid } from "@/components/admin/KpiGrid";
import { UploadCard } from "@/components/admin/UploadCard";
import { UserRow } from "@/components/admin/UserRow";
import { Container } from "@/components/layout/Container";
import { PageHeader } from "@/components/layout/PageHeader";
import { Section } from "@/components/layout/Section";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { isAdmin, overview, uploads, users } from "@/lib/admin";
import { currentUser } from "@/lib/auth";
import { KIND_LABELS, getPlans } from "@/lib/credits";
import { one } from "@/lib/db";
import { connected } from "@/lib/youtube";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const metadata = { title: "Admin" };

const inr = (n: number) => `₹${Math.round(n).toLocaleString("en-IN")}`;
const int = (n: number) => Math.round(n).toLocaleString("en-IN");
const one1 = (n: number) => (Math.round(n * 10) / 10).toLocaleString("en-IN");

export default async function Admin({ searchParams }: { searchParams: Promise<{ tab?: string; days?: string; q?: string; yt?: string }> }) {
  const viewer = await currentUser();
  if (!viewer || !(await isAdmin(viewer))) notFound();
  const sp = await searchParams;
  const tab = ["overview", "users", "youtube", "settings"].includes(sp.tab ?? "") ? sp.tab! : "overview";
  const days = [7, 30, 90, 365].includes(Number(sp.days)) ? Number(sp.days) : 30;

  return (
    <Container main>
      <PageHeader title="Admin" lead="How Vivaran is doing, and the tools to run it." />
      <AdminNav tab={tab} days={days} />
      {tab === "overview" ? <Overview days={days} /> : null}
      {tab === "users" ? <Users q={sp.q ?? ""} /> : null}
      {tab === "youtube" ? <YouTube flash={sp.yt} /> : null}
      {tab === "settings" ? <Settings /> : null}
    </Container>
  );
}

async function Overview({ days }: { days: number }) {
  const o = await overview(days);
  const k = o.kpi;
  const margin = k.revenue_inr - k.cost_inr;
  const failRate = k.videos_done + k.videos_failed ? (k.videos_failed / (k.videos_done + k.videos_failed)) * 100 : 0;
  const per = (n: number) => (k.minutes ? n / k.minutes : 0);
  const ch = k.yt_channel;
  return (
    <>
      <Section title={`Last ${days === 365 ? "year" : `${days} days`}`} first>
        <KpiGrid items={[
          { label: "Accounts", value: int(k.users_total), sub: `${int(k.users_new)} new` },
          { label: "Active creators", value: int(k.users_rendering), sub: `rendered in the period` },
          { label: "Pro", value: int(k.pro), sub: `MRR ${inr(k.mrr_inr)}` },
          { label: "Creator program", value: int(k.creators) },
          { label: "Videos made", value: int(k.videos_done), sub: `${one1(failRate)}% failed`, tone: failRate > 10 ? "bad" : undefined },
          { label: "Video minutes", value: one1(k.minutes), sub: `${one1(k.render_s_per_min)} s render per minute` },
          { label: "Estimated cost", value: inr(k.cost_inr), sub: `${inr(per(k.cost_inr))} per video minute` },
          { label: "Money received", value: inr(k.revenue_inr), sub: `margin ${inr(margin)}`, tone: k.revenue_inr > 0 ? (margin >= 0 ? "good" : "bad") : undefined },
          { label: "Credits given", value: one1(k.credits_given), sub: `${one1(k.credits_spent)} spent on renders` },
          { label: "Views on the site", value: int(k.site_views), sub: `${int(k.site_views_total)} all time · ${int(k.public_videos)} public videos` },
          { label: "On YouTube", value: int(k.yt_published), sub: `${int(k.yt_views)} views · ${int(k.yt_pending)} waiting` },
          { label: "Channel subscribers", value: ch?.subscribers != null ? int(ch.subscribers) : "–", sub: ch?.title ?? "sync on the YouTube tab" },
          { label: "Downloads", value: int(k.downloads) },
          { label: "Figures drawn", value: int(k.figures), sub: `${int(k.seo_ai)} SEO written by AI` },
        ]} />
      </Section>
      <Section title="Day by day">
        <div className={styles.charts}>
          <BarChart title="Sign-ups" data={o.series} value="signups" />
          <BarChart title="Videos made" data={o.series} value="renders" stack={{ key: "failures", label: "failed" }} />
          <BarChart title="Video minutes" data={o.series} value="minutes" format={one1} />
          <BarChart title="Estimated cost" data={o.series} value="cost" format={inr} />
          <BarChart title="Creators who rendered" data={o.series} value="active" total={int(k.users_rendering)} />
          <BarChart title="Site views" data={o.series} value="views" />
          <BarChart title="Credits spent" data={o.series} value="credits_spent" format={one1} />
          <BarChart title="Downloads" data={o.series} value="downloads" />
        </div>
      </Section>
      <Section title="Where people stop">
        <Funnel steps={[
          { label: "Signed up", value: Number(o.funnel.signed_up ?? 0) },
          { label: "Used the connector", value: Number(o.funnel.connected ?? 0) },
          { label: "Made a video", value: Number(o.funnel.rendered ?? 0) },
          { label: "Made one public", value: Number(o.funnel.published ?? 0) },
          { label: "Sent to YouTube", value: Number(o.funnel.submitted ?? 0) },
          { label: "On the channel", value: Number(o.funnel.on_youtube ?? 0) },
        ]} />
      </Section>
      <Section title="What is being made">
        <div className={styles.tables}>
          {[["By language", o.byLanguage], ["By subject", o.bySubject], ["Voiced or silent", o.byVoice]].map(([title, rows]) => (
            <DataTable key={title as string} title={title as string} columns={[{ key: "key", label: "" }, { key: "videos", label: "Videos", numeric: true }, { key: "minutes", label: "Minutes", numeric: true }]}
              rows={(rows as { key: string; videos: string; minutes: string }[]).map((r) => ({ ...r }))} />
          ))}
        </div>
      </Section>
      <Section title="Top videos and creators">
        <div className={styles.tables2}>
          <DataTable title="Most watched (site + YouTube)" columns={[{ key: "title", label: "Video" }, { key: "views", label: "Site", numeric: true }, { key: "yt", label: "YouTube", numeric: true }]}
            rows={o.topVideos.map((v) => ({ title: <Link href={`/v/${v.id}`}>{v.title}</Link>, views: int(v.views), yt: v.yt_views ? int(Number(v.yt_views)) : "–" }))} />
          <DataTable title="Creators by minutes made" columns={[{ key: "who", label: "Creator" }, { key: "videos", label: "Videos", numeric: true }, { key: "minutes", label: "Minutes", numeric: true }, { key: "views", label: "Views", numeric: true }]}
            rows={o.topCreators.map((c) => ({ who: <Link href={`/u/${c.handle}`}>{c.name}</Link>, videos: c.videos, minutes: c.minutes, views: int(Number(c.views)) }))} />
        </div>
      </Section>
      <Section title="Rewards and failures">
        <div className={styles.tables2}>
          <DataTable title="Bonus credits given" columns={[{ key: "kind", label: "For" }, { key: "times", label: "Times", numeric: true }, { key: "credits", label: "Credits", numeric: true }]}
            rows={o.rewards.map((r) => ({ kind: KIND_LABELS[r.kind] ?? r.kind, times: r.times, credits: Number(r.credits).toString() }))} />
          <DataTable title="Recent failed renders" empty="No failures in this period."
            columns={[{ key: "what", label: "Video" }, { key: "error", label: "Why" }]}
            rows={o.failures.map((f) => ({ what: <>{f.title} <small>@{f.handle}</small></>, error: <small>{f.error}</small> }))} />
        </div>
      </Section>
      <p className={styles.footnote}>Costs are estimates from the cost model on the settings tab (Gnani per 1,000 characters, server per video minute), not bills. Money received counts what you entered when granting packs and Pro.</p>
    </>
  );
}

async function Users({ q }: { q: string }) {
  const list = await users(q);
  return (
    <Section title={`${list.length} ${list.length === 1 ? "account" : "accounts"}${q ? ` matching “${q}”` : ""}`} first>
      <form className={styles.search}>
        <input type="hidden" name="tab" value="users" />
        <input name="q" defaultValue={q} placeholder="Name, handle or email" aria-label="Search accounts" />
        <Button type="submit" size="sm">Search</Button>
      </form>
      <div className={styles.list}>
        {list.map((u) => <UserRow key={u.id} u={u} grant={grantCredits} setPro={setProUntil} toggleAdmin={toggleAdmin} />)}
      </div>
      <p className={styles.footnote}>Until online payment is set up: when someone pays you, give the credits with “Pack bought” or set Pro, and enter the amount received so it shows in the analytics.</p>
    </Section>
  );
}

async function YouTube({ flash }: { flash?: string }) {
  const [isConnected, pending, recent, channel, syncError] = await Promise.all([
    connected(), uploads(["pending", "approved", "uploading", "failed"]), uploads(["published", "rejected"]),
    one<{ value: { title?: string; subscribers?: number; views?: number; videos?: number }; updated_at: Date }>(`select value, updated_at from settings where key = 'youtube_channel'`),
    one<{ value: string }>(`select value from settings where key = 'youtube_sync_error' and updated_at > now() - interval '1 hour'`),
  ]);
  return (
    <>
      <Section title="The channel" first>
        {flash ? <Alert tone={flash === "connected" ? "info" : "danger"}>{flash === "connected" ? "The channel is connected." : `Could not connect: ${flash}`}</Alert> : null}
        <div className={styles.channel}>
          {isConnected ? (
            <>
              <div>
                <strong>{channel?.value.title ?? "Connected"}</strong>
                {channel ? <p className={styles.muted}>{int(channel.value.subscribers ?? 0)} subscribers · {int(channel.value.views ?? 0)} views · {int(channel.value.videos ?? 0)} videos · as of {new Date(channel.updated_at).toLocaleString("en-IN")}</p> : <p className={styles.muted}>Sync to see its numbers.</p>}
                {syncError ? <p className={styles.error}>{syncError.value}</p> : null}
              </div>
              <div className={styles.row}>
                <form action={syncYouTube}><Button type="submit">Sync views and give milestone credits</Button></form>
                <form action={disconnectYouTube}><Button type="submit" variant="ghost">Disconnect</Button></form>
              </div>
            </>
          ) : (
            <>
              <p className={styles.muted}>Connect the Vivaran channel once, signed in as its owner. Uploads and view counts use this.</p>
              <Button href="/api/admin/youtube/connect" variant="primary">Connect the YouTube channel</Button>
            </>
          )}
        </div>
      </Section>
      <Section title={`Waiting (${pending.length})`}>
        {pending.length ? <div className={styles.uploads}>{pending.map((u) => <UploadCard key={u.id} u={u} approve={approveUpload} reject={rejectUpload} />)}</div>
          : <p className={styles.muted}>Nothing to review.</p>}
      </Section>
      <Section title="Done">
        {recent.length ? <div className={styles.uploads}>{recent.map((u) => <UploadCard key={u.id} u={u} approve={approveUpload} reject={rejectUpload} />)}</div>
          : <p className={styles.muted}>No videos on the channel yet.</p>}
      </Section>
    </>
  );
}

async function Settings() {
  const plans = await getPlans();
  const playlists = await one<{ value: Record<string, string> }>(`select value from settings where key = 'youtube_playlists'`);
  return (
    <>
      <Section title="Plans, prices and rewards" first>
        <JsonForm name="plans" label="Plans" save={savePlans} initial={JSON.stringify(plans, null, 2)}
          help="Credits each month per tier, the longest video, the watermark, figure allowance, what a video costs, the rewards, the packs, downloads per day, the YouTube channel link (shown for the subscribe reward) and the cost model the analytics use. Changes apply at once." />
      </Section>
      <Section title="YouTube playlists">
        <JsonForm name="playlists" label="Playlist for each subject" save={savePlaylists}
          initial={JSON.stringify(playlists?.value ?? { dsa: "", coa: "", os: "", dbms: "", ml: "", networks: "", maths: "", other: "" }, null, 2)}
          help="The playlist id (from the playlist's link, after list=) that each subject's videos are added to. Leave one empty to skip it." />
      </Section>
    </>
  );
}
