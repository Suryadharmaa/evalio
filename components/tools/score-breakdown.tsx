import { Card } from "@/components/ui/card";
import { ScoreBar } from "@/components/ui/score-bar";

interface ScoreBreakdownItem {
  label: string;
  value: number | string;
}

export function ScoreBreakdown({ id, items, title = "Score breakdown" }: { id?: string; items: ScoreBreakdownItem[]; title?: string }) {
  return (
    <Card className="p-5 sm:p-6">
      <h2 className="font-sans text-lg font-bold" id={id}>{title}</h2>
      {items.length ? (
        <dl className="mt-4">
          {items.map((item) => <div className="score-row rounded-lg px-2 py-3" key={item.label}>
            <div className="flex items-start justify-between gap-4 text-sm"><dt>{item.label}</dt><dd className="data-type font-bold">{item.value}</dd></div>
            {(typeof item.value === "number" || /^\d+(\.\d+)? \/ 100$/.test(String(item.value))) && Number.isFinite(Number(String(item.value).split(" /")[0])) ? <ScoreBar label={item.label} value={Number(String(item.value).split(" /")[0])} /> : null}
          </div>)}
        </dl>
      ) : (
        <p className="mt-3 text-sm text-muted">Insufficient data for a breakdown.</p>
      )}
    </Card>
  );
}
