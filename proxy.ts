import { NextRequest, NextResponse } from "next/server";

// Dynamic Next.js deployments receive one unpredictable script nonce per request.
// GitHub Pages uses its existing post-build SHA-256 meta CSP, not this proxy.
function trustedOrigin(value: string | undefined): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" ? url.origin : null;
  } catch {
    return null;
  }
}

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const isDev = process.env.NODE_ENV === "development";
  const supabaseOrigin = trustedOrigin(process.env.NEXT_PUBLIC_SUPABASE_URL);
  const apiOrigin = trustedOrigin(process.env.NEXT_PUBLIC_API_ORIGIN);
  const connections = new Set<string>(["'self'"]);
  if (supabaseOrigin) {
    connections.add(supabaseOrigin);
    connections.add(supabaseOrigin.replace(/^https:/, "wss:"));
  }
  if (apiOrigin) connections.add(apiOrigin);
  if (isDev) {
    connections.add("http://127.0.0.1:8000");
    connections.add("ws://127.0.0.1:3000");
    connections.add("ws://localhost:3000");
  }

  const policy = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    // Existing UI uses inline style attributes; tighten this separately after migration.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https://commons.wikimedia.org https://upload.wikimedia.org",
    `connect-src ${[...connections].join(" ")}`,
    "font-src 'self' data:",
    "worker-src 'self' blob:",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    ...(isDev ? [] : ["upgrade-insecure-requests"]),
  ].join("; ");

  // Next.js reads the request CSP to nonce its own rendered scripts.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", policy);
  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", policy);
  return response;
}

export const config = {
  matcher: [
    {
      source: "/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|jpeg|svg|webp|ico|woff2?|ttf)$).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
