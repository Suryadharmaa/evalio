import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CollegeExplorer } from "@/components/college/college-explorer";

const college = {
  id: "1",
  slug: "example-university",
  name: "Example University",
  country_code: "US",
  state_region: "CA",
  city: "Example City",
  institution_type: "Private nonprofit",
  application_platform_primary: "COMMON_APP",
  application_platforms: ["COMMON_APP"],
  official_website: "https://example.edu",
  test_policy: "OPTIONAL",
  need_policy: "NEED_AWARE",
  primary_media: null,
};

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("CollegeExplorer", () => {
  it("loads US colleges by default and debounces name searches", async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: [college], meta: { page: 1, page_size: 12, total: 1 } }),
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<CollegeExplorer />);

    await act(async () => { await vi.advanceTimersByTimeAsync(300); });
    expect(String(fetchMock.mock.calls[0][0])).toContain("country=US");

    fireEvent.change(screen.getByLabelText("College name"), { target: { value: "Stanford" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(299); });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await act(async () => { await vi.advanceTimersByTimeAsync(1); });
    expect(String(fetchMock.mock.calls[1][0])).toContain("q=Stanford");

    fireEvent.change(screen.getByLabelText("Application platform"), {
      target: { value: "COMMON_APP" },
    });
    await act(async () => { await vi.advanceTimersByTimeAsync(300); });
    expect(String(fetchMock.mock.calls[2][0])).toContain("application_platform=COMMON_APP");

    fireEvent.change(screen.getByLabelText("Institution type"), { target: { value: "PRIVATE_NONPROFIT" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(300); });
    expect(String(fetchMock.mock.calls[3][0])).toContain("institution_type=PRIVATE_NONPROFIT");

    fireEvent.change(screen.getByLabelText("Selectivity band"), { target: { value: "UNDER_10" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(300); });
    expect(String(fetchMock.mock.calls[4][0])).toContain("selectivity_band=UNDER_10");
  });

  it("requests the next page and renders no-result state", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [college], meta: { page: 1, page_size: 12, total: 13 } }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [], meta: { page: 2, page_size: 12, total: 13 } }),
      })
      .mockResolvedValue({
        ok: true,
        json: async () => ({ data: [], meta: { page: 1, page_size: 12, total: 0 } }),
      });
    vi.stubGlobal("fetch", fetchMock);
    render(<CollegeExplorer />);

    await waitFor(() => expect(screen.getByText("Example University")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    await waitFor(() => expect(String(fetchMock.mock.calls[1][0])).toContain("page=2"));

    fireEvent.change(screen.getByLabelText("College name"), { target: { value: "No such school" } });
    await waitFor(() => expect(screen.getByText("No matching colleges")).toBeInTheDocument());
  });
});
