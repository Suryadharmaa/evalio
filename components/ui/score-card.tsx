import Link from "next/link";

import { Card } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/ui/status-badge";
import { cx } from "@/lib/utils/cx";

interface ScoreCardProps {
  className?: string;
  confidence: "High" | "Medium" | "Low";
  description?: string;
  score: number | null;
  title: string;
  methodologyHref?: string;
}

export function ScoreCard({ className, confidence, description, score, title, methodologyHref = "/methodology" }: ScoreCardProps) {
  const tone = confidence === "High" ? "success" : confidence === "Medium" ? "warning" : "neutral";

  return (
    <Card className={cx("overflow-hidden", className)}>
      <div className="border-b border-border bg-[var(--primary-soft)] p-6">
      <p className="hairline-label text-primary">{title}</p>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
        <p className="data-type text-5xl font-bold tracking-[-0.04em]">
          {score === null ? "N/A" : <>{score}<span className="text-lg font-medium text-muted"> / 100</span></>}
        </p>
        <ConfidenceBadge tone={tone}>Confidence: {confidence}</ConfidenceBadge>
      </div>
      </div>
      <div className="p-6">
      {description ? <p className="text-sm leading-6 text-muted">{description}</p> : null}
      <p className="evidence-rail mt-4 rounded-r-lg px-4 py-3 text-xs font-bold uppercase tracking-[0.08em] text-primary">Score → Evidence → Rule → Explanation</p>
      <Link className="mt-5 inline-flex min-h-11 items-center font-bold text-primary hover:text-[var(--primary-hover)]" href={methodologyHref}>
        Why this score? <span aria-hidden="true" className="ml-1">→</span>
      </Link>
      </div>
    </Card>
  );
}
