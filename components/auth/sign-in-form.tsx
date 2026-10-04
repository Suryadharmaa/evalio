"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/field";
import { createSupabaseBrowserClient } from "@/lib/auth/browser";
import { safeInternalPath } from "@/lib/utils/safe-url";
import { sitePath } from "@/lib/site";
import { firstValidationError, signInFormSchema } from "@/lib/schemas/forms";

export function SignInForm({ nextPath }: { nextPath?: string }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function signIn(formData: FormData) {
    setBusy(true); setMessage(null);
    try {
      const validation = signInFormSchema.safeParse({
        email: formData.get("email"),
        password: formData.get("password"),
        mode: formData.get("mode"),
      });
      if (!validation.success) throw new Error(firstValidationError(validation));
      const { email, mode, password } = validation.data;
      const client = createSupabaseBrowserClient();
      const destination = safeInternalPath(nextPath) ?? "/dashboard";
      if (mode === "password") {
        const { error } = await client.auth.signInWithPassword({ email, password });
        if (error) setMessage(error.message); else router.push(destination);
      } else if (mode === "signup") {
        const { error } = await client.auth.signUp({ email, password, options: { emailRedirectTo: `${window.location.origin}${sitePath(destination)}` } });
        setMessage(error ? error.message : "Account created. Check your email if confirmation is required.");
      } else {
        const { error } = await client.auth.signInWithOtp({ email, options: { emailRedirectTo: `${window.location.origin}${sitePath(destination)}` } });
        setMessage(error ? error.message : "Check your email for a secure sign-in link.");
      }
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to start sign in."); }
    finally { setBusy(false); }
  }
  return <form className="mt-7 grid gap-5" action={signIn}>
    <Input id="email" label="Email address" name="email" type="email" autoComplete="email" required />
    <Input id="password" label="Password (for password sign-in)" name="password" type="password" autoComplete="current-password" minLength={6} />
    {message ? <Alert title="Sign-in status">{message}</Alert> : null}
    <div className="grid gap-3"><Button disabled={busy} type="submit" name="mode" value="password">{busy ? "Working…" : "Sign in with password"}</Button><div className="grid gap-3 sm:grid-cols-2"><Button disabled={busy} type="submit" name="mode" value="signup" variant="secondary">Create account</Button><Button disabled={busy} type="submit" name="mode" value="magic" variant="secondary">Send magic link</Button></div></div>
  </form>;
}
