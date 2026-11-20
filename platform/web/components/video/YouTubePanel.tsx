"use client";

import { useState, useTransition } from "react";
import type { SeoDraft } from "@/app/actions";
import { Alert } from "../ui/Alert";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Icon } from "../ui/Icon";
import { Input } from "../ui/Input";
import styles from "./YouTubePanel.module.css";

export type UploadState = {
  status: string; youtube_id: string | null; review_note: string | null; yt_views: number;
  title: string; description: string; tags: string[] | null;
} | null;

/** What the creator wrote, without the credit line the site adds at the end. */
function ownText(description: string): string {
  return description.replace(/\n*Made (by .+ )?with Vivaran: \S+\s*$/, "").trim();
}

const STATUS: Record<string, string> = {
  pending: "Waiting for review", approved: "Approved, uploading soon", uploading: "Uploading", published: "On the channel",
  rejected: "Not approved", failed: "Upload failed; we are looking into it",
};

/** Send a public video to the Vivaran YouTube channel, with its title, description and tags. */
export function YouTubePanel({ videoId, title, isPro, isPublic, upload, submit, writeSeo }:
  { videoId: string; title: string; isPro: boolean; isPublic: boolean; upload: UploadState;
    submit: (form: FormData) => Promise<{ ok: boolean; message: string }>;
    writeSeo: (id: string) => Promise<SeoDraft | { error: string }> }) {
  // After sending, the form shows what was sent, so it can be checked or changed and sent again.
  const [form, setForm] = useState(upload
    ? { title: upload.title, description: ownText(upload.description), tags: (upload.tags ?? []).join(", ") }
    : { title, description: "", tags: "" });
  const [byAi, setByAi] = useState(false);
  const [note, setNote] = useState<{ ok: boolean; text: string } | null>(null);
  const [pending, start] = useTransition();
  const [writing, startWriting] = useTransition();
  const editable = !upload || ["pending", "rejected", "failed"].includes(upload.status);

  if (!isPublic) {
    return (
      <Card title="Vivaran YouTube channel">
        <p className={styles.muted}>Make the video public first. Then you can send it to the channel, with your name on it.</p>
      </Card>
    );
  }
  return (
    <Card title="Vivaran YouTube channel" aside={upload ? <Badge tone={upload.status === "published" ? "positive" : upload.status === "rejected" ? "negative" : "neutral"}>{STATUS[upload.status] ?? upload.status}</Badge> : null}>
      {upload?.status === "published" && upload.youtube_id ? (
        <p className={styles.muted}>
          <a href={`https://www.youtube.com/watch?v=${upload.youtube_id}`} target="_blank" rel="noreferrer">Watch it on YouTube</a> · {upload.yt_views.toLocaleString("en-IN")} views
        </p>
      ) : null}
      {upload?.status === "rejected" && upload.review_note ? <Alert tone="danger">{upload.review_note}</Alert> : null}
      {editable ? (
        <form className={styles.form} action={(data) => start(async () => {
          const result = await submit(data);
          setNote({ ok: result.ok, text: result.message });
        })}>
          <input type="hidden" name="id" value={videoId} />
          <input type="hidden" name="seo_by_ai" value={byAi ? "1" : "0"} />
          <div className={styles.head}>
            <span className={styles.muted}>{isPro ? "Let us write it, then edit anything you like." : "Write how people will find it: the title, a description and search tags."}</span>
            {isPro ? (
              <Button loading={writing} icon={<Icon name="spark" />} onClick={() => startWriting(async () => {
                const draft = await writeSeo(videoId);
                if ("error" in draft) setNote({ ok: false, text: draft.error });
                else { setForm({ title: draft.title, description: draft.description, tags: draft.tags.join(", ") }); setByAi(true); setNote(null); }
              })}>Write it for me</Button>
            ) : <Badge>Pro writes this for you</Badge>}
          </div>
          <Input label="Title" name="title" value={form.title} maxLength={100} required
            hint={`${form.title.length}/100. The topic first, the way students search it.`}
            onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <label className={styles.label} htmlFor="yt-description">Description</label>
          <textarea id="yt-description" name="description" className={styles.textarea} rows={10} minLength={100} maxLength={4900} required
            value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="What will a student be able to do after watching? What is covered, in order? Chapters (0:00 Intro)…" />
          <span className={styles.hint}>{form.description.length}/4,900, at least 100. Your name and the Vivaran link are added for you.</span>
          <Input label="Tags" name="tags" value={form.tags} hint="Comma-separated search phrases, 480 characters in all."
            onChange={(e) => setForm({ ...form, tags: e.target.value })} />
          <Alert>A video on the channel stays only there for 12 months: you can download it for class or offline use, but please do not upload it to another YouTube channel.</Alert>
          <div><Button type="submit" variant="primary" loading={pending}>{upload ? "Send again for review" : "Send for review"}</Button></div>
        </form>
      ) : null}
      {note ? <Alert tone={note.ok ? "info" : "danger"}>{note.text}</Alert> : null}
    </Card>
  );
}
