import { getOverview } from "../api/endpoints";
import { useApiResource } from "../hooks/useApiResource";
import { KpiCard } from "../components/kpi/KpiCard";
import { KpiRow } from "../components/kpi/KpiRow";
import { StatusMessage } from "../components/status/StatusMessage";
import { formatMW, formatPercent } from "../lib/format";
import type { AnalysisFiltersValue } from "../components/filters/AnalysisFilters";

interface OverviewViewProps {
  query: AnalysisFiltersValue;
  refreshToken: number;
}

export function OverviewView({ query, refreshToken }: OverviewViewProps) {
  const { status, data, error, retry } = useApiResource(
    (signal) =>
      getOverview(
        { startDate: query.startDate, endDate: query.endDate, mode: query.mode, asOf: query.asOf || undefined },
        signal
      ),
    [query.startDate, query.endDate, query.mode, query.asOf, refreshToken]
  );

  if (status === "loading") {
    return <StatusMessage kind="loading" message="Loading analysis overview…" />;
  }
  if (status === "error" || !data) {
    return <StatusMessage kind="error" message={error ?? "Failed to load the overview."} onRetry={retry} />;
  }
  if (data.expected_intervals === 0) {
    return <StatusMessage kind="empty" message="No delivery intervals fall within the selected range." />;
  }

  return (
    <div className="flex flex-col gap-4">
      <KpiRow>
        <KpiCard
          label="MAE"
          value={formatMW(data.mae)}
          description="Mean absolute forecast error"
          unavailable={data.mae === null}
        />
        <KpiCard
          label="RMSE"
          value={formatMW(data.rmse)}
          description="Root mean squared error"
          unavailable={data.rmse === null}
        />
        <KpiCard
          label="Bias"
          value={formatMW(data.bias)}
          description="Mean forecast minus actual"
          unavailable={data.bias === null}
        />
        <KpiCard
          label="Coverage"
          value={formatPercent(data.coverage_percent)}
          description={`${data.matched_intervals} of ${data.expected_intervals} intervals matched`}
        />
      </KpiRow>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <KpiCard
          label="Wind shortfall"
          value={formatMW(data.total_wind_shortfall)}
          description="Sum of max(forecast - actual, 0) across matched intervals"
          helpText="Deviation only -- not a verified purchase volume or cost."
          unavailable={data.total_wind_shortfall === null}
        />
        <KpiCard
          label="Wind surplus"
          value={formatMW(data.total_wind_surplus)}
          description="Sum of max(actual - forecast, 0) across matched intervals"
          helpText="Deviation only -- not a verified purchase volume or cost."
          unavailable={data.total_wind_surplus === null}
        />
      </div>

      {data.warnings.length > 0 && (
        <ul className="flex flex-col gap-1">
          {data.warnings.map((warning) => (
            <li key={warning} className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
              {warning}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
