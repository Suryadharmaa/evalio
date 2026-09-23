"use client";

import { useEffect, useState, type ReactNode } from "react";
import { Alert } from "@/components/ui/alert";
import { Button, ButtonLink } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import { createSupabaseBrowserClient } from "@/lib/auth/browser";
import { safeExternalUrl } from "@/lib/utils/safe-url";
import { CampusMedia, type CollegeMedia } from "./campus-media";
import { collegeBoolean, collegeDate, collegeLabel, collegeMoney, collegeNumber, UNVERIFIED } from "./college-format";
import styles from "./college-surfaces.module.css";

interface Admission {
  academic_cycle: string; source_cycle: string | null;
  applicants_total: number | null; admits_total: number | null; enrolled_total: number | null;
  acceptance_rate: string | null; yield_rate_pct: string | null;
  international_applicants: number | null; international_admits: number | null;
  sat_25: string | null; sat_50: string | null; sat_75: string | null;
  act_25: string | null; act_50: string | null; act_75: string | null;
  test_policy: string; test_policy_status: string | null; application_fee_usd: string | null;
}
interface Requirement { academic_cycle: string; requirement_type: string; status: string; details: string | null; deadline: string | null; quantity?: number | null; word_limit?: number | null }
interface FinancialAid {
  academic_cycle: string; source_cycle: string | null; need_policy: string; aid_policy_status: string | null;
  international_need_based_aid: boolean | null; international_need_based_aid_status: string | null;
  meets_full_demonstrated_need: boolean | null; meets_full_demonstrated_need_status: string | null;
  estimated_cost_of_attendance: string | null; tuition: string | null; mandatory_fees: string | null;
  room_board: string | null; books_personal?: string | null; cost_basis: string | null; aid_forms_or_process: string | null; currency: string; notes?: string | null;
}
interface Source { field_group: string; field_name: string; source_type: string; source_url: string; academic_cycle?: string | null; retrieved_at?: string | null; verified_at: string | null; freshness: string; confidence: string }
interface College {
  id: string; name: string; city: string | null; country_code: string; state_region: string | null;
  institution_type: string | null; official_website: string | null; common_app_member: boolean | null;
  application_platforms?: string[]; admissions: Admission | null; requirements: Requirement[];
  financial_aid: FinancialAid | null; sources: Source[]; media: CollegeMedia[];
}
const sections = [["overview", "Overview"], ["admissions", "Admissions"], ["testing", "Testing"], ["requirements", "Requirements"], ["international", "International"], ["financial-aid", "Financial aid"], ["costs", "Costs"], ["sources", "Sources"]];
function Fact({ label, children }: { label: string; children: ReactNode }) { return <div><dt>{label}</dt><dd>{children}</dd></div>; }
function policyBoolean(value: boolean | null | undefined, status?: string | null) {
  return status && !["YES", "NO", "UNKNOWN"].includes(status) ? collegeLabel(status) : collegeBoolean(value);
}

export function CollegeDetailView({ slug }: { slug: string }) {
  const [college, setCollege] = useState<College | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [activeSection, setActiveSection] = useState("overview");
  useEffect(() => {
    const controller = new AbortController();
    void fetch(`/api/v1/colleges/${encodeURIComponent(slug)}`, { signal: controller.signal }).then(async (response) => {
      if (!response.ok) throw new Error(response.status === 404 ? "College not found." : "College data is temporarily unavailable.");
      const data = ((await response.json()) as { data: College }).data;
      if (!controller.signal.aborted) setCollege(data);
    }).catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Unable to load college."); });
    return () => controller.abort();
  }, [slug, attempt]);
  useEffect(() => {
    try {
      const client = createSupabaseBrowserClient();
      void client.auth.getSession().then(({ data }) => setSignedIn(Boolean(data.session))).catch(() => setSignedIn(false));
      const { data } = client.auth.onAuthStateChange((_event, session) => setSignedIn(Boolean(session)));
      return () => data.subscription.unsubscribe();
    } catch { return; }
  }, []);
  if (error) return <Alert className="mt-8" title="Unable to load college" tone="danger"><p>{error} Your profile has not been changed.</p><Button className="mt-4" variant="secondary" onClick={() => { setCollege(null); setError(null); setAttempt(attempt + 1); }}>Try again</Button></Alert>;
  if (!college) return <div role="status" aria-label="Loading college profile" className="mt-8 grid gap-4"><Skeleton className="h-64" /><Skeleton className="h-28" /><Skeleton className="h-48" /></div>;
  const admission = college.admissions;
  const aid = college.financial_aid;
  const website = safeExternalUrl(college.official_website);
  const media = college.media ?? [];
  const logo = media.find((item) => item.media_type === "LOGO" && item.is_primary)
    ?? media.find((item) => item.media_type === "LOGO");
  const campusMedia = media.filter((item) => item.media_type !== "LOGO");
  const location = [college.city, college.state_region, college.country_code].filter(Boolean).join(" · ");
  const verified = college.sources.filter((source) => safeExternalUrl(source.source_url) && source.verified_at && source.academic_cycle && source.confidence !== "UNKNOWN");
  const latest = verified.map((source) => source.verified_at!).sort().at(-1);
  const destination = `/tools/application-evaluator?college=${college.id}&college_name=${encodeURIComponent(college.name)}`;
  return <>
    <section className={styles.hero} id="overview" aria-labelledby="college-overview">
      <CampusMedia hero kind="logo" location={location} media={logo} name={college.name} />
      <div className={styles.heroBody}><div><p className="eyebrow">Evalio / College profile</p><h1 className={styles.heroTitle} id="college-overview">{college.name}</h1><p className={styles.heroMeta}>{location} · {collegeLabel(college.institution_type)}</p></div><div className="flex flex-wrap gap-3"><ButtonLink href={signedIn === true ? destination : `/sign-in?next=${encodeURIComponent(destination)}`}>{signedIn === true ? "Evaluate My Profile" : "Sign in to evaluate"} <span aria-hidden="true">→</span></ButtonLink>{website && <ButtonLink href={website} variant="secondary" rel="noopener noreferrer" target="_blank">Official website ↗</ButtonLink>}</div></div>
      <div className={styles.sourceStrip}><StatusBadge tone={verified.length ? "info" : "warning"}>{verified.length ? `${verified.length} verified source records` : "Verification incomplete"}</StatusBadge><span>Policy cycle: {admission?.academic_cycle ?? aid?.academic_cycle ?? UNVERIFIED}</span>{latest && <span>Latest verification: {collegeDate(latest)}</span>}<a href="#sources">Inspect provenance →</a></div>
    </section>
    <nav aria-label="College profile sections" className={styles.sectionNav}>{sections.map(([id, label]) => <a href={`#${id}`} aria-current={activeSection === id ? "location" : undefined} key={id} onClick={() => setActiveSection(id)}>{label}</a>)}</nav>
    <div className={styles.detailGrid}>
      <section id="admissions" className={styles.detailSection}><h2>Admissions</h2><p className={styles.sectionCaption}>Published institutional data, never your admission probability.</p><dl className={styles.facts}><Fact label="Acceptance rate">{admission?.acceptance_rate == null ? UNVERIFIED : `${collegeNumber(Number(admission.acceptance_rate) * 100)}%`}</Fact><Fact label="Statistics source cycle">{admission?.source_cycle ?? UNVERIFIED}</Fact><Fact label="Applicants">{collegeNumber(admission?.applicants_total)}</Fact><Fact label="Admits">{collegeNumber(admission?.admits_total)}</Fact><Fact label="Enrolled">{collegeNumber(admission?.enrolled_total)}</Fact><Fact label="Yield rate">{admission?.yield_rate_pct == null ? UNVERIFIED : `${collegeNumber(admission.yield_rate_pct)}%`}</Fact></dl></section>
      <section id="testing" className={styles.detailSection}><h2>Testing</h2><p className={styles.sectionCaption}>Policy cycle: {admission?.academic_cycle ?? UNVERIFIED}. Historical score ranges do not establish eligibility.</p><dl className={styles.facts}><Fact label="Test policy">{collegeLabel(admission?.test_policy)}{admission?.test_policy_status && <span className={styles.factDetail}>{collegeLabel(admission.test_policy_status)}</span>}</Fact><Fact label="Common App">{collegeBoolean(college.common_app_member)}</Fact><Fact label="SAT 25 / 50 / 75">{[admission?.sat_25, admission?.sat_50, admission?.sat_75].map(collegeNumber).join(" / ")}</Fact><Fact label="ACT 25 / 50 / 75">{[admission?.act_25, admission?.act_50, admission?.act_75].map(collegeNumber).join(" / ")}</Fact></dl></section>
      <section id="requirements" className={`${styles.detailSection} ${styles.wideSection}`}><h2>Application requirements</h2><p className={styles.sectionCaption}>Expand an item to inspect the research detail and cycle. Confirm deadlines at the official source.</p>{college.requirements.length ? <div className={styles.requirementList}>{college.requirements.map((item, index) => <details className={styles.requirement} key={`${item.requirement_type}-${index}`}><summary><span>{collegeLabel(item.requirement_type)}</span><StatusBadge tone={item.status === "REQUIRED" ? "warning" : "neutral"}>{item.status.replaceAll("_", " ")}</StatusBadge></summary><div><p>{item.details || "Additional detail not yet verified."}</p><dl className={styles.facts}><Fact label="Cycle">{item.academic_cycle}</Fact><Fact label="Deadline">{collegeDate(item.deadline)}</Fact><Fact label="Quantity">{collegeNumber(item.quantity)}</Fact><Fact label="Word limit">{collegeNumber(item.word_limit)}</Fact></dl></div></details>)}</div> : <p className="mt-4 text-sm text-muted">Requirements not yet verified.</p>}</section>
      <section id="international" className={styles.detailSection}><h2>International applicants</h2><p className={styles.sectionCaption}>International-specific figures are not inferred from overall admission rates.</p><dl className={styles.facts}><Fact label="International applicants">{collegeNumber(admission?.international_applicants)}</Fact><Fact label="International admits">{collegeNumber(admission?.international_admits)}</Fact><Fact label="Need-based aid">{policyBoolean(aid?.international_need_based_aid, aid?.international_need_based_aid_status)}</Fact><Fact label="Meets full demonstrated need">{policyBoolean(aid?.meets_full_demonstrated_need, aid?.meets_full_demonstrated_need_status)}</Fact></dl></section>
      <section id="financial-aid" className={styles.detailSection}><h2>Financial aid</h2><p className={styles.sectionCaption}>Policy cycle: {aid?.academic_cycle ?? UNVERIFIED} · Source cycle: {aid?.source_cycle ?? UNVERIFIED}</p><dl className={styles.facts}><Fact label="International aid policy">{collegeLabel(aid?.need_policy)}</Fact><Fact label="Research status">{collegeLabel(aid?.aid_policy_status)}</Fact><Fact label="Forms / process">{aid?.aid_forms_or_process || UNVERIFIED}</Fact></dl>{aid?.notes && <p className={styles.sectionCaption}>{aid.notes}</p>}</section>
      <section id="costs" className={`${styles.detailSection} ${styles.wideSection}`}><h2>Costs</h2><p className={styles.sectionCaption}>Published estimates, not a financial-aid offer. {aid?.cost_basis ? collegeLabel(aid.cost_basis) : "Cost basis not yet verified."}</p><dl className={styles.facts}><Fact label="Estimated cost of attendance">{collegeMoney(aid?.estimated_cost_of_attendance, aid?.currency)}</Fact><Fact label="Tuition">{collegeMoney(aid?.tuition, aid?.currency)}</Fact><Fact label="Mandatory fees">{collegeMoney(aid?.mandatory_fees, aid?.currency)}</Fact><Fact label="Room and board">{collegeMoney(aid?.room_board, aid?.currency)}</Fact><Fact label="Books and personal expenses">{collegeMoney(aid?.books_personal, aid?.currency)}</Fact><Fact label="Application fee">{collegeMoney(admission?.application_fee_usd)}</Fact></dl></section>
      <section id="sources" className={`${styles.detailSection} ${styles.wideSection}`}><h2>Sources & freshness</h2><p className={styles.sectionCaption}>Verification is field-specific. A verified record is not a claim that every college fact is current.</p>{college.sources.length ? <ul className={styles.sourceList}>{college.sources.map((source, index) => { const url = safeExternalUrl(source.source_url); return <li className={styles.sourceRow} key={`${source.field_name}-${index}`}><div className={styles.sourceHeading}><strong>{collegeLabel(source.field_group)} / {collegeLabel(source.field_name)}</strong><div className="flex flex-wrap gap-2"><StatusBadge tone={source.freshness === "CURRENT" ? "success" : "warning"}>{collegeLabel(source.freshness)}</StatusBadge><StatusBadge>{source.confidence} confidence</StatusBadge></div></div><div className={styles.sourceMeta}><span>{collegeLabel(source.source_type)}</span><span>Cycle: {source.academic_cycle ?? UNVERIFIED}</span><span>Retrieved: {collegeDate(source.retrieved_at)}</span><span>Verified: {collegeDate(source.verified_at)}</span></div>{url ? <a className={styles.sourceUrl} href={url} rel="noopener noreferrer" target="_blank">Open source ↗</a> : <p className="mt-2 text-sm text-muted">Invalid source URL withheld.</p>}</li>; })}</ul> : <Alert className="mt-4" title="Limited provenance" tone="warning">No source records are available for this college.</Alert>}</section>
    </div>
    {campusMedia.length > 0 && <section className="mt-8" aria-label="Campus gallery"><h2 className="text-2xl">Campus gallery</h2><div className="mt-4 grid gap-4 sm:grid-cols-2">{campusMedia.map((item) => <CampusMedia key={item.id} media={item} location={location} name={college.name} />)}</div></section>}
  </>;
}
