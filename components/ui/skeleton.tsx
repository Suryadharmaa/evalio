import type { HTMLAttributes } from "react";

import { cx } from "@/lib/utils/cx";

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div aria-hidden="true" className={cx("animate-pulse rounded-lg bg-[var(--surface-muted)]", className)} {...props} />;
}

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 text-sm font-medium text-muted" role="status">
      <span className="size-5 animate-spin rounded-full border-2 border-border border-t-primary" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
