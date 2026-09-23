import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "commons.wikimedia.org" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
    ],
  },
  turbopack: {
    root: process.cwd(),
  },
  async rewrites() {
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
  },
  async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
      ],
    }];
  },
};

export default nextConfig;
