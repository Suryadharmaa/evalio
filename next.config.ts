import type { NextConfig } from "next";

const staticExport = process.env.EVALIO_STATIC_EXPORT === "1";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH?.trim() ?? "";
if (basePath && !/^\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*$/.test(basePath)) {
  throw new Error("NEXT_PUBLIC_BASE_PATH must be empty or a path like /evalio, without a trailing slash.");
}
if (staticExport) {
  for (const name of ["NEXT_PUBLIC_API_ORIGIN", "NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]) {
    if (!process.env[name]?.trim()) throw new Error(`${name} is required for the GitHub Pages build.`);
  }
  const apiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN!;
  const url = new URL(apiOrigin);
  if (url.protocol !== "https:" || url.origin !== apiOrigin) {
    throw new Error("NEXT_PUBLIC_API_ORIGIN must be an HTTPS origin, without a path or trailing slash.");
  }
}

const nextConfig: NextConfig = {
  ...(staticExport ? { output: "export" as const, trailingSlash: true } : {}),
  basePath,
  allowedDevOrigins: ["127.0.0.1"],
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    unoptimized: staticExport,
    remotePatterns: [
      { protocol: "https", hostname: "commons.wikimedia.org" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
    ],
  },
  turbopack: {
    root: process.cwd(),
  },
  ...(!staticExport ? { async rewrites() {
    const configuredOrigin = process.env.EVALIO_API_ORIGIN?.trim();
    if (!configuredOrigin && process.env.NETLIFY) {
      throw new Error("EVALIO_API_ORIGIN is required for Netlify. Deploy FastAPI separately and set its HTTPS origin.");
    }
    if (configuredOrigin) {
      const origin = new URL(configuredOrigin);
      if (origin.protocol !== "https:" || origin.origin !== configuredOrigin || origin.username || origin.password) {
        throw new Error("EVALIO_API_ORIGIN must be an HTTPS origin without a path, credentials, or trailing slash.");
      }
      return [{ source: "/api/v1/:path*", destination: `${origin.origin}/api/v1/:path*` }];
    }
    if (process.env.NODE_ENV !== "development") return [];
    return [{ source: "/api/v1/:path*", destination: "http://127.0.0.1:8000/api/v1/:path*" }];
  }, async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
      ],
    }];
  } } : {}),
};

export default nextConfig;
