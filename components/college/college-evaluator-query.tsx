"use client";

import { useSearchParams } from "next/navigation";
import { CollegeEvaluator } from "./college-evaluator";

export function CollegeEvaluatorQuery() {
  const query = useSearchParams();
  return <CollegeEvaluator key={query.get("college") ?? ""} initialCollegeId={query.get("college") ?? undefined} initialCollegeName={query.get("college_name") ?? undefined} />;
}
