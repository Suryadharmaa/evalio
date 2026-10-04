"use client";

import { useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/auth/browser";
import { Alert } from "@/components/ui/alert";

const protectedPrefixes = ["/admin", "/application", "/dashboard", "/essays", "/profile", "/recommendations", "/reports", "/settings", "/targets"];

// This guard controls the UI only. FastAPI verifies the bearer token and record ownership.
export function AuthBoundary({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const protectedRoute = protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const [signedIn, setSignedIn] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!protectedRoute) return;
    let active = true;
    const update = (authenticated: boolean) => {
      if (!active) return;
      setSignedIn(authenticated);
      if (!authenticated) {
        router.replace(`/sign-in?next=${encodeURIComponent(`${pathname}${window.location.search}`)}`);
      }
    };
    let unsubscribe: (() => void) | undefined;
    void Promise.resolve().then(async () => {
      if (!active) return;
      const client = createSupabaseBrowserClient();
      const { data } = client.auth.onAuthStateChange((_event, session) => update(Boolean(session)));
      unsubscribe = () => data.subscription.unsubscribe();
      const session = await client.auth.getSession();
      if (session.error) throw session.error;
      update(Boolean(session.data.session));
    }).catch((error: unknown) => { if (active) setMessage(error instanceof Error ? error.message : "Unable to check your session."); });
    return () => { active = false; unsubscribe?.(); };
  }, [pathname, protectedRoute, router]);

  if (!protectedRoute || signedIn) return children;
  return <div className="site-container py-16">{message ? <Alert title="Sign-in unavailable" tone="danger">{message}</Alert> : <p role="status" className="text-muted">Checking your session…</p>}</div>;
}
