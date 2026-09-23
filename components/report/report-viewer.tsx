"use client";

import { useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Report { report_type: string; report_version: string; report_json: { generated_at?: string; disclaimer?: string; sections?: Record<string, unknown> } }

export function ReportViewer({ reportId }: { reportId: string }) {
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { authenticatedFetch(`/api/v1/reports/${reportId}`).then(async (response) => { if (!response.ok) throw new Error(await apiError(response)); setReport(((await response.json()) as { data: Report }).data); }).catch((error: unknown) => setError(error instanceof Error ? error.message : "Report unavailable.")); }, [reportId]);
  if (error) return <Alert title="Report unavailable" tone="danger">{error}</Alert>;
  if (!report) return <p aria-live="polite">Loading report…</p>;
  return <article><div className="flex items-start justify-between gap-4 print:hidden"><div><p className="text-sm font-semibold text-primary">Saved report · {report.report_version}</p><h1 className="mt-2 text-4xl font-bold">{report.report_type}</h1></div><Button type="button" onClick={() => window.print()}>Print</Button></div><div className="mt-8 grid gap-5">{Object.entries(report.report_json.sections ?? {}).map(([title, value]) => <Card className="p-6" key={title}><h2 className="text-xl font-semibold capitalize">{title.replaceAll("_", " ")}</h2><pre className="mt-4 whitespace-pre-wrap break-words font-sans text-sm leading-6 text-muted">{JSON.stringify(value, null, 2)}</pre></Card>)}</div><p className="mt-8 text-xs text-muted">{report.report_json.disclaimer}</p></article>;
}
