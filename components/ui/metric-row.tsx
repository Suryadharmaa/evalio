export function MetricRow({ label, value }: { label: string; value: string | number }) {
  return <div className="flex items-baseline justify-between gap-4 border-b border-border py-2.5"><dt className="text-muted">{label}</dt><dd className="data-type font-semibold">{value}</dd></div>;
}
