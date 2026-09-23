import { StatusBadge } from "@/components/ui/status-badge";

export function ConfidenceBadge({ level }: { level: "HIGH" | "MEDIUM" | "LOW" }) {
  return <StatusBadge tone={level === "HIGH" ? "success" : level === "MEDIUM" ? "warning" : "neutral"}>Confidence: {level}</StatusBadge>;
}
