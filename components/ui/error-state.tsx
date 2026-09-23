import type { ReactNode } from "react";

import { Alert } from "@/components/ui/alert";

export function ErrorState({ action, message, title = "Something went wrong" }: { action?: ReactNode; message: string; title?: string }) {
  return (
    <Alert title={title} tone="danger">
      <p>{message}</p>
      {action ? <div className="mt-3">{action}</div> : null}
    </Alert>
  );
}

