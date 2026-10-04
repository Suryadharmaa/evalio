"use client";

import { apiFetch } from "@/lib/api/client";

import { useEffect, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Input } from "@/components/ui/field";
import { Skeleton } from "@/components/ui/skeleton";
import { CollegeCard, type CollegeSummary } from "./college-card";
import { collegeLabel } from "./college-format";
import styles from "./college-surfaces.module.css";

const PAGE_SIZE = 12;
const states = "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split(" ");
const filterDefinitions = [
  { key: "country", label: "Country", all: "United States", values: ["US"] },
  { key: "state", label: "State", all: "All states", values: states },
  { key: "test_policy", label: "Test policy", all: "All testing policies", values: ["REQUIRED", "OPTIONAL", "OPTIONAL_FOR_INTL_OUTSIDE_US", "OPTIONAL_WITH_PROGRAM_EXCEPTIONS", "FLEXIBLE", "PROGRAM_DEPENDENT", "BLIND", "NOT_ACCEPTED", "UNKNOWN"] },
  { key: "need_policy", label: "Aid policy", all: "All international aid", values: ["NEED_BLIND", "NEED_AWARE", "NEED_AWARE_OR_SELECTIVE", "LIMITED", "LIMITED_NEED_BASED", "MERIT_FOCUSED_LIMITED", "NO_NEED_BASED_AID", "NO_NEED_BASED_AID_OR_VERY_LIMITED", "UNKNOWN"] },
  { key: "institution_type", label: "Institution type", all: "All types", values: ["PUBLIC", "PRIVATE_NONPROFIT", "PRIVATE_FOR_PROFIT", "UNKNOWN"] },
  { key: "application_platform", label: "Application platform", all: "All platforms", values: ["COMMON_APP", "COALITION", "INSTITUTIONAL", "UC_APPLICATION", "CAL_STATE_APPLY", "APPLYTEXAS", "SUNY", "OTHER", "UNKNOWN"] },
  { key: "selectivity_band", label: "Selectivity band", all: "All published rates", values: ["UNDER_10", "10_TO_20", "20_TO_40", "OVER_40", "UNKNOWN"] },
] as const;
type Filters = Record<(typeof filterDefinitions)[number]["key"], string>;
const defaults: Filters = { country: "US", state: "", test_policy: "", need_policy: "", institution_type: "", application_platform: "", selectivity_band: "" };
const rateLabels: Record<string, string> = { UNDER_10: "Under 10%", "10_TO_20": "10–19.9%", "20_TO_40": "20–39.9%", OVER_40: "40% or higher" };
interface CollegeResponse { data: CollegeSummary[]; meta: { page: number; page_size: number; total: number } }

export function CollegeExplorer() {
  const [q, setQ] = useState("");
  const [filters, setFilters] = useState<Filters>(defaults);
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<CollegeResponse | null>(null);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(true);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      const params = new URLSearchParams({ country: filters.country, page: String(page), page_size: String(PAGE_SIZE) });
      if (q.trim()) params.set("q", q.trim());
      Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, value); });
      try {
        const response = await apiFetch(`/api/v1/colleges?${params}`, { signal: controller.signal });
        if (!response.ok) throw new Error("unavailable");
        const body = await response.json() as CollegeResponse;
        if (!controller.signal.aborted) { setResult(body); setError(false); }
      } catch {
        if (!controller.signal.aborted) setError(true);
      } finally { if (!controller.signal.aborted) setBusy(false); }
    }, 300);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [q, filters, page, retry]);
  function changed() { setPage(1); setBusy(true); setError(false); }
  function clear() { setQ(""); setFilters(defaults); changed(); setRetry((value) => value + 1); }
  function submit(event: FormEvent) { event.preventDefault(); changed(); setRetry((value) => value + 1); }
  const total = result?.meta.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / (result?.meta.page_size || PAGE_SIZE)));
  const selected = filterDefinitions.filter(({ key }) => filters[key] !== defaults[key]);
  const hasFilters = Boolean(q.trim() || selected.length);
  return <>
    <form className={styles.searchSurface} onSubmit={submit}>
      <div className={styles.searchRow}><div className={styles.searchInput}><Input id="college-search" label="College name" placeholder="Search by college name…" value={q} onChange={(event) => { setQ(event.target.value); changed(); }} /></div><Button type="submit" disabled={busy}>{busy ? "Searching…" : "Search"}</Button></div>
      <details className="evidence-disclosure mt-3" open><summary>Refine your search <span className="text-xs text-muted">{selected.length ? `${selected.length} selected` : "US · All states"}</span></summary>
        <div className={styles.filterRow}>{filterDefinitions.map(({ key, label, all, values }) => <div className={styles.filter} data-selected={filters[key] !== defaults[key]} key={key}>
          <label className={styles.filterLabel} htmlFor={`filter-${key}`}>{label}</label><select id={`filter-${key}`} value={filters[key]} onChange={(event) => { setFilters({ ...filters, [key]: event.target.value }); changed(); }}>
            {key !== "country" && <option value="">{all}</option>}{values.map((value) => <option value={value} key={value}>{key === "country" ? "United States" : key === "state" ? value : rateLabels[value] ?? collegeLabel(value)}</option>)}
          </select>
        </div>)}</div>
      </details>
      {hasFilters && <div className={styles.activeFilters}>{selected.map(({ key, label }) => <button className={styles.activeChip} key={key} type="button" onClick={() => { setFilters({ ...filters, [key]: defaults[key] }); changed(); }}>Remove {label}: {collegeLabel(filters[key])}<span aria-hidden="true">×</span></button>)}<Button variant="ghost" onClick={clear}>Clear filters</Button></div>}
    </form>
    <div aria-live="polite" aria-busy={busy}>
      {busy ? <div className="mt-6"><p className="mb-4 text-sm text-muted" role="status">Loading colleges…</p><div className={styles.resultGrid}>{[0, 1, 2, 3, 4, 5].map((item) => <div className="rounded-xl border border-border p-4" key={item}><Skeleton className="h-40" /><Skeleton className="mt-4 h-7 w-3/4" /><Skeleton className="mt-3 h-24" /></div>)}</div></div> : error ? <div className="mt-6"><ErrorState title="College database unavailable" message="College data is temporarily unavailable. Your profile has not been changed." action={<Button variant="secondary" onClick={() => { setBusy(true); setRetry((value) => value + 1); }}>Try again</Button>} /></div> : total === 0 ? <div className="mt-6"><EmptyState title={hasFilters ? "No matching colleges" : "College data is empty"} description={hasFilters ? "Try a broader name, remove a testing policy, or expand the state filter." : "No active college records are available yet."} />{hasFilters && <Button className="mt-4" variant="secondary" onClick={clear}>Clear filters</Button>}</div> : <>
        <div className={styles.resultHeader}><p><strong>{total}</strong> {total === 1 ? "college" : "colleges"}</p><p>Page {page} of {pages} · Up to {PAGE_SIZE} per page</p></div>
        <div className={styles.resultGrid}>{result?.data.map((college) => <CollegeCard college={college} key={college.id} />)}</div>
        <nav aria-label="College result pages" className={styles.pagination}><Button variant="secondary" disabled={page <= 1} onClick={() => { setPage(page - 1); setBusy(true); }}>Previous</Button><span className={styles.paginationText}>{page} / {pages}</span><Button variant="secondary" disabled={page >= pages} onClick={() => { setPage(page + 1); setBusy(true); }}>Next</Button></nav>
      </>}
    </div>
  </>;
}
