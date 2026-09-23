import Link from "next/link";
import { HeroTrustSignals } from "@/components/home/hero-trust-signals";
import { ProductPreview, MethodologyPreview, FitPreview } from "@/components/home/product-preview";
import { CollegePreview } from "@/components/home/college-preview";
import { ButtonLink } from "@/components/ui/button";
import { Reveal } from "@/components/ui/reveal";
import styles from "@/components/home/home.module.css";

const tools = [
  { name: "Application Evaluator", href: "/tools/application-evaluator", tag: "The complete picture", description: "Connect your evidence to a target college. Understand your strengths, requirements, and the gaps worth addressing.", meta: "Saved profile · College-specific analysis" },
  { name: "Essay Evaluator", href: "/tools/essay-evaluator", tag: "01 / Writing", description: "A closer read of the signals you can actually inspect.", meta: "8 dimensions · Rule-based" },
  { name: "College Explorer", href: "/colleges", tag: "02 / Research", description: "Find the facts behind your college shortlist.", meta: "Source provenance · Policy context" },
  { name: "GPA Toolkit", href: "/tools/gpa", tag: "03 / Academics", description: "Your grades, on their original scale.", meta: "US + international · Exact formulas" },
  { name: "Coursework", href: "/tools/coursework-evaluator", tag: "04 / Context", description: "Challenge measured against opportunity.", meta: "5 components · School-aware" },
  { name: "Scholarships", href: "/tools/scholarships", tag: "In development", description: "Source-backed discovery and tracking are planned. No unverified awards.", meta: "See availability →" },
];

function Arrow() { return <span aria-hidden="true">→</span>; }

export default function Home() {
  return <>
    <section className={styles.hero}>
      <div className={`site-container ${styles.heroLayout}`}>
        <div className={styles.heroCopy}>
          <p className="eyebrow">Evalio / Application analysis</p>
          <h1 className="display-title">Know where your application <em>stands.</em></h1>
          <p>Transparent analysis across academics, activities, essays, and college fit—built from visible rules, not black-box AI.</p>
          <div className={styles.actions}><ButtonLink href="/tools/application-evaluator">Evaluate my application <Arrow /></ButtonLink><ButtonLink href="/tools/essay-evaluator" variant="secondary">Analyze an essay</ButtonLink></div>
          <HeroTrustSignals />
          <div className={styles.heroSignature}>Every score has a reason.</div>
        </div>
        <Reveal><ProductPreview /></Reveal>
      </div>
    </section>

    <section className="border-b border-border" aria-label="Evalio principles"><Reveal className={`site-container ${styles.principles}`}>
      {[["100%", "Explainable scoring"], ["0", "AI models required"], ["Versioned", "Methodology"], ["Source-aware", "College data"]].map(([value, label]) => <div className={styles.principle} key={label}><strong className="data-type">{value}</strong><span>{label}</span></div>)}
    </Reveal></section>

    <section className="section-space" id="tools" aria-labelledby="tools-title"><div className="site-container">
      <div className={styles.sectionHead}><div><p className="eyebrow">Evalio / Your toolkit</p><h2 className="section-title mt-4" id="tools-title">One application.<br />Every angle.</h2></div><p>Start with a question. Leave with evidence you can use. Each tool has a clear job—and a visible method.</p></div>
      <Reveal className={styles.toolsGrid}>{tools.map((tool, index) => <Link className={`${styles.toolCard} ${index === 0 ? styles.featured : ""}`} href={tool.href} key={tool.name}>
        <div className={styles.toolTop}><span>{tool.tag}</span><Arrow /></div><h3>{tool.name}</h3><p>{tool.description}</p>
        {index === 0 && <div className={styles.featuredSignals}><div><span>Strength</span><strong>Evidence, not assumptions</strong></div><div><span>College fit</span><strong>Separate dimensions</strong></div><div><span>Next action</span><strong>Traceable priorities</strong></div></div>}
        <div className={styles.toolMeta}>{tool.meta}</div>
      </Link>)}</Reveal>
      <Link className="quiet-link mt-6 inline-flex min-h-11 items-center gap-2 text-sm" href="/tools">Explore all tools <Arrow /></Link>
    </div></section>

    <section className="section-space border-y border-border bg-[var(--canvas)]" aria-labelledby="method-title"><Reveal className={`site-container ${styles.split}`}>
      <div className={styles.splitCopy}><p className="eyebrow">Evalio / Methodology</p><h2 className="section-title mt-4" id="method-title">Nothing hidden<br />behind the score.</h2><p>A number is only useful when you can understand it. Follow a result to its evidence, the rule that applies, and the explanation behind it.</p><p>Same input. Same data snapshot. Same rule version. Same result.</p><ButtonLink className="mt-7" href="/methodology" variant="secondary">Inspect the methodology <Arrow /></ButtonLink></div>
      <MethodologyPreview />
    </Reveal></section>

    <section className="section-space ink-section" aria-labelledby="fit-title"><Reveal className={`site-container ${styles.split}`}>
      <div className={`${styles.splitCopy} ${styles.darkCopy}`}><p className="eyebrow">Evalio / College fit</p><h2 className="section-title mt-4" id="fit-title">Fit without<br /><em>fake certainty.</em></h2><p>Strong academics and a selective college can both be true. Keep alignment, requirements, financial fit, and risk in view—without turning them into a promise.</p><ButtonLink className="mt-8" href="/colleges" variant="inverse">Explore colleges <Arrow /></ButtonLink></div>
      <FitPreview />
    </Reveal></section>

    <section className="section-space" aria-labelledby="college-title"><div className="site-container">
      <div className={styles.sectionHead}><div><p className="eyebrow">Evalio / College data</p><h2 className="section-title mt-4" id="college-title">A shortlist built<br />on better questions.</h2></div><p>Testing policies. International aid. Application requirements. Real records, with source dates and missing information kept visible.</p></div>
      <CollegePreview />
      <Link className="quiet-link mt-6 inline-flex min-h-11 items-center gap-2 text-sm" href="/colleges">Open the college directory <Arrow /></Link>
    </div></section>

    <section className="border-t border-border pb-16 pt-12" aria-labelledby="steps-title"><div className="site-container"><p className="eyebrow">Evalio / From input to insight</p><h2 className="section-title mt-4" id="steps-title">A clearer next step.</h2><div className={styles.steps}>
      {[["01", "Bring your evidence", "Start with an essay, a course list, or your saved profile. You decide what to share and save."], ["02", "Inspect the analysis", "Versioned rules surface measurable signals, with confidence and limitations in view."], ["03", "Choose what comes next", "Follow a finding, check a source, or revisit an input. The reasoning stays yours to inspect."]].map(([number, title, description]) => <div className={styles.step} key={number}><p className="hairline-label text-primary">{number}</p><h3>{title}</h3><p>{description}</p></div>)}
    </div></div></section>

    <section className={styles.final}><Reveal className={`site-container ${styles.finalLayout}`}><div><p className="eyebrow">Evalio / Start with clarity</p><h2 className={`section-title mt-4 ${styles.finalTitle}`}>Every score<br />has a reason.</h2></div><div className={styles.finalRight}><p>Start with your application, your essay, or a college.</p><div className={styles.actions}><ButtonLink href="/tools/application-evaluator">Evaluate my application <Arrow /></ButtonLink><ButtonLink href="/colleges" variant="secondary">Find your colleges <Arrow /></ButtonLink></div><Link className="quiet-link mt-4 inline-flex min-h-11 items-center text-sm" href="/privacy">Your text. Your choice to save.</Link></div></Reveal></section>
  </>;
}
