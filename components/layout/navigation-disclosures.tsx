"use client";

import { useEffect, useRef, type ReactNode } from "react";

/** Enhance native disclosures without making the server-rendered shell client-only. */
export function NavigationDisclosures({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function outside(event: PointerEvent) {
      if (!ref.current?.contains(event.target as Node)) ref.current?.querySelectorAll<HTMLDetailsElement>("details[open]").forEach((item) => { item.open = false; });
    }
    document.addEventListener("pointerdown", outside);
    return () => document.removeEventListener("pointerdown", outside);
  }, []);
  return <div ref={ref} className="contents" onKeyDown={(event) => {
    if (event.key !== "Escape") return;
    const detail = (event.target as HTMLElement).closest<HTMLDetailsElement>("details[open]");
    if (detail) { detail.open = false; detail.querySelector("summary")?.focus(); event.stopPropagation(); }
  }} onClick={(event) => {
    if ((event.target as HTMLElement).closest("a")) ref.current?.querySelectorAll<HTMLDetailsElement>("details[open]").forEach((item) => { item.open = false; });
  }}>{children}</div>;
}
