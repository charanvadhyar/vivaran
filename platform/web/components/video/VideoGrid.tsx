import type { Video } from "@/lib/videos";
import { VideoCard } from "./VideoCard";
import styles from "./VideoGrid.module.css";

export function VideoGrid({ videos, own }: { videos: Video[]; own?: boolean }) {
  return <div className={styles.grid}>{videos.map((v) => <VideoCard key={v.id} video={v} own={own} />)}</div>;
}
