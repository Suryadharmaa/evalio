"use client";

import { recordPath } from "@/lib/site";

import { useCallback, useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Profile { id: string; profile_name: string }
interface Evaluation { evaluation_type: string; display_score: number | null; confidence: string; evaluated_at: string }
interface Report { id: string; report_type: string; report_version: string; created_at: string }

export function ReportManager() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => { const profiles = await authenticatedFetch("/api/v1/profiles"); if (!profiles.ok) throw new Error(await apiError(profiles)); const first = ((await profiles.json()) as { data: Profile[] }).data[0] ?? null; setProfile(first); if (!first) return; const response = await authenticatedFetch(`/api/v1/profiles/${first.id}/reports`); if (!response.ok) throw new Error(await apiError(response)); setReports(((await response.json()) as { data: Report[] }).data); }, []);
  useEffect(() => { void (async () => { try { await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to load reports."); } })(); }, [load]);
  async function create() { if (!profile) return; setBusy(true); setMessage(null); try { const evaluationsResponse = await authenticatedFetch(`/api/v1/profiles/${profile.id}/evaluations`); if (!evaluationsResponse.ok) throw new Error(await apiError(evaluationsResponse)); const evaluations = ((await evaluationsResponse.json()) as { data: Evaluation[] }).data; const latestByType = new Map<string, Evaluation>(); for (const item of evaluations) { if (!latestByType.has(item.evaluation_type)) latestByType.set(item.evaluation_type, item); } const latest = [...latestByType.values()]; const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/reports`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ report_type: "APPLICATION_READINESS", sections: { profile: { profile_name: profile.profile_name }, latest_evaluations: latest.map(({ evaluation_type, display_score, confidence, evaluated_at }) => ({ evaluation_type, display_score, confidence, evaluated_at })) } }) }); if (!response.ok) throw new Error(await apiError(response)); setMessage("Report created."); await load(); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to create report."); } finally { setBusy(false); } }
  async function remove(id: string) { const response = await authenticatedFetch(`/api/v1/reports/${id}`, { method: "DELETE" }); if (!response.ok) setMessage(await apiError(response)); else await load(); }
  return <>{message ? <Alert className="mt-8" title="Report status">{message}</Alert> : null}{profile ? <div className="mt-8"><Button disabled={busy} onClick={() => void create()}>{busy ? "Generating…" : "Generate readiness report"}</Button></div> : <Alert className="mt-8" title="Profile needed" tone="warning">Create a profile first.</Alert>}{reports.length ? <div className="mt-6 grid gap-4">{reports.map((report) => <Card className="flex flex-wrap items-center justify-between gap-4 p-5" key={report.id}><div><p className="font-semibold">{report.report_type.replaceAll("_", " ")}</p><p className="mt-1 text-sm text-muted">Version {report.report_version} · {new Date(report.created_at).toLocaleDateString()}</p></div><div className="flex gap-2"><ButtonLink href={recordPath("reports", report.id)} variant="secondary">Open / print</ButtonLink><Button onClick={() => void remove(report.id)} variant="danger">Delete</Button></div></Card>)}</div> : <div className="mt-6"><EmptyState description="Generate a report from your latest saved evaluations." title="No saved reports" /></div>}</>;
}
