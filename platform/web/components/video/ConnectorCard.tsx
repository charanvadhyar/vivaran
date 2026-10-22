import { Alert } from "../ui/Alert";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { CopyField } from "../ui/CopyField";
import { Icon } from "../ui/Icon";

/** The creator's connector address, with the warning that it is a secret. */
export function ConnectorCard({ address, local, regenerate }: { address: string; local: boolean; regenerate: () => Promise<void> }) {
  return (
    <Card title="Your connector address" subtitle="Add it to Claude or ChatGPT once. Every video you ask for then lands here.">
      <div style={{ margin: "12px 0" }}><CopyField value={address} label="Connector address" /></div>
      <Alert tone="note">
        Keep this address to yourself: anyone who has it can make videos in your account.
        {local ? " Right now it only works on this computer; Claude and ChatGPT need the site on an https address." : ""}
      </Alert>
      <form action={regenerate} style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 14, flexWrap: "wrap" }}>
        <Button type="submit" icon={<Icon name="refresh" />}>Get a new address</Button>
        <span style={{ color: "var(--fg-subtle)", fontSize: "var(--text-sm)" }}>The old one stops working within a minute.</span>
      </form>
    </Card>
  );
}
