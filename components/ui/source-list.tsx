import { DataFreshnessBadge } from "@/components/ui/data-freshness-badge";
import { safeExternalUrl } from "@/lib/utils/safe-url";

interface SourceItem { label: string; url: string; sourceType: string; freshness: string; verifiedAt?: string | null }
export function SourceList({ sources }: { sources: SourceItem[] }) {
  return <ul className="grid gap-3">{sources.map((source, index) => { const url = safeExternalUrl(source.url); return <li className="evidence-rail rounded-r-lg p-4" key={`${source.label}-${index}`}><div className="flex flex-wrap items-center justify-between gap-2"><strong>{source.label}</strong><DataFreshnessBadge value={source.freshness} /></div><p className="mt-2 text-sm text-muted">{source.sourceType} · verified {source.verifiedAt ? new Date(source.verifiedAt).toLocaleDateString() : "not yet"}</p>{url ? <a className="mt-2 inline-block min-h-11 py-2 text-sm font-semibold text-primary" href={url} rel="noopener noreferrer" target="_blank">Open source ↗</a> : <p className="mt-2 text-sm text-[var(--danger)]">Invalid source URL withheld.</p>}</li>; })}</ul>;
}
