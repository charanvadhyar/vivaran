"use client";

import { Button } from "./Button";
import { Icon } from "./Icon";
import { useToast } from "./Toast";
import styles from "./CopyField.module.css";

/** A value in a box with a Copy button. Says "Copied" in a toast. */
export function CopyField({ value, label }: { value: string; label: string }) {
  const toast = useToast();
  return (
    <div className={styles.field}>
      <code className={styles.value} aria-label={label} tabIndex={0}>{value}</code>
      <Button icon={<Icon name="copy" />} onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          toast("Copied", "check");
        } catch {
          // No clipboard access (an http page, or a locked-down browser): select it for a manual copy.
          const range = document.createRange();
          const node = document.querySelector<HTMLElement>(`[aria-label="${label}"]`);
          if (node) { range.selectNodeContents(node); getSelection()?.removeAllRanges(); getSelection()?.addRange(range); }
          toast("Press Ctrl+C to copy");
        }
      }}>
        Copy
      </Button>
    </div>
  );
}
