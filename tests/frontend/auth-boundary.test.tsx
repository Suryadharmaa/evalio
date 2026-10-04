import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthBoundary } from "@/components/auth/auth-boundary";

const mocks = vi.hoisted(() => ({ pathname: "/profile", router: { replace: vi.fn() }, getSession: vi.fn(), onAuthStateChange: vi.fn() }));
vi.mock("next/navigation", () => ({ usePathname: () => mocks.pathname, useRouter: () => mocks.router }));
vi.mock("@/lib/auth/browser", () => ({ createSupabaseBrowserClient: () => ({ auth: { getSession: mocks.getSession, onAuthStateChange: mocks.onAuthStateChange } }) }));
afterEach(() => { cleanup(); vi.resetAllMocks(); mocks.pathname = "/profile"; window.history.replaceState(null, "", "/"); });

describe("browser auth boundary", () => {
  it("keeps private children unmounted while checking the session", async () => {
    mocks.getSession.mockReturnValue(new Promise(() => {}));
    mocks.onAuthStateChange.mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } });
    render(<AuthBoundary><p>Private record</p></AuthBoundary>);
    expect(screen.getByRole("status")).toHaveTextContent("Checking your session");
    await waitFor(() => expect(mocks.getSession).toHaveBeenCalled());
    expect(screen.queryByText("Private record")).not.toBeInTheDocument();
  });

  it("redirects guests and preserves the query string", async () => {
    window.history.replaceState(null, "", "/reports/view/?id=example");
    mocks.pathname = "/reports/view/";
    mocks.getSession.mockResolvedValue({ data: { session: null }, error: null });
    mocks.onAuthStateChange.mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } });
    render(<AuthBoundary><p>Private record</p></AuthBoundary>);
    await waitFor(() => expect(mocks.router.replace).toHaveBeenCalledWith("/sign-in?next=%2Freports%2Fview%2F%3Fid%3Dexample"));
    expect(screen.queryByText("Private record")).not.toBeInTheDocument();
  });

  it("shows signed-in content and removes it on sign-out", async () => {
    let notify: (_event: string, session: unknown) => void = () => {};
    mocks.onAuthStateChange.mockImplementation((callback) => { notify = callback; return { data: { subscription: { unsubscribe: vi.fn() } } }; });
    mocks.getSession.mockResolvedValue({ data: { session: { access_token: "test" } }, error: null });
    render(<AuthBoundary><p>Private record</p></AuthBoundary>);
    expect(await screen.findByText("Private record")).toBeInTheDocument();
    act(() => notify("SIGNED_OUT", null));
    expect(screen.queryByText("Private record")).not.toBeInTheDocument();
    expect(mocks.router.replace).toHaveBeenCalled();
  });

  it("keeps public pages available without auth configuration", () => {
    mocks.pathname = "/colleges/";
    render(<AuthBoundary><p>Public colleges</p></AuthBoundary>);
    expect(screen.getByText("Public colleges")).toBeInTheDocument();
    expect(mocks.getSession).not.toHaveBeenCalled();
  });
});
