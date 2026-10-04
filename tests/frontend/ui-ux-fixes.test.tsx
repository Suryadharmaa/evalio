import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthNavigation } from "@/components/auth/auth-navigation";
import { HeroTrustSignals } from "@/components/home/hero-trust-signals";
import { ProfileEditor } from "@/components/profile/profile-editor";
import { authenticatedFetch } from "@/lib/api/client";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/lib/auth/browser", () => ({
  createSupabaseBrowserClient: () => ({
    auth: {
      getSession: async () => ({
        data: { session: { user: { email: "surya@example.com" } } },
      }),
      onAuthStateChange: () => ({ data: { subscription: { unsubscribe: vi.fn() } } }),
      signOut: vi.fn(),
    },
  }),
}));

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...await importOriginal<typeof import("@/lib/api/client")>(),
  apiError: vi.fn(async () => "Request failed."),
  authenticatedFetch: vi.fn(),
}));

const mockedFetch = vi.mocked(authenticatedFetch);

afterEach(() => {
  vi.clearAllMocks();
});

describe("UI and UX fixes", () => {
  it("replaces guest hero copy when the user is signed in", async () => {
    render(<HeroTrustSignals />);

    expect(await screen.findByText("Ready to save to your workspace")).toBeInTheDocument();
    expect(screen.queryByText(/No account needed/)).not.toBeInTheDocument();
  });

  it("groups signed-in account actions under an account menu", async () => {
    render(<AuthNavigation />);

    expect(await screen.findByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByLabelText("Open account menu")).toHaveTextContent("S");
    expect(screen.getByRole("link", { name: "Profile" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign out" })).toBeInTheDocument();
  });

  it("shows unambiguous normalized profile numbers and currency", async () => {
    mockedFetch.mockResolvedValue(new Response(JSON.stringify({ data: [{
      id: "profile-1",
      profile_name: "2027",
      applicant_type: "INTERNATIONAL",
      country_code: "ID",
      graduation_year: 2027,
      curriculum_type: null,
      grading_scale_name: "0-100",
      grading_scale_min: "0.000",
      grading_scale_max: "100.000",
      intended_major: null,
      school_name: null,
      class_size: null,
      class_rank: null,
      max_family_contribution: "53000.00",
      budget_currency: "USD",
      requires_need_based_aid: true,
    }] }), { status: 200 }));
    render(<ProfileEditor />);

    await waitFor(() => expect(screen.getByLabelText("Scale maximum")).toHaveValue(100));
    expect(screen.getByLabelText("Maximum annual family contribution")).toHaveValue(53000);
    expect(screen.getByText("Formatted amount: $53,000.00")).toBeInTheDocument();
  });
});
