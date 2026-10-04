import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApplicationAudit } from "@/components/college/application-audit";
import { DashboardOverview } from "@/components/dashboard/dashboard-overview";
import { ReportManager } from "@/components/report/report-manager";
import { authenticatedFetch } from "@/lib/api/client";

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...await importOriginal<typeof import("@/lib/api/client")>(),
  apiError: vi.fn(async () => "Request failed."),
  authenticatedFetch: vi.fn(),
}));

const mockedFetch = vi.mocked(authenticatedFetch);
const jsonResponse = (data: unknown, status = 200) => new Response(JSON.stringify({ data }), { status, headers: { "Content-Type": "application/json" } });

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); mockedFetch.mockReset(); });

describe("authenticated workflows", () => {
  it("uses the newest saved evaluation and shows target count", async () => {
    mockedFetch.mockImplementation(async (path) => {
      if (path === "/api/v1/profiles") return jsonResponse([{ id: "profile-1", profile_name: "2027" }]);
      if (path.endsWith("/evaluations")) return jsonResponse([
        { evaluation_type: "ACADEMIC", display_score: 90, overall_score: 90, confidence: "HIGH", status: "COMPLETE" },
        { evaluation_type: "ACADEMIC", display_score: 50, overall_score: 50, confidence: "LOW", status: "COMPLETE" },
      ]);
      if (path.endsWith("/targets")) return jsonResponse([{}, {}]);
      return jsonResponse(null, 404);
    });
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({ evaluation: { display_score: 90, disclaimer: "Planning only." } })));
    render(<DashboardOverview />);
    await waitFor(() => expect(screen.getAllByText("90").length).toBeGreaterThan(0));
    expect(screen.getByRole("table", { name: /Profile component scores/ })).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual(["Component", "Score", "Data status", "Evidence covered", "Next action"]);
    expect(screen.getByText("2 target colleges")).toBeInTheDocument();
    expect(screen.queryByText("50")).not.toBeInTheDocument();
    expect(screen.getByText(/Components marked N\/A are excluded, not counted as zero/)).toBeInTheDocument();
  });

  it("renders and persists an application material checklist", async () => {
    mockedFetch.mockImplementation(async (path, init) => {
      if (path === "/api/v1/profiles") return jsonResponse([{ id: "profile-1" }]);
      if (path.endsWith("/audit")) return jsonResponse({ audit: { completeness_score: 0, readiness: "INCOMPLETE", missing_required: ["ESSAY"], critical_issues: ["Missing required material: ESSAY"], priorities: ["Missing required material: ESSAY"], checklist: [{ requirement_type: "ESSAY", required: true, completion_status: "MISSING", deadline: null, quality_status: "NOT_EVALUATED" }] } });
      if (path.endsWith("/materials") && init?.method === "PUT") return jsonResponse([]);
      return jsonResponse(null, 404);
    });
    render(<ApplicationAudit collegeId="college-1" />);
    const run = await screen.findByRole("button", { name: "Run application audit" });
    fireEvent.click(run);
    await screen.findByText("Prioritized actions");
    fireEvent.change(screen.getByLabelText("Completion"), { target: { value: "PRESENT" } });
    fireEvent.click(screen.getByRole("button", { name: "Save checklist" }));
    await waitFor(() => expect(screen.getByText(/Material status saved/)).toBeInTheDocument());
    const materialCall = mockedFetch.mock.calls.find(([path]) => path.endsWith("/materials"));
    expect(materialCall?.[1]?.body).toContain('"completion_status":"PRESENT"');
  });

  it("generates reports from only the newest evaluation of each type", async () => {
    mockedFetch.mockImplementation(async (path, init) => {
      if (path === "/api/v1/profiles") return jsonResponse([{ id: "profile-1", profile_name: "2027" }]);
      if (path.endsWith("/evaluations")) return jsonResponse([
        { evaluation_type: "ESSAY", display_score: 91, confidence: "HIGH", evaluated_at: "2026-09-12T00:00:00Z" },
        { evaluation_type: "ESSAY", display_score: 44, confidence: "LOW", evaluated_at: "2026-01-01T00:00:00Z" },
      ]);
      if (path.endsWith("/reports") && init?.method === "POST") return jsonResponse({ id: "report-1" }, 201);
      if (path.endsWith("/reports")) return jsonResponse([]);
      return jsonResponse(null, 404);
    });
    render(<ReportManager />);
    const generate = await screen.findByRole("button", { name: "Generate readiness report" });
    fireEvent.click(generate);
    await waitFor(() => expect(screen.getByText("Report created.")).toBeInTheDocument());
    const createCall = mockedFetch.mock.calls.find(([, init]) => init?.method === "POST");
    expect(createCall?.[1]?.body).toContain('"display_score":91');
    expect(createCall?.[1]?.body).not.toContain('"display_score":44');
  });
});
