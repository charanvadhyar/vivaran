import path from "node:path";
import { many, one } from "./db";

export type Video = {
  id: string;
  user_id: string;
  title: string;
  subject: string | null;
  language: string;
  speaker: string | null;
  voiced: boolean;
  status: "queued" | "running" | "done" | "failed";
  progress: string;
  error: string | null;
  seconds: number | null;
  steps: number | null;
  is_public: boolean;
  outline: { scene: string; steps: number; seconds: number; opens_with: string }[] | null;
  views: number;
  created_at: Date;
  published_at: Date | null;
  creator_name: string;
  creator_handle: string;
};

const SELECT = `select v.id, v.user_id::text as user_id, v.title, v.subject, v.language, v.speaker, v.voiced, v.status, v.progress,
  v.error, v.seconds, v.steps, v.is_public, v.outline, v.views, v.created_at, v.published_at,
  u.name as creator_name, u.handle as creator_handle
  from videos v join users u on u.id = v.user_id`;

export const videoById = (id: string) => one<Video>(`${SELECT} where v.id = $1`, [id]);

export const videosOf = (userId: string) =>
  many<Video>(`${SELECT} where v.user_id::text = $1 order by v.created_at desc limit 100`, [userId]);

/** Public videos, newest first, narrowed by subject and by words in the title. */
export function publicVideos(filter: { subject?: string; q?: string } = {}, limit = 60) {
  const where = ["v.is_public", "v.status = 'done'"];
  const params: unknown[] = [];
  if (filter.subject) {
    params.push(filter.subject);
    where.push(`v.subject = $${params.length}`);
  }
  for (const word of (filter.q ?? "").split(/\s+/).filter(Boolean).slice(0, 6)) {
    // Each word must appear in the title or the creator's name.
    params.push(`%${word.replace(/[\\%_]/g, "\\$&")}%`);
    where.push(`(v.title ilike $${params.length} or u.name ilike $${params.length})`);
  }
  params.push(limit);
  return many<Video>(`${SELECT} where ${where.join(" and ")} order by v.published_at desc limit $${params.length}`, params);
}

export const publicVideosOf = (userId: string) =>
  many<Video>(`${SELECT} where v.user_id::text = $1 and v.is_public and v.status = 'done' order by v.published_at desc`, [userId]);

/** Who may watch: anyone if it is public, otherwise only its creator. */
export function canWatch(video: Video, viewerId: string | null | undefined): boolean {
  return video.status === "done" && (video.is_public || video.user_id === viewerId);
}

export function storage(): string {
  // A relative path is taken from the platform folder, the same as the MCP server does.
  return path.resolve(/* turbopackIgnore: true */ process.cwd(), "..", process.env.CEVG_STORAGE ?? "storage");
}

export { minutes, LANGUAGES } from "./format";
