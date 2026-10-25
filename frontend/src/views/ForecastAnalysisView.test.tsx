import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ForecastAnalysisView } from "./ForecastAnalysisView";
import * as endpoints from "../api/endpoints";
import type { AnalysisFiltersValue } from "../components/filters/AnalysisFilters";

vi.mock("../api/endpoints");

const QUERY: AnalysisFiltersValue = {
  startDate: "2026-01-01",
  endDate: "2026-01-02",
  mode: "decision_time",
  asOf: "",
};

describe("ForecastAnalysisView", () => {
  it("renders the table without treating a missing actual as zero", async () => {
    vi.mocked(endpoints.getForecasts).mockResolvedValue({
      mode: "decision_time",
      as_of: null,
      total_count: 1,
      limit: 500,
      offset: 0,
      records: [
        {
          delivery_start: "2026-01-01T00:00:00Z",
          forecast_generation_mw: 150,
          actual_generation_mw: null,
          forecast_publish_time: "2025-12-31T11:00:00Z",
          error_mw: null,
          wind_shortfall_mw: null,
          wind_surplus_mw: null,
          status: "actual_unavailable",
        },
      ],
    });

    render(
      <ForecastAnalysisView query={QUERY} onQueryChange={vi.fn()} onReset={vi.fn()} refreshToken={0} />
    );

    await waitFor(() => expect(screen.getByText("Actual not yet available")).toBeInTheDocument());
    const row = screen.getByText("Actual not yet available").closest("tr") as HTMLTableRowElement;
    const actualCell = row.querySelectorAll("td")[2];
    expect(actualCell.textContent?.trim()).toBe("—");
  });

  it("shows an empty state when no records are returned", async () => {
    vi.mocked(endpoints.getForecasts).mockResolvedValue({
      mode: "decision_time",
      as_of: null,
      total_count: 0,
      limit: 500,
      offset: 0,
      records: [],
    });

    render(
      <ForecastAnalysisView query={QUERY} onQueryChange={vi.fn()} onReset={vi.fn()} refreshToken={0} />
    );
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("No delivery intervals"));
  });

  it("applies new filters through onQueryChange", async () => {
    vi.mocked(endpoints.getForecasts).mockResolvedValue({
      mode: "decision_time",
      as_of: null,
      total_count: 0,
      limit: 500,
      offset: 0,
      records: [],
    });
    const onQueryChange = vi.fn();

    render(
      <ForecastAnalysisView query={QUERY} onQueryChange={onQueryChange} onReset={vi.fn()} refreshToken={0} />
    );
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onQueryChange).toHaveBeenCalledWith(QUERY);
  });
});
