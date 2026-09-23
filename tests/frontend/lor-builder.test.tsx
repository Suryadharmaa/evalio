import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LorBuilder } from "@/components/evaluation/lor-builder";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const result = {
  builder_version: "lor-builder-1.0.0",
  missing_evidence: ["comparative_evidence"],
  ethics_notice: "Final wording should be reviewed and owned by the recommender.",
  sections: [
    {
      key: "opening",
      title: "Opening",
      purpose: "Establish relationship, duration, and capacity.",
      items: [
        { item_type: "USER_EVIDENCE", text: "Student: Jordan Lee", source_fields: ["student_name"] },
        { item_type: "SENTENCE_SHELL", text: "I have known [student_name] through [relationship_context].", source_fields: ["student_name", "relationship_context"] },
      ],
    },
  ],
};

describe("LOR Builder T8", () => {
  it("states recommender ownership and anti-fabrication limits", () => {
    render(<LorBuilder />);
    expect(screen.getByText(/reviewed and owned by the recommender/i)).toBeInTheDocument();
    expect(screen.getByText(/will not invent anecdotes, awards, rankings/i)).toBeInTheDocument();
  });

  it("submits structured evidence and renders an editable traceable framework", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { result } }),
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<LorBuilder />);

    fireEvent.change(screen.getByLabelText("Recommender role"), { target: { value: "Mathematics teacher" } });
    fireEvent.change(screen.getByLabelText("Student name"), { target: { value: "Jordan Lee" } });
    fireEvent.change(screen.getByLabelText("Relationship context"), { target: { value: "Advanced calculus class" } });
    fireEvent.change(screen.getByLabelText("Relationship duration"), { target: { value: "Two academic years" } });
    fireEvent.change(screen.getByLabelText("Observed qualities"), { target: { value: "Analytical curiosity\nCollaborative leadership" } });
    fireEvent.change(screen.getByLabelText("Specific examples"), { target: { value: "Tested three modeling approaches\nLed weekly peer review" } });
    fireEvent.click(screen.getByRole("button", { name: /build letter framework/i }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Editable letter framework" })).toBeInTheDocument());
    expect((screen.getByLabelText("Opening — editable framework") as HTMLTextAreaElement).value).toContain("source: student_name");
    expect(screen.getAllByText(/comparative evidence/i).length).toBeGreaterThan(0);
    const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as { qualities: string[]; specific_examples: string[] };
    expect(body.qualities).toEqual(["Analytical curiosity", "Collaborative leadership"]);
    expect(body.specific_examples).toEqual(["Tested three modeling approaches", "Led weekly peer review"]);
  });
});
