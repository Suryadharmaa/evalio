import { SavedEssayDetail } from "@/components/evaluation/saved-essay-detail";
export default async function SavedEssayPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <div className="mx-auto w-full max-w-4xl px-5 py-12 sm:px-8"><SavedEssayDetail essayId={id} /></div>; }
