import { useState } from "react";
import type { AnalysisMode } from "../../api/types";

export interface AnalysisFiltersValue {
  startDate: string;
  endDate: string;
  mode: AnalysisMode;
  asOf: string;
}

interface AnalysisFiltersProps {
  value: AnalysisFiltersValue;
  onApply: (value: AnalysisFiltersValue) => void;
  onReset: () => void;
}

export function AnalysisFilters({ value, onApply, onReset }: AnalysisFiltersProps) {
  const [draft, setDraft] = useState(value);
  const [validationError, setValidationError] = useState<string | null>(null);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (draft.endDate <= draft.startDate) {
      setValidationError("End date must be after start date.");
      return;
    }
    if (draft.mode === "as_of" && !draft.asOf) {
      setValidationError("As-of timestamp is required for as-of analysis.");
      return;
    }
    setValidationError(null);
    onApply(draft);
  }

  function handleReset() {
    setValidationError(null);
    onReset();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-wrap items-end gap-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-card"
      aria-label="Analysis filters"
    >
      <div className="flex flex-col gap-1">
        <label htmlFor="start-date" className="text-xs font-medium text-[var(--color-text-secondary)]">
          Start date
        </label>
        <input
          id="start-date"
          type="date"
          value={draft.startDate}
          onChange={(e) => setDraft({ ...draft, startDate: e.target.value })}
          className="rounded-md border border-[var(--color-border)] px-2 py-1.5 text-sm"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="end-date" className="text-xs font-medium text-[var(--color-text-secondary)]">
          End date
        </label>
        <input
          id="end-date"
          type="date"
          value={draft.endDate}
          onChange={(e) => setDraft({ ...draft, endDate: e.target.value })}
          className="rounded-md border border-[var(--color-border)] px-2 py-1.5 text-sm"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="mode" className="text-xs font-medium text-[var(--color-text-secondary)]">
          Analysis mode
        </label>
        <select
          id="mode"
          value={draft.mode}
          onChange={(e) => setDraft({ ...draft, mode: e.target.value as AnalysisMode })}
          className="rounded-md border border-[var(--color-border)] px-2 py-1.5 text-sm"
        >
          <option value="decision_time">Decision-time (day-ahead cutoff)</option>
          <option value="as_of">As-of (custom timestamp)</option>
        </select>
      </div>

      {draft.mode === "as_of" && (
        <div className="flex flex-col gap-1">
          <label htmlFor="as-of" className="text-xs font-medium text-[var(--color-text-secondary)]">
            As-of (UTC)
          </label>
          <input
            id="as-of"
            type="datetime-local"
            value={draft.asOf}
            onChange={(e) => setDraft({ ...draft, asOf: e.target.value })}
            className="rounded-md border border-[var(--color-border)] px-2 py-1.5 text-sm"
          />
        </div>
      )}

      <div className="flex gap-2">
        <button
          type="submit"
          className="rounded-md bg-teal-600 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-teal-700"
        >
          Apply
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="rounded-md border border-[var(--color-border)] px-4 py-1.5 text-sm font-medium text-[var(--color-text-primary)] transition hover:border-teal-500"
        >
          Reset
        </button>
      </div>

      {validationError && (
        <p role="alert" className="w-full text-sm text-red-700">
          {validationError}
        </p>
      )}
    </form>
  );
}
