import type { ReactNode } from "react";

import { Card } from "@/components/ui/card";
import { cx } from "@/lib/utils/cx";

interface ToolInputShellProps {
  children: ReactNode;
  className?: string;
  description?: string;
  footer?: ReactNode;
  title: string;
}

export function ToolInputShell({ children, className, description, footer, title }: ToolInputShellProps) {
  return (
    <Card className={cx("overflow-hidden shadow-[var(--shadow-sm)]", className)}>
      <div className="border-b border-border bg-[var(--surface-muted)] px-5 py-5 sm:px-7">
        <p className="hairline-label text-primary">Input evidence</p>
        <h2 className="mt-1.5 text-xl font-semibold tracking-[-0.015em]">{title}</h2>
        {description ? <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p> : null}
      </div>
      <div className="p-5 sm:p-7">{children}</div>
      {footer ? <div className="border-t border-border bg-[var(--primary-soft)] px-5 py-4 sm:px-7">{footer}</div> : null}
    </Card>
  );
}
