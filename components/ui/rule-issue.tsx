import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

interface RuleIssueProps { ruleId: string; severity: string; title: string; message: string; evidence?: string }
export function RuleIssue({ evidence, message, ruleId, severity, title }: RuleIssueProps) {
  return <Card className="p-4"><div className="flex flex-wrap items-center gap-2"><StatusBadge tone={severity === "CRITICAL" || severity === "HIGH" ? "danger" : "warning"}>{severity}</StatusBadge><span className="text-xs text-muted">{ruleId}</span></div><h3 className="mt-3 font-semibold">{title}</h3><p className="mt-1 text-sm leading-6 text-muted">{message}</p>{evidence ? <p className="mt-3 rounded-lg bg-[var(--surface-muted)] p-3 text-sm"><strong>Evidence:</strong> {evidence}</p> : null}</Card>;
}
