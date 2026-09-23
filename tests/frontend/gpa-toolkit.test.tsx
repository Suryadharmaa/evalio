import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GpaToolkit } from "@/components/evaluation/gpa-toolkit";

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("GPA Toolkit T4", () => {
  it("states that international grades are not forced onto 4.0", () => {
    render(<GpaToolkit />);
    expect(screen.getByText(/does not force international grades into a 4.0 GPA/i)).toBeInTheDocument();
  });

  it("submits an explicit US weighting method and shows formulas", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { result: {
      calculator_version: "gpa-calculator-1.0.0", mode: "US_COURSES", unweighted_gpa: 4, weighted_gpa: 5,
      academic_average: null, scale_min: null, scale_max: null, total_credits_or_weight: 1,
      conversion: "NOT_APPLIED", weighting_method: "HONORS_0_5_ADVANCED_1_0",
      formula: ["Unweighted formula", "Weighted formula"], breakdown: [{ label: "Calculus", credits_or_weight: 1, base_value: 4, weighted_value: 5, course_level: "AP" }],
    } } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<GpaToolkit />);
    fireEvent.change(screen.getByLabelText("Weighting method"), { target: { value: "HONORS_0_5_ADVANCED_1_0" } });
    fireEvent.change(screen.getByLabelText("Course"), { target: { value: "Calculus" } });
    fireEvent.change(screen.getByLabelText("Course level"), { target: { value: "AP" } });
    fireEvent.click(screen.getByRole("button", { name: /calculate/i }));
    await waitFor(() => expect(screen.getByText("5.000")).toBeInTheDocument());
    expect(screen.getByText("Weighted formula")).toBeInTheDocument();
    const request = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as { weighting_method: string };
    expect(request.weighting_method).toBe("HONORS_0_5_ADVANCED_1_0");
  });

  it("exposes custom offsets instead of assuming a universal scale", () => {
    render(<GpaToolkit />);
    fireEvent.change(screen.getByLabelText("Weighting method"), { target: { value: "CUSTOM" } });
    expect(screen.getByRole("group", { name: /custom offsets/i })).toBeInTheDocument();
    expect(screen.getByLabelText("HONORS")).toHaveValue(0.5);
  });

  it("submits international values on their original scale", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { result: {
      calculator_version: "gpa-calculator-1.0.0", mode: "INTERNATIONAL_RAW", unweighted_gpa: null, weighted_gpa: null,
      academic_average: 90.53, scale_min: 0, scale_max: 100, total_credits_or_weight: 1,
      conversion: "NOT_APPLIED", weighting_method: null, formula: ["Raw formula"], breakdown: [],
    } } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<GpaToolkit />);
    fireEvent.click(screen.getByRole("tab", { name: "International" }));
    fireEvent.change(screen.getByLabelText("Curriculum"), { target: { value: "National curriculum" } });
    fireEvent.change(screen.getByLabelText("Label"), { target: { value: "Term 1" } });
    fireEvent.click(screen.getByRole("button", { name: /calculate/i }));
    await waitFor(() => expect(screen.getByText(/90.530/)).toBeInTheDocument());
    expect(screen.getByText(/Conversion not applied/i)).toBeInTheDocument();
  });
});
