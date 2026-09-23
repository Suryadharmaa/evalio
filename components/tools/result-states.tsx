import type { ReactNode } from "react";

import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Skeleton } from "@/components/ui/skeleton";

export function EmptyResult({ action, description = "Add your input to see a transparent result.", title = "No result yet" }: { action?: ReactNode; description?: string; title?: string }) {
  return <EmptyState action={action} description={description} title={title} />;
}

export function LoadingResult({ label = "Analyzing your input" }: { label?: string }) {
  return (
    <div aria-busy="true" aria-live="polite" className="rounded-[var(--radius-lg)] border border-border bg-white p-6" role="status">
      <span className="sr-only">{label}</span>
      <Skeleton className="h-4 w-28" />
      <Skeleton className="mt-5 h-14 w-44" />
      <Skeleton className="mt-6 h-20 w-full" />
    </div>
  );
}

export function ErrorResult({ action, message = "Your input has not changed. Try the analysis again.", title = "We couldn't load this result" }: { action?: ReactNode; message?: string; title?: string }) {
  return <ErrorState action={action} message={message} title={title} />;
}
