import { Button } from "../ui/Button";
import styles from "./Earn.module.css";

/** The creator deal in one screen: free to make, yours to keep, paid by views. */
export function Earn() {
  return (
    <div className={styles.earn}>
      <div className={styles.points}>
        <p><strong>Making videos is free.</strong> They render silently first so you can check every step; voice is added when you publish.</p>
        <p><strong>You own what you make.</strong> Published videos go on the Vivaran YouTube channel with your name in the title, on the end card and in the watermark.</p>
        <p><strong>You are paid for views</strong> from the first one, before the channel earns anything itself, and you share the ad revenue once it does.</p>
        <div><Button href="/terms">Read the creator terms</Button></div>
      </div>
      <div className={styles.rates}>
        <div className={styles.rate}><b>₹50</b><span>per 1,000 YouTube views</span></div>
        <div className={styles.rate}><b>₹500</b><span>bonus when a video passes 10,000 views</span></div>
        <div className={styles.rate}><b>50%</b><span>of net ad revenue from your videos, once the channel is monetised</span></div>
      </div>
    </div>
  );
}
