"use client";

import { useEffect, useState } from "react";

import { createSupabaseBrowserClient } from "@/lib/auth/browser";

export function HeroTrustSignals() {
  const [signedIn, setSignedIn] = useState<boolean | null>(null);

  useEffect(() => {
    try {
      const client = createSupabaseBrowserClient();
      void client.auth.getSession().then(({ data }) => setSignedIn(Boolean(data.session))).catch(() => setSignedIn(false));
      const { data } = client.auth.onAuthStateChange((_event, session) => {
        setSignedIn(Boolean(session));
      });
      return () => data.subscription.unsubscribe();
    } catch {
      return;
    }
  }, []);

  return (
    <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm font-semibold text-foreground/75">
      {signedIn === true ? (
        <span className="inline-flex items-center gap-2">
          <span className="size-2 rounded-full bg-[var(--success)]" />
          Ready to save to your workspace
        </span>
      ) : signedIn === false ? (
        <span className="inline-flex items-center gap-2">
          <span className="size-2 rounded-full bg-[var(--success)]" />
          No account needed for your first analysis
        </span>
      ) : null}
      <span className="inline-flex items-center gap-2">
        <span className="size-2 rounded-full bg-primary" />
        Raw text is not saved by default
      </span>
    </div>
  );
}
