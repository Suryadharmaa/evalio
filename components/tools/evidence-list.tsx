import { Card } from "@/components/ui/card";

export interface EvidenceItem {
  detail?: string;
  label: string;
  value: string;
}

export function EvidenceList({ evidence, title = "Evidence found" }: { evidence: EvidenceItem[]; title?: string }) {
  return (
    <section aria-labelledby="evidence-title">
      <h2 className="text-xl font-extrabold" id="evidence-title">{title}</h2>
      {evidence.length ? (
        <ul className="mt-4 grid gap-3">
          {evidence.map((item, index) => (
            <li className="evidence-rail rounded-r-lg" key={`${item.label}-${index}`}>
              <Card className="border-0 bg-transparent p-4 shadow-none">
                <p className="hairline-label text-primary">{item.label}</p>
                <p className="mt-2 font-semibold">{item.value}</p>
                {item.detail ? <p className="mt-2 text-sm leading-6 text-muted">{item.detail}</p> : null}
              </Card>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted">No evidence is available yet.</p>
      )}
    </section>
  );
}
