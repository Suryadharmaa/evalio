"use client";

import { useSearchParams } from "next/navigation";
import { SignInForm } from "./sign-in-form";

export function SignInQuery() {
  return <SignInForm nextPath={useSearchParams().get("next") ?? undefined} />;
}
