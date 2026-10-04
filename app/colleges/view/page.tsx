import { Suspense } from "react";
import { CollegeQueryView } from "@/components/routing/record-view";

export default function CollegeDetailPage() {
  return <div className="mx-auto w-full max-w-6xl px-5 py-12 sm:px-8 lg:px-12"><p className="text-sm font-semibold text-primary">College reference data</p><Suspense fallback={<p role="status" className="mt-8 text-muted">Loading college…</p>}><CollegeQueryView /></Suspense></div>;
}
