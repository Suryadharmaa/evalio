import type { HTMLAttributes } from "react";

import { cx } from "@/lib/utils/cx";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cx("evalio-surface rounded-[var(--radius-lg)] border border-border bg-white", className)} {...props} />;
}
