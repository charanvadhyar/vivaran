import Link from "next/link";
import type { Video } from "@/lib/videos";
import { LANGUAGES, minutes } from "@/lib/format";
import { Icon } from "../ui/Icon";
import styles from "./DemoChat.module.css";

/** The product working: the conversation that makes a video, then the video it made.
    `sample` is a real public video from the library; without one, a still stands in. */
export function DemoChat({ sample }: { sample: Video | null }) {
  const title = sample?.title ?? "Binary search, step by step";
  const topic = title.replace(/[.:].*$/, "").replace(/,.*$/, "").split(" ").map((w) => (/^[A-Z0-9-]{2,}$/.test(w) ? w : w.toLowerCase())).join(" ");
  const language = sample ? (LANGUAGES[sample.language] ?? sample.language) : "Telugu";
  const mins = sample?.seconds ? Math.max(1, Math.round(sample.seconds / 60)) : 2;
  const length = `${mins} minute`;
  const lengthPlural = `${mins} minute${mins === 1 ? "" : "s"}`;
  const voice = sample?.voiced && sample.speaker ? `in ${sample.speaker[0].toUpperCase()}${sample.speaker.slice(1)}'s voice` : "silent, with captions";
  // The plan is the first sentence of each part, without a "Step 2." counter the narration may open with.
  const plan = (sample?.outline ?? []).slice(0, 4).map((part) => {
    const line = part.opens_with.replace(/^step\s*\d+\s*[.:]\s*/i, "").replace(/([.!?])\s.*$/s, "$1").replace(/[.!?]$/, "");
    return (line.length > 8 ? line : part.scene.replace(/[-_]/g, " ")).slice(0, 72);
  });
  const fallback = ["The problem and the sorted array", "Why the middle element decides the half", "Two checks, step by step, to the answer", "Why it takes about log n checks"];
  return (
    <div className={styles.demo} aria-label="How a video is made">
      <div className={styles.bar}><span className={styles.dot} /><span className={styles.dot} /><span className={styles.dot} />claude · vivaran connected</div>
      <div className={styles.chat}>
        <div className={`${styles.bubble} ${styles.user}`}>Make {mins === 8 || mins === 11 || mins === 18 ? "an" : "a"} {length} {language} video on {topic}.</div>
        <div className={`${styles.bubble} ${styles.bot}`}>
          Here is the plan, about {lengthPlural}, {voice}:
          <ol>
            {(plan.length ? plan : fallback).map((line) => <li key={line}>{line}</li>)}
          </ol>
          Shall I render it?
        </div>
        <div className={`${styles.bubble} ${styles.user}`}>Yes</div>
        <div className={styles.tool}><Icon name="check" className={styles.ok} /> validate · preview · estimate · render</div>
        <div className={`${styles.bubble} ${styles.bot}`}>Done. It is saved to your account, private until you make it public.</div>
      </div>
      <div className={styles.player}>
        {sample ? (
          <video src={`/api/videos/${sample.id}/file`} poster={`/api/videos/${sample.id}/thumb`} muted autoPlay loop playsInline preload="metadata" />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img src="/sample-frame.png" alt="A frame from a Vivaran video" />
        )}
      </div>
      <div className={styles.caption}>
        <span>{sample ? <Link href={`/v/${sample.id}`}>{sample.title}</Link> : title}</span>
        <span>{sample?.seconds ? `${minutes(sample.seconds)} · ${sample.creator_name}` : "2:04 · Telugu"}</span>
      </div>
    </div>
  );
}
