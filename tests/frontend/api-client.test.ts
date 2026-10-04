import { afterEach, describe, expect, it, vi } from "vitest";
import { apiFetch, apiUrl, authenticatedFetch } from "@/lib/api/client";
import { recordPath, sitePath } from "@/lib/site";
import { createSupabaseBrowserClient } from "@/lib/auth/browser";

vi.mock("@/lib/auth/browser", () => ({ createSupabaseBrowserClient: vi.fn() }));
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.resetAllMocks(); });

describe("static frontend API access", () => {
  it("sends public calls directly to FastAPI, outside the Pages base path", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.example.com");
    vi.stubEnv("NEXT_PUBLIC_BASE_PATH", "/evalio");
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}"));
    vi.stubGlobal("fetch", fetchMock);
    await apiFetch("/api/v1/colleges?country=US", { method: "GET" });
    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/api/v1/colleges?country=US", expect.objectContaining({ credentials: "omit", cache: "no-store" }));
    expect(sitePath("/evalio-icon.png")).toBe("/evalio/evalio-icon.png");
  });

  it("preserves bearer authentication without sending browser cookies", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.example.com");
    vi.mocked(createSupabaseBrowserClient).mockReturnValue({ auth: { getSession: async () => ({ data: { session: { access_token: "test-token" } } }) } } as unknown as ReturnType<typeof createSupabaseBrowserClient>);
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}"));
    vi.stubGlobal("fetch", fetchMock);
    await authenticatedFetch("/api/v1/profiles", { headers: { "Idempotency-Key": "test-id" } });
    const init = fetchMock.mock.calls[0][1];
    expect(init.headers.get("Authorization")).toBe("Bearer test-token");
    expect(init.headers.get("Idempotency-Key")).toBe("test-id");
    expect(init.credentials).toBe("omit");
  });

  it("rejects non-API paths and misconfigured origins before sending credentials", () => {
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "https://api.example.com/api/v1");
    expect(() => apiUrl("/api/v1/profiles")).toThrow();
    vi.stubEnv("NEXT_PUBLIC_API_ORIGIN", "http://api.example.com");
    expect(() => apiUrl("/api/v1/profiles")).toThrow();
    expect(() => apiUrl("https://other.example.com/api/v1/profiles")).toThrow();
  });

  it("encodes mutable IDs in static detail routes", () => {
    expect(recordPath("colleges", "a&b")).toBe("/colleges/view?slug=a%26b");
    expect(recordPath("essays", "example-id")).toBe("/essays/view?id=example-id");
  });
});
