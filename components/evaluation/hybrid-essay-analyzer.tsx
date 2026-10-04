"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/field";
import { apiFetch, apiError } from "@/lib/api/client";
import styles from "./hybrid-essay-analyzer.module.css";

const RUBRIC = [
  ["content", "Content & ideas"], ["structure", "Structure & progression"],
  ["voice", "Voice & authenticity"], ["specificity", "Specificity"],
  ["reflection", "Reflection & insight"], ["writing_quality", "Writing quality"],
] as const;
const MESSAGES = {
  early: ["Getting everything ready...", "Reading your essay...", "Looking at the details..."],
  middle: ["Reading between the lines...", "Looking for your voice...", "Following your story...", "Connecting the dots..."],
  late: ["Finding the strongest moments...", "Putting the pieces together...", "One last thought...", "Almost there..."],
};
type Signal = { score: number | null; label: string };
type Metrics = {
  word_count: number; sentence_count: number; paragraph_count: number;
  average_words_per_sentence: number;
  sentence_variety: Signal; vocabulary_diversity: Signal; readability: Signal;
  repetition: { label: string; repeated_phrases: string[]; repeated_openings: string[]; repeated_transitions?: string[] };
  structure?: { opening_ratio: number; conclusion_ratio: number; largest_paragraph_ratio: number; flags: string[] };
};
type Category = { score: number; max_score: number; feedback: string };
type Review = {
  overall_impression: string; categories: Record<string, Category>;
  strengths: string[]; improvements: string[]; priority_action: string;
};
type Result = {
  status: "complete" | "partial"; analysis_id?: string; score?: number;
  label?: string; review?: Review; metrics: Metrics; message?: string; retry_after_seconds?: number;
  meta: { cached: boolean; ai_calls: number };
};
type DeepResult = {
  strongest_paragraph: number; weakest_paragraph: number;
  opening: string; conclusion: string; narrative_arc: string;
  paragraph_feedback: string[]; revision_priorities: string[];
};

export function HybridEssayAnalyzer() {
  const [essay, setEssay] = useState("");
  const [reviewedEssay, setReviewedEssay] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [deep, setDeep] = useState<DeepResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [deepBusy, setDeepBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deepError, setDeepError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);
  const [retryRemaining, setRetryRemaining] = useState(0);
  const wordCount = useMemo(() => essay.match(/[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu)?.length ?? 0, [essay]);
  const changed = Boolean(result && essay !== reviewedEssay);
  const messageStage = progress < 35 ? "early" : progress < 82 ? "middle" : "late";

  useEffect(() => {
    if (!busy) return;
    const timer = window.setInterval(() => {
      setProgress((current) => {
        const ceiling = current < 35 ? 55 : current < 85 ? 92 : 98;
        return Math.min(98, current + Math.max(0.15, (ceiling - current) * 0.065));
      });
    }, 180);
    return () => window.clearInterval(timer);
  }, [busy]);

  useEffect(() => {
    if (!busy) return;
    const timer = window.setTimeout(() => {
      setMessageIndex((current) => {
        const options = MESSAGES[messageStage];
        return (current + 1 + Math.floor(Math.random() * (options.length - 1))) % options.length;
      });
    }, 1900 + Math.round(Math.random() * 1100));
    return () => window.clearTimeout(timer);
  }, [busy, messageIndex, messageStage]);

  useEffect(() => {
    if (retryRemaining <= 0) return;
    const timer = window.setTimeout(() => setRetryRemaining((current) => Math.max(0, current - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [retryRemaining]);

  async function analyze(refresh = false) {
    if (retryRemaining > 0) return;
    setError(null);
    if (wordCount < 50 || wordCount > 5000) {
      setError("Essay must contain between 50 and 5,000 words.");
      return;
    }
    setBusy(true); setProgress(0); setMessageIndex(0); setDeep(null);
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 60_000);
    try {
      const response = await apiFetch("/api/v1/essay-review", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ essay, refresh }), signal: controller.signal,
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json() as { data: Result };
      setProgress(100);
      await new Promise((resolve) => window.setTimeout(resolve, 250));
      setResult(payload.data); setReviewedEssay(essay);
      setRetryRemaining(payload.data.retry_after_seconds ?? 0);
    } catch (caught) {
      setError(caught instanceof Error && caught.name === "AbortError" ? "Analysis timed out. Please try again." : caught instanceof Error ? caught.message : "Analysis could not load.");
    } finally { window.clearTimeout(timeout); setBusy(false); }
  }

  async function analyzeDeep() {
    if (!result?.analysis_id || changed) return;
    setDeepBusy(true); setDeepError(null);
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 60_000);
    try {
      const response = await apiFetch("/api/v1/essay-review/deep", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: result.analysis_id, essay: reviewedEssay }), signal: controller.signal,
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json() as { data: { review: DeepResult } };
      setDeep(payload.data.review);
    } catch (caught) {
      setDeepError(caught instanceof Error && caught.name === "AbortError" ? "Deep Review timed out. Please try again." : caught instanceof Error ? caught.message : "Deep Review could not load.");
    } finally { window.clearTimeout(timeout); setDeepBusy(false); }
  }

  return <div className={styles.workspace}>
    <Card className={styles.editorCard}>
      <div className={styles.cardHeader}>
        <p className="eyebrow">Your draft</p>
        <h2 className="mt-2 text-2xl font-bold">Start with the story you have.</h2>
        <p className="mt-2 text-sm text-muted">Paste 50–5,000 words. Evalio caches the result and text hash, never your raw essay.</p>
      </div>
      <div className={styles.editorBody}>
        <Textarea className={styles.editor} id="hybrid-essay" label="Essay text" maxLength={50_000} onChange={(event) => setEssay(event.target.value)} placeholder="Paste your essay here..." value={essay} />
        <div className={styles.editorFooter}>
          <span aria-live="polite">{wordCount.toLocaleString()} words</span>
          <Button disabled={busy || deepBusy || retryRemaining > 0 || !essay.trim()} onClick={() => void analyze()} type="button">{busy ? "Analyzing..." : "Analyze essay"} <span aria-hidden="true">→</span></Button>
        </div>
      </div>
    </Card>
    <div className={styles.results} aria-live="polite" aria-busy={busy}>
      {busy ? <Card className={styles.loadingCard}>
        <p className="eyebrow">Essay review in progress</p>
        <p className={styles.progressNumber}>{Math.floor(progress)}%</p>
        <progress className={styles.progressTrack} value={progress} max={100} aria-label="Analysis progress" />
        <p className="mt-4 text-sm text-muted">{MESSAGES[messageStage][messageIndex % MESSAGES[messageStage].length]}</p>
      </Card> : null}
      {error ? <Card className="border-[var(--danger)] p-5" role="alert">{error}</Card> : null}
      {!busy && !result ? <Card className="p-7"><p className="eyebrow">One review · useful next steps</p><h2 className="mt-3 text-xl font-bold">Your feedback will appear here.</h2><p className="mt-2 text-sm leading-6 text-muted">You’ll see six rubric scores, concise feedback, and locally measured writing signals.</p></Card> : null}
      {result && !busy ? <>
        {changed ? <Card className="p-4 text-sm" role="status">Your draft changed. Analyze it again to update the review.</Card> : null}
        {result.status === "complete" && result.review ? <>
          <Card className={styles.scoreCard}><p className="text-xs font-bold uppercase tracking-[.14em] text-white/75">Essay review</p><p className={styles.score}>{result.score}<span> / 100</span></p><p className="font-bold">{result.label}</p><p className="mt-3 text-sm leading-6 text-white/85">{result.review.overall_impression}</p>{result.meta.cached ? <p className="mt-4 text-xs text-white/70">Saved analysis reused</p> : null}</Card>
          <Card className="overflow-hidden"><h3 className="p-5 text-lg font-bold">Scoring rubric</h3><div className={styles.categoryList}>{RUBRIC.map(([key, label]) => {
            const category = result.review?.categories[key];
            return category ? <details className={styles.category} key={key}><summary><span>{label}</span><strong>{category.score} / {category.max_score}</strong></summary><p className="px-5 pb-4 text-sm leading-6 text-muted">{category.feedback}</p></details> : null;
          })}</div></Card>
          <div className={styles.insightGrid}>
            <Card className="p-5"><h3 className="font-bold">What’s working</h3><ul className={styles.insightList}>{result.review.strengths.map((item, index) => <li key={`${index}-${item}`}>✓ {item}</li>)}</ul></Card>
            <Card className="p-5"><h3 className="font-bold">What could be stronger</h3><ul className={styles.insightList}>{result.review.improvements.map((item, index) => <li key={`${index}-${item}`}>→ {item}</li>)}</ul></Card>
          </div>
          <Card className="p-5"><p className="eyebrow">First revision to make</p><p className="mt-2 font-semibold leading-6">{result.review.priority_action}</p></Card>
        </> : <Card className="p-5" role="status"><h3 className="font-bold">Writing analysis is ready</h3><p className="mt-2 text-sm text-muted">{result.message}</p>{retryRemaining > 0 ? <p className="mt-2 text-sm text-muted">Retry available in {retryRemaining} seconds.</p> : null}<Button className="mt-4" disabled={busy || changed || retryRemaining > 0} onClick={() => void analyze(true)} type="button" variant="secondary">Try AI analysis again</Button></Card>}
        <Card className="p-5"><p className="eyebrow">Measured locally · no AI score adjustment</p><h3 className="mt-2 text-lg font-bold">Writing signals</h3><div className={styles.signalGrid}>
          <div><span>Words</span><strong>{result.metrics.word_count}</strong></div><div><span>Sentences</span><strong>{result.metrics.sentence_count}</strong></div><div><span>Paragraphs</span><strong>{result.metrics.paragraph_count}</strong></div><div><span>Sentence variety</span><strong>{result.metrics.sentence_variety.label}</strong></div><div><span>Vocabulary diversity</span><strong>{result.metrics.vocabulary_diversity.label}</strong></div><div><span>Repetition</span><strong>{result.metrics.repetition.label}</strong></div><div><span>Readability heuristic</span><strong>{result.metrics.readability.score ?? "N/A"} / 100</strong></div><div><span>Average sentence</span><strong>{result.metrics.average_words_per_sentence} words</strong></div>
        </div>
        {result.metrics.structure?.flags?.length ? <p className="mt-4 text-sm text-muted">Structure: {result.metrics.structure.flags.join(" · ")}</p> : null}
        {result.metrics.repetition.repeated_transitions?.length ? <p className="mt-2 text-sm text-muted">Repeated transitions: {result.metrics.repetition.repeated_transitions.join(", ")}</p> : null}
        <p className="mt-4 text-xs leading-5 text-muted">These heuristics describe writing patterns. They do not measure authenticity or predict admission.</p></Card>
        {result.status === "complete" ? <Card className="p-5"><h3 className="font-bold">Go deeper when you’re ready</h3><p className="mt-2 text-sm text-muted">Deep Review adds paragraph feedback and revision priorities in a separate AI request.</p><Button className="mt-4" disabled={deepBusy || changed || Boolean(deep)} onClick={() => void analyzeDeep()} type="button" variant="secondary">{deepBusy ? "Reviewing paragraphs..." : deep ? "Deep Review complete" : "Run Deep Review"}</Button>
          {deepError ? <p className="mt-3 text-sm text-[var(--danger)]" role="alert">{deepError}</p> : null}
          {deep ? <div className="mt-5 border-t border-border pt-5"><p className="text-sm"><strong>Opening:</strong> {deep.opening}</p><p className="mt-3 text-sm"><strong>Conclusion:</strong> {deep.conclusion}</p><p className="mt-3 text-sm"><strong>Narrative arc:</strong> {deep.narrative_arc}</p><p className="mt-4 text-xs text-muted">Strongest paragraph: {deep.strongest_paragraph} · Most revision needed: {deep.weakest_paragraph}</p><ol className="mt-4 list-decimal space-y-2 pl-5 text-sm">{deep.paragraph_feedback.map((item, index) => <li key={index}>{item}</li>)}</ol><p className="mt-4 font-semibold">Revision priorities</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{deep.revision_priorities.map((item, index) => <li key={index}>{item}</li>)}</ul></div> : null}
        </Card> : null}
      </> : null}
    </div>
  </div>;
}
