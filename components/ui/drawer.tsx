"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { Button } from "@/components/ui/button";

export function Drawer({ children, onClose, open, title }: { children: ReactNode; onClose: () => void; open: boolean; title: string }) {
  const ref = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!open) return;
    ref.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose, open]);
  if (!open) return null;
  return <aside aria-labelledby="drawer-title" aria-modal="true" className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-auto border-l border-border bg-white p-6 shadow-[var(--shadow-md)]" ref={ref} role="dialog" tabIndex={-1}><div className="flex items-center justify-between gap-4"><h2 className="text-xl font-bold" id="drawer-title">{title}</h2><Button aria-label="Close drawer" onClick={onClose} variant="ghost">Close</Button></div><div className="mt-5">{children}</div></aside>;
}
