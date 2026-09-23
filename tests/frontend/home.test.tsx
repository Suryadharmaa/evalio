import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "@/app/page";

describe("Home", () => {
  it("identifies the application and deterministic positioning", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", {
        name: "Know where your application stands.",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText(/visible rules, not black-box AI/i)).toBeInTheDocument();
  });
});
