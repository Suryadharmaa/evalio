"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Select, Textarea } from "@/components/ui/field";
import { EmptyState } from "@/components/ui/empty-state";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Profile { id: string }
interface Essay { id: string; title: string | null; essay_type: string; raw_text: string | null; save_raw_text: boolean; created_at: string; evaluation_id: string | null; display_score: number | null; confidence: string | null }
interface Evaluation { display_score: number; components: Record<string, number> }

export function EssayLibrary() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [essays, setEssays] = useState<Essay[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<Evaluation | null>(null);
  const [comparison, setComparison] = useState<{ left: Evaluation; right: Evaluation; overall_delta: number } | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const profilesResponse = await authenticatedFetch("/api/v1/profiles");
    if (!profilesResponse.ok) throw new Error(await apiError(profilesResponse));
    const first = ((await profilesResponse.json()) as { data: Profile[] }).data[0] ?? null;
    setProfile(first);
    if (!first) return;
    const response = await authenticatedFetch(`/api/v1/profiles/${first.id}/essays`);
    if (!response.ok) throw new Error(await apiError(response));
    setEssays(((await response.json()) as { data: Essay[] }).data);
  }, []);

  useEffect(() => { void (async () => { try { await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to load essays."); } })(); }, [load]);

  async function save(form: FormData) {
    if (!profile) return;
    setBusy(true); setMessage(null); setResult(null);
    try {
      const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/essays`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: String(form.get("title") ?? "").trim() || null, essay_type: form.get("essay_type"), text: form.get("text"), min_words: Number(form.get("min_words")), word_limit: Number(form.get("word_limit")), prompt_text: null, save: false, save_raw_text: form.get("save_raw_text") === "on" }) });
      if (!response.ok) throw new Error(await apiError(response));
      const data = ((await response.json()) as { data: { evaluation: Evaluation } }).data;
      setResult(data.evaluation); setMessage("Analysis saved. Raw text was stored only if you opted in."); await load();
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to save analysis."); }
    finally { setBusy(false); }
  }

  async function compare(form: FormData) {
    setBusy(true); setMessage(null); setComparison(null);
    const common = { essay_type: "COMMON_APP", min_words: 250, word_limit: 650, prompt_text: null, save: false };
    try {
      const response = await fetch("/api/v1/evaluations/essay/compare", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify([{ ...common, text: form.get("left") }, { ...common, text: form.get("right") }]) });
      if (!response.ok) throw new Error(await apiError(response));
      setComparison(((await response.json()) as { data: { left: Evaluation; right: Evaluation; overall_delta: number } }).data);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to compare drafts."); }
    finally { setBusy(false); }
  }

  async function compareSaved(form: FormData) {
    setBusy(true); setMessage(null); setComparison(null);
    try {
      const response = await authenticatedFetch("/api/v1/evaluations/essay/compare", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ left_evaluation_id: form.get("left_saved"), right_evaluation_id: form.get("right_saved") }) });
      if (!response.ok) throw new Error(await apiError(response));
      setComparison(((await response.json()) as { data: { left: Evaluation; right: Evaluation; overall_delta: number } }).data);
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to compare saved evaluations."); }
    finally { setBusy(false); }
  }

  async function remove(id: string) {
    if (!profile) return;
    const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/essays/${id}`, { method: "DELETE" });
    if (!response.ok) setMessage(await apiError(response)); else await load();
  }

  if (!profile) return <Alert className="mt-8" title="Profile needed" tone="warning">Create a profile before saving essay analyses.</Alert>;
  const savedEssays = essays.filter((essay) => essay.evaluation_id);
  return <>
    <Card className="mt-8 p-6"><h2 className="text-xl font-bold">Analyze and optionally save</h2><form action={save} className="mt-5 grid gap-5"><div className="grid gap-5 sm:grid-cols-2"><Input id="essay-title" label="Draft title" name="title" /><Select id="saved-essay-type" label="Essay type" name="essay_type" defaultValue="COMMON_APP"><option value="COMMON_APP">Common App</option><option value="SUPPLEMENTAL">Supplemental</option><option value="OTHER">Other</option></Select><Input id="saved-min" label="Minimum words" name="min_words" type="number" defaultValue="250" /><Input id="saved-limit" label="Word limit" name="word_limit" type="number" defaultValue="650" /></div><Textarea id="saved-text" label="Essay text" name="text" required maxLength={100000} /><Checkbox id="save-raw" label="Save this text to my account" name="save_raw_text" description="Unchecked by default. Scores and metrics are saved even when raw text is discarded." />{message ? <Alert title="Essay status">{message}</Alert> : null}<div className="flex justify-end"><Button disabled={busy} type="submit">{busy ? "Analyzing…" : "Analyze and save result"}</Button></div></form>{result ? <p className="mt-5 font-semibold">Mechanical Essay Score: {result.display_score} / 100</p> : null}</Card>
    <section className="mt-8"><h2 className="text-2xl font-bold">History</h2>{essays.length ? <div className="mt-4 grid gap-3">{essays.map((essay) => <Card className="flex flex-wrap items-center justify-between gap-4 p-5" key={essay.id}><div><p className="font-semibold">{essay.title || "Untitled draft"}</p><p className="mt-1 text-sm text-muted">{essay.essay_type} · {essay.save_raw_text ? "raw text saved" : "metrics only"}{essay.display_score == null ? "" : ` · score ${essay.display_score}`}</p></div><div className="flex gap-2"><ButtonLink href={`/essays/${essay.id}`} variant="secondary">Open</ButtonLink><Button disabled={busy} onClick={() => void remove(essay.id)} variant="danger">Delete</Button></div></Card>)}</div> : <div className="mt-4"><EmptyState description="Run and save an analysis above." title="No saved analyses" /></div>}</section>
    <Card className="mt-8 p-6"><h2 className="text-xl font-bold">Compare saved evaluations</h2><p className="mt-2 text-sm text-muted">Uses stored metrics; raw essay text is not required.</p><form action={compareSaved} className="mt-5 grid gap-5 md:grid-cols-2"><Select defaultValue={savedEssays[0]?.evaluation_id ?? ""} id="left-saved" label="Earlier saved evaluation" name="left_saved" required>{savedEssays.map((essay) => <option key={`left-${essay.id}`} value={essay.evaluation_id ?? ""}>{essay.title || "Untitled draft"} · {essay.display_score ?? "N/A"}</option>)}</Select><Select defaultValue={savedEssays[1]?.evaluation_id ?? ""} id="right-saved" label="Later saved evaluation" name="right_saved" required>{savedEssays.map((essay) => <option key={`right-${essay.id}`} value={essay.evaluation_id ?? ""}>{essay.title || "Untitled draft"} · {essay.display_score ?? "N/A"}</option>)}</Select><div className="md:col-span-2 flex justify-end"><Button disabled={busy || savedEssays.length < 2} type="submit">Compare saved results</Button></div></form></Card>
    <Card className="mt-8 p-6"><h2 className="text-xl font-bold">Compare two drafts</h2><p className="mt-2 text-sm text-muted">Comparison is processed within this request and is not persisted.</p><form action={compare} className="mt-5 grid gap-5 md:grid-cols-2"><Textarea id="left-draft" label="Earlier draft" name="left" required /><Textarea id="right-draft" label="Later draft" name="right" required /><div className="md:col-span-2 flex justify-end"><Button disabled={busy} type="submit">Compare drafts</Button></div></form></Card>
    {comparison ? <div className="mt-5 grid gap-3 sm:grid-cols-3"><Card className="p-4">Earlier: <strong>{comparison.left.display_score}</strong></Card><Card className="p-4">Later: <strong>{comparison.right.display_score}</strong></Card><Card className="p-4">Delta: <strong>{comparison.overall_delta > 0 ? "+" : ""}{comparison.overall_delta}</strong></Card></div> : null}
  </>;
}
