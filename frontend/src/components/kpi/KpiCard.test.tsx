import { render, screen } from "@testing-library/react";
import { KpiCard } from "./KpiCard";

describe("KpiCard", () => {
  it("renders the label, value and description", () => {
    render(<KpiCard label="MAE" value="120 MW" description="Mean absolute error" />);
    expect(screen.getByText("MAE")).toBeInTheDocument();
    expect(screen.getByText("120 MW")).toBeInTheDocument();
    expect(screen.getByText("Mean absolute error")).toBeInTheDocument();
  });

  it("exposes the help text as an accessible title attribute", () => {
    render(<KpiCard label="MAE" value="120 MW" description="desc" helpText="Explains the metric" />);
    expect(screen.getByTitle("Explains the metric")).toBeInTheDocument();
  });

  it("shows an unavailable state without crashing on a null-derived value", () => {
    render(<KpiCard label="MAE" value="—" description="desc" unavailable />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
