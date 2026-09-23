import Link from "next/link";

import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

interface RuleFindingProps {
  evidence?: string;
  explanation: string;
  confidence?: "HIGH" | "MEDIUM" | "LOW";
  methodologyLink?: string;
  ruleId: string;
  scoreEffect?: string;
  severity: string;
  title: string;
}

export function RuleFinding({ confidence, evidence, explanation, methodologyLink = "/methodology", ruleId, scoreEffect, severity, title }: RuleFindingProps) {
  const tone = severity === "CRITICAL" || severity === "HIGH" ? "danger" : severity === "INFO" ? "info" : "warning";

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-border bg-[var(--surface-muted)] p-5">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge tone={tone}>{severity}</StatusBadge>
        {confidence ? <StatusBadge>Confidence: {confidence}</StatusBadge> : null}
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted">{explanation}</p>
      </div>
      <details className="evidence-disclosure p-5">
      <summary>Why this matters</summary>
      <dl className="evidence-rail grid gap-3 rounded-r-lg p-4 text-sm sm:grid-cols-3">
        <div><dt className="hairline-label text-primary">Evidence</dt><dd className="mt-1 break-words text-muted">{evidence || "Evidence unavailable"}</dd></div>
        <div><dt className="hairline-label text-primary">Rule</dt><dd className="data-type mt-1 text-muted">{ruleId}</dd></div>
        <div><dt className="hairline-label text-primary">Effect</dt><dd className="mt-1 text-muted">{scoreEffect || "No separate point adjustment"}</dd></div>
      </dl>
      <Link className="quiet-link mt-3 inline-flex min-h-11 items-center text-sm" href={methodologyLink}>View methodology&nbsp;<span aria-hidden="true">→</span></Link>
      </details>
    </Card>
  );
}
