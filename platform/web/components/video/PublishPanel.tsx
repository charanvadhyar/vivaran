import { SUBJECTS } from "@/lib/brand";
import type { Video } from "@/lib/videos";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Icon } from "../ui/Icon";
import { Select } from "../ui/Select";
import { DeleteButton } from "./DeleteButton";
import styles from "./PublishPanel.module.css";

/** What the creator sees under their own video: publish or unpublish, download, delete. */
export function PublishPanel({ video, setPublic, deleteVideo }:
  { video: Video; setPublic: (form: FormData) => Promise<void>; deleteVideo: (form: FormData) => Promise<void> }) {
  const options = SUBJECTS.map((s) => ({ value: s.id, label: s.name }));
  return (
    <Card accent>
      <div className={styles.state}>
        <Badge tone={video.is_public ? "positive" : "neutral"}>{video.is_public ? "Public" : "Private"}</Badge>
        <span>
          {video.is_public
            ? "Anyone can watch this, and it is listed under its subject."
            : "Only you can see this. Watch it through and check each step against the explanation. If it is all correct, choose a subject and make it public."}
        </span>
      </div>
      <div className={styles.row}>
        <form action={setPublic} className={styles.row}>
          <input type="hidden" name="id" value={video.id} />
          <input type="hidden" name="public" value={video.is_public ? "0" : "1"} />
          {video.is_public ? null : <Select name="subject" options={options} placeholder="Subject…" defaultValue={video.subject ?? ""} required aria-label="Subject" />}
          <Button type="submit" variant={video.is_public ? "default" : "primary"} icon={<Icon name={video.is_public ? "lock" : "globe"} />}>
            {video.is_public ? "Make private" : "Make public"}
          </Button>
        </form>
        <Button href={`/api/videos/${video.id}/file`} download={`${video.title}.mp4`} icon={<Icon name="download" />}>Download</Button>
        <DeleteButton id={video.id} title={video.title} action={deleteVideo} />
      </div>
    </Card>
  );
}
