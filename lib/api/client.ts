import { createSupabaseBrowserClient } from "@/lib/auth/browser";

export async function authenticatedFetch(path: string, init: RequestInit = {}) {
  const { data: { session } } = await createSupabaseBrowserClient().auth.getSession();
  if (!session) throw new Error("Sign in to continue.");
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${session.access_token}`);
  return fetch(path, { ...init, headers });
}

export async function apiError(response: Response): Promise<string> {
  try {
    const payload = await response.json() as { error?: { message?: string } };
    return payload.error?.message ?? `Request failed (${response.status}).`;
  } catch {
    return `Request failed (${response.status}).`;
  }
}
