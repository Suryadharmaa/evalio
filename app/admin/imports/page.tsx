import { AdminPanel } from "@/components/admin/admin-panel";
export default function AdminImportsPage() { return <div className="mx-auto w-full max-w-5xl px-5 py-12 sm:px-8"><h1 className="text-4xl font-bold">Import lifecycle</h1><p className="mt-3 text-muted">Record, validate, explicitly approve, then promote a staged dataset.</p><AdminPanel mode="imports" /></div>; }
