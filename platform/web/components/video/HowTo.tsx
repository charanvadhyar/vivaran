import { Card } from "../ui/Card";
import { Tabs } from "../ui/Tabs";
import styles from "./HowTo.module.css";

const ASK = <li><span>Ask: <strong>“Make a 3 minute Telugu video on Dijkstra’s algorithm with a worked example.”</strong> It will ask about voice and length, show an outline, and render.</span></li>;
const CHECK = <li><span>Watch it here, check every step, then make it public.</span></li>;

/** How to connect, one tab per app. */
export function HowTo() {
  return (
    <Card title="How to make a video">
      <Tabs tabs={[
        { label: "Claude", content: (
          <ol className={styles.list}>
            <li><span>Open <strong>Settings → Connectors → Add custom connector</strong> and paste your address.</span></li>
            <li><span>In a chat, enable the <strong>Vivaran</strong> connector.</span></li>
            {ASK}{CHECK}
          </ol>
        ) },
        { label: "ChatGPT", content: (
          <ol className={styles.list}>
            <li><span>Open <strong>Settings</strong> and turn on <strong>Developer mode</strong>.</span></li>
            <li><span>Create an app for a remote MCP server, paste your address, and choose <strong>No authentication</strong>.</span></li>
            {ASK}{CHECK}
          </ol>
        ) },
      ]} />
    </Card>
  );
}
