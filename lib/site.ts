export function sitePath(path: string): string {
  return `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}${path}`;
}

export function recordPath(kind: "colleges" | "essays" | "reports" | "application", id: string): string {
  const parameter = kind === "colleges" ? "slug" : "id";
  return `/${kind}/view?${parameter}=${encodeURIComponent(id)}`;
}
