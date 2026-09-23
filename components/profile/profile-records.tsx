"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Select } from "@/components/ui/field";
import { EmptyState } from "@/components/ui/empty-state";
import { apiError, authenticatedFetch } from "@/lib/api/client";
import { SchoolContextEditor } from "@/components/profile/school-context-editor";
import { CourseEditor } from "@/components/profile/course-editor";

type RecordKind = "academics" | "testing" | "activities" | "honors";
interface Profile { id: string; profile_name: string }
interface SavedRecord { id: string; [key: string]: unknown }
interface Config {
  title: string;
  description: string;
  endpoint: string;
  nameKey: string;
  evaluate?: string;
  methodology: string;
}

const configs: Record<RecordKind, Config> = {
  academics: { title: "Academics", description: "Enter term averages in the grading scale your school actually uses.", endpoint: "academic-terms", nameKey: "term_name", evaluate: "academic", methodology: "academic" },
  testing: { title: "Testing", description: "Record official or self-reported standardized test results.", endpoint: "tests", nameKey: "test_type", methodology: "testing" },
  activities: { title: "Activities", description: "Capture sustained responsibility, impact, initiative, and progression.", endpoint: "activities", nameKey: "activity_name", evaluate: "activities", methodology: "activities" },
  honors: { title: "Honors", description: "Provide evidence such as scope, placement, and selectivity—not title alone.", endpoint: "honors", nameKey: "honor_name", evaluate: "honors", methodology: "honors" },
};

function optionalNumber(form: FormData, name: string) {
  const value = String(form.get(name) ?? "").trim();
  return value ? Number(value) : null;
}

function optionalText(form: FormData, name: string) {
  return String(form.get(name) ?? "").trim() || null;
}

function stripServerFields(record: SavedRecord): Record<string, unknown> {
  const copy: Record<string, unknown> = { ...record };
  delete copy.id;
  delete copy.created_at;
  delete copy.updated_at;
  return copy;
}

function payloadFor(kind: RecordKind, form: FormData, count: number): Record<string, unknown> {
  if (kind === "academics") return { term_order: count, term_name: String(form.get("term_name") ?? "").trim(), school_year: String(form.get("school_year") ?? "").trim(), average_grade: optionalNumber(form, "average_grade"), scale_min: optionalNumber(form, "scale_min"), scale_max: optionalNumber(form, "scale_max") };
  if (kind === "testing") return { test_type: String(form.get("test_type") ?? "").trim(), composite_score: optionalNumber(form, "composite_score"), test_date: optionalText(form, "test_date"), is_official: form.get("is_official") === "on", section_scores: null };
  if (kind === "activities") return { activity_order: count, activity_name: String(form.get("activity_name") ?? "").trim(), position_title: optionalText(form, "position_title"), organization_name: optionalText(form, "organization_name"), description: optionalText(form, "description"), category: optionalText(form, "category"), hours_per_week: optionalNumber(form, "hours_per_week"), weeks_per_year: optionalNumber(form, "weeks_per_year"), duration_months: optionalNumber(form, "duration_months"), people_impacted: optionalNumber(form, "people_impacted"), leadership_level: optionalText(form, "leadership_level"), recognition_scope: optionalText(form, "recognition_scope"), progression_level: optionalNumber(form, "progression_level"), participant_count: null, start_date: null, end_date: null, is_founder: form.get("is_founder") === "on" };
  return { honor_name: String(form.get("honor_name") ?? "").trim(), scope: optionalText(form, "scope"), placement: optionalText(form, "placement"), participant_count: optionalNumber(form, "participant_count"), selection_rate: optionalNumber(form, "selection_rate"), organizer: optionalText(form, "organizer"), countries_represented: optionalNumber(form, "countries_represented"), academic_area: optionalText(form, "academic_area"), grade_received: optionalText(form, "grade_received"), repeat_count: optionalNumber(form, "repeat_count") ?? 1 };
}

function RecordFields({ kind }: { kind: RecordKind }) {
  if (kind === "academics") return <div className="grid gap-5 sm:grid-cols-2"><Input id="term-name" label="Term name" name="term_name" placeholder="Grade 11 Semester 1" required /><Input id="school-year" label="School year" name="school_year" placeholder="2025–2026" required /><Input id="average-grade" label="Average grade" name="average_grade" type="number" step="0.001" /><Input id="scale-min" label="Scale minimum" name="scale_min" type="number" step="0.001" /><Input id="scale-max" label="Scale maximum" name="scale_max" type="number" step="0.001" /></div>;
  if (kind === "testing") return <div className="grid gap-5 sm:grid-cols-2"><Select id="test-type" label="Test" name="test_type" required defaultValue="SAT"><option>SAT</option><option>ACT</option><option>TOEFL</option><option>IELTS</option><option>DUOLINGO</option><option>OTHER</option></Select><Input id="composite-score" label="Composite score" name="composite_score" type="number" step="0.01" /><Input id="test-date" label="Test date" name="test_date" type="date" /><Checkbox id="official" label="Official score" name="is_official" /></div>;
  if (kind === "activities") return <div className="grid gap-5 sm:grid-cols-2"><Input id="activity-name" label="Activity" name="activity_name" required /><Input id="position-title" label="Role / position" name="position_title" /><Input id="organization-name" label="Organization" name="organization_name" /><Input id="category" label="Category" name="category" /><Input id="hours-week" label="Hours per week" name="hours_per_week" type="number" min="0" max="168" step="0.5" /><Input id="weeks-year" label="Weeks per year" name="weeks_per_year" type="number" min="0" max="53" step="0.5" /><Input id="duration-months" label="Duration (months)" name="duration_months" type="number" min="0" max="240" /><Input id="people-impacted" label="People impacted" name="people_impacted" type="number" min="0" /><Select id="leadership" label="Leadership" name="leadership_level" defaultValue="PARTICIPANT"><option value="PARTICIPANT">Participant</option><option value="INFORMAL">Informal leadership</option><option value="OPERATIONAL">Operational responsibility</option><option value="LEAD">Team lead</option><option value="EXECUTIVE">Executive</option><option value="FOUNDER">Founder</option></Select><Select id="recognition" label="Recognition scope" name="recognition_scope" defaultValue="NONE"><option value="NONE">None</option><option value="SCHOOL_LOCAL">School / local</option><option value="REGIONAL">Regional</option><option value="STATE">State</option><option value="NATIONAL">National</option><option value="INTERNATIONAL">International</option></Select><Input id="progression" label="Progression level (0–3)" name="progression_level" type="number" min="0" max="3" /><Checkbox id="founder" label="Founded this activity" name="is_founder" /><div className="sm:col-span-2"><Input id="activity-description" label="Description" name="description" maxLength={2000} /></div></div>;
  return <div className="grid gap-5 sm:grid-cols-2"><Input id="honor-name" label="Honor / award" name="honor_name" required /><Select id="scope" label="Scope" name="scope" defaultValue="SCHOOL"><option value="SCHOOL">School</option><option value="LOCAL">Local</option><option value="REGIONAL">Regional</option><option value="STATE">State</option><option value="NATIONAL">National</option><option value="INTERNATIONAL">International</option></Select><Select id="placement" label="Placement" name="placement" defaultValue="PARTICIPANT"><option value="PARTICIPANT">Participant / recipient</option><option value="HONORABLE_MENTION">Honorable mention</option><option value="TOP_10">Top 10</option><option value="TOP_5">Top 5</option><option value="THIRD">Third</option><option value="SECOND">Second</option><option value="FIRST">First</option></Select><Input id="organizer" label="Organizer" name="organizer" /><Input id="participants" label="Participant count" name="participant_count" type="number" min="1" /><Input id="selection-rate" label="Selection rate (0–1)" name="selection_rate" type="number" min="0" max="1" step="0.001" /><Input id="countries" label="Countries represented" name="countries_represented" type="number" min="1" /><Input id="academic-area" label="Academic area" name="academic_area" /><Input id="repeat-count" label="Times received" name="repeat_count" type="number" min="1" max="10" defaultValue="1" /></div>;
}

export function ProfileRecords({ kind }: { kind: RecordKind }) {
  const config = configs[kind];
  const [profile, setProfile] = useState<Profile | null>(null);
  const [records, setRecords] = useState<SavedRecord[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const profileResponse = await authenticatedFetch("/api/v1/profiles");
    if (!profileResponse.ok) throw new Error(await apiError(profileResponse));
    const selected = ((await profileResponse.json()) as { data: Profile[] }).data[0] ?? null;
    setProfile(selected);
    if (!selected) return;
    const response = await authenticatedFetch(`/api/v1/profiles/${selected.id}/${config.endpoint}`);
    if (!response.ok) throw new Error(await apiError(response));
    setRecords(((await response.json()) as { data: SavedRecord[] }).data);
  }, [config.endpoint]);

  useEffect(() => { void (async () => { try { await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to load records."); } })(); }, [load]);

  async function save(formData: FormData) {
    if (!profile) return;
    setBusy(true); setMessage(null); setResult(null);
    try {
      const payload = payloadFor(kind, formData, records.length);
      const bulk = kind === "academics";
      const body = bulk ? [...records.map(stripServerFields), payload] : payload;
      const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/${config.endpoint}`, { method: bulk ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (!response.ok) throw new Error(await apiError(response));
      setMessage("Saved.");
      await load();
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to save."); }
    finally { setBusy(false); }
  }

  async function remove(recordId: string) {
    if (!profile) return;
    setBusy(true); setMessage(null);
    try {
      if (kind === "academics") {
        const body = records.filter((item) => item.id !== recordId).map((item, index) => ({ ...stripServerFields(item), term_order: index }));
        const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/${config.endpoint}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
        if (!response.ok) throw new Error(await apiError(response));
      } else {
        const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/${config.endpoint}/${recordId}`, { method: "DELETE" });
        if (!response.ok) throw new Error(await apiError(response));
      }
      await load();
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to delete."); }
    finally { setBusy(false); }
  }

  async function evaluate() {
    if (!profile || !config.evaluate) return;
    setBusy(true); setMessage(null);
    try {
      const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/evaluate/${config.evaluate}`, { method: "POST" });
      if (!response.ok) throw new Error(await apiError(response));
      setResult(((await response.json()) as { data: Record<string, unknown> }).data);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Evaluation failed."); }
    finally { setBusy(false); }
  }

  return <div className="mx-auto w-full max-w-5xl px-5 py-12 sm:px-8 lg:px-12"><p className="text-sm font-semibold text-primary">Applicant profile</p><h1 className="mt-2 text-4xl font-bold tracking-tight">{config.title}</h1><p className="mt-3 max-w-2xl leading-7 text-muted">{config.description}</p>{!profile ? <Alert className="mt-8" title="Profile needed" tone="warning">Create a profile first.</Alert> : <>{kind === "academics" ? <><SchoolContextEditor profileId={profile.id} /><CourseEditor profileId={profile.id} /></> : null}<Card className="mt-8 p-6"><h2 className="text-xl font-bold">Add record</h2><form action={save} className="mt-5 grid gap-6"><RecordFields kind={kind} />{message ? <Alert title="Status">{message}</Alert> : null}<div className="flex flex-wrap justify-end gap-3">{config.evaluate ? <Button disabled={busy || records.length === 0} onClick={evaluate} type="button" variant="secondary">Evaluate saved data</Button> : null}<Button disabled={busy} type="submit">{busy ? "Working…" : "Save"}</Button></div></form></Card><section className="mt-8"><h2 className="text-2xl font-bold">Saved records</h2>{records.length ? <div className="mt-4 grid gap-3">{records.map((record) => <Card className="flex items-center justify-between gap-4 p-5" key={record.id}><div><p className="font-semibold">{String(record[config.nameKey] ?? "Untitled")}</p><p className="mt-1 text-sm text-muted">Stored in {profile.profile_name}{typeof record.current_score === "number" ? ` · Current internal score ${record.current_score}/100` : ""}</p></div><Button disabled={busy} onClick={() => void remove(record.id)} variant="danger">Delete</Button></Card>)}</div> : <div className="mt-4"><EmptyState description="Add the first record above." title={`No ${config.title.toLowerCase()} yet`} /></div>}</section>{result ? <Card className="mt-8 p-6"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-bold">Latest deterministic result</h2><ButtonLink href={`/methodology/${config.methodology}`} variant="secondary">Why this result?</ButtonLink></div><pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-[var(--surface-muted)] p-4 text-sm">{JSON.stringify(result, null, 2)}</pre></Card> : null}</>}</div>;
}
