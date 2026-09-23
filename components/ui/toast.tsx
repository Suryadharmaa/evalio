export function Toast({ message, tone = "info" }: { message: string; tone?: "info" | "success" | "danger" }) {
  const toneClass = tone === "success" ? "bg-[var(--success)]" : tone === "danger" ? "bg-[var(--danger)]" : "bg-[var(--info)]";
  return <div aria-live="polite" className={`fixed bottom-5 right-5 z-50 max-w-sm rounded-lg px-4 py-3 text-sm font-semibold text-white shadow-[var(--shadow-md)] ${toneClass}`} role="status">{message}</div>;
}
