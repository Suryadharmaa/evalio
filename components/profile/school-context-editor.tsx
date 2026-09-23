"use client";

import { useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/field";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Context { advanced_courses_available: number | null; advanced_program_types: string[] | null; notes: string | null }
export function SchoolContextEditor({ profileId }: { profileId: string }) {
  const [context, setContext] = useState<Context | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  useEffect(() => { authenticatedFetch(`/api/v1/profiles/${profileId}/school-context`).then(async (response) => { if (!response.ok) throw new Error(await apiError(response)); setContext(((await response.json()) as { data: Context | null }).data); }).catch((reason: unknown) => setMessage(reason instanceof Error ? reason.message : "Unable to load school context.")); }, [profileId]);
  async function save(form: FormData) { const count = String(form.get("advanced_courses_available") ?? "").trim(); const programs = String(form.get("advanced_program_types") ?? "").split(",").map((item) => item.trim()).filter(Boolean); const response = await authenticatedFetch(`/api/v1/profiles/${profileId}/school-context`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ advanced_courses_available: count ? Number(count) : null, advanced_program_types: programs.length ? programs : null, highest_course_levels: null, notes: String(form.get("notes") ?? "").trim() || null }) }); setMessage(response.ok ? "School context saved." : await apiError(response)); }
  return <Card className="mt-8 p-6"><h2 className="text-xl font-bold">School context</h2><p className="mt-2 text-sm text-muted">Rigor is evaluated against what your school offers.</p><form action={save} className="mt-5 grid gap-5" key={JSON.stringify(context)}><Input id="advanced-courses" label="Advanced courses available" name="advanced_courses_available" type="number" min="0" max="100" defaultValue={context?.advanced_courses_available ?? ""} /><Input id="advanced-programs" label="Advanced programs (comma-separated)" name="advanced_program_types" placeholder="IB HL, AP, A-Level" defaultValue={context?.advanced_program_types?.join(", ") ?? ""} /><Textarea id="school-context-notes" label="Context notes" name="notes" maxLength={2000} defaultValue={context?.notes ?? ""} />{message ? <Alert title="School context status">{message}</Alert> : null}<div className="flex justify-end"><Button type="submit">Save school context</Button></div></form></Card>;
}
