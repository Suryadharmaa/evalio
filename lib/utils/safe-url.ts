export function safeExternalUrl(value: string | null | undefined): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    const safeProtocol = url.protocol === "https:" || url.protocol === "http:";
    return safeProtocol && !url.username && !url.password ? url.href : null;
  } catch {
    return null;
  }
}

const COLLEGE_IMAGE_HOSTS = new Set(["commons.wikimedia.org", "upload.wikimedia.org"]);

export function safeCollegeImageUrl(value: string | null | undefined): string | null {
  const safeUrl = safeExternalUrl(value);
  if (!safeUrl) return null;
  return COLLEGE_IMAGE_HOSTS.has(new URL(safeUrl).hostname) ? safeUrl : null;
}

export function safeInternalPath(value: string | null | undefined): string | null {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\u0000-\u001f]/.test(value)) {
    return null;
  }
  try {
    const url = new URL(value, "https://evalio.invalid");
    return url.origin === "https://evalio.invalid" ? `${url.pathname}${url.search}${url.hash}` : null;
  } catch {
    return null;
  }
}
