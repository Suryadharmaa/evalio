"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { CollegeDetailView } from "@/components/college/college-detail";
import { ApplicationAudit } from "@/components/college/application-audit";
import { SavedEssayDetail } from "@/components/evaluation/saved-essay-detail";
import { ReportViewer } from "@/components/report/report-viewer";
import { EmptyState } from "@/components/ui/empty-state";

function MissingRecord({ href }: { href: string }) {
  return <EmptyState title="No record selected" description="Open a record from the list to view it." action={<Link className="quiet-link" href={href}>Return to the list →</Link>} />;
}

export function CollegeQueryView() {
  const slug = useSearchParams().get("slug")?.trim();
  return slug ? <CollegeDetailView key={slug} slug={slug} /> : <MissingRecord href="/colleges" />;
}

export function EssayQueryView() {
  const id = useSearchParams().get("id")?.trim();
  return id ? <SavedEssayDetail key={id} essayId={id} /> : <MissingRecord href="/essays" />;
}

export function ReportQueryView() {
  const id = useSearchParams().get("id")?.trim();
  return id ? <ReportViewer key={id} reportId={id} /> : <MissingRecord href="/reports" />;
}

export function ApplicationQueryView() {
  const id = useSearchParams().get("id")?.trim();
  return id ? <ApplicationAudit key={id} collegeId={id} /> : <MissingRecord href="/targets" />;
}
