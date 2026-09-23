import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ToolsPage from "@/app/tools/page";
import { EvidenceList, EmptyResult, ErrorResult, LoadingResult, MethodologyLink, RelatedTools, RuleFinding, ScoreBreakdown, ToolHeader, ToolHowItWorks, ToolInputShell } from "@/components/tools";
import { findTool, toolCatalog, toolGroups, toolsInGroup } from "@/lib/tools/catalog";

describe("shared tool foundation", () => {
  it("defines every specified tool once and groups it for navigation", () => {
    expect(toolCatalog).toHaveLength(10);
    expect(new Set(toolCatalog.map((tool) => tool.slug)).size).toBe(toolCatalog.length);
    expect(toolGroups.map((group) => group.label)).toEqual(["Essays", "Application", "Letters"]);
    expect(toolsInGroup("essays")).toHaveLength(3);
    expect(findTool("gpa")?.name).toBe("GPA Toolkit");
  });

  it("renders the grouped tools directory with methodology context", () => {
    render(<ToolsPage />);

    expect(screen.getByRole("heading", { name: "Tools for a clearer application." })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Essays" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Application" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Letters" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /view tool/i })).toHaveLength(10);
    expect(screen.getByText(/score → evidence → rule → explanation/i)).toBeInTheDocument();
  });

  it("renders reusable input, result, evidence, rule, and methodology UI", () => {
    const related = toolCatalog.slice(0, 4);
    render(
      <div>
        <ToolHeader title="Example Tool" description="A deterministic example." />
        <ToolInputShell title="Your input" footer="Not saved"><label>Evidence<input aria-label="Evidence" /></label></ToolInputShell>
        <ScoreBreakdown items={[{ label: "Clarity", value: 82 }]} />
        <EvidenceList evidence={[{ label: "Sentence 2", value: "Specific action" }]} />
        <RuleFinding ruleId="TEST-001" severity="MEDIUM" title="Example finding" explanation="A documented rule was triggered." />
        <MethodologyLink />
        <ToolHowItWorks steps={[{ title: "Input", description: "Add evidence." }, { title: "Analyze", description: "Apply rules." }, { title: "Understand", description: "Read findings." }]} />
        <RelatedTools tools={related} />
      </div>,
    );

    expect(screen.getByRole("heading", { name: "Example Tool." })).toBeInTheDocument();
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Specific action")).toBeInTheDocument();
    expect(screen.getByText("TEST-001")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /see how this is calculated/i })).toHaveAttribute("href", "/methodology");
    expect(within(screen.getByRole("region", { name: "Related tools" })).getAllByRole("link")).toHaveLength(3);
  });

  it("renders accessible empty, loading, and error states", () => {
    const { rerender } = render(<EmptyResult />);
    expect(screen.getByRole("heading", { name: "No result yet" })).toBeInTheDocument();

    rerender(<LoadingResult label="Calculating result" />);
    expect(screen.getByRole("status")).toHaveTextContent("Calculating result");

    rerender(<ErrorResult />);
    expect(screen.getByText("We couldn't load this result")).toBeInTheDocument();
  });
});
