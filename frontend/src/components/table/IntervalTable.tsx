import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight } from "lucide-react";
import type { ForecastIntervalResponse, IntervalStatus } from "../../api/types";
import { formatLondonDateTime, formatLondonTime, formatMW, formatSignedMW } from "../../lib/format";

type SortKey = "delivery_start" | "forecast_generation_mw" | "actual_generation_mw" | "error_mw";

const STATUS_LABEL: Record<IntervalStatus, string> = {
  matched: "Matched",
  forecast_unavailable: "Forecast not available by cutoff",
  actual_unavailable: "Actual not yet available",
  both_unavailable: "No data",
};

const STATUS_CLASS: Record<IntervalStatus, string> = {
  matched: "bg-emerald-50 text-emerald-700",
  forecast_unavailable: "bg-amber-50 text-amber-700",
  actual_unavailable: "bg-sky-50 text-sky-700",
  both_unavailable: "bg-slate-100 text-slate-500",
};

interface IntervalTableProps {
  records: ForecastIntervalResponse[];
  totalCount: number;
  limit: number;
  offset: number;
  onPageChange: (offset: number) => void;
}

export function IntervalTable({ records, totalCount, limit, offset, onPageChange }: IntervalTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("delivery_start");
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = useMemo(() => {
    const copy = [...records];
    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (av === null && bv === null) return 0;
      if (av === null) return 1;
      if (bv === null) return -1;
      return av < bv ? -1 : av > bv ? 1 : 0;
    });
    return sortAsc ? copy : copy.reverse();
  }, [records, sortKey, sortAsc]);

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortAsc((asc) => !asc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  }

  function headerButton(key: SortKey, label: string) {
    const isActive = key === sortKey;
    return (
      <button
        type="button"
        onClick={() => toggleSort(key)}
        className="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-[var(--color-text-secondary)] hover:text-teal-700"
        aria-sort={isActive ? (sortAsc ? "ascending" : "descending") : "none"}
      >
        {label}
        {isActive && (sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
      </button>
    );
  }

  const page = Math.floor(offset / limit) + 1;
  const pageCount = Math.max(1, Math.ceil(totalCount / limit));

  return (
    <div className="overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] shadow-card">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-slate-50">
              <th className="px-4 py-2 text-left">{headerButton("delivery_start", "Delivery (UK time)")}</th>
              <th className="px-4 py-2 text-left">{headerButton("forecast_generation_mw", "Forecast")}</th>
              <th className="px-4 py-2 text-left">{headerButton("actual_generation_mw", "Actual")}</th>
              <th className="px-4 py-2 text-left">{headerButton("error_mw", "Error")}</th>
              <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[var(--color-text-secondary)]">
                Published
              </th>
              <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[var(--color-text-secondary)]">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((record) => (
              <tr key={record.delivery_start} className="border-b border-[var(--color-border)] last:border-0">
                <td className="px-4 py-2">{formatLondonDateTime(record.delivery_start)}</td>
                <td className="px-4 py-2">{formatMW(record.forecast_generation_mw)}</td>
                <td className="px-4 py-2">{formatMW(record.actual_generation_mw)}</td>
                <td className="px-4 py-2">{formatSignedMW(record.error_mw)}</td>
                <td className="px-4 py-2 text-[var(--color-text-secondary)]">
                  {formatLondonTime(record.forecast_publish_time)}
                </td>
                <td className="px-4 py-2">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_CLASS[record.status]}`}>
                    {STATUS_LABEL[record.status]}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-[var(--color-border)] px-4 py-2 text-xs text-[var(--color-text-secondary)]">
        <span>
          Page {page} of {pageCount} &middot; {totalCount} intervals
        </span>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => onPageChange(Math.max(0, offset - limit))}
            disabled={offset === 0}
            aria-label="Previous page"
            className="rounded-md border border-[var(--color-border)] p-1 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => onPageChange(offset + limit)}
            disabled={offset + limit >= totalCount}
            aria-label="Next page"
            className="rounded-md border border-[var(--color-border)] p-1 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
