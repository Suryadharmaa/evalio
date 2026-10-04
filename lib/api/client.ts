import { createSupabaseBrowserClient } from "@/lib/auth/browser";
import { sitePath } from "@/lib/site";

export function apiUrl(path: string): string {
  if (!path.startsWith("/api/v1/") || /[\\\u0000-\u001f]/.test(path)) {
    throw new Error("Invalid API path.");
  }
  const origin = process.env.NEXT_PUBLIC_API_ORIGIN?.trim();
  if (!origin) return sitePath(path);
  const url = new URL(origin);
  const local = process.env.NODE_ENV !== "production" && ["localhost", "127.0.0.1"].includes(url.hostname);
  if (url.origin !== origin || (url.protocol !== "https:" && !local)) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be an HTTPS origin.");
  }
  return `${origin}${path}`;
}

export function apiFetch(path: string, init: RequestInit = {}) {
  return fetch(apiUrl(path), { ...init, credentials: "omit", cache: "no-store" });
}

export async function authenticatedFetch(path: string, init: RequestInit = {}) {
  const { data: { session } } = await createSupabaseBrowserClient().auth.getSession();
  if (!session) throw new Error("Sign in to continue.");
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${session.access_token}`);
  return apiFetch(path, { ...init, headers });
}

export async function apiError(response: Response): Promise<string> {
  try {
    const payload = await response.json() as { error?: { message?: string } };
    return payload.error?.message ?? `Request failed (${response.status}).`;
  } catch {
    return `Request failed (${response.status}).`;
  }
}
