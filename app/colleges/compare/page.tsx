import { redirect } from "next/navigation";

export default async function CollegeComparePage({ searchParams }: { searchParams: Promise<{ college?: string }> }) {
  const { college } = await searchParams;
  redirect(college ? `/tools/application-evaluator?college=${encodeURIComponent(college)}` : "/tools/application-evaluator");
}
