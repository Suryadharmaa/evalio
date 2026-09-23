import type { Metadata } from "next";

import { GpaToolkit } from "@/components/evaluation/gpa-toolkit";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = { title: "GPA Toolkit | Evalio", description: "Calculate weighted, unweighted, cumulative, percentage, and international academic averages transparently." };
const relatedTools = toolCatalog.filter((tool) => ["coursework-evaluator", "application-evaluator", "colleges"].includes(tool.slug));

export default function GpaPage() {
  return <div className="site-container py-14 sm:py-20">
    <ToolHeader description="Calculate US GPAs or preserve international grades on their original scale—with every method and formula visible." eyebrow="Transparent academic calculation" title="GPA Toolkit" />
    <GpaToolkit />
    <div className="mt-24"><ToolHowItWorks steps={[{ title: "Choose the grading context", description: "Use US course grades or an international/custom percentage scale." }, { title: "Select weighting explicitly", description: "Weighted GPA uses only the method you select; no universal weighting rule is assumed." }, { title: "Inspect the math", description: "Review the exact formula and every row used in the result." }]} /></div>
    <div className="mt-8"><MethodologyLink href="/methodology/gpa" /></div>
    <div className="mt-16"><RelatedTools tools={relatedTools} /></div>
  </div>;
}
