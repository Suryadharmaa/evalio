"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/field";
import { apiError, authenticatedFetch } from "@/lib/api/client";
import { createSupabaseBrowserClient } from "@/lib/auth/browser";

export function PrivacyControls() {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function download() {
    setBusy(true); setMessage(null);
    try {
      const response = await authenticatedFetch("/api/v1/account/export");
      if (!response.ok) throw new Error(await apiError(response));
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement("a"); anchor.href = url; anchor.download = "evalio-export.json"; anchor.click(); URL.revokeObjectURL(url);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Export failed."); }
    finally { setBusy(false); }
  }
  async function remove(formData: FormData) {
    setBusy(true); setMessage(null);
    try {
      const response = await authenticatedFetch("/api/v1/account", { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ confirm: formData.get("confirm") }) });
      if (!response.ok) throw new Error(await apiError(response));
      await createSupabaseBrowserClient().auth.signOut();
      router.replace("/");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Deletion failed."); setBusy(false); }
  }
  return <div className="mt-8 grid gap-5">
    {message ? <Alert title="Account action" tone="danger">{message}</Alert> : null}
    <Card className="p-6"><h2 className="text-xl font-semibold">Saved-content controls</h2><p className="mt-2 leading-7 text-muted">Review or delete saved essay and recommendation records. Raw text is stored only when its opt-in box was checked.</p><div className="mt-5 flex flex-wrap gap-3"><ButtonLink href="/essays" variant="secondary">Manage essays</ButtonLink><ButtonLink href="/recommendations" variant="secondary">Manage recommendations</ButtonLink></div></Card>
    <Card className="p-6"><h2 className="text-xl font-semibold">Export my data</h2><p className="mt-2 leading-7 text-muted">Download all user-owned profile, content, evaluation, target, and report data as JSON.</p><Button className="mt-5" disabled={busy} onClick={download} type="button" variant="secondary">Download export</Button></Card>
    <Card className="border-[var(--danger)]/30 p-6"><h2 className="text-xl font-semibold text-[var(--danger)]">Delete account data</h2><Alert className="mt-4" title="Permanent action" tone="danger">Deletion removes saved private content and cannot be undone.</Alert><form action={remove} className="mt-5 grid gap-4"><Input id="delete-confirm" label="Type DELETE to confirm" name="confirm" autoComplete="off" required /><div><Button disabled={busy} type="submit" variant="danger">Delete my account</Button></div></form></Card>
  </div>;
}
