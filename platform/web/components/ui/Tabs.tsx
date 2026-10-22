"use client";

import { useId, useState, type ReactNode } from "react";
import styles from "./Tabs.module.css";

/** Tabs with keyboard support (left and right arrows). */
export function Tabs({ tabs, initial = 0 }: { tabs: { label: string; content: ReactNode }[]; initial?: number }) {
  const [active, setActive] = useState(initial);
  const id = useId();
  return (
    <div>
      <div role="tablist" className={styles.list}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight") setActive((a) => (a + 1) % tabs.length);
          if (e.key === "ArrowLeft") setActive((a) => (a - 1 + tabs.length) % tabs.length);
        }}>
        {tabs.map((tab, i) => (
          <button key={tab.label} role="tab" id={`${id}-tab-${i}`} aria-selected={i === active} aria-controls={`${id}-panel-${i}`}
            tabIndex={i === active ? 0 : -1} className={styles.tab} onClick={() => setActive(i)}>
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, i) => (
        <div key={tab.label} role="tabpanel" id={`${id}-panel-${i}`} aria-labelledby={`${id}-tab-${i}`} hidden={i !== active}>
          {tab.content}
        </div>
      ))}
    </div>
  );
}
