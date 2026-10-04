"use client";

import { useState } from "react";

import { ErrorResult, LoadingResult, ToolInputShell } from "@/components/tools";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Select, Textarea } from "@/components/ui/field";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiFetch, apiError } from "@/lib/api/client";

interface CourseRow { id: number; course: string; subject: string; grade: string; level: string; major: boolean; }
interface CourseworkResult {
  rubric_version: string; display_score: number; rating: string; confidence: "HIGH" | "MEDIUM" | "LOW";
  school_context: string; no_advanced_penalty: boolean; formula: string;
  components: Array<{ key: string; label: string; score: number | null; points: number; points_available: number; evidence: string; rule: string; explanation: string }>;
}

const areas = [
  ["ENGLISH", "English / language"], ["MATHEMATICS", "Mathematics"], ["LAB_SCIENCE", "Laboratory science"],
  ["SOCIAL_SCIENCE", "Social science"], ["FOREIGN_LANGUAGE", "Foreign language"], ["OTHER", "Other / elective"],
] as const;
const levels = [["STANDARD", "Standard"], ["HONORS", "Honors"], ["AP", "AP"], ["IB_SL", "IB SL"], ["IB_HL", "IB HL"], ["A_LEVEL", "A-Level"], ["DUAL_ENROLLMENT", "Dual enrollment"], ["OTHER_ADVANCED", "Other advanced"]] as const;
const coreAreas = areas.slice(0, 5);
let rowId = 2;
const freshRow = (): CourseRow => ({ id: rowId++, course: "", subject: "ENGLISH", grade: "9", level: "STANDARD", major: false });

export function CourseworkEvaluator() {
  const [rows, setRows] = useState<CourseRow[]>([{ id: 1, course: "", subject: "ENGLISH", grade: "9", level: "STANDARD", major: false }]);
  const [result, setResult] = useState<CourseworkResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function update(id: number, values: Partial<CourseRow>) {
    setRows((current) => current.map((row) => row.id === id ? { ...row, ...values } : row));
  }

  async function submit(formData: FormData) {
    setBusy(true); setError(null); setResult(null);
    try {
      const highest = Object.fromEntries(coreAreas.map(([area]) => [area, formData.get(`highest_${area}`)]));
      const payload = {
        curriculum_type: String(formData.get("curriculum_type") ?? "").trim(),
        grade_levels: [...new Set(rows.map((row) => Number(row.grade)))].sort((a, b) => a - b),
        courses: rows.map((row) => ({ course: row.course.trim(), subject_area: row.subject, grade_level: Number(row.grade), course_level: row.level, is_major_related: row.major })),
        advanced_courses_available: Number(formData.get("advanced_courses_available")),
        advanced_program_types: String(formData.get("advanced_program_types") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
        highest_levels_available: highest,
        intended_major: String(formData.get("intended_major") ?? "").trim(),
        school_context_notes: String(formData.get("school_context_notes") ?? "").trim() || null,
      };
      const response = await apiFetch("/api/v1/evaluations/coursework", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error(await apiError(response));
      setResult(((await response.json()) as { data: { evaluation: CourseworkResult } }).data.evaluation);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to evaluate coursework.");
    } finally { setBusy(false); }
  }

  return <form action={submit} className="mt-12 grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
    <ToolInputShell className="lg:sticky lg:top-24" description="Report the curriculum and opportunities your school actually offers. Evalio does not infer them from country." footer={<p className="text-xs leading-5 text-muted">This public evaluation is stateless. School context and course data are not saved.</p>} title="Coursework and school context">
      <div className="grid gap-6">
        <div className="grid gap-4 sm:grid-cols-2"><Input id="coursework-curriculum" label="Curriculum type" name="curriculum_type" placeholder="IB Diploma, A-Level, national curriculum…" required /><Input id="coursework-major" label="Intended major" name="intended_major" placeholder="Computer science" required /></div>
        <div className="grid gap-4 sm:grid-cols-2"><Input defaultValue="0" description="Count opportunities, not the number of programs." id="advanced-available" label="Advanced courses available" max="100" min="0" name="advanced_courses_available" required type="number" /><Input description="Required when advanced opportunities exist." id="advanced-programs-coursework" label="Advanced program types" name="advanced_program_types" placeholder="AP, IB HL, dual enrollment" /></div>

        <fieldset className="grid gap-3 rounded-lg border border-border bg-[var(--surface-muted)] p-4"><legend className="px-1 text-sm font-bold">Highest level available by core area</legend><p className="text-sm leading-6 text-muted">Select what the school offers—not what the student took.</p><div className="grid gap-3 sm:grid-cols-2">{coreAreas.map(([area, label]) => <Select defaultValue="STANDARD" id={`highest-${area}`} key={area} label={label} name={`highest_${area}`} required>{levels.map(([value, name]) => <option key={value} value={value}>{name}</option>)}</Select>)}</div></fieldset>

        <div className="grid gap-3"><div className="flex items-end justify-between gap-4"><div><p className="font-bold">Courses taken</p><p className="text-sm text-muted">Add each distinct course used in this evaluation.</p></div><Button onClick={() => setRows((current) => [...current, freshRow()])} variant="secondary">+ Add course</Button></div>
          {[...new Set(rows.map((row) => row.grade))].sort().map((grade) => <fieldset className="grid min-w-0 gap-3 rounded-xl border border-border p-3" key={grade}><legend className="px-2 text-sm font-bold text-primary">Grade {grade}</legend>{rows.map((row, index) => row.grade === grade ? <Card className="page-enter grid gap-4 p-4 shadow-none" key={row.id}><div className="flex justify-between gap-4"><p className="hairline-label text-primary">Course {String(index + 1).padStart(2, "0")}</p>{rows.length > 1 ? <Button aria-label={`Remove course ${index + 1}`} className="min-h-0 px-2 py-1" onClick={() => setRows((current) => current.filter((item) => item.id !== row.id))} variant="ghost">Remove</Button> : null}</div><StatusBadge tone={row.level === "STANDARD" ? "neutral" : "info"}>{levels.find(([value]) => value === row.level)?.[1]}</StatusBadge><Input id={`coursework-name-${row.id}`} label="Course name" onChange={(event) => update(row.id, { course: event.target.value })} required value={row.course} /><div className="grid gap-3 sm:grid-cols-3"><Select id={`coursework-area-${row.id}`} label="Subject area" onChange={(event) => update(row.id, { subject: event.target.value })} value={row.subject}>{areas.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</Select><Select id={`coursework-grade-${row.id}`} label="Grade level" onChange={(event) => update(row.id, { grade: event.target.value })} value={row.grade}>{[9, 10, 11, 12, 13].map((grade) => <option key={grade}>{grade}</option>)}</Select><Select id={`coursework-level-${row.id}`} label="Course level" onChange={(event) => update(row.id, { level: event.target.value })} value={row.level}>{levels.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</Select></div><Checkbox checked={row.major} id={`coursework-major-${row.id}`} label="Related to intended major" onChange={(event) => update(row.id, { major: event.target.checked })} /></Card> : null)}</fieldset>)}
        </div>
        <Textarea description="Optional evidence such as restricted enrollment, scheduling constraints, or unavailable programs." id="school-context-coursework" label="School context notes" maxLength={2_000} name="school_context_notes" />
        <Alert title="Context comes first" tone="info">If the school offers zero advanced courses, Evalio applies the documented neutral-context score instead of penalizing the student.</Alert>
        <div className="flex justify-end"><Button disabled={busy} type="submit">{busy ? "Evaluating coursework…" : "Evaluate coursework"} <span aria-hidden="true">→</span></Button></div>
      </div>
    </ToolInputShell>

    <div className="grid content-start gap-5" aria-live="polite">
      {busy ? <LoadingResult label="Evaluating coursework" /> : null}
      {error ? <ErrorResult message={error} title="Coursework evaluation unavailable" /> : null}
      {!busy && !error && !result ? <Card className="p-7"><p className="eyebrow">Course rigor</p><h2 className="mt-3 text-2xl font-semibold">Your context-aware result will appear here</h2><p className="mt-3 leading-7 text-muted">Each component will show its evidence, rule, points, and explanation.</p></Card> : null}
      {result ? <><Card className="overflow-hidden"><div className="border-b border-border bg-[var(--primary-soft)] p-6"><div className="flex flex-wrap justify-between gap-4"><div><p className="hairline-label text-primary">Course rigor</p><p className="data-type mt-3 text-5xl font-extrabold">{result.display_score}<span className="text-lg text-muted"> / 100</span></p></div><div className="grid justify-items-end gap-2"><StatusBadge tone={result.rating === "STRONG" ? "success" : "warning"}>{result.rating}</StatusBadge><StatusBadge tone={result.confidence === "HIGH" ? "success" : result.confidence === "MEDIUM" ? "warning" : "neutral"}>{result.confidence} confidence</StatusBadge></div></div></div><div className="p-6"><p className="hairline-label text-primary">School context</p><p className="mt-2 leading-7">{result.school_context}</p>{result.no_advanced_penalty ? <Alert className="mt-4" title="No penalty applied" tone="success">Advanced opportunity was not available, so ACAD-005 applied the neutral-context score.</Alert> : null}<p className="evidence-rail mt-5 rounded-r-lg p-4 text-sm font-bold text-primary">{result.formula}</p></div></Card>
        <div className="grid gap-4">{result.components.map((component) => <Card className="overflow-hidden" key={component.key}><div className="flex items-center justify-between gap-4 border-b border-border bg-[var(--surface-muted)] p-5"><div><p className="hairline-label text-primary">{component.rule}</p><h3 className="mt-2 text-xl font-semibold">{component.label}</h3></div><p className="data-type text-2xl font-extrabold">{component.score === null ? "N/A" : <>{component.score}<span className="text-sm text-muted"> / 100</span></>}</p></div><details className="evidence-disclosure p-5"><summary>Evidence, rule & explanation</summary><dl className="evidence-rail grid gap-3 rounded-r-lg p-4 text-sm"><div><dt className="hairline-label text-primary">Evidence</dt><dd className="mt-1 leading-6 text-muted">{component.evidence}</dd></div><div><dt className="hairline-label text-primary">Effect</dt><dd className="data-type mt-1 text-muted">{component.points} / {component.points_available} {component.score === null ? "neutral-context " : ""}rigor points</dd></div></dl><p className="mt-4 text-sm leading-6 text-muted">{component.explanation}</p></details></Card>)}</div><p className="text-xs text-muted">Rubric {result.rubric_version}</p></> : null}
    </div>
  </form>;
}
