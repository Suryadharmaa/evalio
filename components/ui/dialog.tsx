"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";
import { Button } from "@/components/ui/button";

export function Dialog({ children, onClose, open, title }: { children: ReactNode; onClose: () => void; open: boolean; title: string }) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);
  return <dialog aria-labelledby={titleId} className="m-auto max-h-[90vh] w-[calc(100%-2.5rem)] max-w-xl overflow-auto rounded-xl bg-white p-6 text-foreground shadow-[var(--shadow-md)] backdrop:bg-black/45" onCancel={onClose} onClose={onClose} ref={ref}><div className="flex items-start justify-between gap-4"><h2 id={titleId} className="text-xl font-bold">{title}</h2><Button aria-label="Close dialog" onClick={() => ref.current?.close()} variant="ghost">Close</Button></div><div className="mt-5">{children}</div></dialog>;
}
