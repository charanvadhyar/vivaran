"use client";

import { useEffect, useRef, type ReactNode } from "react";
import styles from "./Dialog.module.css";

/** A modal built on the native <dialog>, so focus, Escape and the backdrop come for free. */
export function Dialog({ open, onClose, title, children, actions }:
  { open: boolean; onClose: () => void; title: string; children?: ReactNode; actions?: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);
  return (
    <dialog ref={ref} className={styles.dialog} onClose={onClose}
      onClick={(e) => { if (e.target === ref.current) onClose(); }}>
      <div className={styles.body}>
        <h2>{title}</h2>
        {children}
        {actions ? <div className={styles.actions}>{actions}</div> : null}
      </div>
    </dialog>
  );
}
