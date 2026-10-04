import { Suspense } from "react";
import { ReportQueryView } from "@/components/routing/record-view";

export default function ReportPage() {
  return <div className="mx-auto w-full max-w-4xl px-5 py-12 sm:px-8"><Suspense fallback={<p role="status" className="text-muted">Loading report…</p>}><ReportQueryView /></Suspense></div>;
}
