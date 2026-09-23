import type { Metadata } from "next";

import { CourseworkEvaluator } from "@/components/evaluation/coursework-evaluator";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = { title: "Coursework Evaluator | Evalio", description: "Evaluate course rigor against documented school opportunities with visible evidence and rules." };
const related = toolCatalog.filter((tool) => ["gpa", "application-evaluator", "activity-evaluator"].includes(tool.slug));

export default function CourseworkEvaluatorPage() {
  return <div className="site-container py-14 sm:py-20"><ToolHeader description="Evaluate challenge, coverage, progression, and major preparation against what your school actually offers." eyebrow="Context-aware academic rigor" title="Coursework Evaluator" /><CourseworkEvaluator /><div className="mt-24"><ToolHowItWorks steps={[{ title: "Document opportunity", description: "Report the curriculum, highest levels, and advanced courses offered by the school." }, { title: "Compare coursework", description: "Versioned rigor rules compare courses taken with those explicit opportunities." }, { title: "Inspect every component", description: "Review evidence, rule, point effect, context, and confidence behind the result." }]} /></div><div className="mt-8"><MethodologyLink href="/methodology/coursework" /></div><div className="mt-16"><RelatedTools tools={related} /></div></div>;
}
