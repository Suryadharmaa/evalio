"use client";

import { useMemo, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Select, Textarea } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { ErrorResult, LoadingResult, ToolInputShell } from "@/components/tools";
import { apiFetch, apiError } from "@/lib/api/client";

interface FrameworkItem {
  item_type: "USER_EVIDENCE" | "SENTENCE_SHELL" | "WRITING_PROMPT";
  text: string;
  source_fields: string[];
}

interface FrameworkSection {
  key: string;
  title: string;
  purpose: string;
  items: FrameworkItem[];
}

interface LorBuildResult {
  builder_version: string;
  sections: FrameworkSection[];
  missing_evidence: string[];
  ethics_notice: string;
}

function lines(formData: FormData, name: string) {
  return String(formData.get(name) ?? "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
}

function sectionText(section: FrameworkSection) {
  return section.items.map((item) => {
    const origin = item.source_fields.length ? ` · source: ${item.source_fields.join(", ")}` : "";
    return `[${item.item_type.replaceAll("_", " ")}${origin}]\n${item.text}`;
  }).join("\n\n");
}

export function LorBuilder() {
  const [result, setResult] = useState<LorBuildResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [edits, setEdits] = useState<Record<string, string>>({});

  async function submit(formData: FormData) {
    setBusy(true);
    setError(null);
    setResult(null);
    setCopyStatus(null);
    setEdits({});
    try {
      const payload = {
        recommender_role: formData.get("recommender_role"),
        student_name: formData.get("student_name"),
        relationship_context: formData.get("relationship_context"),
        relationship_duration: formData.get("relationship_duration"),
        subject_or_context: String(formData.get("subject_or_context") ?? "").trim() || null,
        qualities: lines(formData, "qualities"),
        specific_examples: lines(formData, "specific_examples"),
        comparative_evidence: String(formData.get("comparative_evidence") ?? "").trim() || null,
        community_evidence: String(formData.get("community_evidence") ?? "").trim() || null,
        academic_evidence: String(formData.get("academic_evidence") ?? "").trim() || null,
        endorsement_strength: formData.get("endorsement_strength"),
      };
      const response = await apiFetch("/api/v1/lor/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(await apiError(response));
      setResult(((await response.json()) as { data: { result: LorBuildResult } }).data.result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to build the letter framework.");
    } finally {
      setBusy(false);
    }
  }

  const frameworkText = useMemo(() => result?.sections.map((section) => `${section.title.toUpperCase()}\n${edits[section.key] ?? sectionText(section)}`).join("\n\n") ?? "", [result, edits]);

  async function copyFramework() {
    try {
      await navigator.clipboard.writeText(frameworkText);
      setCopyStatus("Framework copied.");
    } catch {
      setCopyStatus("Copy failed. Select the editable sections and copy them manually.");
    }
  }

  return <form action={submit} onInvalidCapture={(event) => { let element = event.target as HTMLElement | null; while (element) { if (element instanceof HTMLDetailsElement) element.open = true; element = element.parentElement; } }} className="mt-12 grid gap-6 lg:grid-cols-[1fr_1fr] lg:items-start">
    <ToolInputShell className="lg:sticky lg:top-28" description="Enter only facts the recommender can verify. Use one quality or specific example per line." footer={<p className="text-xs leading-5 text-muted">Inputs are processed for this request only and are not persisted.</p>} title="Recommendation evidence">
      <div className="grid gap-5">
        <details className="evidence-disclosure rounded-lg border border-border p-4" open><summary>01 / Relationship</summary><div className="mt-4 grid gap-5">
        <div className="grid gap-5 sm:grid-cols-2"><Input id="builder-recommender-role" label="Recommender role" maxLength={160} name="recommender_role" placeholder="Mathematics teacher" required /><Input id="builder-student-name" label="Student name" maxLength={160} name="student_name" placeholder="Student's name" required /></div>
        <Textarea description="Explain how and in what capacity the recommender knows the student." id="builder-relationship" label="Relationship context" maxLength={500} name="relationship_context" placeholder="Taught the student in advanced calculus and advised the math club." required />
        <div className="grid gap-5 sm:grid-cols-2"><Input id="builder-duration" label="Relationship duration" maxLength={120} name="relationship_duration" placeholder="Two academic years" required /><Input id="builder-subject" label="Subject or context (optional)" maxLength={300} name="subject_or_context" placeholder="Advanced calculus" /></div>
        </div></details><details className="evidence-disclosure rounded-lg border border-border p-4" open><summary>02 / Evidence</summary><div className="mt-4 grid gap-5"><Textarea description="One quality per line. Use qualities the recommender directly observed." id="builder-qualities" label="Observed qualities" maxLength={4_000} name="qualities" placeholder={"Analytical curiosity\nCollaborative leadership"} required />
        <Textarea description="One concrete event per line. Do not add examples that did not happen." id="builder-examples" label="Specific examples" maxLength={8_000} name="specific_examples" placeholder={"During the modeling project, she tested three approaches before presenting the result.\nShe organized weekly peer-review sessions for six classmates."} required />
        </div></details><details className="evidence-disclosure rounded-lg border border-border bg-[var(--surface-muted)] p-4"><summary>03 / Comparative context</summary><div className="mt-5 grid gap-5"><Textarea id="builder-academic" label="Academic or professional evidence" maxLength={1_000} name="academic_evidence" /><Textarea id="builder-community" label="Character or community evidence" maxLength={1_000} name="community_evidence" /><Textarea description="Use only a ranking or comparison the recommender can substantiate." id="builder-comparative" label="Comparative evidence" maxLength={1_000} name="comparative_evidence" /></div></details>
        <div className="rounded-lg border border-border p-4"><p className="eyebrow mb-4">04 / Endorsement</p>
        <Select defaultValue="STRONG" id="builder-endorsement" label="Endorsement strength" name="endorsement_strength"><option value="MEASURED">Measured recommendation</option><option value="CLEAR">Clear recommendation</option><option value="STRONG">Strong recommendation</option><option value="WITHOUT_RESERVATION">Without reservation</option></Select>
        </div><Alert title="Recommender ownership" tone="warning">Final wording should be reviewed and owned by the recommender. Evalio will not invent anecdotes, awards, rankings, or relationship details.</Alert>
        <div className="flex justify-end"><Button disabled={busy} type="submit">{busy ? "Building framework…" : "Build letter framework"} <span aria-hidden="true">→</span></Button></div>
      </div>
    </ToolInputShell>

    <div aria-live="polite" className="grid content-start gap-5">
      {busy ? <LoadingResult label="Building recommendation framework" /> : null}
      {error ? <ErrorResult message={error} title="Framework needs more evidence" /> : null}
      {!busy && !error && !result ? <Card className="p-7"><p className="eyebrow">Framework</p><h2 className="mt-3 text-xl font-extrabold">Your evidence-backed outline will appear here</h2><p className="mt-2 leading-7 text-muted">Every factual item will show its input origin. Sentence shells retain visible placeholders.</p></Card> : null}
      {result ? <><div className="flex flex-wrap items-end justify-between gap-3"><div><p className="eyebrow">Builder result</p><h2 className="mt-2 text-2xl font-extrabold">Editable letter framework</h2></div><StatusBadge tone="info">{result.builder_version}</StatusBadge></div>
        {result.missing_evidence.length ? <Alert title="Evidence still missing" tone="warning">Add these only when the recommender can verify them: {result.missing_evidence.map((item) => item.replaceAll("_", " ")).join(", ")}.</Alert> : <Alert title="Core evidence supplied" tone="success">No optional evidence gaps were detected.</Alert>}
        {result.sections.map((section) => <Card className="overflow-hidden" key={section.key}><div className="border-b border-border bg-[var(--primary-soft)] p-5"><p className="hairline-label text-primary">{section.key.replaceAll("_", " ")}</p><h3 className="mt-2 text-xl font-extrabold">{section.title}</h3><p className="mt-2 text-sm leading-6 text-muted">{section.purpose}</p></div><div className="p-5"><Textarea value={edits[section.key] ?? sectionText(section)} onChange={(event) => { setEdits({ ...edits, [section.key]: event.target.value }); setCopyStatus(null); }} id={`framework-${section.key}`} label={`${section.title} — editable framework`} rows={Math.max(10, section.items.length * 4)} /></div></Card>)}
        <Alert title="Final review required" tone="info">{result.ethics_notice}</Alert><div className="flex flex-wrap items-center justify-end gap-3"><span className="text-sm text-muted" role="status">{copyStatus}</span><Button onClick={() => void copyFramework()} type="button" variant="secondary">Copy full framework</Button></div>
      </> : null}
    </div>
  </form>;
}
