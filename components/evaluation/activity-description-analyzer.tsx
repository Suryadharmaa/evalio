"use client";

import { useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/field";
import { ScoreBreakdown, LoadingResult } from "@/components/tools";
import styles from "./analysis-workspace.module.css";

interface Result { display_score: number; confidence: string; components: Record<string, number>; triggered_rules: string[] }

export function ActivityDescriptionAnalyzer() {
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [description, setDescription] = useState("");
  async function analyze(formData: FormData) {
    setBusy(true); setError(null); setResult(null);
    try {
      const response = await fetch("/api/v1/evaluations/activity-description", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ position_title: formData.get("position_title"), organization: formData.get("organization"), description: formData.get("description"), character_limit: 150 }) });
      if (!response.ok) throw new Error("Unable to analyze this description.");
      setResult(((await response.json()) as { data: { evaluation: Result } }).data.evaluation);
    } catch (error) { setError(error instanceof Error ? error.message : "Analysis failed."); }
    finally { setBusy(false); }
  }
  return <div className={styles.workspace}>
    <Card className="p-6 sm:p-8"><form action={analyze} className="grid gap-6">
      <div className="grid gap-6 sm:grid-cols-2"><Input id="position" label="Position title" name="position_title" maxLength={100} /><Input id="organization" label="Organization" name="organization" maxLength={160} /></div>
      <Textarea id="description" label="Description" name="description" maxLength={150} required description="Common App activities allow up to 150 characters." value={description} onChange={(event) => { setDescription(event.target.value); setResult(null); }} />
      <p className="text-sm text-muted" aria-live="polite">{description.length} / 150 characters · Not saved</p>
      {error ? <Alert title="Analysis failed" tone="danger">{error}</Alert> : null}
      <div className="flex justify-end"><Button type="submit" disabled={busy}>{busy ? "Analyzing…" : "Analyze description"}</Button></div>
    </form></Card>
    <div aria-live="polite">{busy ? <LoadingResult label="Analyzing activity description" /> : <Card className="p-6 sm:p-8">{result ? <><p className="hairline-label text-primary">Description score</p><p className="data-type mt-2 text-5xl font-bold">{result.display_score}<span className="text-lg text-muted"> / 100</span></p><p className="mt-2 text-sm">Confidence: {result.confidence}</p><div className="mt-6"><ScoreBreakdown items={Object.entries(result.components).map(([name, score]) => ({ label: name.replaceAll("_", " "), value: score }))} /></div>{result.triggered_rules.length ? <details className="evidence-disclosure mt-5"><summary>Triggered rules</summary><p className="evidence-rail p-4 text-sm">{result.triggered_rules.join(", ")}</p><p className="mt-2 text-xs text-muted">The current API returns rule IDs, not excerpt-level evidence. No additional evidence is inferred.</p></details> : null}<ButtonLink className="mt-5" href="/methodology/activities" variant="secondary">Why this result?</ButtonLink></> : <><p className="eyebrow">Evalio / Activity evidence</p><h2 className="mt-3 text-xl font-semibold">Make the responsibility visible.</h2><p className="mt-2 text-muted">Inspect action clarity, impact signals, character use, and redundancy. A title alone does not establish impact.</p></>}</Card>}</div>
  </div>;
}
