import { notFound } from "next/navigation";
import { Container } from "@/components/layout/Container";
import { EmptyState } from "@/components/ui/EmptyState";
import { CreatorHeader } from "@/components/video/CreatorHeader";
import { VideoGrid } from "@/components/video/VideoGrid";
import { userByHandle } from "@/lib/users";
import { publicVideosOf } from "@/lib/videos";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ handle: string }> }) {
  const creator = await userByHandle((await params).handle);
  return { title: creator?.name ?? "Creator" };
}

export default async function Creator({ params }: { params: Promise<{ handle: string }> }) {
  const creator = await userByHandle((await params).handle);
  if (!creator) notFound();
  const videos = await publicVideosOf(creator.id);
  const views = videos.reduce((sum, v) => sum + v.views, 0);
  return (
    <Container main>
      <CreatorHeader name={creator.name} image={creator.image}
        meta={`${videos.length} public ${videos.length === 1 ? "video" : "videos"} · ${views} ${views === 1 ? "view" : "views"}`} />
      {videos.length ? <VideoGrid videos={videos} /> : <EmptyState title="No public videos yet" />}
    </Container>
  );
}
