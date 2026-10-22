import Link from "next/link";
import { subjectShort } from "@/lib/brand";
import { LANGUAGES, minutes, type Video } from "@/lib/videos";
import { Badge, type BadgeTone } from "../ui/Badge";
import styles from "./VideoCard.module.css";

const STATE: Record<string, [string, BadgeTone]> = {
  queued: ["Waiting", "accent"],
  running: ["Rendering", "accent"],
  failed: ["Failed", "negative"],
};

/** One video in a grid: thumbnail, title, who made it. `own` shows its state instead of the creator. */
export function VideoCard({ video, own = false }: { video: Video; own?: boolean }) {
  const state = STATE[video.status];
  return (
    <Link href={`/v/${video.id}`} className={styles.card}>
      <div className={styles.thumb}>
        {video.status === "done" ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={`/api/videos/${video.id}/thumb`} alt="" loading="lazy" />
        ) : (
          <span>{video.status === "failed" ? "This render failed" : "Rendering…"}</span>
        )}
        <span className={`${styles.tag} ${styles.lang}`}>{LANGUAGES[video.language] ?? video.language}</span>
        {video.seconds ? <span className={`${styles.tag} ${styles.length}`}>{minutes(video.seconds)}</span> : null}
      </div>
      <div className={styles.title}>{video.title}</div>
      <div className={styles.meta}>
        {own ? (
          <Badge tone={state ? state[1] : video.is_public ? "positive" : "neutral"}>
            {state ? state[0] : video.is_public ? "Public" : "Private"}
          </Badge>
        ) : (
          <span>{video.creator_name}</span>
        )}
        {subjectShort(video.subject) ? <span className={styles.sub}>{subjectShort(video.subject)}</span> : null}
        {video.voiced ? null : <span className={styles.sub}>Silent</span>}
      </div>
    </Link>
  );
}
