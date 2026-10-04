import { Suspense } from "react";
import { ClientRedirect } from "@/components/routing/client-redirect";

export default function CollegeComparePage() {
  return <Suspense><ClientRedirect to="/tools/application-evaluator" preserveCollege /></Suspense>;
}
