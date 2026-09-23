import { ActivityDescriptionAnalyzer } from "@/components/evaluation/activity-description-analyzer";

export default function ActivityAnalyzerPage() {
  return <div className="mx-auto w-full max-w-5xl px-5 py-12 sm:px-8 lg:px-12">
    <p className="text-sm font-semibold text-primary">Public tool</p>
    <h1 className="mt-2 text-4xl font-bold tracking-tight">Activity description analyzer</h1>
    <p className="mt-3 max-w-2xl leading-7 text-muted">Measure action clarity, impact evidence, specificity, character use, and title redundancy.</p>
    <ActivityDescriptionAnalyzer />
  </div>;
}
