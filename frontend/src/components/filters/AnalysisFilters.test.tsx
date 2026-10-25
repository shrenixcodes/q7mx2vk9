import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AnalysisFilters, type AnalysisFiltersValue } from "./AnalysisFilters";

const BASE_VALUE: AnalysisFiltersValue = {
  startDate: "2026-01-01",
  endDate: "2026-02-01",
  mode: "decision_time",
  asOf: "",
};

describe("AnalysisFilters", () => {
  it("has accessible labels for every control", () => {
    render(<AnalysisFilters value={BASE_VALUE} onApply={vi.fn()} onReset={vi.fn()} />);
    expect(screen.getByLabelText("Start date")).toBeInTheDocument();
    expect(screen.getByLabelText("End date")).toBeInTheDocument();
    expect(screen.getByLabelText("Analysis mode")).toBeInTheDocument();
  });

  it("calls onApply with the current draft on submit", async () => {
    const onApply = vi.fn();
    render(<AnalysisFilters value={BASE_VALUE} onApply={onApply} onReset={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).toHaveBeenCalledWith(BASE_VALUE);
  });

  it("rejects an end date that is not after the start date", async () => {
    const onApply = vi.fn();
    render(
      <AnalysisFilters
        value={{ ...BASE_VALUE, startDate: "2026-02-01", endDate: "2026-01-01" }}
        onApply={onApply}
        onReset={vi.fn()}
      />
    );
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent("End date must be after start date.");
  });

  it("requires an as-of timestamp when as-of mode is selected", async () => {
    const onApply = vi.fn();
    render(
      <AnalysisFilters value={{ ...BASE_VALUE, mode: "as_of", asOf: "" }} onApply={onApply} onReset={vi.fn()} />
    );
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent("As-of timestamp is required");
  });

  it("calls onReset when the reset button is clicked", async () => {
    const onReset = vi.fn();
    render(<AnalysisFilters value={BASE_VALUE} onApply={vi.fn()} onReset={onReset} />);
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});
