import type { Metadata } from "next";

import { HybridEssayAnalyzer } from "@/components/evaluation/hybrid-essay-analyzer";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { Card } from "@/components/ui/card";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "College Essay Evaluator | Evalio",
  description: "Get concise semantic essay feedback with transparent writing signals and optional paragraph review.",
};

const relatedTools = toolCatalog.filter((tool) => ["writing-pattern-checker", "essay-idea-builder", "gpa"].includes(tool.slug));

export default function EssayEvaluatorPage() {
  return (
    <div className="site-container py-14 sm:py-20">
      <ToolHeader
        description="Understand what works in your essay, what to revise first, and which writing patterns are measurable."
        eyebrow="Hybrid essay review"
        title="College Essay Evaluator"
      />

      <HybridEssayAnalyzer />

      <div className="mt-24">
        <ToolHowItWorks steps={[
          { title: "Add your draft", description: "Paste 50 to 5,000 words. Your text is validated before analysis." },
          { title: "Read one clear review", description: "One structured AI response scores six essay dimensions and supplies concise feedback." },
          { title: "Revise with context", description: "Inspect locally measured writing signals, then request paragraph feedback only if useful." },
        ]} />
      </div>

      <section className="mt-20 grid gap-5 border-y border-border py-12 lg:grid-cols-[1fr_0.7fr] lg:items-start" aria-labelledby="essay-methodology-title">
        <div>
          <p className="eyebrow">Methodology</p>
          <h2 className="mt-3 text-3xl font-extrabold tracking-[-0.04em]" id="essay-methodology-title">Essay feedback with visible boundaries.</h2>
          <p className="mt-4 max-w-2xl leading-7 text-muted">The score comes from a six-category writing rubric. Word count, readability, repetition, and other writing signals are calculated separately. This review does not predict admission.</p>
          <div className="mt-4"><MethodologyLink href="/methodology/essay" /></div>
        </div>
        <Card className="p-5">
          <p className="text-sm font-extrabold">Privacy default</p>
          <p className="mt-2 text-sm leading-6 text-muted">The review sends your essay to the configured AI provider. Evalio caches the result and text hash without storing the raw essay. Deep Review sends the essay again only when you request it.</p>
        </Card>
      </section>

      <div className="mt-16"><RelatedTools tools={relatedTools} /></div>
    </div>
  );
}
