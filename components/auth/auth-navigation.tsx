"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { createSupabaseBrowserClient } from "@/lib/auth/browser";
import { Button, ButtonLink } from "@/components/ui/button";
import { cx } from "@/lib/utils/cx";

export function AuthNavigation({ mobile = false }: { mobile?: boolean }) {
  const router = useRouter();
  const [signedIn, setSignedIn] = useState(false);
  const [accountInitial, setAccountInitial] = useState("A");

  useEffect(() => {
    try {
      const client = createSupabaseBrowserClient();
      void client.auth.getSession().then(({ data }) => {
        setSignedIn(Boolean(data.session));
        setAccountInitial(data.session?.user.email?.charAt(0).toUpperCase() || "A");
      }).catch(() => setSignedIn(false));
      const { data } = client.auth.onAuthStateChange((_event, session) => {
        setSignedIn(Boolean(session));
        setAccountInitial(session?.user.email?.charAt(0).toUpperCase() || "A");
      });
      return () => data.subscription.unsubscribe();
    } catch {
      return;
    }
  }, []);

  const quietClass = cx(
    "rounded-lg text-sm font-bold transition-colors",
    mobile
      ? "px-3 py-3 hover:bg-[var(--surface-muted)]"
      : "px-2 py-2 text-muted hover:text-foreground",
  );
  const actionClass = cx(
    "inline-flex min-h-11 items-center justify-center rounded-[10px] bg-primary px-5 text-sm font-bold text-white shadow-[0_8px_20px_rgb(103_87_245/18%)] transition-colors hover:bg-[var(--primary-hover)]",
    mobile && "w-full",
  );

  if (!signedIn) {
    return (
      <div className={cx("flex items-center gap-2", mobile && "mt-1 grid border-t border-border pt-3")}>
        <Link className={quietClass} href="/sign-in">Sign in</Link>
        <ButtonLink className={mobile ? "w-full" : undefined} href="/tools">Get started <span aria-hidden="true">→</span></ButtonLink>
      </div>
    );
  }

  async function signOut() {
    await createSupabaseBrowserClient().auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <div className={cx("flex items-center gap-2", mobile && "mt-1 grid border-t border-border pt-3")}>
      <Link className={quietClass} href="/dashboard">Dashboard</Link>
      {mobile ? (
        <>
          <Link className={quietClass} href="/profile">Profile</Link>
          <Link className={quietClass} href="/settings">Account</Link>
          <Button className={actionClass} onClick={() => void signOut()} type="button">Sign out</Button>
        </>
      ) : (
        <details className="group relative">
          <summary className="grid size-11 cursor-pointer list-none place-items-center rounded-full border border-border bg-white text-sm font-extrabold text-primary shadow-sm transition-colors hover:border-primary/30 hover:bg-[var(--primary-soft)]" aria-label="Open account menu">
            <span aria-hidden="true">{accountInitial}</span>
          </summary>
          <div className="absolute right-0 top-14 z-50 grid min-w-48 gap-1 rounded-xl border border-border bg-white p-2 shadow-[var(--shadow-md)]">
            <Link className="rounded-lg px-3 py-3 text-sm font-bold hover:bg-[var(--surface-muted)]" href="/profile">Profile</Link>
            <Link className="rounded-lg px-3 py-3 text-sm font-bold hover:bg-[var(--surface-muted)]" href="/settings">Account settings</Link>
            <button className="rounded-lg px-3 py-3 text-left text-sm font-bold text-[var(--danger)] hover:bg-[var(--danger-soft)]" onClick={() => void signOut()} type="button">Sign out</button>
          </div>
        </details>
      )}
    </div>
  );
}
