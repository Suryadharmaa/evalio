import { Suspense } from "react";
import { ClientRedirect } from "@/components/routing/client-redirect";

export default function LegacyEssayPage() {
  return <Suspense><ClientRedirect to="/tools/essay-evaluator" /></Suspense>;
}
