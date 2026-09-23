import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "@/lib/utils/cx";

type AlertTone = "info" | "success" | "warning" | "danger";

const tones: Record<AlertTone, string> = {
  info: "border-[var(--info)]/25 bg-[var(--info-soft)] text-[var(--info)]",
  success: "border-[var(--success)]/25 bg-[var(--success-soft)] text-[var(--success)]",
  warning: "border-[var(--warning)]/25 bg-[var(--warning-soft)] text-[var(--warning)]",
  danger: "border-[var(--danger)]/25 bg-[var(--danger-soft)] text-[var(--danger)]",
};

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  tone?: AlertTone;
  children?: ReactNode;
}

export function Alert({ children, className, title, tone = "info", ...props }: AlertProps) {
  return (
    <div className={cx("rounded-lg border border-l-[3px] p-4", tones[tone], className)} role={tone === "danger" ? "alert" : "status"} {...props}>
      <p className="font-semibold">{title}</p>
      {children ? <div className="mt-1 text-sm leading-6">{children}</div> : null}
    </div>
  );
}
