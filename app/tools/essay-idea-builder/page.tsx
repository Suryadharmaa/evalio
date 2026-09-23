import type { Metadata } from "next";

import { EssayIdeaBuilder } from "@/components/evaluation/essay-idea-builder";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { Card } from "@/components/ui/card";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "College Essay Idea Builder | Evalio",
  description: "Combine your real moments, tensions, values, and changes into deterministic essay brainstorming directions.",
};

const relatedTools = toolCatalog.filter((tool) => ["essay-evaluator", "writing-pattern-checker", "activity-evaluator"].includes(tool.slug));

export default function EssayIdeaBuilderPage() {
  return (
    <div className="site-container py-14 sm:py-20">
      <ToolHeader description="Turn your real experiences into structured story directions without generating a finished essay." eyebrow="Guided, deterministic brainstorming" title="Essay Idea Builder" />
      <EssayIdeaBuilder />

      <div className="mt-24"><ToolHowItWorks steps={[
        { title: "Add real evidence", description: "List specific moments, tensions, values, and changes from your own experience." },
        { title: "Build combinations", description: "A versioned rule combines only submitted details into three to eight distinct directions." },
        { title: "Explore, then write", description: "Use the questions to find detail and reflection before drafting in your own words." },
      ]} /></div>

      <section className="mt-20 grid gap-5 border-y border-border py-12 lg:grid-cols-[1fr_0.7fr]" aria-labelledby="idea-methodology-title">
        <div><p className="eyebrow">Methodology</p><h2 className="mt-3 text-3xl font-extrabold tracking-[-0.04em]" id="idea-methodology-title">Your evidence stays visible.</h2><p className="mt-4 max-w-2xl leading-7 text-muted">Directions are stable combinations of moment, tension, value, and change. Editing an input predictably changes the combinations.</p><div className="mt-4"><MethodologyLink href="/methodology/essay-ideas" /></div></div>
        <Card className="p-5"><p className="font-extrabold">No generated essay</p><p className="mt-2 text-sm leading-6 text-muted">The builder outputs planning fields and follow-up questions only. It does not produce paragraphs for submission.</p></Card>
      </section>
      <div className="mt-16"><RelatedTools tools={relatedTools} /></div>
    </div>
  );
}
