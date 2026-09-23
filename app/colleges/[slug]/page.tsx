import { CollegeDetailView } from "@/components/college/college-detail";

export default async function CollegeDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-12 sm:px-8 lg:px-12">
      <p className="text-sm font-semibold text-primary">College reference data</p>
      <CollegeDetailView key={slug} slug={slug} />
    </div>
  );
}
