"use client";

import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import styles from "./Toast.module.css";

type Toast = { id: number; text: string; icon?: IconName };
const ToastContext = createContext<(text: string, icon?: IconName) => void>(() => {});

/** Wrap the app once; then `useToast()("Copied")` anywhere. */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const show = useCallback((text: string, icon?: IconName) => {
    const id = Date.now() + Math.random();
    setToasts((all) => [...all, { id, text, icon }]);
    setTimeout(() => setToasts((all) => all.filter((t) => t.id !== id)), 2200);
  }, []);
  return (
    <ToastContext.Provider value={show}>
      {children}
      <div className={styles.region} role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={styles.toast}>
            {t.icon ? <Icon name={t.icon} className={styles.positive} /> : null}
            {t.text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
