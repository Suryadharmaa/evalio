"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Textarea } from "@/components/ui/field";
import { EmptyState } from "@/components/ui/empty-state";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Profile { id: string }
interface Recommendation { id: string; recommender_role: string | null; relationship_duration_months: number | null; save_raw_text: boolean; created_at: string }
interface Result { display_score: number; confidence: string; components: Record<string, number>; triggered_rules: string[] }

export function RecommendationLibrary() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [rows, setRows] = useState<Recommendation[]>([]);
  const [result, setResult] = useState<Result | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => { const profiles = await authenticatedFetch("/api/v1/profiles"); if (!profiles.ok) throw new Error(await apiError(profiles)); const first = ((await profiles.json()) as { data: Profile[] }).data[0] ?? null; setProfile(first); if (!first) return; const response = await authenticatedFetch(`/api/v1/profiles/${first.id}/recommendations`); if (!response.ok) throw new Error(await apiError(response)); setRows(((await response.json()) as { data: Recommendation[] }).data); }, []);
  useEffect(() => { void (async () => { try { await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to load recommendations."); } })(); }, [load]);
  async function analyze(form: FormData) { if (!profile) return; setBusy(true); setMessage(null); try { const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/recommendations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: form.get("text"), recommender_role: String(form.get("role") ?? "").trim() || null, relationship_duration_months: Number(form.get("months")) || null, instructional_context: String(form.get("context") ?? "").trim() || null, save: false, save_raw_text: form.get("save_raw_text") === "on" }) }); if (!response.ok) throw new Error(await apiError(response)); setResult(((await response.json()) as { data: { evaluation: Result } }).data.evaluation); setMessage("Signals saved. Raw text was stored only if you opted in."); await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Analysis failed."); } finally { setBusy(false); } }
  async function remove(id: string) { if (!profile) return; const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/recommendations/${id}`, { method: "DELETE" }); if (!response.ok) setMessage(await apiError(response)); else await load(); }
  if (!profile) return <Alert className="mt-8" title="Profile needed" tone="warning">Create a profile before saving recommendation signals.</Alert>;
  return <><Card className="mt-8 p-6"><form action={analyze} className="grid gap-5"><div className="grid gap-5 sm:grid-cols-2"><Input id="recommender-role" label="Recommender role" name="role" placeholder="Math teacher" /><Input id="relationship-months" label="Relationship duration (months)" name="months" type="number" min="0" max="600" /></div><Input id="instructional-context" label="Instructional context" name="context" maxLength={500} /><Textarea id="recommendation-text" label="Recommendation text" name="text" required maxLength={100000} /><Checkbox id="save-recommendation" label="Save this text to my account" name="save_raw_text" description="Unchecked by default. Deterministic metrics can be saved without raw text." />{message ? <Alert title="Recommendation status">{message}</Alert> : null}<div className="flex justify-end"><Button disabled={busy} type="submit">{busy ? "Analyzing…" : "Analyze signals"}</Button></div></form>{result ? <Card className="mt-5 p-5"><p className="text-sm text-muted">Recommendation Signal Score</p><p className="mt-2 text-3xl font-bold">{result.display_score} / 100</p><p className="mt-2 text-sm">Confidence: {result.confidence}</p><ButtonLink className="mt-4" href="/methodology/lor" variant="secondary">Why this result?</ButtonLink></Card> : null}</Card><section className="mt-8"><h2 className="text-2xl font-bold">Saved analyses</h2>{rows.length ? <div className="mt-4 grid gap-3">{rows.map((row) => <Card className="flex items-center justify-between gap-4 p-5" key={row.id}><div><p className="font-semibold">{row.recommender_role || "Unspecified recommender"}</p><p className="mt-1 text-sm text-muted">{row.save_raw_text ? "Raw text saved" : "Metrics only"}</p></div><Button onClick={() => void remove(row.id)} variant="danger">Delete</Button></Card>)}</div> : <div className="mt-4"><EmptyState description="Analyze a recommendation above." title="No saved recommendation signals" /></div>}</section></>;
}
