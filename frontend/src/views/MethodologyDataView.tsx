import { getMetadata } from "../api/endpoints";
import { useApiResource } from "../hooks/useApiResource";
import { StatusMessage } from "../components/status/StatusMessage";
import { formatLondonDateTime } from "../lib/format";

export function MethodologyDataView() {
  const { status, data, error, retry } = useApiResource((signal) => getMetadata(signal), []);

  if (status === "loading") {
    return <StatusMessage kind="loading" message="Loading methodology and data status…" />;
  }
  if (status === "error" || !data) {
    return (
      <StatusMessage kind="error" message={error ?? "Failed to load metadata."} onRetry={retry} />
    );
  }

  return (
    <div className="flex flex-col gap-6 text-sm leading-relaxed text-[var(--color-text-primary)]">
      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-card">
        <h2 className="mb-2 text-base font-semibold">Data sources</h2>
        <p>
          Actual wind generation comes from Elexon&apos;s <strong>FUELHH</strong> dataset, filtered to{" "}
          <code>fuelType = WIND</code>. Forecast wind generation comes from Elexon&apos;s{" "}
          <strong>WINDFOR</strong> dataset. Both are public, unauthenticated endpoints.
        </p>
        <p className="mt-2">
          Generation unit: <strong>{data.generation_unit}</strong>. Actual delivery intervals are{" "}
          {data.actual_interval_resolution_minutes} minutes; forecast delivery intervals are{" "}
          {data.forecast_interval_resolution_minutes} minutes. {data.timezone_note}
        </p>
      </section>

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-card">
        <h2 className="mb-2 text-base font-semibold">startTime vs. publishTime</h2>
        <p>
          <code>startTime</code> identifies the delivery interval a generation figure applies to.{" "}
          <code>publishTime</code> identifies when a forecast vintage was published. A forecast is uniquely
          identified by the combination of the two, not by delivery time alone -- the same half-hour can
          have many forecast vintages published at different times.
        </p>
      </section>

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-card">
        <h2 className="mb-2 text-base font-semibold">Decision cutoff methodology</h2>
        <p>{data.decision_cutoff_methodology}</p>
      </section>

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-card">
        <h2 className="mb-2 text-base font-semibold">Accuracy metrics</h2>
        <ul className="list-disc space-y-1 pl-5">
          <li>MAE: mean absolute error, average |forecast - actual|.</li>
          <li>RMSE: root mean squared error, penalizes large errors more heavily.</li>
          <li>Bias: mean(forecast - actual); positive means forecasts ran high on average.</li>
        </ul>
      </section>

      <section className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-amber-900 shadow-card">
        <h2 className="mb-2 text-base font-semibold">What procurement exposure is not</h2>
        <p>
          Wind shortfall and surplus describe a deviation between a selected forecast and actual wind
          generation only. They are not the utility&apos;s verified additional electricity purchase volume
          and not a financial cost estimate -- no market price or demand data is in scope for this
          analysis.
        </p>
      </section>

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-card">
        <h2 className="mb-2 text-base font-semibold">Known limitations</h2>
        <ul className="list-disc space-y-1 pl-5">
          {data.limitations.map((limitation) => (
            <li key={limitation}>{limitation}</li>
          ))}
        </ul>
        <p className="mt-3 text-[var(--color-text-secondary)]">
          Source data last loaded:{" "}
          {data.source_loaded_at ? formatLondonDateTime(data.source_loaded_at) : "not yet loaded"}.
          {data.source_load_error && ` Last error: ${data.source_load_error}`}
        </p>
      </section>
    </div>
  );
}
