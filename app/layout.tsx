import type { Metadata } from "next";
import { connection } from "next/server";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";

import "./globals.css";

export const metadata: Metadata = {
  title: "Evalio",
  description: "Transparent, deterministic analysis across academics, activities, essays, and college fit.",
  icons: {
    icon: [{ url: "/evalio-icon.png", type: "image/png" }],
    shortcut: "/evalio-icon.png",
    apple: "/evalio-icon.png",
  },
};

export default async function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  await connection();
  return (
    <html data-scroll-behavior="smooth" lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
