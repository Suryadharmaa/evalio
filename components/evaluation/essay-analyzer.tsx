"use client";

import { useMemo, useState } from "react";

import { MethodologyLink, RuleFinding, ScoreBreakdown, ToolInputShell } from "@/components/tools";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Select, Textarea } from "@/components/ui/field";
import { ErrorResult, LoadingResult } from "@/components/tools/result-states";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiFetch, apiError } from "@/lib/api/client";
import { essayAnalysisFormSchema, firstValidationError } from "@/lib/schemas/forms";
import styles from "./analysis-workspace.module.css";

interface EssayIssue {
  confidence?: "HIGH" | "MEDIUM" | "LOW";
  evidence: Record<string, unknown>;
  message: string;
  methodology_link?: string;
  rule_id: string;
  score_delta?: number | null;
  score_effect?: string;
  severity: string;
  title: string;
}

interface EssayResult {
  components: Record<string, number>;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  display_score: number;
  engine_version?: string;
  issues: EssayIssue[];
  label: string;
  metrics: Record<string, number | null> & {
    paragraph_count: number;
    sentence_count: number;
    word_count: number;
  };
  overall_score: number;
  rubric_version?: string;
}

const componentLabels: Record<string, string> = {
  compliance: "Compliance",
  clarity: "Clarity",
  structure: "Structure",
  specificity: "Specificity",
  reflection: "Reflection Signals",
  voice: "Voice Indicators",
  sentence_variety: "Sentence Variety",
  style_hygiene: "Style Hygiene",
};

function evidenceText(evidence: Record<string, unknown>) {
  const entries = Object.entries(evidence);
  if (!entries.length) return "Rule threshold met; no sentence excerpt was returned.";
  return entries
    .map(([key, value]) => `${key.replaceAll("_", " ")}: ${Array.isArray(value) ? value.join(", ") : String(value)}`)
    .join(" · ");
}

export function EssayAnalyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<EssayResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [wordLimit, setWordLimit] = useState(650);
  const [analyzedText, setAnalyzedText] = useState<string | null>(null);
  const [draftChanged, setDraftChanged] = useState(false);
  const wordCount = useMemo(() => text.trim() ? text.trim().split(/\s+/).length : 0, [text]);
  const overLimit = !file && wordCount > wordLimit;

  async function submit(formData: FormData) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const validation = essayAnalysisFormSchema.safeParse({
        essayType: formData.get("essay_type"),
        text,
        hasFile: Boolean(file),
        minWords: formData.get("min_words"),
        wordLimit: formData.get("word_limit"),
      });
      if (!validation.success) throw new Error(firstValidationError(validation));

      const promptText = String(formData.get("prompt_text") ?? "").trim() || null;
      const response = file
        ? await apiFetch("/api/v1/evaluations/essay/upload", { method: "POST", body: formData })
        : await apiFetch("/api/v1/evaluations/essay", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              essay_type: formData.get("essay_type"),
              text,
              min_words: Number(formData.get("min_words")),
              word_limit: Number(formData.get("word_limit")),
              prompt_text: promptText,
              save: false,
              save_raw_text: false,
            }),
          });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json() as { data: { evaluation: EssayResult } };
      setResult(payload.data.evaluation);
      setAnalyzedText(file ? null : text);
      setDraftChanged(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to analyze this draft.");
    } finally {
      setBusy(false);
    }
  }

  const breakdown = result
    ? Object.entries(result.components).map(([name, score]) => ({
        label: componentLabels[name] ?? name.replaceAll("_", " "),
        value: `${Math.round(score)} / 100`,
      }))
    : [];

  function highlightEvidence(issue: EssayIssue) {
    if (!analyzedText || draftChanged) return;
    const phrase = [issue.evidence.phrase, issue.evidence.marker, issue.evidence.excerpt]
      .find((value): value is string => typeof value === "string" && value.length > 0);
    if (!phrase) return;
    const start = analyzedText.toLocaleLowerCase().indexOf(phrase.toLocaleLowerCase());
    const editor = document.getElementById("essay-text");
    if (start >= 0 && editor instanceof HTMLTextAreaElement) {
      editor.focus();
      editor.setSelectionRange(start, start + phrase.length);
      editor.scrollIntoView({ block: "center", behavior: "auto" });
    }
  }

  return (
    <form action={submit} className={styles.workspace} onChange={() => { if (result) setDraftChanged(true); }}>
      <ToolInputShell
        className={styles.editorPanel}
        description="Paste a draft or upload a supported document. The uploaded file takes precedence over pasted text."
        footer={<p className="text-xs leading-5 text-muted">Processed only for this request. Raw text is not persisted by this public analyzer.</p>}
        title="Your essay"
      >
        <fieldset className="grid min-w-0 gap-5" disabled={busy}>
          <div className="grid gap-5 sm:grid-cols-3">
            <Select id="essay-type" label="Essay type" name="essay_type" defaultValue="COMMON_APP">
              <option value="COMMON_APP">Common App</option>
              <option value="SUPPLEMENTAL">Supplemental</option>
              <option value="SCHOLARSHIP">Scholarship</option>
              <option value="OTHER">Other</option>
            </Select>
            <Input id="minimum" label="Minimum words" name="min_words" type="number" defaultValue={250} min={0} max={10_000} />
            <Input id="limit" label="Word limit" name="word_limit" type="number" defaultValue={650} min={1} max={10_000} onChange={(event) => setWordLimit(Number(event.target.value) || 1)} />
          </div>

          <details className={styles.disclosure}>
            <summary>Add essay prompt <span className="text-xs font-normal text-muted">Optional</span></summary>
            <div className="p-4">
              <Textarea className="min-h-28 bg-white" id="essay-prompt" label="Essay prompt (optional)" maxLength={10_000} name="prompt_text" placeholder="Paste the prompt or question here…" />
            </div>
          </details>

          <Textarea
            className={styles.editor}
            id="essay-text"
            label="Essay text"
            maxLength={100_000}
            name="text"
            onChange={(event) => setText(event.target.value)}
            placeholder="Paste your essay here…"
            value={text}
          />
          <div className={styles.editorFooter}>
            <p className={`text-sm font-bold ${overLimit ? "text-[var(--danger)]" : "text-muted"}`} aria-live="polite">
              {file ? "Word count calculated after upload" : `${wordCount} / ${wordLimit} words`}
            </p>
            <Button aria-label="Analyze" type="submit" disabled={busy || (!text.trim() && !file)}>
              {busy ? "Analyzing essay…" : "Analyze essay"} <span aria-hidden="true">→</span>
            </Button>
          </div>
          <details className={styles.disclosure}>
            <summary>Use a document instead <span className="text-xs font-normal text-muted">TXT · MD · DOCX · PDF</span></summary>
            <div className="p-4"><Input
            accept=".txt,.md,.docx,.pdf"
            description="TXT, Markdown, DOCX, or text-based PDF; maximum 4 MB. Scanned PDFs require OCR and are not supported."
            id="essay-file"
            label="Or upload a document"
            name="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            type="file"
          /></div>
          </details>
        </fieldset>
      </ToolInputShell>

      <div aria-live="polite" aria-busy={busy} className={styles.results}>
        {busy ? <LoadingResult label="Analyzing essay" /> : null}
        {error ? <ErrorResult message={error} title="Analysis failed" /> : null}
        {!busy && !error && !result ? (
          <Card className="p-7">
            <p className="eyebrow">Score → evidence → rule</p>
            <h2 className="mt-3 text-xl font-extrabold">Your result will appear here</h2>
            <p className="mt-2 leading-7 text-muted">You will see the mechanical score, all eight dimensions, measurable evidence, and triggered rules.</p>
            <ol className="mt-6 grid gap-4 border-t border-border pt-5 text-sm text-muted"><li><span className="mr-3 font-bold text-primary">01</span> Add a draft and its word limit</li><li><span className="mr-3 font-bold text-primary">02</span> Inspect the measured dimensions</li><li><span className="mr-3 font-bold text-primary">03</span> Open a finding to see its evidence</li></ol>
          </Card>
        ) : null}
        {result ? (
          <>
            {draftChanged ? <p className="rounded-lg border border-border bg-[var(--surface-soft)] p-4 text-sm" role="status">Your draft or settings changed. Analyze again to update the result.</p> : null}
            <Card className="overflow-hidden">
              <div className={styles.scoreIntro}>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-white/80">Mechanical Essay Score</p>
                    <p className={`${styles.scoreNumber} mt-4`}>{result.display_score}<small> / 100</small></p>
                    <p className="mt-2 font-extrabold">{result.label}</p>
                  </div>
                  <StatusBadge className="border-white/30 bg-white/10 text-white">● {result.confidence} confidence</StatusBadge>
                </div>
              </div>
              <dl className="grid grid-cols-3 divide-x divide-border p-5 text-center text-sm">
                <div><dt className="text-muted">Words</dt><dd className="mt-1 text-lg font-extrabold">{result.metrics.word_count}</dd></div>
                <div><dt className="text-muted">Sentences</dt><dd className="mt-1 text-lg font-extrabold">{result.metrics.sentence_count}</dd></div>
                <div><dt className="text-muted">Paragraphs</dt><dd className="mt-1 text-lg font-extrabold">{result.metrics.paragraph_count}</dd></div>
              </dl>
            </Card>

            <section aria-labelledby="essay-components-title">
              <ScoreBreakdown id="essay-components-title" items={breakdown} title="Components" />
            </section>

            <details className={styles.disclosure}>
              <summary>Measured signals</summary>
              <dl className="grid gap-x-6 p-5">
                {Object.entries(result.metrics)
                  .filter(([name]) => !["word_count", "sentence_count", "paragraph_count", "character_count"].includes(name))
                  .map(([name, value]) => (
                    <div className="flex justify-between gap-4 border-b border-border py-2 text-sm" key={name}>
                      <dt className="capitalize text-muted">{name.replaceAll("_", " ")}</dt>
                      <dd className="font-semibold">{value === null ? "N/A" : value}</dd>
                    </div>
                  ))}
              </dl>
            </details>

            <section aria-labelledby="priority-findings-title">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div><p className="eyebrow">Evidence → rule</p><h2 className="mt-2 text-2xl font-extrabold" id="priority-findings-title">Priority findings</h2></div>
                <span className="text-sm font-bold text-muted">{result.issues.length} triggered</span>
              </div>
              {result.issues.length ? (
                <div className="mt-4 grid gap-4">
                  {result.issues.map((issue, index) => (
                    <div key={`${issue.rule_id}-${index}`}>
                    <RuleFinding
                      confidence={issue.confidence ?? result.confidence}
                      evidence={evidenceText(issue.evidence)}
                      explanation={issue.message}
                      methodologyLink={issue.methodology_link ?? "/methodology/essay"}
                      ruleId={issue.rule_id}
                      scoreEffect={issue.score_effect ?? (issue.score_delta == null ? "No separate point adjustment" : `${issue.score_delta > 0 ? "+" : ""}${issue.score_delta} component points`)}
                      severity={issue.severity}
                      title={issue.title}
                    />
                    {analyzedText && [issue.evidence.phrase, issue.evidence.marker, issue.evidence.excerpt].some((value) => typeof value === "string" && value.length > 0 && analyzedText.toLocaleLowerCase().includes(value.toLocaleLowerCase())) ? <Button className="mt-2" disabled={draftChanged} onClick={() => highlightEvidence(issue)} type="button" variant="ghost">Highlight evidence in draft <span aria-hidden="true">↗</span></Button> : null}
                    </div>
                  ))}
                </div>
              ) : <Card className="mt-4 p-5"><p className="font-bold">No deterministic rule was triggered.</p><p className="mt-2 text-sm text-muted">Review the component scores and measured signals for remaining context.</p></Card>}
            </section>

            <Card className="p-5 sm:p-6">
              <h2 className="font-extrabold">Methodology and privacy</h2>
              <p className="mt-2 text-sm leading-6 text-muted">This result measures text patterns—not authenticity, emotional quality, admission probability, or who wrote the essay.</p>
              <div className="mt-3 flex flex-wrap items-center gap-3">
                <MethodologyLink href="/methodology/essay" label="Why this result?" />
                <ButtonLink href="/essays" variant="secondary">Save an analysis</ButtonLink>
              </div>
              {result.engine_version || result.rubric_version ? <p className="mt-3 text-xs text-muted">Engine {result.engine_version ?? "2.0.0"} · Rubric {result.rubric_version ?? "essay-1.0.0"}</p> : null}
            </Card>
          </>
        ) : null}
      </div>
    </form>
  );
}
