"use client";

import { useState } from "react";
import { ErrorResult, LoadingResult, ScoreBreakdown, ScoreCard, ToolInputShell } from "@/components/tools";
import { Button, ButtonLink } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/field";
import { apiError } from "@/lib/api/client";
import styles from "./analysis-workspace.module.css";

interface Result { display_score: number; components: Record<string, number>; triggered_rules: string[]; confidence: "HIGH" | "MEDIUM" | "LOW"; engine_version: string; rubric_version: string }
const rules: Record<string, string> = {
  "LOR-001": "Relationship context missing",
  "LOR-002": "Generic praise without supporting evidence",
  "LOR-003": "Comparative evidence detected",
  "LOR-004": "Concrete example signal detected",
};

export function LorEvaluator() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function analyze(form: FormData) {
    setBusy(true); setResult(null); setError(null);
    try {
      const months = String(form.get("months") ?? "");
      const response = await fetch("/api/v1/evaluations/lor", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, recommender_role: String(form.get("role") ?? "").trim() || null, relationship_duration_months: months === "" ? null : Number(months), instructional_context: String(form.get("context") ?? "").trim() || null, save: false }) });
      if (!response.ok) throw new Error(await apiError(response));
      setResult(((await response.json()) as { data: { evaluation: Result } }).data.evaluation);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Recommendation analysis unavailable."); }
    finally { setBusy(false); }
  }
  return <form action={analyze} className={styles.workspace} onChange={() => { if (result) setResult(null); }}>
    <ToolInputShell title="Recommendation letter" description="Inspect measurable language signals. This cannot determine the recommender's intent or an admissions officer's reaction." footer={<p className="text-xs text-muted">Public analysis only. Raw letter text is not saved.</p>}>
      <fieldset disabled={busy} className="grid min-w-0 gap-5"><details className={styles.disclosure}><summary>Relationship context <span className="text-xs text-muted">Optional</span></summary><div className="grid gap-4 p-4"><Input id="lor-role" label="Recommender role" name="role" maxLength={160} /><Input id="lor-months" label="Relationship duration (months)" name="months" min={0} max={600} type="number" /><Input id="lor-context" label="Instructional context" name="context" maxLength={500} /></div></details><Textarea className={styles.editor} id="lor-text" label="Recommendation text" value={text} onChange={(event) => setText(event.target.value)} maxLength={100000} required /><div className={styles.editorFooter}><p className="text-sm text-muted">{text.trim() ? text.trim().split(/\s+/).length : 0} words</p><Button disabled={busy || !text.trim()} type="submit">{busy ? "Evaluating letter…" : "Evaluate letter"} <span aria-hidden="true">→</span></Button></div></fieldset>
    </ToolInputShell>
    <div className={styles.results} aria-live="polite" aria-busy={busy}>{busy && <LoadingResult label="Evaluating recommendation letter" />}{error && <ErrorResult message={error} title="Letter analysis unavailable" />}{!busy && !result && !error && <div className="rounded-xl border border-border bg-[var(--surface-soft)] p-6"><p className="eyebrow">Evalio / Recommendation signals</p><h2 className="mt-4 text-2xl">Specific evidence, not generic praise.</h2><p className="mt-3 text-sm text-muted">Six dimensions, server-returned rules, and an explicit confidence level. No invented anecdotes or personality judgments.</p></div>}
    {result && <><ScoreCard confidence={result.confidence === "HIGH" ? "High" : result.confidence === "MEDIUM" ? "Medium" : "Low"} score={result.display_score} title="LOR Signal Score" methodologyHref="/methodology/lor" description="Internal textual signals, not recommendation quality certainty." /><ScoreBreakdown items={Object.entries(result.components).map(([key, value]) => ({ label: key.replaceAll("_", " "), value: `${Math.round(value)} / 100` }))} /><section><h2 className="text-xl">Triggered rules</h2><p className="mt-2 text-sm text-muted">This API returns rule IDs, but not sentence excerpts or rule-level point effects. Those details are not inferred in your browser.</p><div className="mt-4 grid gap-3">{result.triggered_rules.map((rule) => <details className="evidence-disclosure rounded-lg border border-border p-4" key={rule}><summary>{rules[rule] ?? rule}</summary><div className="evidence-rail mt-3 p-3 text-sm"><p className="font-semibold">{rule}</p><p className="mt-2 text-muted">Flagged by the server using rubric {result.rubric_version}. Excerpt-level evidence is not provided by the current API.</p><ButtonLink href="/methodology/lor" variant="ghost">View methodology →</ButtonLink></div></details>)}{!result.triggered_rules.length && <p className="text-sm">No rules triggered.</p>}</div></section><p className="text-xs text-muted">Engine {result.engine_version} · Rubric {result.rubric_version}</p><ButtonLink href="/recommendations" variant="secondary">Manage saved recommendations →</ButtonLink></>}
    </div>
  </form>;
}
