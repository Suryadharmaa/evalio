import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EssayAnalyzer } from "@/components/evaluation/essay-analyzer";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const evaluation = {
  overall_score: 81,
  display_score: 81,
  label: "Strong",
  confidence: "HIGH",
  engine_version: "2.0.0",
  rubric_version: "essay-1.0.0",
  components: {
    compliance: 100,
    clarity: 84,
    structure: 81,
    specificity: 76,
    reflection: 83,
    voice: 79,
    sentence_variety: 86,
    style_hygiene: 72,
  },
  metrics: {
    word_count: 8,
    sentence_count: 1,
    paragraph_count: 1,
    average_sentence_length: 8,
  },
  issues: [{
    rule_id: "ESSAY-014",
    severity: "MEDIUM",
    title: "Low specificity signal density",
    message: "Few measurable specificity signals were detected.",
    evidence: { signals_per_100_words: 0.2 },
    score_delta: null,
    score_effect: "Finding only; no separate point adjustment.",
    confidence: "HIGH",
    methodology_link: "/methodology/essay",
  }],
};

describe("Essay Evaluator T1", () => {
  it("shows a live word count and sends prompt with privacy-safe defaults", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { evaluation } }),
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<EssayAnalyzer />);

    fireEvent.change(screen.getByLabelText("Essay text"), { target: { value: "I built twelve prototypes and documented every measured test." } });
    expect(screen.getByText("9 / 650 words")).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Add essay prompt/));
    fireEvent.change(screen.getByLabelText("Essay prompt (optional)"), { target: { value: "Describe a project." } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));

    await waitFor(() => expect(screen.getByText("Mechanical Essay Score")).toBeInTheDocument());
    const request = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as Record<string, unknown>;
    expect(request.prompt_text).toBe("Describe a project.");
    expect(request.save_raw_text).toBe(false);
  });

  it("renders all rubric dimensions and complete finding context", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { evaluation } }) }));
    render(<EssayAnalyzer />);
    fireEvent.change(screen.getByLabelText("Essay text"), { target: { value: "A measurable essay draft." } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));

    await waitFor(() => expect(screen.getByText("Reflection Signals")).toBeInTheDocument());
    expect(screen.getByText("Voice Indicators")).toBeInTheDocument();
    expect(screen.getByText("Sentence Variety")).toBeInTheDocument();
    expect(screen.getByText("Style Hygiene")).toBeInTheDocument();
    expect(screen.getByText("ESSAY-014")).toBeInTheDocument();
    expect(screen.getByText(/signals per 100 words: 0.2/i)).toBeInTheDocument();
    expect(screen.getByText("Finding only; no separate point adjustment.")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Why this matters"));
    expect(screen.getByRole("link", { name: /View methodology/ })).toHaveAttribute("href", "/methodology/essay");
  });
});
