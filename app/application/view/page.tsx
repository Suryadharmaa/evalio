import { Suspense } from "react";
import { ApplicationQueryView } from "@/components/routing/record-view";

export default function ApplicationPage() {
  return <div className="mx-auto w-full max-w-6xl px-5 py-12 sm:px-8 lg:px-12"><p className="text-sm font-semibold text-primary">Application readiness</p><h1 className="mt-2 text-4xl font-bold tracking-tight">Application audit</h1><p className="mt-3 max-w-2xl leading-7 text-muted">Track required materials, deadlines, completeness, and quality independently.</p><Suspense fallback={<p role="status" className="mt-8 text-muted">Loading application…</p>}><ApplicationQueryView /></Suspense></div>;
}
