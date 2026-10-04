import { Suspense } from "react";
import { SignInQuery } from "@/components/auth/sign-in-query";
import { Card } from "@/components/ui/card";

export default function SignInPage() {
  return (
    <div className="hero-wash grid min-h-[calc(100vh-5rem)] place-items-center px-5 py-16 sm:px-8">
      <Card className="product-frame w-full max-w-md p-7 sm:p-9">
        <p className="eyebrow">Private workspace</p>
        <h1 className="mt-3 text-3xl font-extrabold tracking-[-0.045em]">Sign in to Evalio</h1>
        <p className="mt-3 leading-7 text-muted">Public analyzers remain available without an account.</p>
        <Suspense fallback={<p role="status" className="mt-7 text-muted">Loading sign-in…</p>}><SignInQuery /></Suspense>
      </Card>
    </div>
  );
}
