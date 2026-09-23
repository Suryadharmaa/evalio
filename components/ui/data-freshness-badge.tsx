import { StatusBadge } from "@/components/ui/status-badge";

export function DataFreshnessBadge({ value }: { value: string }) {
  return <StatusBadge tone={value === "CURRENT" ? "success" : value === "UNKNOWN" ? "neutral" : "warning"}>{value.replaceAll("_", " ")}</StatusBadge>;
}
