"use client";

import { useState } from "react";
import { Button } from "../ui/Button";
import { Dialog } from "../ui/Dialog";
import { Icon } from "../ui/Icon";

/** Delete, with a confirmation first: deleting is the one thing here that cannot be undone. */
export function DeleteButton({ id, title, action }: { id: string; title: string; action: (form: FormData) => Promise<void> }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="danger" icon={<Icon name="trash" />} onClick={() => setOpen(true)}>Delete</Button>
      <Dialog open={open} onClose={() => setOpen(false)} title="Delete this video?"
        actions={
          <>
            <Button onClick={() => setOpen(false)}>Keep it</Button>
            <form action={action}>
              <input type="hidden" name="id" value={id} />
              <Button type="submit" variant="danger">Delete</Button>
            </form>
          </>
        }>
        <p>“{title}” will be removed from your account and from the site. This cannot be undone.</p>
      </Dialog>
    </>
  );
}
