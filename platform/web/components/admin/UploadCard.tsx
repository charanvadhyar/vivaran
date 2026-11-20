import type { Upload } from "@/lib/admin";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import styles from "./UploadCard.module.css";

/** A video waiting to go on the channel: watch it, fix the text, approve or turn it down. */
export function UploadCard({ u, approve, reject }: { u: Upload; approve: (f: FormData) => Promise<void>; reject: (f: FormData) => Promise<void> }) {
  const open = u.status === "pending" || u.status === "failed";
  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <div>
          <a href={`/v/${u.video_id}`} target="_blank" rel="noreferrer" className={styles.link}>{u.video_title}</a>
          <div className={styles.muted}>@{u.handle} · {u.minutes} min · {u.tier} · sent {new Date(u.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}{u.seo_by_ai ? " · SEO by AI" : ""}</div>
        </div>
        <Badge tone={u.status === "published" ? "positive" : u.status === "failed" || u.status === "rejected" ? "negative" : "neutral"}>{u.status}</Badge>
      </div>
      {u.error ? <p className={styles.error}>{u.error}</p> : null}
      {u.youtube_id ? <p className={styles.muted}><a className={styles.link} href={`https://www.youtube.com/watch?v=${u.youtube_id}`} target="_blank" rel="noreferrer">On YouTube</a> · {Number(u.yt_views).toLocaleString("en-IN")} views</p> : null}
      {open ? (
        <>
          <form action={approve} className={styles.form}>
            <input type="hidden" name="id" value={u.id} />
            <input name="title" defaultValue={u.title} maxLength={100} className={styles.input} aria-label="Title" />
            <textarea name="description" defaultValue={u.description} rows={6} className={styles.input} aria-label="Description" />
            <input name="tags" defaultValue={u.tags.join(", ")} className={styles.input} aria-label="Tags" />
            <div><Button type="submit" variant="primary" size="sm">{u.status === "failed" ? "Try the upload again" : "Approve and upload"}</Button></div>
          </form>
          <form action={reject} className={styles.reject}>
            <input type="hidden" name="id" value={u.id} />
            <input name="note" placeholder="Why not (the creator sees this)" className={styles.input} aria-label="Reason" />
            <Button type="submit" size="sm" variant="danger">Turn down</Button>
          </form>
        </>
      ) : null}
    </div>
  );
}
