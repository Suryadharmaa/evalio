import type { Metadata } from "next";

import { LorBuilder } from "@/components/evaluation/lor-builder";
import { MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks } from "@/components/tools";
import { toolCatalog } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "Recommendation Letter Builder | Evalio",
  description: "Organize recommender-provided facts into an editable, traceable letter framework without invented anecdotes or AI-generated claims.",
};

const relatedTools = toolCatalog.filter((tool) => ["lor-evaluator", "essay-idea-builder", "application-evaluator"].includes(tool.slug));

export default function LorBuilderPage() {
  return <div className="site-container py-14 sm:py-20"><ToolHeader description="Turn verified relationship context, qualities, examples, and endorsement intent into a structured recommendation-letter outline." eyebrow="Grounded recommendation planning" title="LOR Builder" /><LorBuilder /><div className="mt-24"><ToolHowItWorks steps={[{ title: "Supply observed facts", description: "Enter only relationship details, qualities, and examples the recommender can verify." }, { title: "Build a framework", description: "Deterministic templates organize those facts into opening, body, comparison, and closing sections." }, { title: "Recommender rewrites", description: "Edit the framework and let the recommender own every final sentence and claim." }]} /></div><div className="mt-8"><MethodologyLink href="/methodology/lor-builder" label="View methodology" /></div><div className="mt-16"><RelatedTools tools={relatedTools} /></div></div>;
}
