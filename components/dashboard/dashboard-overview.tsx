"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiFetch, apiError, authenticatedFetch } from "@/lib/api/client";
import styles from "@/components/evaluation/analysis-workspace.module.css";

interface Profile { id: string; profile_name: string }
interface Evaluation { evaluation_type: string; display_score: number | null; overall_score: number | string | null; confidence: "HIGH" | "MEDIUM" | "LOW"; status: string }
interface Strength {
  display_score: number | null;
  disclaimer: string;
  effective_weights?: Record<string, number>;
}

const components = [
  { type: "ACADEMIC", name: "Academics", description: "Performance, rigor, trend, context, and major preparation.", href: "/profile/academics", methodology: "academic" },
  { type: "ACTIVITY", name: "Activities", description: "Impact, initiative, leadership, commitment, and distinction.", href: "/profile/activities", methodology: "activities" },
  { type: "HONOR", name: "Honors", description: "Scope, selectivity, consistency, and relevance.", href: "/profile/honors", methodology: "honors" },
  { type: "ESSAY", name: "Essay signals", description: "Clarity, structure, specificity, reflection, and style hygiene.", href: "/essays", methodology: "essay" },
  { type: "LOR", name: "LOR signals", description: "Specificity, examples, role context, and support signals.", href: "/recommendations", methodology: "lor" },
  { type: "TEST", name: "Testing", description: "College-specific test records and policy context.", href: "/profile/testing", methodology: "testing" },
];

function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <Card className="border-t-[3px] border-t-primary p-5 sm:p-6">
      <p className="hairline-label text-muted">{label}</p>
      <p className="data-type mt-4 text-3xl font-extrabold tracking-[-0.025em]">{value}</p>
      <p className="mt-2 text-sm leading-6 text-muted">{detail}</p>
    </Card>
  );
}

export function DashboardOverview() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [strength, setStrength] = useState<Strength | null>(null);
  const [targetCount, setTargetCount] = useState<number | null>(null);
  const [testingCount, setTestingCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const profilesResponse = await authenticatedFetch("/api/v1/profiles");
        if (!profilesResponse.ok) throw new Error(await apiError(profilesResponse));
        const first = ((await profilesResponse.json()) as { data: Profile[] }).data[0];
        if (!first) return;
        setProfile(first);

        const [evaluationsResponse, targetsResponse, testsResponse] = await Promise.all([
          authenticatedFetch(`/api/v1/profiles/${first.id}/evaluations`),
          authenticatedFetch(`/api/v1/profiles/${first.id}/targets`),
          authenticatedFetch(`/api/v1/profiles/${first.id}/tests`),
        ]);
        if (!evaluationsResponse.ok) throw new Error(await apiError(evaluationsResponse));
        const rows = ((await evaluationsResponse.json()) as { data: Evaluation[] }).data;
        const latest = [...rows.reduce((items, item) => {
          if (!items.has(item.evaluation_type)) items.set(item.evaluation_type, item);
          return items;
        }, new Map<string, Evaluation>()).values()];
        setEvaluations(latest);
        if (targetsResponse.ok) setTargetCount(((await targetsResponse.json()) as { data: unknown[] }).data.length);
        if (testsResponse.ok) setTestingCount(((await testsResponse.json()) as { data: unknown[] }).data.length);

        const byType = Object.fromEntries(latest.map((item) => [item.evaluation_type, item.display_score]));
        const response = await apiFetch("/api/v1/evaluations/profile-strength", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            academics: byType.ACADEMIC ?? null,
            activities: byType.ACTIVITY ?? null,
            honors: byType.HONOR ?? null,
            essay_signals: byType.ESSAY ?? null,
            lor_signals: byType.LOR ?? null,
            testing: byType.TEST ?? null,
          }),
        });
        if (response.ok) setStrength(((await response.json()) as { data: { evaluation: Strength } }).data.evaluation);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Workspace data could not be loaded.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <div aria-label="Loading dashboard" className="grid gap-5"><Skeleton className="h-28" /><div className="grid gap-4 md:grid-cols-4"><Skeleton className="h-40" /><Skeleton className="h-40" /><Skeleton className="h-40" /><Skeleton className="h-40" /></div><Skeleton className="h-72" /></div>;
  }

  const byType = Object.fromEntries(evaluations.map((item) => [item.evaluation_type, item]));
  const lowConfidenceCount = evaluations.filter((item) => item.confidence === "LOW").length;
  const readiness = byType.APPLICATION?.overall_score == null ? "N/A" : `${Math.round(Number(byType.APPLICATION.overall_score))}%`;
  const scoredComponentCount = Object.keys(strength?.effective_weights ?? {}).length || evaluations.filter(
    (item) => item.display_score != null && item.evaluation_type !== "APPLICATION",
  ).length;

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="eyebrow">Evalio / Application workspace</p>
          <h1 className="section-title mt-3">Your application, clearly.</h1>
          <p className="mt-3 text-lg text-muted">{profile?.profile_name ?? "Build your first profile to connect saved evaluations."}</p>
        </div>
        <div className="flex flex-wrap gap-3"><ButtonLink href="/reports" variant="secondary">Reports</ButtonLink><ButtonLink href="/profile">Update profile <span aria-hidden="true">→</span></ButtonLink></div>
      </div>

      {error ? (
        <Alert className="mt-8" title="We couldn't load your workspace" tone="danger">
          <p>Your saved data has not changed. Check the API and database connection, then try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()} variant="secondary">Try again</Button>
        </Alert>
      ) : null}

      {!profile && !error ? <Alert className="mt-8" title="Profile setup needed" tone="warning">Create a profile before saving structured evaluations.</Alert> : null}

      <div className={styles.pathways}>{[["/profile", "Continue profile"], ["/tools/essay-evaluator", "Analyze essay"], ["/tools/application-evaluator", "Evaluate college"], ["/tools/scholarships", "Scholarship availability"]].map(([href, label]) => <Link key={href} href={href}>{label}<span aria-hidden="true">→</span></Link>)}</div>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
        <MetricCard label="Application strength" value={strength?.display_score == null ? "N/A" : `${strength.display_score} / 100`} detail={strength?.display_score == null ? "Add a scored component to calculate it" : `Based on ${scoredComponentCount} available scored component${scoredComponentCount === 1 ? "" : "s"}`} />
        <MetricCard label="Application readiness" value={readiness} detail="Completeness, not quality" />
        <MetricCard label="Data confidence" value="Per component" detail="Read the confidence returned with each evaluation below." />
        <MetricCard label="Application audit" value={byType.APPLICATION?.status === "INCOMPLETE" ? "Review needed" : byType.APPLICATION ? "See audit" : "Not yet run"} detail={targetCount === null ? "Targets unavailable" : `${targetCount} target college${targetCount === 1 ? "" : "s"}`} />
      </div>

      {strength?.display_score != null ? <details className="evidence-disclosure mt-4 rounded-xl border border-border p-5"><summary>How application strength is calculated</summary><p className="evidence-rail mt-3 p-4 text-sm">The score uses only components with available scores. Components marked N/A are excluded, not counted as zero, and the remaining component weights are normalized to 100%.</p>{strength.effective_weights && <dl className="mt-4 grid gap-2">{Object.entries(strength.effective_weights).map(([key, weight]) => <div key={key} className="flex justify-between gap-4 text-sm"><dt className="capitalize">{key.replaceAll("_", " ")}</dt><dd>{(weight * 100).toFixed(1)}%</dd></div>)}</dl>}</details> : null}

      {strength?.disclaimer ? <p className="mt-4 text-xs leading-5 text-muted">{strength.disclaimer}</p> : null}
      {lowConfidenceCount ? <Alert className="mt-6" title="Data-quality warning" tone="warning">{lowConfidenceCount} latest evaluation{lowConfidenceCount === 1 ? " has" : "s have"} low confidence. Add missing context before relying on the result.</Alert> : null}
      <section className="mt-8 border-y border-border py-6" aria-labelledby="dashboard-next"><p className="eyebrow">Evalio / Priority findings</p><h2 className="mt-2 text-2xl" id="dashboard-next">What needs your attention?</h2><div className="mt-4 grid gap-4 sm:grid-cols-2"><div><p className="font-semibold">{byType.APPLICATION?.status === "INCOMPLETE" ? "Review incomplete application materials" : "Keep completeness separate from quality"}</p><p className="mt-1 text-sm text-muted">Check your targets for required materials and college-specific deadlines.</p><Link className="quiet-link inline-flex min-h-11 items-center text-sm" href="/targets">Review targets →</Link></div><div><p className="font-semibold">{byType.ESSAY ? "Revisit your saved essay signals" : "Start with an essay analysis"}</p><p className="mt-1 text-sm text-muted">{byType.ESSAY ? "Your latest saved essay evaluation is included below." : "No saved essay evaluation is included in this overview."}</p><Link className="quiet-link inline-flex min-h-11 items-center text-sm" href={byType.ESSAY ? "/essays" : "/tools/essay-evaluator"}>Open essay workspace →</Link></div></div></section>

      <div className="mt-12 flex flex-wrap items-end justify-between gap-4">
        <div><p className="eyebrow">Evalio / Profile components</p><h2 className="mt-3 text-3xl font-semibold tracking-[-0.02em]">Score, evidence, next action.</h2></div>
        <ButtonLink href="/methodology" variant="ghost">View methodology <span aria-hidden="true">→</span></ButtonLink>
      </div>
      <div className={styles.componentTableWrap}>
        <table className={styles.componentTable}>
          <caption className="sr-only">Profile component scores, data confidence, evidence coverage, and next actions</caption>
          <thead><tr><th scope="col">Component</th><th scope="col">Score</th><th scope="col">Data status</th><th scope="col">Evidence covered</th><th scope="col">Next action</th></tr></thead>
          <tbody>
        {components.map((component) => {
          const item = byType[component.type];
          const testingOnly = component.type === "TEST" && !item && testingCount !== null && testingCount > 0;
          const score = testingOnly ? `${testingCount} saved` : item?.display_score ?? (item?.overall_score == null ? "N/A" : Math.round(Number(item.overall_score)));
          const tone = item?.confidence === "HIGH" ? "success" : item || testingOnly ? "warning" : "neutral";
          return (
            <tr key={component.type}>
              <th data-label="Component" scope="row"><span className={styles.componentName}>{component.name}</span></th>
              <td data-label="Score"><span className={styles.componentTableScore}>{score}</span></td>
              <td data-label="Data status"><StatusBadge tone={tone}>{item ? `${item.confidence} confidence` : testingOnly ? "College-specific" : "Limited data"}</StatusBadge></td>
              <td data-label="Evidence covered"><p className={styles.componentEvidence}>{component.description}</p></td>
              <td data-label="Next action"><div className={styles.componentActions}><Link href={component.href}>Improve <span aria-hidden="true">→</span></Link><Link href={`/methodology/${component.methodology}`}>Why this score?</Link></div></td>
            </tr>
          );
        })}
          </tbody>
        </table>
      </div>
    </>
  );
}
