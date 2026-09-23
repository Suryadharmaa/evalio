"use client";

import { useRef, useState } from "react";

import { ErrorResult, LoadingResult, ToolInputShell } from "@/components/tools";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/field";
import { apiError } from "@/lib/api/client";

type Mode = "US_COURSES" | "INTERNATIONAL_RAW";
const views = ["High School GPA", "Weighted", "Unweighted", "Cumulative", "Percentage", "International"] as const;
type View = typeof views[number];
type CourseLevel = "REGULAR" | "HONORS" | "AP" | "IB" | "DUAL_ENROLLMENT" | "OTHER_ADVANCED";
interface Row { id: number; label: string; grade: string; level: string; credits: string; }
interface Result {
  calculator_version: string; mode: Mode; unweighted_gpa: number | null; weighted_gpa: number | null;
  academic_average: number | null; scale_min: number | null; scale_max: number | null;
  total_credits_or_weight: number; conversion: "NOT_APPLIED"; weighting_method: string | null;
  formula: string[]; breakdown: Array<{ label: string; credits_or_weight: number; base_value: number; weighted_value: number | null; course_level: string | null }>;
}

let nextId = 2;
const newRow = (): Row => ({ id: nextId++, label: "", grade: "A", level: "REGULAR", credits: "1" });

export function GpaToolkit() {
  const [mode, setMode] = useState<Mode>("US_COURSES");
  const [view, setView] = useState<View>("High School GPA");
  const drafts = useRef<Partial<Record<Mode, Row[]>>>({});
  const [curriculum, setCurriculum] = useState("");
  const [scaleMin, setScaleMin] = useState("0");
  const [scaleMax, setScaleMax] = useState("100");
  const [rows, setRows] = useState<Row[]>([{ id: 1, label: "", grade: "A", level: "REGULAR", credits: "1" }]);
  const [weightingMethod, setWeightingMethod] = useState("NONE");
  const [customOffsets, setCustomOffsets] = useState<Record<CourseLevel, string>>({ REGULAR: "0", HONORS: "0.5", AP: "1", IB: "1", DUAL_ENROLLMENT: "1", OTHER_ADVANCED: "1" });
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function updateRow(id: number, key: keyof Row, value: string) {
    setRows((current) => current.map((row) => row.id === id ? { ...row, [key]: value } : row));
  }

  async function submit(formData: FormData) {
    setBusy(true); setError(null); setResult(null);
    try {
      const payload = mode === "US_COURSES" ? {
        mode,
        weighting_method: weightingMethod,
        custom_offsets: weightingMethod === "CUSTOM" ? Object.fromEntries(Object.entries(customOffsets).map(([level, value]) => [level, Number(value)])) : null,
        courses: rows.map((row) => ({ course: row.label.trim(), grade: row.grade, course_level: row.level, credits: Number(row.credits) })),
      } : {
        mode,
        curriculum_name: String(formData.get("curriculum_name") ?? "").trim(),
        scale_min: Number(formData.get("scale_min")), scale_max: Number(formData.get("scale_max")),
        international_grades: rows.map((row) => ({ label: row.label.trim(), value: Number(row.grade), weight: Number(row.credits) })),
      };
      const response = await fetch("/api/v1/calculators/gpa", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error(await apiError(response));
      const body = await response.json() as { data: { result: Result } };
      setResult(body.data.result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to calculate GPA.");
    } finally { setBusy(false); }
  }

  function switchMode(value: Mode) {
    if (value === mode) { setResult(null); return; }
    drafts.current[mode] = rows;
    setMode(value); setResult(null); setError(null);
    setRows(drafts.current[value] ?? [{ ...newRow(), grade: value === "US_COURSES" ? "A" : "90" }]);
  }

  return <form action={submit} onChange={() => { if (result) setResult(null); }} className="mt-12 grid gap-6 lg:grid-cols-[1.3fr_1fr] lg:items-start">
    <ToolInputShell className="lg:sticky lg:top-28" description="Enter courses or term averages. Every input and calculation remains visible." title="Grade inputs">
      <div className="grid gap-5">
        <div className="evalio-tabs" role="tablist" aria-label="GPA mode">{views.map((item, index) => <button key={item} id={`gpa-mode-${index}`} role="tab" type="button" aria-selected={view === item} aria-controls="gpa-mode-panel" tabIndex={view === item ? 0 : -1} onKeyDown={(event) => { const keys = ["ArrowRight", "ArrowLeft", "Home", "End"]; if (!keys.includes(event.key)) return; event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? views.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + views.length) % views.length; document.getElementById(`gpa-mode-${next}`)?.click(); document.getElementById(`gpa-mode-${next}`)?.focus(); }} onClick={() => { setView(item); switchMode(item === "International" || item === "Percentage" ? "INTERNATIONAL_RAW" : "US_COURSES"); if (item === "Weighted") setWeightingMethod("HONORS_0_5_ADVANCED_1_0"); if (item === "Unweighted") setWeightingMethod("NONE"); }}>{item}</button>)}</div>
        <div id="gpa-mode-panel" role="tabpanel" aria-labelledby={`gpa-mode-${views.indexOf(view)}`} className="text-sm text-muted">{view === "Cumulative" ? "Enter courses from all terms with their credits. The backend calculates the cumulative, credit-weighted GPA." : mode === "US_COURSES" ? "US courses · Select an explicit weighting method. Switching modes preserves your course entries." : "International / percentage · Original scale retained. No automatic 4.0 conversion."}</div>

        {mode === "US_COURSES" ? <><Select description="A weighted result is calculated only from this explicit method." id="weighting-method" label="Weighting method" name="weighting_method" onChange={(event) => setWeightingMethod(event.target.value)} value={weightingMethod}>
          <option value="NONE">No weighting</option>
          <option value="HONORS_0_5_ADVANCED_1_0">Honors +0.5; AP, IB, dual enrollment, other advanced +1.0</option>
          <option value="CUSTOM">Custom course-level offsets</option>
        </Select>{weightingMethod === "CUSTOM" ? <fieldset className="grid gap-3 rounded-xl border border-border p-4"><legend className="px-1 text-sm font-bold">Custom offsets added to grade points</legend><div className="grid gap-3 sm:grid-cols-3">{(Object.keys(customOffsets) as CourseLevel[]).map((level) => <Input id={`offset-${level}`} key={level} label={level.replaceAll("_", " ")} max="5" min="0" onChange={(event) => setCustomOffsets((current) => ({ ...current, [level]: event.target.value }))} required step="0.1" type="number" value={customOffsets[level]} />)}</div></fieldset> : null}</> : <div className="grid gap-4 sm:grid-cols-3">
          <Input id="curriculum-name" label="Curriculum" name="curriculum_name" placeholder="National curriculum" required value={curriculum} onChange={(event) => setCurriculum(event.target.value)} />
          <Input value={scaleMin} onChange={(event) => setScaleMin(event.target.value)} id="scale-min" label="Scale minimum" name="scale_min" required step="any" type="number" />
          <Input value={scaleMax} onChange={(event) => setScaleMax(event.target.value)} id="scale-max" label="Scale maximum" name="scale_max" required step="any" type="number" />
        </div>}

        <div className="grid gap-3">
          {rows.map((row, index) => <Card className="page-enter grid gap-3 p-4" key={row.id}>
            <div className="flex items-center justify-between"><p className="text-sm font-extrabold">{mode === "US_COURSES" ? "Course" : "Course or term"} {index + 1}</p>{rows.length > 1 ? <Button aria-label={`Remove row ${index + 1}`} className="min-h-0 px-3 py-1" onClick={() => setRows((current) => current.filter((item) => item.id !== row.id))} variant="ghost">Remove</Button> : null}</div>
            <Input id={`label-${row.id}`} label={mode === "US_COURSES" ? "Course" : "Label"} onChange={(event) => updateRow(row.id, "label", event.target.value)} required value={row.label} />
            <div className="grid gap-3 sm:grid-cols-3">
              {mode === "US_COURSES" ? <>
                <Select id={`grade-${row.id}`} label="Grade" onChange={(event) => updateRow(row.id, "grade", event.target.value)} value={row.grade}>{["A+","A","A-","B+","B","B-","C+","C","C-","D+","D","D-","F"].map((grade) => <option key={grade}>{grade}</option>)}</Select>
                <Select id={`level-${row.id}`} label="Course level" onChange={(event) => updateRow(row.id, "level", event.target.value)} value={row.level}><option value="REGULAR">Regular</option><option value="HONORS">Honors</option><option value="AP">AP</option><option value="IB">IB</option><option value="DUAL_ENROLLMENT">Dual enrollment</option><option value="OTHER_ADVANCED">Other advanced</option></Select>
              </> : <Input id={`grade-${row.id}`} label="Grade / average" onChange={(event) => updateRow(row.id, "grade", event.target.value)} required step="any" type="number" value={row.grade} />}
              <Input id={`credits-${row.id}`} label={mode === "US_COURSES" ? "Credits" : "Weight"} min="0.01" onChange={(event) => updateRow(row.id, "credits", event.target.value)} required step="any" type="number" value={row.credits} />
            </div>
          </Card>)}
        </div>
        <div className="flex flex-wrap justify-between gap-3"><Button onClick={() => setRows((current) => [...current, { ...newRow(), grade: mode === "US_COURSES" ? "A" : "90" }])} variant="secondary">+ Add row</Button><Button disabled={busy} type="submit">{busy ? "Calculating…" : "Calculate"} <span aria-hidden="true">→</span></Button></div>
      </div>
    </ToolInputShell>

    <div className="grid content-start gap-5" aria-live="polite">
      <Alert title="Original scale preserved" tone="info">Evalio does not force international grades into a 4.0 GPA. No conversion is performed by this calculator.</Alert>
      {busy ? <LoadingResult label="Calculating GPA" /> : null}
      {error ? <ErrorResult message={error} title="Calculation unavailable" /> : null}
      {!busy && !error && !result ? <Card className="p-7"><p className="eyebrow">Result</p><h2 className="mt-3 text-xl font-extrabold">Your transparent calculation will appear here</h2><p className="mt-2 leading-7 text-muted">The result includes the exact formula and row-level values.</p></Card> : null}
      {result ? <>
        <Card className="overflow-hidden"><div className="bg-[var(--primary-soft)] p-6"><p className="eyebrow">{result.mode === "US_COURSES" ? "Calculated GPA" : "Academic average"}</p><div className="mt-3 flex flex-wrap items-end gap-6">{result.mode === "US_COURSES" ? <><div><p className="text-4xl font-extrabold">{result.unweighted_gpa?.toFixed(3)}</p><p className="text-sm text-muted">Unweighted / 4.0</p></div><div><p className="text-4xl font-extrabold">{result.weighted_gpa?.toFixed(3)}</p><p className="text-sm text-muted">Weighted ({result.weighting_method === "NONE" ? "none" : "selected method"})</p></div></> : <div><p className="text-4xl font-extrabold">{result.academic_average?.toFixed(3)} <span className="text-xl">/ {result.scale_max}</span></p><p className="text-sm text-muted">Scale {result.scale_min}–{result.scale_max} · Conversion not applied</p></div>}</div></div>
          <details className="evidence-disclosure p-6"><summary>Exact formula</summary><ul className="evidence-rail mt-3 grid gap-2 p-4 text-sm leading-6 text-muted">{result.formula.map((line) => <li key={line}>{line}</li>)}</ul><p className="mt-3 text-xs text-muted">Calculator {result.calculator_version}</p></details></Card>
        <Card className="p-5"><h3 className="font-sans font-bold">Calculation breakdown</h3><div className="mt-4 grid gap-3">{result.breakdown.map((item, index) => <div className="rounded-lg border border-border p-4" key={`${item.label}-${index}`}><p className="font-semibold">{item.label}</p><dl className="mt-3 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-muted">Base</dt><dd>{item.base_value}</dd></div><div><dt className="text-muted">Level</dt><dd>{item.course_level?.replaceAll("_", " ") ?? "Not applicable"}</dd></div><div><dt className="text-muted">Weighted</dt><dd>{item.weighted_value ?? "Not applicable"}</dd></div><div><dt className="text-muted">Credits / weight</dt><dd>{item.credits_or_weight}</dd></div></dl></div>)}</div></Card>
      </> : null}
    </div>
  </form>;
}
