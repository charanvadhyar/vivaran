import { Button } from "../ui/Button";
import styles from "./ConnectBox.module.css";

const SITE = (process.env.SITE_URL ?? "https://vivaran-kappa.vercel.app").replace(/\/$/, "");

/** "Connect in a minute": the three steps and the thing the user pastes into their assistant. */
export function ConnectBox({ signedIn, waitlist = false }: { signedIn: boolean; waitlist?: boolean }) {
  return (
    <div className={styles.box}>
      <div className={styles.steps}>
        <div className={styles.step}><span className={styles.num}>1</span><span><strong>Sign in with Google.</strong> You get a personal connector address.</span></div>
        <div className={styles.step}><span className={styles.num}>2</span><span><strong>Paste it into Claude or ChatGPT</strong> as a custom connector. Once.</span></div>
        <div className={styles.step}><span className={styles.num}>3</span><span><strong>Ask for a video.</strong> It is rendered and saved to your account; you check it and publish.</span></div>
        <div style={{ marginTop: 8 }}>
          {waitlist
            ? <Button href="#waitlist" variant="primary">Join the creator list for an address</Button>
            : <Button href={signedIn ? "/dashboard" : "/login"} variant="primary">{signedIn ? "Open my dashboard" : "Get my connector address"}</Button>}
        </div>
      </div>
      <div className={styles.prompt}>
        <div className={styles.promptHead}><span>what you say to your assistant</span><span>example</span></div>
        <div className={styles.promptBody}>
          Connect to <span className={styles.addr}>{SITE}/u/&lt;your address&gt;/mcp</span>{"\n\n"}
          Then: “Make a 3 minute Telugu video on Dijkstra’s algorithm with a worked example. Ask me about the voice first.”
        </div>
      </div>
    </div>
  );
}
