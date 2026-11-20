import type { Metadata } from "next";
import type { ReactNode } from "react";
import { connection } from "next/server";

import { AppShell } from "@/components/layout/app-shell";
import { sitePath } from "@/lib/site";

import "./globals.css";

export const metadata: Metadata = {
  title: "Evalio",
  description: "Transparent, deterministic analysis across academics, activities, essays, and college fit.",
  icons: {
    icon: [{ url: sitePath("/evalio-icon.png"), type: "image/png" }],
    shortcut: sitePath("/evalio-icon.png"),
    apple: sitePath("/evalio-icon.png"),
  },
};

export default async function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  // Nonce CSP needs request-specific rendering. Static export keeps its build-time HTML.
  if (process.env.EVALIO_STATIC_EXPORT !== "1") {
    await connection();
  }
  return (
    <html data-scroll-behavior="smooth" lang="en">
      <head><meta name="referrer" content="strict-origin-when-cross-origin" /></head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
