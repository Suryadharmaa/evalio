import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";

import { AuthNavigation } from "@/components/auth/auth-navigation";
import { AuthBoundary } from "@/components/auth/auth-boundary";
import { sitePath } from "@/lib/site";
import { NavigationDisclosures } from "@/components/layout/navigation-disclosures";
import { toolGroups, toolsInGroup } from "@/lib/tools/catalog";

const navigation = [
  { href: "/colleges", label: "Colleges" },
  { href: "/methodology", label: "Methodology" },
];

const footerGroups = [
  {
    title: "Product",
    links: [
      { href: "/tools", label: "All Tools" },
      { href: "/tools/essay-evaluator", label: "Essay Evaluator" },
      { href: "/colleges", label: "College Explorer" },
    ],
  },
  {
    title: "Methodology",
    links: [
      { href: "/methodology", label: "Scoring" },
      { href: "/methodology", label: "Data Sources" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/privacy", label: "Privacy" },
      { href: "/terms", label: "Terms" },
    ],
  },
];

function Logo() {
  return (
    <Link href="/" className="group inline-flex min-h-11 items-center gap-2.5" aria-label="Evalio home">
      <span className="relative size-8 overflow-hidden rounded-lg shadow-sm transition-transform duration-200 group-hover:-translate-y-px" aria-hidden="true">
        <Image alt="" className="object-cover" fill sizes="32px" src={sitePath("/evalio-icon.png")} />
      </span>
      <span className="editorial-type text-[1.35rem] font-semibold tracking-[-0.025em]">Evalio</span>
    </Link>
  );
}

function ToolsMenu({ mobile = false }: { mobile?: boolean }) {
  if (mobile) {
    return (
      <div className="border-y border-border py-2">
        <Link className="block rounded-lg px-3 py-3 text-sm font-extrabold hover:bg-[var(--surface-muted)]" href="/tools">All tools</Link>
        {toolGroups.map((group) => (
          <details className="evidence-disclosure px-3 py-1" key={group.id}>
            <summary className="text-sm">{group.label}</summary>
            <div className="mt-1 grid">
              {toolsInGroup(group.id).map((tool) => (
                <Link className="min-h-11 rounded-lg py-3 text-sm font-semibold transition-colors hover:text-primary" href={tool.href} key={tool.slug}>{tool.name}</Link>
              ))}
            </div>
          </details>
        ))}
      </div>
    );
  }

  return (
    <details className="group relative">
      <summary className="flex min-h-11 cursor-pointer list-none items-center gap-1.5 text-sm font-bold text-muted transition-colors hover:text-foreground">
        Tools <span className="transition-transform group-open:rotate-180" aria-hidden="true">⌄</span>
      </summary>
      <div className="fixed left-1/2 top-20 max-h-[calc(100dvh-6rem)] w-[min(54rem,calc(100vw-3rem))] -translate-x-1/2 overflow-y-auto rounded-xl border border-border bg-white p-6 shadow-[var(--shadow-md)]">
        <div className="flex items-center justify-between gap-5 border-b border-border pb-4">
          <div><p className="font-extrabold">Evalio tools</p><p className="mt-1 text-xs text-muted">Transparent, deterministic application analysis.</p></div>
          <Link className="quiet-link text-sm" href="/tools">View all&nbsp;→</Link>
        </div>
        <div className="mt-5 grid grid-cols-3 gap-6">
          {toolGroups.map((group) => (
            <div key={group.id}>
              <p className="text-[0.68rem] font-extrabold uppercase tracking-[0.14em] text-muted">{group.label}</p>
              <div className="mt-2 grid gap-1">
                {toolsInGroup(group.id).map((tool) => (
                  <Link className="rounded-lg px-2 py-2 text-sm font-semibold transition-colors hover:bg-[var(--primary-soft)] hover:text-primary" href={tool.href} key={tool.slug}><span>{tool.name}</span><span className="mt-1 block text-xs font-normal leading-5 text-muted">{tool.description}</span></Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </details>
  );
}

export function AppShell({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <div className="min-h-screen">
      <a className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-xl focus:bg-white focus:px-4 focus:py-3" href="#main-content">
        Skip to content
      </a>
      <header className="sticky top-0 z-40 border-b border-border/80 bg-white/95 backdrop-blur-md">
        <div className="site-container flex h-[72px] items-center justify-between gap-6">
          <Logo />
          <NavigationDisclosures><nav className="hidden items-center gap-7 md:flex" aria-label="Primary navigation">
            <ToolsMenu />
            {navigation.map((item) => (
              <Link key={item.href} href={item.href} className="flex min-h-11 items-center text-sm font-bold text-muted transition-colors hover:text-foreground">
                {item.label}
              </Link>
            ))}
            <AuthNavigation />
          </nav>
          <details className="relative md:hidden">
            <summary className="grid size-11 cursor-pointer list-none place-items-center rounded-lg border border-border bg-white text-sm font-bold shadow-sm transition-colors hover:border-primary" aria-label="Open navigation menu">
              <span aria-hidden="true">Menu</span>
            </summary>
            <nav className="absolute right-0 top-14 grid max-h-[calc(100dvh-7rem)] w-[min(22rem,calc(100vw-2.5rem))] gap-1 overflow-y-auto rounded-xl border border-border bg-white p-3 shadow-[var(--shadow-md)]" aria-label="Mobile navigation">
              <ToolsMenu mobile />
              {navigation.map((item) => (
                <Link key={item.href} href={item.href} className="rounded-lg px-3 py-3 text-sm font-bold hover:bg-[var(--surface-muted)]">
                  {item.label}
                </Link>
              ))}
              <AuthNavigation mobile />
            </nav>
          </details></NavigationDisclosures>
        </div>
      </header>
      <main className="page-enter" id="main-content"><AuthBoundary>{children}</AuthBoundary></main>
      <footer className="ink-section border-t border-white/10">
        <div className="site-container grid gap-10 py-12 md:grid-cols-[1.5fr_2fr] lg:py-16">
          <div>
            <Logo />
            <p className="mt-4 max-w-sm text-sm leading-6 text-white/65">
              Transparent admissions analysis without black-box AI or false certainty.
            </p>
            <p className="mt-6 text-xs text-white/50">© {new Date().getFullYear()} Evalio. Internal metrics are not admission probabilities.</p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            {footerGroups.map((group) => (
              <div key={group.title}>
                <h2 className="font-sans text-xs font-extrabold uppercase tracking-[0.14em] text-white">{group.title}</h2>
                <div className="mt-4 grid gap-3">
                  {group.links.map((link) => <Link className="text-sm text-white/60 transition-colors hover:text-white" href={link.href} key={link.label}>{link.label}</Link>)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
