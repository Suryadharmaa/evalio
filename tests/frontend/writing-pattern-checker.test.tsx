import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { WritingPatternChecker } from "@/components/evaluation/writing-pattern-checker";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const evaluation = {
  risk: "MODERATE",
  triggered_count: 1,
  total_signals: 25,
  confidence: "MEDIUM",
  engine_version: "2.0.0",
  rubric_version: "writing-patterns-1.0.0",
  signals: [{
    signal_id: "WP-004",
    label: "Repeated n-gram rate",
    category: "LANGUAGE",
    metric: "repeated_trigram_percent",
    observed_value: 8.2,
    threshold: "triggered above 3% with at least 50 words",
    triggered: true,
    level: "HIGH",
    evidence: ["I learned through"],
    explanation: "Repeated sequences can signal formulaic phrasing.",
  }],
};

describe("Writing Pattern Checker T2", () => {
  it("shows the mandatory limitation before analysis", () => {
    render(<WritingPatternChecker />);
    expect(screen.getByText("This tool identifies measurable writing patterns. It cannot determine who or what wrote a text.")).toBeInTheDocument();
    expect(screen.queryByText(/AI probability/i)).not.toBeInTheDocument();
  });

  it("submits text and displays metric, threshold, evidence, and explanation", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { evaluation } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<WritingPatternChecker />);

    fireEvent.change(screen.getByLabelText("Writing sample"), { target: { value: "I learned through practice. I learned through testing." } });
    expect(screen.getByText("8 words")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Check patterns" }));

    await waitFor(() => expect(screen.getByText("Writing Pattern Risk")).toBeInTheDocument());
    expect(screen.getByText("1 / 25 signals triggered")).toBeInTheDocument();
    expect(screen.getByText(/repeated trigram percent: 8.2/i)).toBeInTheDocument();
    expect(screen.getByText("triggered above 3% with at least 50 words")).toBeInTheDocument();
    expect(screen.getByText("I learned through")).toBeInTheDocument();
    expect(screen.getByText("Repeated sequences can signal formulaic phrasing.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/evaluations/writing-patterns", expect.objectContaining({ method: "POST" }));
  });
});
