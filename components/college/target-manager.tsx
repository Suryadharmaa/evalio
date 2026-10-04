"use client";

import { recordPath } from "@/lib/site";

import { useCallback, useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Profile { id: string }
interface Target { id: string; college_id: string; college_name: string; college_slug: string; application_round: string | null; application_status: string | null }

export function TargetManager() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [targets, setTargets] = useState<Target[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => { const profiles = await authenticatedFetch("/api/v1/profiles"); if (!profiles.ok) throw new Error(await apiError(profiles)); const first = ((await profiles.json()) as { data: Profile[] }).data[0] ?? null; setProfile(first); if (!first) return; const response = await authenticatedFetch(`/api/v1/profiles/${first.id}/targets`); if (!response.ok) throw new Error(await apiError(response)); setTargets(((await response.json()) as { data: Target[] }).data); }, []);
  useEffect(() => { void (async () => { try { await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load targets."); } })(); }, [load]);
  async function remove(id: string) { if (!profile) return; const response = await authenticatedFetch(`/api/v1/profiles/${profile.id}/targets/${id}`, { method: "DELETE" }); if (!response.ok) setError(await apiError(response)); else await load(); }
  return <>{error ? <Alert className="mt-8" title="Targets unavailable" tone="danger">{error}</Alert> : null}{targets.length ? <div className="mt-8 grid gap-4">{targets.map((target) => <Card className="p-6" key={target.id}><div className="flex flex-wrap items-start justify-between gap-4"><div><h2 className="text-xl font-bold">{target.college_name}</h2><p className="mt-1 text-sm text-muted">{target.application_round || "Round not set"} · {target.application_status || "Planning"}</p></div><div className="flex flex-wrap gap-2"><ButtonLink href={recordPath("colleges", target.college_slug)} variant="secondary">College data</ButtonLink><ButtonLink href={recordPath("application", target.college_id)}>Application audit</ButtonLink><Button onClick={() => void remove(target.id)} variant="danger">Remove</Button></div></div></Card>)}</div> : <div className="mt-8"><EmptyState action={<ButtonLink href="/colleges">Explore colleges</ButtonLink>} description="Add a college from an evaluation or the college explorer." title="No target colleges" /></div>}</>;
}
