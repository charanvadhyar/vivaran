"use client";

import { useState, useTransition } from "react";
import { Alert } from "../ui/Alert";
import { Button } from "../ui/Button";
import styles from "./JsonForm.module.css";

/** Edit a JSON setting in place, with the save result shown under it. */
export function JsonForm({ name, label, help, initial, save }:
  { name: string; label: string; help: string; initial: string; save: (form: FormData) => Promise<{ ok: boolean; message: string }> }) {
  const [note, setNote] = useState<{ ok: boolean; message: string } | null>(null);
  const [pending, start] = useTransition();
  return (
    <form className={styles.form} action={(data) => start(async () => setNote(await save(data)))}>
      <label className={styles.label} htmlFor={`json-${name}`}>{label}</label>
      <p className={styles.help}>{help}</p>
      <textarea id={`json-${name}`} name={name} defaultValue={initial} className={styles.area} spellCheck={false}
        rows={Math.min(40, initial.split("\n").length + 2)} />
      <div><Button type="submit" variant="primary" loading={pending}>Save</Button></div>
      {note ? <Alert tone={note.ok ? "info" : "danger"}>{note.message}</Alert> : null}
    </form>
  );
}
