import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

const methods = [
  { title: "Academic Strength", version: "academic-1.1.0", measured: "School-scale performance, OLS trend, canonical core-area rigor relative to availability, context, and major preparation.", weights: "45% performance · 30% rigor · 10% trend · 10% context · 5% major preparation", excluded: "No forced international-to-US GPA conversion." },
  { title: "Activity Portfolio", version: "activity-1.1.0", measured: "Evidence-backed impact, responsibility, duration, initiative, commitment, recognition, and progression.", weights: "Top activities weighted 30% · 25% · 20% · 15% · remaining 10%", excluded: "Founder titles require responsibility evidence; titles and activity count alone do not increase scores." },
  { title: "Honor Evaluation", version: "honor-1.1.0", measured: "Scope, documented selectivity, placement, major-linked academic relevance, and recurrence.", weights: "30% scope · 25% selectivity · 20% placement · 15% relevance · 10% recurrence", excluded: "Award-name prestige is never inferred." },
  { title: "Mechanical Essay Score", version: "essay-1.0.0", measured: "Compliance, clarity, structure, textual specificity/reflection signals, voice indicators, variety, and style hygiene.", weights: "10% · 15% · 15% · 15% · 15% · 10% · 10% · 10%", excluded: "Does not measure authenticity, emotion, personality, or reviewer reaction." },
  { title: "Recommendation Signals", version: "lor-1.0.0", measured: "Relationship context, concrete evidence, academic/community language, comparison evidence, and generic-praise control.", weights: "20% · 30% · 15% · 10% · 15% · 10%", excluded: "Does not infer recommender intent or applicant character beyond entered text." },
  { title: "Recommendation Framework Builder", version: "lor-builder-1.0.0", measured: "Placement of supplied relationship facts, qualities, examples, comparisons, and endorsement intent into five editable sections.", weights: "No score; deterministic templates and explicit source-field labels only.", excluded: "No invented anecdotes, awards, rankings, or final recommender wording." },
  { title: "Testing Context", version: "academic-1.1.0", measured: "A saved score only gains meaning against a college's current policy and published range.", weights: "Excluded when optional and absent; incomplete when required and absent.", excluded: "No standalone admission probability is derived from a test score." },
  { title: "College Evaluation", version: "college-1.1.0", measured: "Academic alignment, CDS-weighted application strength, requirements, financial fit, institution-level selectivity, and data confidence.", weights: "CDS importance maps to 1.00 / 0.70 / 0.35 / 0.00; unavailable signals are excluded and reduce confidence.", excluded: "No exact acceptance probability and no guaranteed/safety label." },
  { title: "Application Audit", version: "application-1.1.0", measured: "Required and optional material completion, explicit evaluation date, deadlines, and separate quality-evaluation status.", weights: "Required items determine readiness; incomplete quality remains visible.", excluded: "Completeness never substitutes for material quality." },
];

export default function MethodologyPage() {
  return (
    <div className="site-container max-w-6xl py-12 sm:py-16">
      <p className="eyebrow">Public methodology</p><h1 className="mt-3 text-4xl font-extrabold tracking-[-0.05em] sm:text-5xl">How Evalio evaluates.</h1><p className="mt-4 max-w-3xl text-lg leading-8 text-muted">Same input + same data snapshot + same rule version = same result. Every score is an internal planning metric with inspectable rules and evidence.</p>
      <div className="mt-10 grid gap-5">{methods.map((method) => <Card className="lift-card p-6 sm:p-8" key={method.title}><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-extrabold tracking-[-0.03em]">{method.title}</h2><StatusBadge tone="info">{method.version}</StatusBadge></div><dl className="mt-6 grid gap-5 border-t border-border pt-6 text-sm sm:grid-cols-3"><div><dt className="font-bold">Measured</dt><dd className="mt-2 leading-6 text-muted">{method.measured}</dd></div><div><dt className="font-bold">Formula</dt><dd className="mt-2 leading-6 text-muted">{method.weights}</dd></div><div><dt className="font-bold">Not measured</dt><dd className="mt-2 leading-6 text-muted">{method.excluded}</dd></div></dl></Card>)}</div>
    </div>
  );
}
