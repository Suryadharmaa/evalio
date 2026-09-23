import type { Metadata } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/card";
import { toolGroups, toolsInGroup } from "@/lib/tools/catalog";

export const metadata: Metadata = {
  title: "College Application Tools | Evalio",
  description: "Explore transparent, deterministic tools for essays, academics, applications, scholarships, and recommendation letters.",
};

const groupCopy = {
  essays: "Turn a draft or early idea into clearer, measurable evidence.",
  application: "Understand academic context, activities, college fit, and planning needs.",
  letters: "Build and review recommendation letters around specific examples.",
};

export default function ToolsPage() {
  return (
    <>
      <section className="hero-wash border-b border-border/70">
        <div className="site-container py-20 sm:py-24 lg:py-28">
          <p className="eyebrow">Evalio / Tools</p>
          <h1 className="display-title mt-5 max-w-4xl">Tools for a clearer application.</h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-muted sm:text-xl">
            Work on one part at a time. Evalio uses visible, versioned rules and connects every result to evidence and methodology.
          </p>
        </div>
      </section>

      <div className="site-container py-16 sm:py-20 lg:py-24">
        {toolGroups.map((group, groupIndex) => {
          const tools = toolsInGroup(group.id);
          return (
            <section className={groupIndex ? "mt-16 border-t border-border pt-16" : ""} key={group.id} aria-labelledby={`${group.id}-title`}>
              <div className="grid gap-5 lg:grid-cols-[0.32fr_0.68fr] lg:gap-12">
                <div>
                  <p className="eyebrow">Evalio / {String(groupIndex + 1).padStart(2, "0")}</p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-[-0.02em]" id={`${group.id}-title`}>{group.label}</h2>
                  <p className="mt-3 max-w-sm leading-7 text-muted">{groupCopy[group.id]}</p>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  {tools.map((tool) => (
                    <Link className="group" href={tool.href} key={tool.slug}>
                      <Card className="lift-card flex h-full min-h-56 flex-col p-6">
                        <span className="data-type grid size-10 place-items-center rounded-lg border border-border bg-[var(--primary-soft)] text-xs font-extrabold text-primary" aria-hidden="true">{tool.shortName}</span>
                        <h3 className="mt-6 text-xl font-semibold tracking-[-0.015em]">{tool.name}</h3>
                        <p className="mt-3 flex-1 text-sm leading-6 text-muted">{tool.description}</p>
                        <span className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-primary">
                          View tool <span className="transition-transform group-hover:translate-x-1" aria-hidden="true">→</span>
                        </span>
                      </Card>
                    </Link>
                  ))}
                </div>
              </div>
            </section>
          );
        })}
      </div>

      <section className="border-y border-border bg-white">
        <div className="site-container grid gap-6 py-14 sm:grid-cols-[1fr_auto] sm:items-center">
          <div>
            <p className="eyebrow">Evalio / A result you can inspect</p>
            <h2 className="mt-3 text-3xl font-extrabold tracking-[-0.04em]">Score → evidence → rule → explanation</h2>
            <p className="mt-3 max-w-2xl leading-7 text-muted">When data is insufficient, Evalio says so instead of filling the gap with a confident-looking guess.</p>
          </div>
          <Link className="quiet-link inline-flex min-h-12 items-center" href="/methodology">View methodology&nbsp;<span aria-hidden="true">→</span></Link>
        </div>
      </section>
    </>
  );
}
