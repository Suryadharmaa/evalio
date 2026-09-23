import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ProductPreview, FitPreview } from "@/components/home/product-preview";
import { CollegePreview } from "@/components/home/college-preview";
import { collegeBoolean, collegeMoney, collegeNumber, collegeLabel } from "@/components/college/college-format";
import { CampusMedia } from "@/components/college/campus-media";
import { Tabs } from "@/components/ui/tabs";
import { GpaToolkit } from "@/components/evaluation/gpa-toolkit";
import { LorEvaluator } from "@/components/evaluation/lor-evaluator";
import { Button } from "@/components/ui/button";

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("Astra interaction and data integrity", () => {
  it("labels sample scores and exposes corresponding evidence on interaction", () => {
    render(<ProductPreview />);
    expect(screen.getByText("Illustrative preview")).toBeInTheDocument();
    const control = screen.getByRole("button", { name: "View evidence" });
    expect(control).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(control);
    expect(screen.getByText("ACAD-003")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Essay signals 81" }));
    expect(screen.getByText("ESSAY-011")).toBeVisible();
    expect(screen.getByText(/diminishing contribution/)).toBeVisible();
  });
  it("exposes planning reasons without making admission probability claims", () => {
    render(<FitPreview />);
    fireEvent.click(screen.getByText("Why this result?"));
    expect(screen.getByText(/not an admission probability/)).toBeVisible();
  });
  it("uses a recoverable API error state for homepage college data", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({ ok: false }).mockResolvedValueOnce({ ok: true, json: async () => ({ data: [] }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<CollegePreview />);
    expect(await screen.findByText("College data is temporarily unavailable.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("The directory is awaiting verified records.")).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toContain("country=US");
  });
  it("keeps null, false, zero and qualified research statuses distinct", () => {
    expect(collegeNumber(0)).toBe("0");
    expect(collegeNumber(null)).toBe("Not yet verified");
    expect(collegeMoney(0)).toBe("$0");
    expect(collegeBoolean(false)).toBe("No");
    expect(collegeBoolean(null)).toBe("Not yet verified");
    expect(collegeLabel("UNKNOWN")).toBe("Not yet verified");
    expect(collegeLabel("LIMITED_NEED_BASED")).toBe("Limited need-based aid");
  });
  it("uses a branded fallback without manufacturing an image", () => {
    render(<CampusMedia name="Example College" location="Example City · US" />);
    expect(screen.getByText("Campus image not yet available")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
  it("renders a verified logo from the local college-logo directory", () => {
    render(<CampusMedia kind="logo" name="Example College" location="Example City · US" media={{
      id: "logo-1", media_type: "LOGO", image_url: "/college-logos/example-college.svg",
      source_url: "https://commons.wikimedia.org/wiki/File:Example.svg", license: "PD-textlogo",
      attribution: "Wikimedia Commons", alt_text: "Example College logo", is_primary: true,
      width: 180, height: 64, sha256: "a".repeat(64), content_type: "image/svg+xml",
      verification_quality: "HIGH", trademark_notice: true,
      verified_at: "2026-09-20T00:00:00+00:00",
    }} />);
    expect(screen.getByRole("img", { name: "Example College logo" }).getAttribute("src"))
      .toContain("/college-logos/example-college.svg");
    expect(screen.queryByText(/Wikimedia Commons/)).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Logo source/ })).not.toBeInTheDocument();
  });
  it("supports keyboard tabs with unique control IDs", () => {
    const items = [{ id: "one", label: "One", content: "First" }, { id: "two", label: "Two", content: "Second" }];
    render(<><Tabs items={items} label="First set" /><Tabs items={items} label="Second set" /></>);
    const first = screen.getAllByRole("tab", { name: "One" })[0];
    first.focus(); fireEvent.keyDown(first, { key: "ArrowRight" });
    expect(screen.getAllByRole("tab", { name: "Two" })[0]).toHaveFocus();
    const ids = [...document.querySelectorAll("[id]")].map((element) => element.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
  it("preserves course drafts across the six GPA modes", () => {
    render(<GpaToolkit />);
    expect(screen.getAllByRole("tab")).toHaveLength(6);
    fireEvent.change(screen.getByLabelText("Course"), { target: { value: "Calculus" } });
    fireEvent.click(screen.getByRole("tab", { name: "International" }));
    fireEvent.change(screen.getByLabelText("Label"), { target: { value: "Semester 1" } });
    fireEvent.click(screen.getByRole("tab", { name: "High School GPA" }));
    expect(screen.getByLabelText("Course")).toHaveValue("Calculus");
    fireEvent.click(screen.getByRole("tab", { name: "International" }));
    expect(screen.getByLabelText("Label")).toHaveValue("Semester 1");
  });
  it("uses the existing LOR API without persistence or fabricated excerpts", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { evaluation: { display_score: 70, confidence: "LOW", components: { relationship_context: 30 }, triggered_rules: ["LOR-001"], engine_version: "2.0.0", rubric_version: "lor-1.0.0" } } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<LorEvaluator />);
    fireEvent.change(screen.getByLabelText("Recommendation text"), { target: { value: "A letter supplied by the user." } });
    fireEvent.click(screen.getByRole("button", { name: "Evaluate letter" }));
    await waitFor(() => expect(screen.getByText("LOR Signal Score")).toBeInTheDocument());
    expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/evaluations/lor");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).save).toBe(false);
    expect(screen.getByText(/not sentence excerpts/)).toBeInTheDocument();
  });
  it("assigns explicit variant contracts even when a caller supplies text utilities", () => {
    render(<Button className="text-black" disabled>Analyze</Button>);
    expect(screen.getByRole("button")).toHaveAttribute("data-variant", "primary");
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
