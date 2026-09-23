import type { HTMLAttributes } from "react";

import { cx } from "@/lib/utils/cx";

type Tone = "neutral" | "success" | "warning" | "danger" | "info";

const tones: Record<Tone, string> = {
  neutral: "bg-[var(--surface-muted)] text-muted",
  success: "bg-[var(--success-soft)] text-[var(--success-foreground)]",
  warning: "bg-[var(--warning-soft)] text-[var(--warning)]",
  danger: "bg-[var(--danger-soft)] text-[var(--danger)]",
  info: "bg-[var(--info-soft)] text-[var(--info)]",
};

interface StatusBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function StatusBadge({ className, tone = "neutral", ...props }: StatusBadgeProps) {
  return <span className={cx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.6875rem] font-bold uppercase tracking-[0.06em] before:size-1.5 before:rounded-full before:bg-current", tones[tone], className)} {...props} />;
}

export const ConfidenceBadge = StatusBadge;
