import { RefreshCw } from "lucide-react";
import { formatLondonDateTime } from "../../lib/format";

interface TopBarProps {
  periodLabel: string;
  sourceLoadedAt: string | null;
  sourceLoadError: string | null;
  onRefresh: () => void;
  refreshing: boolean;
}

export function TopBar({ periodLabel, sourceLoadedAt, sourceLoadError, onRefresh, refreshing }: TopBarProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-4">
      <div>
        <h1 className="text-sm font-semibold text-[var(--color-text-primary)]">{periodLabel}</h1>
        <p className="text-xs text-[var(--color-text-secondary)]">
          {sourceLoadError
            ? `Data issue: ${sourceLoadError}`
            : sourceLoadedAt
              ? `Source data refreshed ${formatLondonDateTime(sourceLoadedAt)} (Europe/London)`
              : "Source data not yet loaded"}
        </p>
      </div>
      <button
        type="button"
        onClick={onRefresh}
        disabled={refreshing}
        className="flex items-center gap-2 rounded-md border border-[var(--color-border)] bg-white px-3 py-1.5 text-sm font-medium text-[var(--color-text-primary)] transition hover:border-teal-500 hover:text-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} aria-hidden="true" />
        {refreshing ? "Refreshing…" : "Refresh"}
      </button>
    </header>
  );
}
