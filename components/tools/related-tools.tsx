import Link from "next/link";

import { Card } from "@/components/ui/card";
import type { ToolCatalogItem } from "@/lib/tools/catalog";

export function RelatedTools({ tools }: { tools: ToolCatalogItem[] }) {
  const visibleTools = tools.slice(0, 3);

  return (
    <section aria-labelledby="related-tools-title">
      <h2 className="text-2xl font-extrabold tracking-[-0.035em]" id="related-tools-title">Related tools</h2>
      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {visibleTools.map((tool) => (
          <Link className="group" href={tool.href} key={tool.slug}>
            <Card className="lift-card h-full p-5">
              <h3 className="font-extrabold">{tool.name}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{tool.description}</p>
              <span className="mt-4 inline-flex text-sm font-bold text-primary">Open tool&nbsp;<span aria-hidden="true">→</span></span>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
