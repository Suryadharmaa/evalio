import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HybridEssayAnalyzer } from "@/components/evaluation/hybrid-essay-analyzer";

const essay = Array.from({ length: 8 }, () => "I measured the door and tested a smaller bracket with my friends.").join(" ");
const metrics = {
  word_count: 96, sentence_count: 8, paragraph_count: 1,
  average_words_per_sentence: 12,
  sentence_variety: { score: 75, label: "Good" },
  vocabulary_diversity: { score: 82, label: "Strong" },
  readability: { score: 80, label: "Strong" },
  repetition: { label: "High", repeated_phrases: [], repeated_openings: [] },
};
const result = {
  status: "complete", analysis_id: "test-id", score: 86, label: "Strong", metrics,
  meta: { cached: false, ai_calls: 1 },
  review: {
    overall_impression: "A clear scene with a useful insight.",
    categories: Object.fromEntries([
      ["content", 20], ["structure", 15], ["voice", 20],
      ["specificity", 15], ["reflection", 20], ["writing_quality", 10],
    ].map(([name, max]) => [name, { score: Number(max) - 2, max_score: max, feedback: "Add one detail." }])),
    strengths: ["The opening is concrete."], improvements: ["Sharpen the ending."],
    priority_action: "Revise the final sentence.",
  },
};

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("Hybrid essay review", () => {
  it("renders one structured response without category requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: result }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<HybridEssayAnalyzer />);
    fireEvent.change(screen.getByLabelText("Essay text"), { target: { value: essay } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze essay/ }));

    await waitFor(() => expect(screen.getByText("Scoring rubric")).toBeInTheDocument());
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(screen.getByText("What’s working")).toBeInTheDocument();
    expect(screen.getByText("Writing signals")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Content & ideas"));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("keeps local metrics and retry when semantic review fails", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      data: { status: "partial", metrics, message: "Deeper feedback could not load.", meta: { cached: false, ai_calls: 1 } },
    }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<HybridEssayAnalyzer />);
    fireEvent.change(screen.getByLabelText("Essay text"), { target: { value: essay } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze essay/ }));

    await waitFor(() => expect(screen.getByText("Writing signals")).toBeInTheDocument());
    expect(screen.queryByText("Essay review")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Try AI analysis again" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    const body = JSON.parse(String(fetchMock.mock.calls[1]?.[1]?.body)) as { refresh: boolean };
    expect(body.refresh).toBe(true);
  });
});
