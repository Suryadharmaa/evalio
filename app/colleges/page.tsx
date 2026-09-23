import { CollegeExplorer } from "@/components/college/college-explorer";

export default function CollegesPage() {
  return <div className="site-container py-12 sm:py-16">
    <p className="eyebrow">Evalio / College data</p>
    <h1 className="display-title mt-4">Explore colleges.</h1>
    <p className="mt-4 max-w-2xl text-lg leading-8 text-muted">Search cycle-versioned admissions, requirements, testing, and financial-aid facts with source provenance.</p>
    <CollegeExplorer />
  </div>;
}
