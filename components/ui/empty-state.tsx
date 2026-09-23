import type { ReactNode } from "react";

import { Card } from "@/components/ui/card";

interface EmptyStateProps {
  action?: ReactNode;
  description: string;
  id?: string;
  title: string;
}

export function EmptyState({ action, description, id, title }: EmptyStateProps) {
  return (
    <Card className="grid justify-items-center p-8 text-center sm:p-12">
      <div aria-hidden="true" className="grid size-12 place-items-center rounded-full bg-[var(--primary-soft)] text-xl text-primary">＋</div>
      <h2 id={id} className="mt-5 text-xl font-semibold">{title}</h2>
      <p className="mt-2 max-w-xl leading-7 text-muted">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </Card>
  );
}

