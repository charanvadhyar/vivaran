import Link from "next/link";
import { notFound } from "next/navigation";
import { deleteVideo, setPublic, submitToYouTube, writeSeo } from "../../actions";
import { Container } from "@/components/layout/Container";
import { Badge } from "@/components/ui/Badge";
import { Player } from "@/components/video/Player";
import { PublishPanel } from "@/components/video/PublishPanel";
import { RenderStatus } from "@/components/video/RenderStatus";
import { SharePanel } from "@/components/video/SharePanel";
import { StepsPanel } from "@/components/video/StepsPanel";
import { YouTubePanel, type UploadState } from "@/components/video/YouTubePanel";
import { account } from "@/lib/credits";
import { currentUser } from "@/lib/auth";
import { subjectName } from "@/lib/brand";
import { db } from "@/lib/db";
import { LANGUAGES, minutes, videoById } from "@/lib/videos";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";

const SITE = (process.env.SITE_URL ?? "https://vivaran-kappa.vercel.app").replace(/\/$/, "");

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const video = await videoById((await params).id);
  return { title: video?.is_public ? video.title : "Video" };
}

export default async function Watch({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [video, viewer] = await Promise.all([videoById(id), currentUser()]);
  if (!video) notFound();
  const own = viewer?.id === video.user_id;
  // A private video does not exist as far as anyone else can tell.
  if (!own && !(video.is_public && video.status === "done")) notFound();
  if (!own) {
    await db.query("update videos set views = views + 1 where id = $1", [id]);
    await db.query("insert into events (type, user_id, video_id) values ('view', $1::uuid, $2)", [viewer?.id ?? null, id]);
  }
  let upload: UploadState = null;
  let isPro = false;
  if (own && video.status === "done") {
    const { rows } = await db.query(`select status, youtube_id, review_note, coalesce(yt_views, 0)::int as yt_views, title, description, tags
         from youtube_uploads where video_id = $1`, [id]);
    upload = (rows[0] as UploadState) ?? null;
    isPro = (await account(video.user_id)).tier === "pro";
  }

  let at = 0;
  const parts = (video.outline ?? []).map((part) => {
    const start = at;
    at += part.seconds;
    const text = part.opens_with.length >= 120 ? `${part.opens_with}…` : part.opens_with;
    return { at: start, label: minutes(start) || "0:00", text };
  });

  return (
    <Container main>
      <div className={styles.watch}>
        <div className={styles.main}>
          {video.status === "done"
            ? <Player src={`/api/videos/${id}/file`} poster={`/api/videos/${id}/thumb`} />
            : <RenderStatus id={id} initial={{ state: video.status, progress: video.progress, error: video.error }} />}
          <h1 className={styles.title}>{video.title}</h1>
          <p className={styles.meta}>
            <Link href={`/u/${video.creator_handle}`} className={styles.creator}>{video.creator_name}</Link>
            {subjectName(video.subject) ? <Link href={`/explore?subject=${video.subject}`}><Badge>{subjectName(video.subject)}</Badge></Link> : null}
            <span>{LANGUAGES[video.language] ?? video.language}</span>
            {video.seconds ? <span>{minutes(video.seconds)}</span> : null}
            <span>{video.voiced ? `Voice: ${video.speaker}` : "Silent, with captions"}</span>
            {video.is_public ? <span>{video.views} {video.views === 1 ? "view" : "views"}</span> : null}
          </p>
          {video.is_public && video.status === "done" ? <SharePanel url={`${SITE}/v/${id}`} title={video.title} /> : null}
          {own && video.status === "done" ? <PublishPanel video={video} setPublic={setPublic} deleteVideo={deleteVideo} /> : null}
          {own && video.status === "done" ? (
            <YouTubePanel videoId={id} title={video.title} isPro={isPro} isPublic={video.is_public} upload={upload}
              submit={submitToYouTube} writeSeo={writeSeo} />
          ) : null}
        </div>
        {parts.length && video.status === "done" ? <aside><StepsPanel parts={parts} /></aside> : null}
      </div>
    </Container>
  );
}
