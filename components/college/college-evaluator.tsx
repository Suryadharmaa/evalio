"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  EmptyResult,
  LoadingResult,
  ScoreBreakdown,
  ScoreCard,
  ToolInputShell,
} from "@/components/tools";
import { apiError, authenticatedFetch } from "@/lib/api/client";
import styles from "@/components/evaluation/analysis-workspace.module.css";

interface Profile { id: string; profile_name: string }
interface College { id: string; name: string; slug: string; state_region: string | null }
type ComponentName = "academics" | "testing" | "activities" | "honors" | "essay" | "recommendations";

interface Result {
  academic_alignment: number | null;
  application_strength: number | null;
  college: { id: string; name: string; slug: string };
  college_data_cycles: Record<string, string | null>;
  components: Partial<Record<ComponentName, number>>;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  confidence_score: number;
  course_rigor: number | null;
  evaluation_date: string;
  financial_confidence: "HIGH" | "MEDIUM" | "LOW";
  financial_fit: string;
  financial_reasons: string[];
  financial_risk: string;
  oldest_critical_source_at: string | null;
  planning_category: string;
  reasons: string[];
  requirements_fit: string;
  rubric_version: string;
  selectivity_risk: string;
  source_freshness: string;
  triggered_rules: string[];
}

function today() {
  const date = new Date();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

function label(value: string) {
  return value.replaceAll("_", " ");
}

function confidence(value: Result["confidence"]): "High" | "Medium" | "Low" {
  return value === "HIGH" ? "High" : value === "MEDIUM" ? "Medium" : "Low";
}

export function CollegeEvaluator({ initialCollegeId, initialCollegeName }: { initialCollegeId?: string; initialCollegeName?: string }) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState("");
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [colleges, setColleges] = useState<College[]>([]);
  const [collegeId, setCollegeId] = useState(initialCollegeId ?? "");
  const [selectedCollegeName, setSelectedCollegeName] = useState(initialCollegeName ?? "");
  const [evaluationDate, setEvaluationDate] = useState(today);
  const [result, setResult] = useState<Result | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [savingTarget, setSavingTarget] = useState(false);
  const [profileAttempt, setProfileAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    void authenticatedFetch("/api/v1/profiles")
      .then(async (response) => {
        if (!response.ok) throw new Error(await apiError(response));
        const rows = ((await response.json()) as { data: Profile[] }).data;
        if (!active) return;
        setProfiles(rows);
        setProfileId((current) => current || rows[0]?.id || "");
      })
      .catch((reason: unknown) => {
        if (active) setProfileError(reason instanceof Error ? reason.message : "Unable to load profiles.");
      })
      .finally(() => {
        if (active) setProfileLoading(false);
      });
    return () => { active = false; };
  }, [profileAttempt]);

  const search = useCallback(async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSearching(true);
    setMessage(null);
    setColleges([]);
    try {
      const params = new URLSearchParams({ country: "US", page_size: "20" });
      if (query.trim()) params.set("q", query.trim());
      const response = await fetch(`/api/v1/colleges?${params}`);
      if (!response.ok) throw new Error(await apiError(response));
      const rows = ((await response.json()) as { data: College[] }).data;
      setColleges(rows);
      if (!rows.length) setMessage("No colleges matched that search.");
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "College search failed.");
    } finally {
      setSearching(false);
    }
  }, [query]);

  async function evaluate() {
    if (!profileId || !collegeId) return;
    setEvaluating(true);
    setMessage(null);
    setResult(null);
    try {
      const response = await authenticatedFetch(`/api/v1/profiles/${profileId}/colleges/${collegeId}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ evaluation_date: evaluationDate }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setResult(((await response.json()) as { data: Result }).data);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "Evaluation failed.");
    } finally {
      setEvaluating(false);
    }
  }

  async function addTarget() {
    if (!profileId || !collegeId || savingTarget) return;
    setSavingTarget(true);
    setMessage(null);
    try {
      const response = await authenticatedFetch(`/api/v1/profiles/${profileId}/targets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ college_id: collegeId, priority: null, application_round: null, application_status: "PLANNING" }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage("College added to targets.");
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "Unable to add target.");
    } finally {
      setSavingTarget(false);
    }
  }

  const componentItems = result ? [
    ["Course rigor", result.course_rigor],
    ["Activities", result.components.activities],
    ["Honors", result.components.honors],
    ["Testing", result.components.testing],
    ["Essay", result.components.essay],
    ["Recommendations", result.components.recommendations],
  ].map(([itemLabel, value]) => ({ label: String(itemLabel), value: typeof value === "number" ? `${Math.round(value)} / 100` : "N/A" })) : [];

  return <>
    <div className={styles.context}>
      <ToolInputShell description="Connect your saved evidence to one target college. Every dimension stays separate and inspectable." footer={<p className="text-sm text-muted">Saved profile evidence only. No admission probability, guarantee, or safety classification.</p>} title="Your profile. Your target.">
        {profileLoading ? <LoadingResult label="Loading saved profiles" /> : null}
        {!profileLoading && profileError ? <Alert title="Your saved profiles are unavailable" tone="warning"><p>Sign in and check the workspace connection. Your saved data has not changed.</p><div className="mt-4 flex flex-wrap gap-3"><ButtonLink href="/sign-in?next=/tools/application-evaluator" variant="secondary">Sign in</ButtonLink><Button onClick={() => { setProfileError(null); setProfileLoading(true); setProfileAttempt((attempt) => attempt + 1); }} variant="secondary">Try again</Button></div></Alert> : null}
        {!profileLoading && !profileError && profiles.length === 0 ? <Alert title="Create a profile first" tone="warning">Application evaluation needs saved academic and application evidence.<ButtonLink className="mt-4 flex w-fit" href="/profile" variant="secondary">Create profile</ButtonLink></Alert> : null}
        {!profileLoading && !profileError && profiles.length > 0 ? <fieldset className="grid min-w-0 gap-6" disabled={evaluating || savingTarget}>
          <div className="flex flex-wrap items-center justify-between gap-3"><p className="eyebrow">01 / Saved evidence</p><StatusBadge tone="success">✓ Use saved profile</StatusBadge></div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Select id="evaluation-profile" label="Saved profile" value={profileId} onChange={(event) => { setProfileId(event.target.value); setResult(null); }}>{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.profile_name}</option>)}</Select>
            <Input id="evaluation-date" label="Evaluation date" max="2100-12-31" min="2000-01-01" type="date" value={evaluationDate} onChange={(event) => { setEvaluationDate(event.target.value); setResult(null); }} />
          </div>
          <form className="grid gap-3 border-t border-border pt-5 sm:grid-cols-[1fr_auto] sm:items-end" onSubmit={search}>
            <Input id="application-college-search" label="Target college" placeholder="Search Harvard, Bowdoin, Stanford…" value={query} onChange={(event) => setQuery(event.target.value)} />
            <Button disabled={searching} type="submit" variant="secondary">{searching ? "Searching…" : "Search"}</Button>
          </form>
          {collegeId && !colleges.length ? <div className="rounded-lg border border-primary/25 bg-[var(--primary-soft)] p-4 text-sm"><span className="font-bold">Selected:</span> {selectedCollegeName || "college from the previous page"}</div> : null}
          {colleges.length ? <fieldset className="grid max-h-72 gap-2 overflow-y-auto pr-1"><legend className="mb-2 text-sm font-semibold">Select a search result</legend>{colleges.map((college) => <label className={`flex min-h-14 cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors hover:border-primary/50 ${collegeId === college.id ? "border-primary bg-[var(--surface-soft)]" : "border-border"}`} key={college.id}><input className="size-4 shrink-0 accent-primary" checked={collegeId === college.id} name="college" onChange={() => { setCollegeId(college.id); setSelectedCollegeName(college.name); setResult(null); }} type="radio" /><span className="text-sm">{college.name}{college.state_region ? <span className="mt-1 block text-xs text-muted">{college.state_region}</span> : null}</span></label>)}</fieldset> : null}
          {message ? <Alert title="Status">{message}</Alert> : null}
          <div className="flex flex-wrap justify-end gap-3"><Button disabled={evaluating || savingTarget || !collegeId} onClick={() => void addTarget()} variant="secondary">{savingTarget ? "Saving target…" : "Add to targets"}</Button><Button disabled={evaluating || savingTarget || !collegeId || !evaluationDate} onClick={() => void evaluate()}>{evaluating ? "Evaluating…" : "Evaluate My Profile"}<span aria-hidden="true">→</span></Button></div>
        </fieldset> : null}
      </ToolInputShell>
      <aside className={styles.contextNote}><p className="eyebrow">Understand the result</p><h2 className="mt-3 font-serif text-3xl leading-tight">Fit without<br />fake certainty.</h2><p className="mt-4 leading-7 text-muted">A strong application and a selective institution are two different things. Evalio shows both.</p><ol className="mt-6 grid gap-5 text-sm"><li><span className="block font-semibold">Score</span><span className="mt-1 block text-muted">Saved academic and application evidence. Missing is N/A, never zero.</span></li><li><span className="block font-semibold">Evidence → rule</span><span className="mt-1 block text-muted">Open the reasons and versioned rules behind your planning category.</span></li><li><span className="block font-semibold">Explanation</span><span className="mt-1 block text-muted">Check confidence, requirements, financial fit, and source freshness together.</span></li></ol><ButtonLink className="mt-5" href="/methodology/college" variant="ghost">Read the methodology →</ButtonLink></aside>
    </div>

    <section aria-live="polite" aria-busy={evaluating} className="mt-12">
      {evaluating ? <LoadingResult label="Evaluating application evidence" /> : null}
      {!evaluating && !result ? <EmptyResult description="Select a saved profile and target college to generate a traceable planning result." title="No evaluation yet" /> : null}
      {!evaluating && result ? <div className="grid gap-6">
        <Card className="overflow-hidden"><div className={styles.scoreIntro}><div className="flex flex-wrap items-start justify-between gap-5"><div><p className="hairline-label text-white/80">{result.college.name}</p><p className="mt-5 text-xs font-bold uppercase tracking-widest text-white/80">Planning category</p><h2 className="mt-2 text-3xl font-semibold sm:text-4xl">{label(result.planning_category)}</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-white/80">Based on your available profile and this college snapshot—not an admission probability.</p></div><div className="flex flex-wrap gap-2"><StatusBadge className="border-white/30 bg-white/10 text-white">● {result.confidence} confidence</StatusBadge><StatusBadge className="border-white/30 bg-white/10 text-white">{result.rubric_version}</StatusBadge></div></div></div></Card>
        <details className={styles.disclosure} open><summary>Why this result? <span className="text-xs font-normal text-muted">Evidence → rule → explanation</span></summary>{result.reasons.length ? <ol className={styles.reasonList}>{result.reasons.map((reason, index) => <li key={`${index}-${reason}`}>{reason}</li>)}</ol> : <p className="p-5 text-sm text-muted">No narrative explanation was returned. Inspect the dimensions and source context below.</p>}</details>
        <div className="grid gap-5 md:grid-cols-2"><ScoreCard confidence={confidence(result.confidence)} description="College-specific comparison of saved academic evidence and available testing context." methodologyHref="/methodology/college" score={result.academic_alignment === null ? null : Math.round(result.academic_alignment)} title="Academic alignment" /><ScoreCard confidence={confidence(result.confidence)} description="Available application components weighted by mapped college CDS factors." methodologyHref="/methodology/college" score={result.application_strength === null ? null : Math.round(result.application_strength)} title="Application strength" /></div>
        <div className="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]"><ScoreBreakdown items={componentItems} title="Component evidence" /><Card className="p-6"><h2 className="text-lg font-extrabold">Planning dimensions</h2><dl className="mt-4 grid gap-4 text-sm">{[["Selectivity risk", result.selectivity_risk], ["Requirements fit", result.requirements_fit], ["Financial fit", result.financial_fit], ["Financial risk", result.financial_risk], ["Data confidence", `${result.confidence} (${result.confidence_score}/100)`]].map(([itemLabel, value]) => <div className="flex items-center justify-between gap-4 border-b border-border pb-3" key={itemLabel}><dt className="text-muted">{itemLabel}</dt><dd className="font-bold text-right">{label(value)}</dd></div>)}</dl></Card></div>
        <Card className="p-6"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-lg font-extrabold">College data context</h2><StatusBadge tone={result.source_freshness === "CURRENT" ? "success" : result.source_freshness === "STALE" ? "danger" : "warning"}>{label(result.source_freshness)}</StatusBadge></div><dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">{Object.entries(result.college_data_cycles).map(([name, cycle]) => <div key={name}><dt className="text-muted">{label(name)}</dt><dd className="data-type mt-1 font-bold">{cycle || "Not available"}</dd></div>)}</dl><p className="mt-4 text-xs text-muted">Evaluated {result.evaluation_date}. Oldest critical source: {result.oldest_critical_source_at ? new Date(result.oldest_critical_source_at).toLocaleDateString() : "not available"}.</p></Card>
        <details className={styles.disclosure}><summary>Financial evidence <StatusBadge>{result.financial_confidence} confidence</StatusBadge></summary>{result.financial_reasons.length ? <ol className={styles.reasonList}>{result.financial_reasons.map((reason, index) => <li key={`${index}-${reason}`}>{reason}</li>)}</ol> : <p className="p-5 text-sm text-muted">No financial explanation was returned. Missing financial evidence is not a zero-cost estimate.</p>}</details>
        <details className={styles.disclosure}><summary>Triggered rules <span className="text-sm font-normal text-muted">{result.triggered_rules.length} rules</span></summary><div className="p-6">{result.triggered_rules.length ? <ul className="flex flex-wrap gap-2">{result.triggered_rules.map((rule) => <li key={rule}><StatusBadge>{rule}</StatusBadge></li>)}</ul> : <p className="text-sm text-muted">No named college rules were triggered.</p>}<p className="mt-5 text-sm text-muted">Inspect thresholds and limitations in the college methodology. Scores are internal planning signals.</p><div className="mt-4 flex flex-wrap gap-3"><ButtonLink href="/methodology/college" variant="secondary">Inspect the rules →</ButtonLink><ButtonLink href={`/colleges/${result.college.slug}#sources`} variant="ghost">View college sources →</ButtonLink></div></div></details>
      </div> : null}
    </section>
  </>;
}
