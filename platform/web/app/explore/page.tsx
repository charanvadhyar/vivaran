import { Container } from "@/components/layout/Container";
import { Section } from "@/components/layout/Section";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { SubjectChips } from "@/components/video/SubjectChips";
import { VideoGrid } from "@/components/video/VideoGrid";
import { BRAND, SUBJECTS, subjectName } from "@/lib/brand";
import { CREATOR_PAY, WAITLIST } from "@/lib/mode";
import { publicVideos, type Video } from "@/lib/videos";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const metadata = { title: "Explore" };

export default async function Explore({ searchParams }: { searchParams: Promise<{ q?: string; subject?: string }> }) {
  const { q = "", subject = "" } = await searchParams;
  const chosen = SUBJECTS.some((s) => s.id === subject) ? subject : "";
  const query = q.trim().slice(0, 80);
  const videos = await publicVideos({ subject: chosen || undefined, q: query || undefined });
  const narrowed = Boolean(chosen || query);
  const shelves: { id: string; name: string; videos: Video[] }[] = narrowed
    ? []
    : SUBJECTS.map((s) => ({ ...s, videos: videos.filter((v) => (v.subject ?? "other") === s.id) })).filter((s) => s.videos.length);
  const subjectLink = (id: string) => (query ? `/explore?subject=${id}&q=${encodeURIComponent(query)}` : `/explore?subject=${id}`);

  return (
    <Container main>
      {narrowed ? null : (
        <section className={styles.hero}>
          <h1>Every step, <span className={styles.mark}>shown</span>.</h1>
          <p>{BRAND.description}</p>
          <div className={styles.actions}>
            <Button href={WAITLIST ? "/#waitlist" : "/dashboard"} variant="primary" size="lg" icon={<Icon name="spark" />}>{WAITLIST ? "Make videos like these" : "Make a video"}</Button>
            {CREATOR_PAY ? <Button href="/creator-terms" variant="ghost" size="lg">How creators earn</Button> : null}
          </div>
        </section>
      )}

      <SubjectChips chosen={chosen} query={query} />

      {narrowed ? (
        <Section first title={query ? `Results for “${query}”${chosen ? ` in ${subjectName(chosen)}` : ""}` : subjectName(chosen)}
          aside={`${videos.length} ${videos.length === 1 ? "video" : "videos"}`}>
          {videos.length ? <VideoGrid videos={videos} /> : (
            <EmptyState icon="search" title="Nothing here yet" text="Try another word, or make the first video on this topic."
              action={<Button href={WAITLIST ? "/#waitlist" : "/dashboard"} variant="primary">{WAITLIST ? "Make videos like these" : "Make a video"}</Button>} />
          )}
        </Section>
      ) : shelves.length ? (
        shelves.map((shelf, i) => (
          <Section key={shelf.id} first={i === 0} title={shelf.name} href={shelf.videos.length > 4 ? subjectLink(shelf.id) : undefined}
            aside={shelf.videos.length > 4 ? `See all ${shelf.videos.length}` : undefined}>
            <VideoGrid videos={shelf.videos.slice(0, 4)} />
          </Section>
        ))
      ) : (
        <EmptyState title="No public videos yet" text="The first one could be yours." action={<Button href={WAITLIST ? "/#waitlist" : "/dashboard"} variant="primary">{WAITLIST ? "Make videos like these" : "Make a video"}</Button>} />
      )}
    </Container>
  );
}
