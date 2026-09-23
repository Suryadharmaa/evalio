"use client";

import { useMemo, useState } from "react";

import { ErrorResult, LoadingResult, ToolInputShell } from "@/components/tools";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiError } from "@/lib/api/client";
import styles from "./analysis-workspace.module.css";

type PatternLevel = "NORMAL" | "LOW" | "MEDIUM" | "HIGH" | "INSUFFICIENT_DATA";
type PatternCategory = "RHYTHM" | "DETAIL" | "LANGUAGE" | "STANCE";

interface PatternSignal {
  category: PatternCategory;
  evidence: string[];
  explanation: string;
  label: string;
  level: PatternLevel;
  metric: string;
  observed_value: number | string;
  signal_id: string;
  threshold: string;
  triggered: boolean;
}

interface PatternResult {
  confidence: "HIGH" | "MEDIUM" | "LOW";
  engine_version: string;
  risk: "LOW" | "MODERATE" | "HIGH";
  rubric_version: string;
  signals: PatternSignal[];
  total_signals: number;
  triggered_count: number;
}

const categories: Array<{ id: PatternCategory; label: string }> = [
  { id: "RHYTHM", label: "Rhythm and structure" },
  { id: "DETAIL", label: "Specific detail" },
  { id: "LANGUAGE", label: "Language patterns" },
  { id: "STANCE", label: "Perspective and stance" },
];

function levelTone(level: PatternLevel) {
  if (level === "HIGH") return "danger" as const;
  if (level === "MEDIUM") return "warning" as const;
  if (level === "LOW") return "info" as const;
  return "neutral" as const;
}

export function WritingPatternChecker() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<PatternResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [triggeredOnly, setTriggeredOnly] = useState(false);
  const [analyzedText, setAnalyzedText] = useState("");
  const wordCount = useMemo(() => text.trim() ? text.trim().split(/\s+/).length : 0, [text]);

  async function submit(formData: FormData) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const submittedText = String(formData.get("text") ?? "").trim();
      if (!submittedText) throw new Error("Paste text before checking its writing patterns.");
      const response = await fetch("/api/v1/evaluations/writing-patterns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: submittedText }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json() as { data: { evaluation: PatternResult } };
      setResult(payload.data.evaluation);
      setAnalyzedText(submittedText);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to check this text.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form action={submit} className={styles.workspace}>
      <ToolInputShell
        className={styles.editorPanel}
        description="Paste an essay or another piece of prose. Longer samples make more signals available."
        footer={<p className="text-xs leading-5 text-muted">This public check processes text for the request and does not persist it.</p>}
        title="Text to check"
      >
        <Textarea
          className={styles.editor}
          disabled={busy}
          id="pattern-text"
          label="Writing sample"
          maxLength={100_000}
          name="text"
          onChange={(event) => setText(event.target.value)}
          placeholder="Paste your writing here…"
          value={text}
        />
        <div className={`${styles.editorFooter} mt-5`}>
          <p className="text-sm font-bold text-muted" aria-live="polite">{wordCount} words</p>
          <Button aria-label="Check patterns" disabled={busy || !text.trim()} type="submit">
            {busy ? "Checking patterns…" : "Check writing patterns"} <span aria-hidden="true">→</span>
          </Button>
        </div>
      </ToolInputShell>

      <div className={styles.results} aria-live="polite" aria-busy={busy}>
        <p className="border-l-2 border-primary pl-4 text-sm leading-6 text-muted">
          This tool identifies measurable writing patterns. It cannot determine who or what wrote a text.
        </p>
        {busy ? <LoadingResult label="Checking writing patterns" /> : null}
        {error ? <ErrorResult message={error} title="Pattern check failed" /> : null}
        {!busy && !error && !result ? (
          <Card className="p-7">
            <p className="eyebrow">Evidence, not authorship</p>
            <h2 className="mt-3 text-xl font-extrabold">Writing pattern risk will appear here</h2>
            <p className="mt-2 leading-7 text-muted">Triggered patterns include their observed metric, threshold, evidence, and explanation.</p>
            <div className="mt-6 grid grid-cols-2 gap-2">{categories.map((category) => <span className="rounded-lg bg-[var(--surface-soft)] px-3 py-3 text-xs font-semibold" key={category.id}>{category.label}</span>)}</div>
          </Card>
        ) : null}
        {result ? (
          <>
            {text.trim() !== analyzedText ? <p role="status" className="rounded-lg border border-border p-4 text-sm">Your sample changed. Check it again to update these signals.</p> : null}
            <Card className="overflow-hidden">
              <div className={styles.scoreIntro}>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-white/80">Writing Pattern Risk</p>
                    <p className="mt-3 text-4xl font-extrabold tracking-[-0.045em]">{result.risk}</p>
                    <p className="mt-3 text-sm font-bold text-white/80">{result.triggered_count} / {result.total_signals} signals triggered</p>
                  </div>
                  <StatusBadge className="border-white/30 bg-white/10 text-white">● {result.confidence} confidence</StatusBadge>
                </div>
                <div aria-hidden="true" className={styles.signalTrack}>{result.signals.map((signal) => <span data-triggered={signal.triggered} key={signal.signal_id} />)}</div>
              </div>
              <p className="p-5 text-sm leading-6 text-muted">Risk reflects the share of available deterministic checks that crossed their visible thresholds. It is not an authorship classification.</p>
            </Card>

            <div className={styles.filterBar} aria-label="Filter writing signals"><button aria-pressed={!triggeredOnly} onClick={() => setTriggeredOnly(false)} type="button">All signals</button><button aria-pressed={triggeredOnly} onClick={() => setTriggeredOnly(true)} type="button">Triggered ({result.triggered_count})</button></div>
            {triggeredOnly && result.triggered_count === 0 ? <p className="p-4 text-sm text-muted">No signals crossed their thresholds. Choose All signals to inspect the measurements.</p> : null}

            {categories.map((category) => {
              const allCategorySignals = result.signals.filter((signal) => signal.category === category.id);
              const categorySignals = allCategorySignals.filter((signal) => !triggeredOnly || signal.triggered);
              if (!categorySignals.length) return null;
              return (
                <section key={category.id} aria-labelledby={`pattern-${category.id.toLowerCase()}`}>
                  <div className="flex flex-wrap items-center justify-between gap-2"><h2 className="text-lg font-extrabold" id={`pattern-${category.id.toLowerCase()}`}>{category.label}</h2><span className="text-xs text-muted">{allCategorySignals.filter((signal) => signal.triggered).length} / {allCategorySignals.length} triggered</span></div>
                  <div className="mt-3 overflow-hidden rounded-[var(--radius-lg)] border border-border bg-white">
                    {categorySignals.map((signal) => (
                      <details className={styles.signalRow} key={signal.signal_id}>
                        <summary>
                            <span className="min-w-0"><span className="block text-xs text-muted">{signal.signal_id} · {signal.triggered ? "Triggered" : "Not triggered"}</span><span className="mt-1 block text-sm font-bold">{signal.label}</span></span>
                            <StatusBadge tone={levelTone(signal.level)}>{signal.level.replaceAll("_", " ")}</StatusBadge>
                        </summary>
                        <dl className="grid gap-4 bg-[var(--surface-muted)] p-4 text-sm">
                          <div><dt className="font-extrabold">Observed metric</dt><dd className="mt-1 break-words text-muted">{signal.metric.replaceAll("_", " ")}: {signal.observed_value}</dd></div>
                          <div><dt className="font-extrabold">Threshold</dt><dd className="mt-1 text-muted">{signal.threshold}</dd></div>
                          <div><dt className="font-extrabold">Evidence</dt><dd className="mt-1 break-words text-muted">{signal.evidence.length ? signal.evidence.join(" · ") : "No item-level evidence for this metric."}</dd></div>
                        </dl>
                        <div className="p-4"><p className="text-xs font-bold uppercase tracking-wider text-primary">Why this matters</p><p className="mt-2 text-sm leading-6 text-muted">{signal.explanation}</p></div>
                      </details>
                    ))}
                  </div>
                </section>
              );
            })}

            <p className="text-xs text-muted">Engine {result.engine_version} · Rubric {result.rubric_version}</p>
          </>
        ) : null}
      </div>
    </form>
  );
}
