import { Card } from "@/components/ui/card";

export default function PrivacyPage() {
  return <div className="mx-auto w-full max-w-3xl px-5 py-12 sm:px-8"><p className="text-sm font-semibold text-primary">Privacy</p><h1 className="mt-2 text-4xl font-bold">Your content stays under your control</h1><div className="mt-8 grid gap-4"><Card className="p-6"><h2 className="font-semibold">Anonymous analysis</h2><p className="mt-2 leading-7 text-muted">Raw essay, recommendation, upload, and profile content is not persisted. Temporary upload data is discarded after processing.</p></Card><Card className="p-6"><h2 className="font-semibold">Saved content</h2><p className="mt-2 leading-7 text-muted">Structured account data may be saved. Raw essay or recommendation text requires an explicit opt-in that is off by default.</p></Card><Card className="p-6"><h2 className="font-semibold">Your controls</h2><p className="mt-2 leading-7 text-muted">Authenticated users can export their data or permanently delete their account data from Settings.</p></Card></div></div>;
}

