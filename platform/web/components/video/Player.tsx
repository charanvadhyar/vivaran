"use client";

import { useEffect, useRef, useState } from "react";
import { minutes } from "@/lib/format";
import { Icon } from "../ui/Icon";
import { Slider } from "../ui/Slider";
import styles from "./Player.module.css";

/** The video player: own controls so students get a speed slider and keyboard shortcuts.
    Space plays and pauses, arrows seek 5 s, M mutes, F goes full screen. */
export function Player({ src, poster, id = "player" }: { src: string; poster?: string; id?: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [length, setLength] = useState(0);
  const [muted, setMuted] = useState(false);
  const [speed, setSpeed] = useState(1);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    const onTime = () => setTime(v.currentTime);
    const onMeta = () => setLength(v.duration || 0);
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    v.addEventListener("timeupdate", onTime); v.addEventListener("loadedmetadata", onMeta);
    v.addEventListener("play", onPlay); v.addEventListener("pause", onPause);
    return () => { v.removeEventListener("timeupdate", onTime); v.removeEventListener("loadedmetadata", onMeta); v.removeEventListener("play", onPlay); v.removeEventListener("pause", onPause); };
  }, []);

  const toggle = () => { const v = ref.current; if (!v) return; if (v.paused) void v.play(); else v.pause(); };
  const seekBy = (s: number) => { const v = ref.current; if (v) v.currentTime = Math.max(0, Math.min(v.duration || 0, v.currentTime + s)); };
  const changeSpeed = (s: number) => { setSpeed(s); if (ref.current) ref.current.playbackRate = s; };

  return (
    <div className={styles.player}
      onKeyDown={(e) => {
        if (e.target instanceof HTMLInputElement) return;
        if (e.key === " " || e.key === "k") { e.preventDefault(); toggle(); }
        if (e.key === "ArrowRight") seekBy(5);
        if (e.key === "ArrowLeft") seekBy(-5);
        if (e.key === "m") setMuted((m) => !m);
        if (e.key === "f") void ref.current?.parentElement?.requestFullscreen?.();
      }}>
      <div className={styles.frame}>
        <video id={id} ref={ref} className={styles.video} src={src} poster={poster} preload="metadata" muted={muted} playsInline onClick={toggle} />
        {!playing && time === 0 ? (
          <button type="button" className={styles.big} onClick={toggle} aria-label="Play"><Icon name="play" size={24} /></button>
        ) : null}
      </div>
      <div className={styles.controls}>
        <input type="range" className={styles.seek} min={0} max={length || 0} step={0.1} value={time} aria-label="Seek"
          style={{ "--fill": `${length ? (time / length) * 100 : 0}%` } as React.CSSProperties}
          onChange={(e) => { if (ref.current) ref.current.currentTime = Number(e.target.value); }} />
        <div className={styles.row}>
          <button type="button" className={styles.btn} onClick={toggle} aria-label={playing ? "Pause" : "Play"}><Icon name={playing ? "pause" : "play"} /></button>
          <button type="button" className={styles.btn} onClick={() => setMuted((m) => !m)} aria-label={muted ? "Unmute" : "Mute"}><Icon name={muted ? "mute" : "volume"} /></button>
          <span className={styles.time}>{minutes(time) || "0:00"} / {minutes(length) || "0:00"}</span>
          <span className={styles.spacer} />
          <div className={styles.speed}>
            <Slider label="Speed" value={speed} min={0.5} max={2} step={0.25} onChange={changeSpeed} format={(v) => `${v}×`} />
          </div>
          <button type="button" className={styles.btn} onClick={() => void ref.current?.parentElement?.requestFullscreen?.()} aria-label="Full screen"><Icon name="fullscreen" /></button>
        </div>
      </div>
    </div>
  );
}
