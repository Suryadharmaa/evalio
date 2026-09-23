"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { cx } from "@/lib/utils/cx";

/** Progressive enhancement: content is visible even without JS or observers. */
export function Reveal({ children, className }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = ref.current;
    if (!element || !window.IntersectionObserver || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        element.dataset.entered = "true";
        observer.disconnect();
      }
    }, { threshold: .08 });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  return <div className={cx("viewport-reveal", className)} ref={ref}>{children}</div>;
}
