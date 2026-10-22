"use client";

import { Card } from "../ui/Card";
import styles from "./StepsPanel.module.css";

/** The parts of a video with their start times; pressing one jumps the player there. */
export function StepsPanel({ parts, playerId = "player" }: { parts: { at: number; label: string; text: string }[]; playerId?: string }) {
  const jump = (at: number) => {
    const player = document.getElementById(playerId) as HTMLVideoElement | null;
    if (!player) return;
    player.currentTime = at;
    void player.play();
    player.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };
  return (
    <Card flush className={styles.panel} aria-label="In this video">
      <h2 className={styles.head}>In this video</h2>
      <ol className={styles.list}>
        {parts.map((part) => (
          <li key={part.at}>
            <button type="button" className={styles.item} onClick={() => jump(part.at)}>
              <span className={styles.when}>{part.label}</span>
              <span>{part.text}</span>
            </button>
          </li>
        ))}
      </ol>
    </Card>
  );
}
