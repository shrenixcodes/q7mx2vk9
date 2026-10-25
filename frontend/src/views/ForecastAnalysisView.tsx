import { useState } from "react";
import { getForecasts } from "../api/endpoints";
import { useApiResource } from "../hooks/useApiResource";
import { AnalysisFilters, type AnalysisFiltersValue } from "../components/filters/AnalysisFilters";
import { GenerationChart } from "../components/charts/GenerationChart";
import { IntervalTable } from "../components/table/IntervalTable";
import { StatusMessage } from "../components/status/StatusMessage";

const PAGE_SIZE = 500;

interface ForecastAnalysisViewProps {
  query: AnalysisFiltersValue;
  onQueryChange: (value: AnalysisFiltersValue) => void;
  onReset: () => void;
  refreshToken: number;
}

export function ForecastAnalysisView({ query, onQueryChange, onReset, refreshToken }: ForecastAnalysisViewProps) {
  const [offset, setOffset] = useState(0);

  const { status, data, error, retry } = useApiResource(
    (signal) =>
      getForecasts(
        { startDate: query.startDate, endDate: query.endDate, mode: query.mode, asOf: query.asOf || undefined },
        { limit: PAGE_SIZE, offset },
        signal
      ),
    [query.startDate, query.endDate, query.mode, query.asOf, offset, refreshToken]
  );

  function handleApply(next: AnalysisFiltersValue) {
    setOffset(0);
    onQueryChange(next);
  }

  function handleReset() {
    setOffset(0);
    onReset();
  }

  return (
    <div className="flex flex-col gap-4">
      <AnalysisFilters value={query} onApply={handleApply} onReset={handleReset} />

      {status === "loading" && <StatusMessage kind="loading" message="Loading forecast vs. actual data…" />}
      {status === "error" && (
        <StatusMessage kind="error" message={error ?? "Failed to load forecast data."} onRetry={retry} />
      )}
      {status === "success" && data && data.records.length === 0 && (
        <StatusMessage kind="empty" message="No delivery intervals fall within the selected range." />
      )}
      {status === "success" && data && data.records.length > 0 && (
        <>
          <GenerationChart records={data.records} />
          <IntervalTable
            records={data.records}
            totalCount={data.total_count}
            limit={data.limit}
            offset={data.offset}
            onPageChange={setOffset}
          />
        </>
      )}
    </div>
  );
}
