"use client";

import { useId, useState } from "react";
import Link from "next/link";
import { StatusBadge } from "@/components/ui/status-badge";
import { ScoreBar } from "@/components/ui/score-bar";
import styles from "./home.module.css";

// Explicitly illustrative interface values, never used by an evaluator.
const examples = [
  { label: "Academics", score: 91, rule: "ACAD-003", evidence: "Four term averages show a positive academic trend.", explanation: "The academic rubric uses chronological grades and a documented trend rule, not a guessed GPA conversion." },
  { label: "Activities", score: 84, rule: "ACT-004", evidence: "A description contains a quantified outcome and its context.", explanation: "Concrete impact is a measurable signal. A title alone does not establish responsibility." },
  { label: "Essay signals", score: 81, rule: "ESSAY-011", evidence: "The same reflection marker appears three times.", explanation: "Repeated reflection markers have diminishing contribution. This is a textual signal, not a judgment of authenticity." },
  { label: "Honors", score: 76, rule: "HON-002", evidence: "An award has no documented selection rate.", explanation: "Unknown selectivity is acknowledged rather than inferred from the award's name." },
];

export function ProductPreview() {
  const [selected, setSelected] = useState(0);
  const [open, setOpen] = useState(false);
  const id = useId();
  const example = examples[selected];
  return <div className={styles.preview} aria-label="Illustrative application analysis">
    <div className={styles.previewToolbar}><span className="hairline-label">Evalio / Analysis</span><span>Illustrative preview</span></div>
    <div className={styles.previewBody}>
      <div className={styles.previewHeading}><div><p className="hairline-label text-primary">Application strength</p><p className={styles.heroScore}>84 <span>/ 100</span></p></div><StatusBadge tone="success">High confidence</StatusBadge></div>
      <p className={styles.previewNote}>A sample interface, not an applicant result.</p>
      <div className={styles.metrics} aria-label="Explore a sample component">
        {examples.map((item, index) => <button className={styles.metric} aria-pressed={selected === index} aria-controls={id} key={item.label} onClick={() => { setSelected(index); setOpen(true); }} type="button">
          <span className={styles.metricHeading}><span>{item.label}</span><strong>{item.score}</strong></span>
          <span aria-hidden="true"><ScoreBar label={`Illustrative ${item.label}`} value={item.score} /></span>
        </button>)}
      </div>
      <div className={styles.previewBottom}><span><strong>3</strong> sample priority findings</span><button aria-controls={id} aria-expanded={open} className={styles.evidenceButton} onClick={() => setOpen(!open)} type="button">{open ? "Hide evidence" : "View evidence"} <span aria-hidden="true">{open ? "−" : "→"}</span></button></div>
      <div id={id} hidden={!open} className={styles.previewEvidence}>
        <p className="hairline-label text-primary">Evidence / {example.label}</p>
        <p className="mt-2 text-sm">{example.evidence}</p>
        <div className={styles.ruleLine}><code>{example.rule}</code><span>Versioned rule</span></div>
        <p className="text-sm text-muted">{example.explanation}</p>
        <Link href="/methodology" className="quiet-link mt-3 inline-flex min-h-11 items-center text-sm">Read the methodology <span aria-hidden="true"> →</span></Link>
      </div>
    </div>
    <div className={styles.traceStrip}><span>Score</span><span aria-hidden="true">→</span><span>Evidence</span><span aria-hidden="true">→</span><span>Rule</span><span aria-hidden="true">→</span><span>Explanation</span></div>
  </div>;
}

export function MethodologyPreview() {
  return <div className={styles.methodPreview}>
    <div className={styles.previewToolbar}><span className="hairline-label">Inside the rubric</span><span>Illustrative score</span></div>
    <div className={styles.previewBody}>
      <p className="hairline-label text-primary">Academic strength</p>
      <div className={styles.previewHeading}><p className={styles.heroScore}>91 <span>/ 100</span></p><StatusBadge tone="success">High confidence</StatusBadge></div>
      <div className={styles.weightStrip} aria-hidden="true">{[0, 1, 2, 3, 4].map((index) => <span key={index} />)}</div>
      <dl className={styles.weightRows}>{[["Performance", 45], ["Course rigor", 30], ["Academic trend", 10], ["Context", 10], ["Major preparation", 5]].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}%</dd></div>)}</dl>
      <details className="evidence-disclosure border-t border-border pt-2"><summary>View evidence</summary><div className={styles.previewEvidence}><p className="hairline-label text-primary">Illustrative evidence</p><p className="mt-2 text-sm">Term averages: 86, 88, 89, 91. The trend is positive.</p><div className={styles.ruleLine}><code>ACAD-003</code><span>Academic trend</span></div><p className="text-sm text-muted">A positive slope of at least one point per semester triggers this rule. The backend applies the published trend table; it does not add arbitrary bonus points.</p><Link className="quiet-link mt-3 inline-flex min-h-11 items-center text-sm" href="/methodology/academic">Inspect the academic methodology →</Link></div></details>
    </div>
  </div>;
}

export function FitPreview() {
  return <div className={styles.fitPreview}>
    <div className={styles.fitHeader}><p className="hairline-label">College-specific analysis</p><span>Illustrative scenario</span></div>
    <dl className={styles.fitRows}>{[["Academic alignment", "STRONG"], ["Selectivity risk", "VERY HIGH"], ["Requirements", "COMPATIBLE"], ["Financial fit", "NEEDS REVIEW"]].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
    <div className={styles.planning}><p className="hairline-label text-muted">Planning category</p><p className="data-type mt-2 text-3xl font-bold">HIGH REACH</p><details className="evidence-disclosure mt-2"><summary>Why this result?</summary><div className="border-t border-border pt-4"><p className="text-sm text-muted">In this illustrative scenario, very high institutional selectivity remains a planning risk even with strong academics. Requirements and financial fit stay separate. This is not an admission probability.</p><p className="mt-3 text-xs text-muted">COL-003 · Ultra-selective safety guard</p><Link className="mt-3 inline-flex min-h-11 items-center font-semibold text-primary" href="/methodology/college">Read the college methodology →</Link></div></details></div>
  </div>;
}
