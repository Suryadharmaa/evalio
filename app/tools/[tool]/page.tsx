import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { EmptyResult, MethodologyLink, RelatedTools, ToolHeader, ToolHowItWorks, ToolInputShell } from "@/components/tools";
import { findTool, toolCatalog } from "@/lib/tools/catalog";
import { LorEvaluator } from "@/components/evaluation/lor-evaluator";
import { ActivityDescriptionAnalyzer } from "@/components/evaluation/activity-description-analyzer";
import { ButtonLink } from "@/components/ui/button";

interface ToolPageProps {
  params: Promise<{ tool: string }>;
}

export const dynamicParams = false;

export function generateStaticParams() {
  return toolCatalog.map((tool) => ({ tool: tool.slug }));
}

export async function generateMetadata({ params }: ToolPageProps): Promise<Metadata> {
  const { tool: slug } = await params;
  const tool = findTool(slug);
  if (!tool) return {};

  return {
    title: `${tool.name} | Evalio`,
    description: tool.description,
  };
}

export default async function PlannedToolPage({ params }: ToolPageProps) {
  const { tool: slug } = await params;
  const tool = findTool(slug);
  if (!tool) notFound();

  const related = toolCatalog.filter((candidate) => candidate.group === tool.group && candidate.slug !== tool.slug);

  if (slug === "lor-evaluator" || slug === "activity-evaluator") return <div className="site-container py-14 sm:py-20"><ToolHeader title={tool.name} eyebrow={slug === "lor-evaluator" ? "Recommendation letter" : "Activities"} description={tool.description} />{slug === "lor-evaluator" ? <LorEvaluator /> : <><ActivityDescriptionAnalyzer /><div className="mt-6 border-y border-border py-6"><p className="text-sm text-muted">The public tool analyzes descriptions. Full activity and portfolio evaluation uses your saved profile.</p><ButtonLink className="mt-3" href="/profile/activities" variant="secondary">Evaluate saved activities →</ButtonLink></div></>}<div className="mt-12"><MethodologyLink href={slug === "lor-evaluator" ? "/methodology/lor" : "/methodology/activities"} /><RelatedTools tools={related} /></div></div>;

  return (
    <div className="site-container py-14 sm:py-20">
      <ToolHeader description={tool.description} title={tool.name} />

      <div className="mt-12 grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
        <ToolInputShell
          description="Verified scholarship search and account-based tracking are not connected yet. No awards, deadlines, or saved statuses are fabricated."
          footer={<p className="text-sm text-muted">No input is collected or stored on this page.</p>}
          title="Tool not enabled yet"
        >
          <p className="leading-7 text-muted">
            Planned discovery includes international eligibility, award amount, deadline, need or merit basis, and major restrictions. Until the verified directory is available, research aid through college profiles and official sources.
          </p>
        </ToolInputShell>
        <EmptyResult
          description={`The ${tool.name} result will become available when ${tool.milestone} is implemented.`}
          title="No analysis available"
        />
      </div>
      {slug === "scholarships" && <section className="mt-8 border-y border-border py-6"><p className="eyebrow">Planned tracking workflow · Not enabled</p><ol className="mt-4 flex flex-wrap gap-2">{["Saved", "Researching", "Applying", "Submitted", "Finalist", "Won", "Rejected", "Expired"].map((status) => <li className="rounded-full border border-border px-3 py-2 text-sm text-muted" key={status}>{status}</li>)}</ol><ButtonLink className="mt-6" href="/colleges" variant="secondary">Research college financial aid →</ButtonLink></section>}

      <div className="mt-20">
        <ToolHowItWorks steps={[
          { title: "Input", description: "Provide only the evidence needed for the selected tool." },
          { title: "Analyze", description: "Versioned server-side rules calculate a deterministic result." },
          { title: "Understand", description: "Trace the result through evidence, rules, and explanations." },
        ]} />
      </div>

      <section className="mt-20 border-y border-border py-10" aria-labelledby="methodology-title">
        <p className="eyebrow">Methodology</p>
        <h2 className="mt-3 text-2xl font-extrabold" id="methodology-title">No hidden scoring logic</h2>
        <p className="mt-3 max-w-2xl leading-7 text-muted">Tool-specific formulas will live on the server and remain traceable to documented rules.</p>
        <div className="mt-4"><MethodologyLink /></div>
      </section>

      {related.length ? <div className="mt-16"><RelatedTools tools={related} /></div> : null}
    </div>
  );
}
