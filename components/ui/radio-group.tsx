import type { ReactNode } from "react";

export function RadioGroup({ children, legend }: { children: ReactNode; legend: string }) {
  return <fieldset className="grid gap-2"><legend className="mb-1 text-sm font-semibold">{legend}</legend>{children}</fieldset>;
}
