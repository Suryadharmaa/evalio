import type { Metadata } from "next";

import { WritingPatternChecker } from "@/components/evaluation/writing-pattern-checker";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { Card } from "@/components/ui/card";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "Writing Pattern Checker | Evalio",
  description: "Inspect reproducible rhythm, detail, language, and perspective patterns without AI-authorship claims.",
};

const relatedTools = toolCatalog.filter((tool) => ["essay-evaluator", "essay-idea-builder", "lor-evaluator"].includes(tool.slug));

export default function WritingPatternCheckerPage() {
  return (
    <div className="site-container py-14 sm:py-20">
      <ToolHeader
        description="Inspect reproducible rhythm, detail, language, and perspective signals in a piece of writing."
        eyebrow="Deterministic pattern analysis"
        title="Writing Pattern Checker"
      />
      <WritingPatternChecker />

      <div className="mt-24">
        <ToolHowItWorks steps={[
          { title: "Paste a sample", description: "Use enough prose for sentence-, paragraph-, and vocabulary-level measurements." },
          { title: "Run 25 checks", description: "Versioned rules compare observed metrics with thresholds shown in the result." },
          { title: "Review patterns", description: "Use evidence as an editing prompt—not as a judgment of authorship or quality." },
        ]} />
      </div>

      <section className="mt-20 grid gap-5 border-y border-border py-12 lg:grid-cols-[1fr_0.7fr]" aria-labelledby="pattern-methodology-title">
        <div>
          <p className="eyebrow">Methodology</p>
          <h2 className="mt-3 text-3xl font-extrabold tracking-[-0.04em]" id="pattern-methodology-title">Metrics, thresholds, evidence.</h2>
          <p className="mt-4 max-w-2xl leading-7 text-muted">Every signal reports its observed value and trigger threshold. Unavailable checks are marked as insufficient data rather than assumed normal.</p>
          <div className="mt-4"><MethodologyLink href="/methodology/writing-patterns" /></div>
        </div>
        <Card className="p-5">
          <p className="font-extrabold">Mandatory limitation</p>
          <p className="mt-2 text-sm leading-6 text-muted">This tool identifies measurable writing patterns. It cannot determine who or what wrote a text.</p>
        </Card>
      </section>

      <div className="mt-16"><RelatedTools tools={relatedTools} /></div>
    </div>
  );
}
