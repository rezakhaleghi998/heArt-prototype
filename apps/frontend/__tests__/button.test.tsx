import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders a primary action", () => {
    render(<Button>Inizia</Button>);
    expect(screen.getByRole("button", { name: "Inizia" })).toBeInTheDocument();
  });
});
