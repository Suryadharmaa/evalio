import { SignInForm } from "@/components/auth/sign-in-form";
import { Card } from "@/components/ui/card";

export default async function SignInPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const nextPath = (await searchParams).next;
  return (
    <div className="hero-wash grid min-h-[calc(100vh-5rem)] place-items-center px-5 py-16 sm:px-8">
      <Card className="product-frame w-full max-w-md p-7 sm:p-9">
        <p className="eyebrow">Private workspace</p>
        <h1 className="mt-3 text-3xl font-extrabold tracking-[-0.045em]">Sign in to Evalio</h1>
        <p className="mt-3 leading-7 text-muted">Public analyzers remain available without an account.</p>
        <SignInForm nextPath={nextPath} />
      </Card>
    </div>
  );
}
