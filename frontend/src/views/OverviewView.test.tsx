import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { OverviewView } from "./OverviewView";
import * as endpoints from "../api/endpoints";
import type { AnalysisFiltersValue } from "../components/filters/AnalysisFilters";

vi.mock("../api/endpoints");

const QUERY: AnalysisFiltersValue = {
  startDate: "2026-01-01",
  endDate: "2026-02-01",
  mode: "decision_time",
  asOf: "",
};

describe("OverviewView", () => {
  it("renders KPI values with units from the API response", async () => {
    vi.mocked(endpoints.getOverview).mockResolvedValue({
      mode: "decision_time",
      as_of: null,
      delivery_range_start: "2026-01-01T00:00:00Z",
      delivery_range_end: "2026-02-01T00:00:00Z",
      expected_intervals: 1488,
      matched_intervals: 1000,
      coverage_percent: 67.2,
      unit: "MW",
      mae: 123.4,
      rmse: 150.1,
      bias: -12.5,
      total_wind_shortfall: 5000,
      total_wind_surplus: 3000,
      source_loaded_at: "2026-01-20T10:00:00Z",
      warnings: [],
    });

    render(<OverviewView query={QUERY} refreshToken={0} />);

    await waitFor(() => expect(screen.getByText("123 MW")).toBeInTheDocument());
    expect(screen.getByText("67.2%")).toBeInTheDocument();
  });

  it("shows an empty state when there are no expected intervals", async () => {
    vi.mocked(endpoints.getOverview).mockResolvedValue({
      mode: "decision_time",
      as_of: null,
      delivery_range_start: "2026-01-01T00:00:00Z",
      delivery_range_end: "2026-01-01T00:00:00Z",
      expected_intervals: 0,
      matched_intervals: 0,
      coverage_percent: 0,
      unit: "MW",
      mae: null,
      rmse: null,
      bias: null,
      total_wind_shortfall: null,
      total_wind_surplus: null,
      source_loaded_at: null,
      warnings: [],
    });

    render(<OverviewView query={QUERY} refreshToken={0} />);
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("No delivery intervals"));
  });

  it("shows a retryable error state on API failure", async () => {
    vi.mocked(endpoints.getOverview)
      .mockRejectedValueOnce(new Error("Service unavailable"))
      .mockResolvedValueOnce({
        mode: "decision_time",
        as_of: null,
        delivery_range_start: "2026-01-01T00:00:00Z",
        delivery_range_end: "2026-02-01T00:00:00Z",
        expected_intervals: 10,
        matched_intervals: 10,
        coverage_percent: 100,
        unit: "MW",
        mae: 10,
        rmse: 12,
        bias: 1,
        total_wind_shortfall: 10,
        total_wind_surplus: 5,
        source_loaded_at: "2026-01-20T10:00:00Z",
        warnings: [],
      });

    render(<OverviewView query={QUERY} refreshToken={0} />);
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Service unavailable"));

    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(screen.getByText("100.0%")).toBeInTheDocument());
  });
});
