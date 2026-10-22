import { one } from "./db";

/** The numbers the landing page shows. */
export async function siteStats() {
  const row = await one<{ videos: number; creators: number; seconds: number; languages: number }>(
    `select count(*)::int as videos, count(distinct user_id)::int as creators,
            coalesce(sum(seconds), 0)::float as seconds, count(distinct language)::int as languages
     from videos where is_public and status = 'done'`,
  );
  return row ?? { videos: 0, creators: 0, seconds: 0, languages: 0 };
}
