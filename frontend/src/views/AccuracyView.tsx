import { getAccuracy } from "../api/endpoints";
import { useApiResource } from "../hooks/useApiResource";
import { AccuracySummary } from "../components/accuracy/AccuracySummary";
import { StatusMessage } from "../components/status/StatusMessage";
import { AnalysisFilters, type AnalysisFiltersValue } from "../components/filters/AnalysisFilters";

interface AccuracyViewProps {
  query: AnalysisFiltersValue;
  onQueryChange: (value: AnalysisFiltersValue) => void;
  onReset: () => void;
  refreshToken: number;
}

export function AccuracyView({ query, onQueryChange, onReset, refreshToken }: AccuracyViewProps) {
  const { status, data, error, retry } = useApiResource(
    (signal) =>
      getAccuracy(
        { startDate: query.startDate, endDate: query.endDate, mode: query.mode, asOf: query.asOf || undefined },
        signal
      ),
    [query.startDate, query.endDate, query.mode, query.asOf, refreshToken]
  );

  return (
    <div className="flex flex-col gap-4">
      <AnalysisFilters value={query} onApply={onQueryChange} onReset={onReset} />

      {status === "loading" && <StatusMessage kind="loading" message="Computing accuracy metrics…" />}
      {status === "error" && (
        <StatusMessage kind="error" message={error ?? "Failed to load accuracy metrics."} onRetry={retry} />
      )}
      {status === "success" && data && <AccuracySummary accuracy={data} />}
    </div>
  );
}
