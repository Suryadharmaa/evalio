import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EssayIdeaBuilder } from "@/components/evaluation/essay-idea-builder";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const result = {
  engine_version: "2.0.0",
  builder_version: "idea-builder-1.0.0",
  ideas: [{
    idea_number: 1,
    title: "The 3 AM server outage",
    moment: "The 3 AM server outage",
    tension: "Responsibility versus being unprepared",
    core_value: "responsibility",
    change: "I learned to test assumptions",
    reflection_direction: "Explore how your understanding of responsibility changed through this experience.",
    people_or_place: "The community lab",
    possible_fit: "Common App Prompt 5",
    questions_to_explore: ["What exactly happened during the outage?"],
  }],
};

describe("Essay Idea Builder T3", () => {
  it("states that output is brainstorming rather than ghostwriting", () => {
    render(<EssayIdeaBuilder />);
    expect(screen.getByText(/does not write a finished essay or invent experiences/i)).toBeInTheDocument();
  });

  it("submits structured arrays and renders a grounded direction", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ data: { result } }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<EssayIdeaBuilder />);

    fireEvent.change(screen.getByLabelText("Specific moments"), { target: { value: "The 3 AM server outage\nThe failed test\nThe team meeting" } });
    fireEvent.change(screen.getByLabelText("Challenges or tensions"), { target: { value: "Responsibility versus being unprepared" } });
    fireEvent.click(screen.getByLabelText("Responsibility"));
    fireEvent.change(screen.getByLabelText("Lessons or changes"), { target: { value: "I learned to test assumptions" } });
    fireEvent.click(screen.getByRole("button", { name: "Build idea directions" }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "1 grounded direction" })).toBeInTheDocument());
    expect(screen.getAllByText("The 3 AM server outage").length).toBeGreaterThan(0);
    expect(screen.getByText("Responsibility versus being unprepared")).toBeInTheDocument();
    expect(screen.getByText("What exactly happened during the outage?")).toBeInTheDocument();
    const request = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as { specific_moments: string[]; values: string[] };
    expect(request.specific_moments).toEqual(["The 3 AM server outage", "The failed test", "The team meeting"]);
    expect(request.values).toEqual(["responsibility"]);
  });
});
