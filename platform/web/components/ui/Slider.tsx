"use client";

import { useId } from "react";
import styles from "./Slider.module.css";

/** A range control with its label and current value shown. */
export function Slider({ label, value, min, max, step = 1, onChange, format = (v) => String(v), id }:
  { label: string; value: number; min: number; max: number; step?: number; onChange: (value: number) => void;
    format?: (value: number) => string; id?: string }) {
  const auto = useId();
  const inputId = id ?? auto;
  const fill = `${((value - min) / (max - min)) * 100}%`;
  return (
    <div className={styles.slider}>
      <div className={styles.head}>
        <label htmlFor={inputId}>{label}</label>
        <output htmlFor={inputId} className={styles.value}>{format(value)}</output>
      </div>
      <input id={inputId} type="range" className={styles.input} min={min} max={max} step={step} value={value}
        style={{ "--fill": fill } as React.CSSProperties} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}
