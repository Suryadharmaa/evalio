import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import MethodologyPage from "@/app/methodology/page";
import { CollegeEvaluator } from "@/components/college/college-evaluator";
import { EssayAnalyzer } from "@/components/evaluation/essay-analyzer";
import { ProfileRecords } from "@/components/profile/profile-records";
import { ConfidenceBadge } from "@/components/ui/confidence-badge";
import { RuleIssue } from "@/components/ui/rule-issue";
import { authenticatedFetch } from "@/lib/api/client";

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...await importOriginal<typeof import("@/lib/api/client")>(),
  apiError: vi.fn(async () => "Request failed."),
  authenticatedFetch: vi.fn(),
}));

const mockedFetch = vi.mocked(authenticatedFetch);
const jsonResponse = (data: unknown, status = 200) =>
  new Response(JSON.stringify({ data }), {
    status,
    headers: { "Content-Type": "application/json" },
  });

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  mockedFetch.mockReset();
});

describe("specified business components", () => {
  it("renders rule severity and evidence as text", () => {
    render(<RuleIssue evidence="Sentence 4" message="Repeated phrase." ruleId="ESSAY-023" severity="MEDIUM" title="Repetition" />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
    expect(screen.getByText(/Sentence 4/)).toBeInTheDocument();
  });

  it("renders confidence without relying on color", () => {
    render(<ConfidenceBadge level="LOW" />);
    expect(screen.getByText("Confidence: LOW")).toBeInTheDocument();
  });

  it("renders public methodology versions and limitations", () => {
    render(<MethodologyPage />);
    expect(screen.getByText("college-1.1.0")).toBeInTheDocument();
    expect(screen.getAllByText("Not measured").length).toBeGreaterThan(0);
  });

  it("submits essay input and renders rule-driven results", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({ evaluation: {
      display_score: 82,
      overall_score: 81.5,
      label: "Strong",
      confidence: "HIGH",
      components: { clarity: 80 },
      metrics: { word_count: 8, sentence_count: 1, paragraph_count: 1 },
      issues: [],
    } })));
    render(<EssayAnalyzer />);
    fireEvent.change(screen.getByLabelText("Essay text"), { target: { value: "I built a measured project for twelve students." } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await waitFor(() => expect(screen.getByText("82")).toBeInTheDocument());
    expect(screen.getByText("Clarity", { exact: true })).toBeInTheDocument();
  });

  it("loads profile records with current server-evaluated status", async () => {
    mockedFetch.mockImplementation(async (path) => {
      if (path === "/api/v1/profiles") return jsonResponse([{ id: "profile-1", profile_name: "2027" }]);
      if (path.endsWith("/activities")) return jsonResponse([{ id: "activity-1", activity_name: "Debate", current_score: 73 }]);
      return jsonResponse(null, 404);
    });
    render(<ProfileRecords kind="activities" />);
    await waitFor(() => expect(screen.getByText(/Current internal score 73\/100/)).toBeInTheDocument());
    expect(screen.getByLabelText("Activity")).toBeInTheDocument();
  });

  it("shows application strength separately in college comparison", async () => {
    mockedFetch.mockImplementation(async (path) => {
      if (path === "/api/v1/profiles") return jsonResponse([{ id: "profile-1", profile_name: "2027" }]);
      if (path.endsWith("/evaluate")) return jsonResponse({
        academic_alignment: 88,
        application_strength: 79,
        college: { id: "college-1", name: "Example University", slug: "example-university" },
        college_data_cycles: { admissions: "2026-27", requirements: null, financial_aid: "2026-27", cds: "2026-27" },
        components: { academics: 88, activities: 72, honors: 76 },
        confidence_score: 90,
        course_rigor: 84,
        evaluation_date: "2026-09-14",
        selectivity_risk: "HIGH",
        requirements_fit: "COMPATIBLE",
        financial_fit: "POSSIBLE",
        financial_risk: "MEDIUM",
        financial_confidence: "MEDIUM",
        oldest_critical_source_at: "2026-08-01T00:00:00+00:00",
        planning_category: "COMPETITIVE",
        confidence: "HIGH",
        reasons: ["CDS weighted."],
        financial_reasons: ["More cost data is needed."],
        rubric_version: "college-1.1.0",
        source_freshness: "CURRENT",
        triggered_rules: ["COL-007"],
      });
      return jsonResponse(null, 404);
    });
    render(<CollegeEvaluator initialCollegeId="college-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "Evaluate My Profile" }));
    await waitFor(() => expect(screen.getByText("Application strength")).toBeInTheDocument());
    expect(screen.getByText("79")).toBeInTheDocument();
    expect(screen.getByText("Testing")).toBeInTheDocument();
    expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/not an admission probability/i).length).toBeGreaterThan(0);
  });
});
