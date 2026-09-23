import { ReportViewer } from "@/components/report/report-viewer";

export default async function ReportPage({ params }: { params: Promise<{ reportId: string }> }) {
  return <div className="mx-auto w-full max-w-4xl px-5 py-12 sm:px-8"><ReportViewer reportId={(await params).reportId} /></div>;
}
