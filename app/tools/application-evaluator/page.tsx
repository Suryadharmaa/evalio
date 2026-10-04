import type { Metadata } from "next";

import { Suspense } from "react";
import { CollegeEvaluatorQuery } from "@/components/college/college-evaluator-query";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "Application Evaluator | Evalio",
  description: "Compare saved application evidence with a college using transparent dimensions, source confidence, and deterministic planning rules.",
};

const relatedTools = toolCatalog.filter((tool) => ["coursework-evaluator", "gpa", "activity-evaluator"].includes(tool.slug));

export default function ApplicationEvaluatorPage() {
  return <div className="site-container py-14 sm:py-20">
    <ToolHeader description="Compare your saved evidence with one college across academic alignment, rigor, activities, honors, testing, requirements, finances, and data confidence." eyebrow="College-specific planning" title="Application Evaluator" />
    <Suspense fallback={<p role="status" className="mt-8 text-muted">Loading evaluator…</p>}><CollegeEvaluatorQuery /></Suspense>
    <div className="mt-24"><ToolHowItWorks steps={[{ title: "Choose evidence", description: "Select a saved profile, target college, and explicit evaluation date." }, { title: "Evaluate dimensions", description: "The server applies versioned academic, CDS, selectivity, requirement, financial, and confidence rules." }, { title: "Inspect the result", description: "Review component scores, N/A values, data cycles, source freshness, reasons, and triggered rules separately." }]} /></div>
    <div className="mt-8"><MethodologyLink href="/methodology/college" label="View methodology" /></div>
    <div className="mt-16"><RelatedTools tools={relatedTools} /></div>
  </div>;
}
