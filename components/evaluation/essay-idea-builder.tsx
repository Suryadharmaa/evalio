"use client";

import { useState } from "react";

import { ErrorResult, LoadingResult, ToolInputShell } from "@/components/tools";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Select, Textarea } from "@/components/ui/field";
import { apiError } from "@/lib/api/client";
import styles from "./analysis-workspace.module.css";

interface EssayIdea {
  change: string;
  core_value: string;
  idea_number: number;
  moment: string;
  people_or_place: string | null;
  possible_fit: string;
  questions_to_explore: string[];
  reflection_direction: string;
  tension: string;
  title: string;
}

interface IdeaResult {
  builder_version: string;
  engine_version: string;
  ideas: EssayIdea[];
}

const suggestedValues = [
  "curiosity", "responsibility", "independence", "resilience", "leadership", "service", "creativity",
  "community", "family", "discipline", "risk", "identity", "learning", "adaptability",
];

function lines(formData: FormData, name: string) {
  return String(formData.get(name) ?? "")
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function LineListField({ description, id, label, name, placeholder }: { description: string; id: string; label: string; name: string; placeholder: string }) {
  return <Textarea description={description} id={id} label={label} maxLength={6_000} name={name} placeholder={placeholder} />;
}

export function EssayIdeaBuilder() {
  const [result, setResult] = useState<IdeaResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(formData: FormData) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        essay_type: formData.get("essay_type"),
        prompt_selection: String(formData.get("prompt_selection") ?? "").trim() || null,
        specific_moments: lines(formData, "specific_moments"),
        experiences: lines(formData, "experiences"),
        activities: lines(formData, "activities"),
        values: formData.getAll("values").map(String),
        challenges: lines(formData, "challenges"),
        turning_points: lines(formData, "turning_points"),
        people_or_places: lines(formData, "people_or_places"),
        lessons_or_changes: lines(formData, "lessons_or_changes"),
      };
      const response = await fetch("/api/v1/essay-ideas/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const responsePayload = await response.json() as { data: { result: IdeaResult } };
      setResult(responsePayload.data.result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to build idea directions.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form action={submit} className={styles.workspace}>
      <ToolInputShell
        className="lg:sticky lg:top-28"
        description="Enter one item per line. Evalio recombines only the details you provide."
        footer={<p className="text-xs leading-5 text-muted">Inputs are used for this request only and are not persisted.</p>}
        title="Your story evidence"
      >
        <div className="grid gap-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <Select defaultValue="COMMON_APP" id="idea-essay-type" label="Essay type" name="essay_type">
              <option value="COMMON_APP">Common App</option>
              <option value="SUPPLEMENTAL">Supplemental</option>
              <option value="SCHOLARSHIP">Scholarship</option>
              <option value="OTHER">Other</option>
            </Select>
            <Input id="prompt-selection" label="Prompt selection (optional)" maxLength={500} name="prompt_selection" placeholder="Common App Prompt 5" />
          </div>

          <LineListField description="Use concrete scenes. Add multiple moments for more varied directions." id="specific-moments" label="Specific moments" name="specific_moments" placeholder={"The 3 AM server outage\nThe first failed field test\nThe meeting where I changed the plan"} />
          <LineListField description="Name the uncertainty, conflict, or constraint in each moment." id="challenges" label="Challenges or tensions" name="challenges" placeholder={"Responsibility versus being unprepared\nLimited materials and one week remaining"} />

          <fieldset>
            <legend className="text-sm font-bold">Core values</legend>
            <p className="mt-1 text-sm leading-5 text-muted">Choose at least one. More values can produce distinct angles.</p>
            <div className="value-chips mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
              {suggestedValues.map((value) => <Checkbox id={`value-${value}`} key={value} label={value[0]!.toUpperCase() + value.slice(1)} name="values" value={value} />)}
            </div>
          </fieldset>

          <LineListField description="Describe what changed in your action, belief, or understanding." id="lessons-changes" label="Lessons or changes" name="lessons_or_changes" placeholder={"I began treating leadership as responsibility under uncertainty\nI learned to test assumptions before scaling"} />

          <details className="evidence-disclosure rounded-xl border border-border bg-[var(--surface-muted)] p-4">
            <summary className="cursor-pointer font-bold text-primary">＋ Add more context</summary>
            <div className="mt-5 grid gap-5">
              <LineListField description="Broader contexts that can also serve as story anchors." id="experiences" label="Experiences" name="experiences" placeholder="Moving schools midway through the year" />
              <LineListField description="Activities that contain a specific story." id="idea-activities" label="Activities" name="activities" placeholder="Running the robotics workshop" />
              <LineListField description="Moments when your direction changed." id="turning-points" label="Turning points" name="turning_points" placeholder="A teammate challenged my original plan" />
              <LineListField description="Optional context; no names are inferred." id="people-places" label="People or places" name="people_or_places" placeholder={"The community lab\nMy project partner"} />
            </div>
          </details>

          <Alert title="Grounding requirement" tone="info">Provide enough distinct moments, tensions, values, or changes to create at least three unique combinations.</Alert>
          <div className="flex justify-end"><Button aria-label="Build idea directions" disabled={busy} type="submit">{busy ? "Building directions…" : "Build idea directions"} <span aria-hidden="true">→</span></Button></div>
        </div>
      </ToolInputShell>

      <div className="grid content-start gap-5" aria-live="polite">
        <Alert title="Brainstorming, not ghostwriting" tone="warning">Evalio produces planning directions and questions. It does not write a finished essay or invent experiences.</Alert>
        {busy ? <LoadingResult label="Building essay idea directions" /> : null}
        {error ? <ErrorResult message={error} title="Idea builder needs more context" /> : null}
        {!busy && !error && !result ? <Card className="p-7"><p className="eyebrow">Directions</p><h2 className="mt-3 text-xl font-extrabold">Your grounded ideas will appear here</h2><p className="mt-2 leading-7 text-muted">Each direction connects a moment, tension, value, change, and reflection path.</p></Card> : null}
        {result ? (
          <>
            <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="eyebrow">Brainstorming result</p><h2 className="mt-2 text-2xl font-extrabold">{result.ideas.length} grounded direction{result.ideas.length === 1 ? "" : "s"}</h2></div><p className="text-xs text-muted">Builder {result.builder_version}</p></div>
            {result.ideas.map((idea) => (
              <Card className="overflow-hidden" key={idea.idea_number}>
                <div className="border-b border-border bg-[var(--primary-soft)] p-5">
                  <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-primary">Idea {String(idea.idea_number).padStart(2, "0")}</p>
                  <h3 className="mt-2 text-xl font-extrabold">{idea.title}</h3>
                </div>
                <dl className="grid gap-4 p-5 text-sm sm:grid-cols-2">
                  <div><dt className="font-extrabold">Moment</dt><dd className="mt-1 leading-6 text-muted">{idea.moment}</dd></div>
                  <div><dt className="font-extrabold">Tension</dt><dd className="mt-1 leading-6 text-muted">{idea.tension}</dd></div>
                  <div><dt className="font-extrabold">Core value</dt><dd className="mt-1 leading-6 text-muted">{idea.core_value}</dd></div>
                  <div><dt className="font-extrabold">Change</dt><dd className="mt-1 leading-6 text-muted">{idea.change}</dd></div>
                  {idea.people_or_place ? <div><dt className="font-extrabold">Person or place</dt><dd className="mt-1 leading-6 text-muted">{idea.people_or_place}</dd></div> : null}
                  <div><dt className="font-extrabold">Possible fit</dt><dd className="mt-1 leading-6 text-muted">{idea.possible_fit}</dd></div>
                  <div className="sm:col-span-2"><dt className="font-extrabold">Reflection direction</dt><dd className="mt-1 leading-6 text-muted">{idea.reflection_direction}</dd></div>
                </dl>
                <details className="evidence-disclosure border-t border-border p-5"><summary>Questions to explore</summary><ul className="mt-3 grid gap-2 text-sm leading-6 text-muted">{idea.questions_to_explore.map((question) => <li className="flex gap-2" key={question}><span aria-hidden="true">→</span><span>{question}</span></li>)}</ul></details>
              </Card>
            ))}
          </>
        ) : null}
      </div>
    </form>
  );
}
