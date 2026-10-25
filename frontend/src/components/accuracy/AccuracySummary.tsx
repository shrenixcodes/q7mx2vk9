import { AlertTriangle } from "lucide-react";
import type { AccuracyResponse } from "../../api/types";
import { formatMW, formatPercent, formatSignedMW } from "../../lib/format";
import { KpiCard } from "../kpi/KpiCard";
import { KpiRow } from "../kpi/KpiRow";

interface AccuracySummaryProps {
  accuracy: AccuracyResponse;
}

export function AccuracySummary({ accuracy }: AccuracySummaryProps) {
  const noSamples = accuracy.sample_count === 0;

  return (
    <div className="flex flex-col gap-4">
      <KpiRow>
        <KpiCard
          label="MAE"
          value={formatMW(accuracy.mae)}
          description="Mean absolute error"
          helpText="Average absolute difference between forecast and actual wind generation, across matched intervals."
          unavailable={noSamples}
        />
        <KpiCard
          label="RMSE"
          value={formatMW(accuracy.rmse)}
          description="Root mean squared error"
          helpText="Penalizes large errors more heavily than MAE; always >= MAE."
          unavailable={noSamples}
        />
        <KpiCard
          label="Bias"
          value={formatSignedMW(accuracy.bias)}
          description={
            accuracy.bias === null
              ? "Mean forecast minus actual"
              : accuracy.bias > 0
                ? "Forecast tends to overestimate"
                : accuracy.bias < 0
                  ? "Forecast tends to underestimate"
                  : "No systematic bias"
          }
          helpText="Mean(forecast - actual). Positive means forecasts ran high on average."
          unavailable={noSamples}
        />
        <KpiCard
          label="Coverage"
          value={formatPercent(accuracy.coverage_percent)}
          description={`${accuracy.sample_count} matched intervals`}
          helpText="Share of expected delivery intervals with both a forecast and an actual value."
        />
      </KpiRow>

      <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-sm shadow-card">
        <p>
          MAPE:{" "}
          {accuracy.mape_percent === null ? (
            <span className="text-slate-400">not available</span>
          ) : (
            formatPercent(accuracy.mape_percent)
          )}{" "}
          <span className="text-[var(--color-text-secondary)]">
            ({accuracy.mape_excluded_low_actual_count} low-actual intervals excluded from the denominator)
          </span>
        </p>
      </div>

      {accuracy.warnings.length > 0 && (
        <ul className="flex flex-col gap-1">
          {accuracy.warnings.map((warning) => (
            <li
              key={warning}
              className="flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800"
            >
              <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0" aria-hidden="true" />
              {warning}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
