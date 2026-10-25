import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { IntervalTable } from "./IntervalTable";
import type { ForecastIntervalResponse } from "../../api/types";

const RECORDS: ForecastIntervalResponse[] = [
  {
    delivery_start: "2026-01-10T00:00:00Z",
    forecast_generation_mw: 120,
    actual_generation_mw: 100,
    forecast_publish_time: "2026-01-09T11:00:00Z",
    error_mw: 20,
    wind_shortfall_mw: 20,
    wind_surplus_mw: 0,
    status: "matched",
  },
  {
    delivery_start: "2026-01-10T00:30:00Z",
    forecast_generation_mw: 90,
    actual_generation_mw: null,
    forecast_publish_time: "2026-01-09T11:00:00Z",
    error_mw: null,
    wind_shortfall_mw: null,
    wind_surplus_mw: null,
    status: "actual_unavailable",
  },
];

describe("IntervalTable", () => {
  it("renders one row per record with a status label", () => {
    render(<IntervalTable records={RECORDS} totalCount={2} limit={500} offset={0} onPageChange={vi.fn()} />);
    expect(screen.getAllByRole("row")).toHaveLength(3); // header + 2 records
    expect(screen.getByText("Matched")).toBeInTheDocument();
    expect(screen.getByText("Actual not yet available")).toBeInTheDocument();
  });

  it("shows a missing actual as a dash, never as zero", () => {
    render(<IntervalTable records={RECORDS} totalCount={2} limit={500} offset={0} onPageChange={vi.fn()} />);
    const row = screen.getByText("Actual not yet available").closest("tr") as HTMLTableRowElement;
    const actualCell = row.querySelectorAll("td")[2];
    expect(actualCell).toHaveTextContent("—");
    expect(actualCell.textContent?.trim()).not.toBe("0 MW");
  });

  it("toggles sort direction when a sortable header is clicked twice", async () => {
    render(<IntervalTable records={RECORDS} totalCount={2} limit={500} offset={0} onPageChange={vi.fn()} />);
    const header = screen.getByRole("button", { name: /Delivery \(UK time\)/ });
    expect(header).toHaveAttribute("aria-sort", "ascending");
    await userEvent.click(header);
    expect(header).toHaveAttribute("aria-sort", "descending");
  });

  it("disables pagination buttons at the range boundaries", () => {
    render(<IntervalTable records={RECORDS} totalCount={2} limit={500} offset={0} onPageChange={vi.fn()} />);
    expect(screen.getByLabelText("Previous page")).toBeDisabled();
    expect(screen.getByLabelText("Next page")).toBeDisabled();
  });

  it("calls onPageChange with the next offset", async () => {
    const onPageChange = vi.fn();
    render(<IntervalTable records={RECORDS} totalCount={10} limit={2} offset={0} onPageChange={onPageChange} />);
    await userEvent.click(screen.getByLabelText("Next page"));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });
});
