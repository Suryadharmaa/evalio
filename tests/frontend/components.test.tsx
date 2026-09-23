import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ActivityDescriptionAnalyzer } from "@/components/evaluation/activity-description-analyzer";
import { ErrorState } from "@/components/ui/error-state";
import { ScoreCard } from "@/components/ui/score-card";
import { Tabs } from "@/components/ui/tabs";
import { safeCollegeImageUrl, safeExternalUrl, safeInternalPath } from "@/lib/utils/safe-url";
import { essayAnalysisFormSchema, signInFormSchema } from "@/lib/schemas/forms";

afterEach(() => vi.restoreAllMocks());

describe("business components", () => {
  it("renders a textual score and confidence without relying on color", () => {
    render(<ScoreCard confidence="Medium" score={82} title="Academics" />);
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Confidence: Medium")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Why this score/ })).toBeInTheDocument();
  });

  it("renders an actionable error state", () => {
    render(<ErrorState title="Could not load" message="Try again." action={<button type="button">Try again</button>} />);
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });

  it("submits and renders activity analysis", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { evaluation: { display_score: 84, confidence: "HIGH", components: { action_clarity: 90 }, triggered_rules: [] } } }),
    }));
    render(<ActivityDescriptionAnalyzer />);
    fireEvent.change(screen.getByLabelText("Description"), { target: { value: "Led 12 students through weekly workshops" } });
    fireEvent.submit(screen.getByRole("button", { name: "Analyze description" }).closest("form")!);
    await waitFor(() => expect(screen.getByText("84")).toBeInTheDocument());
    expect(screen.getByText("Confidence: HIGH")).toBeInTheDocument();
  });

  it("rejects unsafe external link protocols", () => {
    expect(safeExternalUrl("javascript:alert(1)")).toBeNull();
    expect(safeExternalUrl("https://user:secret@example.edu/path")).toBeNull();
    expect(safeExternalUrl("https://example.edu/path")).toBe("https://example.edu/path");
    expect(safeCollegeImageUrl("https://commons.wikimedia.org/image.jpg")).toBe("https://commons.wikimedia.org/image.jpg");
    expect(safeCollegeImageUrl("https://tracker.example/image.jpg")).toBeNull();
  });

  it("allows only same-origin redirect paths", () => {
    expect(safeInternalPath("/reports?from=login")).toBe("/reports?from=login");
    expect(safeInternalPath("//attacker.example")).toBeNull();
    expect(safeInternalPath("https://attacker.example")).toBeNull();
    expect(safeInternalPath("/\\attacker.example")).toBeNull();
  });

  it("validates core form relationships before API submission", () => {
    expect(essayAnalysisFormSchema.safeParse({ essayType: "COMMON_APP", text: "", hasFile: false, minWords: 700, wordLimit: 650 }).success).toBe(false);
    expect(essayAnalysisFormSchema.safeParse({ essayType: "COMMON_APP", text: "draft", hasFile: false, minWords: 250, wordLimit: 650 }).success).toBe(true);
    expect(signInFormSchema.safeParse({ email: "bad", password: "secret", mode: "password" }).success).toBe(false);
    expect(signInFormSchema.safeParse({ email: "student@example.com", password: "", mode: "magic" }).success).toBe(true);
  });

  it("switches accessible tab panels", () => {
    render(<Tabs label="Example" items={[{ id: "one", label: "One", content: "First" }, { id: "two", label: "Two", content: "Second" }]} />);
    fireEvent.click(screen.getByRole("tab", { name: "Two" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("Second");
  });
});
