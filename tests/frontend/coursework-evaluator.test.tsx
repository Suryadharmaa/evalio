import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CourseworkEvaluator } from "@/components/evaluation/coursework-evaluator";

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("Coursework Evaluator T5", () => {
  it("explains the no-advanced-opportunity rule before evaluation", () => {
    render(<CourseworkEvaluator />);
    expect(screen.getByText(/applies the documented neutral-context score instead of penalizing/i)).toBeInTheDocument();
    expect(screen.getByText(/does not infer them from country/i)).toBeInTheDocument();
  });

  it("submits school context and renders evidence for every component", async () => {
    const result = {
      rubric_version: "coursework-1.0.0", display_score: 91, rating: "STRONG", confidence: "HIGH",
      school_context: "No AP or IB courses are available.", no_advanced_penalty: true,
      formula: "Challenge (40) + Core coverage (20)",
      components: [{ key: "advanced_utilization", label: "Advanced utilization", score: null, points: 16, points_available: 20, evidence: "No advanced opportunities available; neutral context score applied.", rule: "ACAD-005", explanation: "No penalty is applied." }],
    };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { evaluation: result } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<CourseworkEvaluator />);
    fireEvent.change(screen.getByLabelText("Curriculum type"), { target: { value: "National curriculum" } });
    fireEvent.change(screen.getByLabelText("Intended major"), { target: { value: "Economics" } });
    fireEvent.change(screen.getByLabelText("Course name"), { target: { value: "English Literature" } });
    fireEvent.change(screen.getByLabelText("School context notes"), { target: { value: "No AP or IB courses are available." } });
    fireEvent.click(screen.getByRole("button", { name: /evaluate coursework/i }));
    await waitFor(() => expect(screen.getByText("91")).toBeInTheDocument());
    expect(screen.getByText("No penalty applied")).toBeInTheDocument();
    expect(screen.getByText("ACAD-005")).toBeInTheDocument();
    const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as { curriculum_type: string; advanced_courses_available: number; highest_levels_available: Record<string, string> };
    expect(body.curriculum_type).toBe("National curriculum");
    expect(body.advanced_courses_available).toBe(0);
    expect(body.highest_levels_available.ENGLISH).toBe("STANDARD");
  });
});
