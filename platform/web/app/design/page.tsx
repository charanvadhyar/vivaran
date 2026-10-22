import { Container } from "@/components/layout/Container";
import { PageHeader } from "@/components/layout/PageHeader";
import { Section } from "@/components/layout/Section";
import { Alert } from "@/components/ui/Alert";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { CopyField } from "@/components/ui/CopyField";
import { Divider } from "@/components/ui/Divider";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { IconButton } from "@/components/ui/IconButton";
import { Input } from "@/components/ui/Input";
import { Kbd } from "@/components/ui/Kbd";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { Stat, StatGroup } from "@/components/ui/Stat";
import { Tabs } from "@/components/ui/Tabs";
import { Tooltip } from "@/components/ui/Tooltip";
import { Playground } from "./Playground";
import styles from "./page.module.css";

export const metadata = { title: "Design" };

const TOKENS = ["bg-canvas", "bg-surface", "bg-raised", "bg-strong", "fg-default", "fg-muted", "fg-subtle", "border-subtle", "border-default", "border-strong", "accent", "positive", "negative", "info"];

/** Every component, in one place, so a change can be seen everywhere it matters. */
export default function Design() {
  return (
    <Container main>
      <PageHeader title="Design" lead="Vivaran's design system: paper, ink, serif headings and one amber accent used as punctuation. Every component lives in its own file under components/ui." />

      <Section first title="Colour tokens">
        <div className={styles.swatches}>
          {TOKENS.map((t) => (
            <div key={t} className={styles.swatch}>
              <div className={styles.chipColour} style={{ background: `var(--${t})` }} />
              <code>--{t}</code>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Type">
        <div className={styles.type}>
          <h1>Every step, shown.</h1>
          <h2>Section heading</h2>
          <h3>Card heading</h3>
          <p>Body text at 16px with a 1.6 line height, for reading explanations in Telugu, Hindi and English: ప్రతి step explain చేస్తాం · हर step explain करते हैं.</p>
          <p style={{ color: "var(--fg-muted)" }}>Muted text for secondary information.</p>
          <code>mono for addresses, times and code</code>
        </div>
      </Section>

      <Section title="Buttons">
        <div className={styles.row}>
          <Button variant="primary" icon={<Icon name="spark" />}>Primary</Button>
          <Button>Default</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger" icon={<Icon name="trash" />}>Danger</Button>
          <Button variant="knockout">Knockout</Button>
          <Button loading>Loading</Button>
          <Button disabled>Disabled</Button>
        </div>
        <div className={styles.row}>
          <Button size="sm">Small</Button>
          <Button>Medium</Button>
          <Button size="lg">Large</Button>
          <IconButton icon="copy" label="Copy" outlined />
          <IconButton icon="x" label="Close" />
          <Tooltip text="A tooltip"><IconButton icon="info" label="Information" /></Tooltip>
        </div>
      </Section>

      <Section title="Inputs">
        <div className={styles.grid2}>
          <Input label="Name" placeholder="Asha Rao" hint="Shown on your videos." />
          <Input label="Email" placeholder="you@example.com" error="This does not look like an email address." />
          <div><label className={styles.label}>Subject</label><Select options={[{ value: "dsa", label: "Data Structures" }, { value: "ml", label: "Machine Learning" }]} placeholder="Choose…" defaultValue="" /></div>
          <Playground />
        </div>
      </Section>

      <Section title="Badges and chips">
        <div className={styles.row}>
          <Badge>Private</Badge><Badge tone="positive">Public</Badge><Badge tone="accent">Rendering</Badge><Badge tone="negative">Failed</Badge><Badge tone="info">New</Badge><Badge tone="solid">Solid</Badge>
        </div>
        <div className={styles.row}>
          <Chip on>All</Chip><Chip>DSA</Chip><Chip>ML</Chip><Chip>DBMS</Chip>
        </div>
      </Section>

      <Section title="Cards, stats, tabs">
        <div className={styles.grid2}>
          <Card title="A card" subtitle="With a subtitle and an aside." aside={<Badge tone="positive">Live</Badge>}>
            <StatGroup><Stat value={12} label="made" /><Stat value={9} label="public" /><Stat value="1.2k" label="views" /></StatGroup>
          </Card>
          <Card title="Tabs">
            <Tabs tabs={[{ label: "Claude", content: <p>Add the connector in Settings.</p> }, { label: "ChatGPT", content: <p>Turn on Developer mode.</p> }]} />
          </Card>
        </div>
      </Section>

      <Section title="Feedback">
        <div className={styles.stack}>
          <Alert tone="note">Keep this address to yourself.</Alert>
          <Alert tone="info">Introductory rates can change with 30 days' notice.</Alert>
          <Alert tone="danger">This render failed: the script has errors.</Alert>
          <ProgressBar label="Rendering" value={0.62} />
          <ProgressBar label="Waiting" />
          <CopyField value="https://vivaran.example/u/abc123/mcp" label="Connector address" />
          <div className={styles.row}><Skeleton width={240} height={135} radius={10} /><div className={styles.stack} style={{ flex: 1 }}><Skeleton height={18} /><Skeleton width="60%" /></div></div>
          <EmptyState title="Nothing here yet" text="Try another word, or make the first video." action={<Button variant="primary">Make a video</Button>} />
        </div>
      </Section>

      <Section title="Small things">
        <div className={styles.row}>
          <Avatar name="Asha Rao" size={48} /><Avatar name="Meena K" size={32} /><Avatar name="R" size={24} />
          <span>Press <Kbd>Space</Kbd> to play, <Kbd>←</Kbd> <Kbd>→</Kbd> to seek</span>
        </div>
        <Divider label="a divider" />
      </Section>
    </Container>
  );
}
