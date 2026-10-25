import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TooltipProps } from "recharts";
import type { ForecastIntervalResponse } from "../../api/types";
import { formatLondonDateTime, formatLondonTime, formatMW } from "../../lib/format";

interface GenerationChartProps {
  records: ForecastIntervalResponse[];
}

function ChartTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  const point = payload[0]?.payload as ForecastIntervalResponse | undefined;
  if (!point) return null;

  return (
    <div className="rounded-md border border-[var(--color-border)] bg-white p-3 text-xs shadow-card">
      <p className="mb-1 font-medium">{formatLondonDateTime(point.delivery_start)}</p>
      <p className="text-wind-forecast">Forecast: {formatMW(point.forecast_generation_mw)}</p>
      <p className="text-wind-actual">Actual: {formatMW(point.actual_generation_mw)}</p>
      <p className="text-[var(--color-text-secondary)]">
        Error: {point.error_mw === null ? "—" : formatMW(point.error_mw)}
      </p>
      <p className="text-[var(--color-text-secondary)]">
        Published: {formatLondonTime(point.forecast_publish_time)}
      </p>
    </div>
  );
}

export function GenerationChart({ records }: GenerationChartProps) {
  const missingActualCount = records.filter((r) => r.actual_generation_mw === null).length;
  const missingForecastCount = records.filter((r) => r.forecast_generation_mw === null).length;

  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-card">
      <p className="sr-only">
        Chart of forecast versus actual wind generation for {records.length} delivery intervals.{" "}
        {missingActualCount} intervals are missing an actual value and {missingForecastCount} are missing
        a forecast; those points are not drawn as zero.
      </p>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={records} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e5ea" />
          <XAxis
            dataKey="delivery_start"
            tickFormatter={(value: string) => formatLondonTime(value)}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            tick={{ fontSize: 11 }}
            label={{ value: "Generation (MW)", angle: -90, position: "insideLeft", fontSize: 11 }}
          />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="forecast_generation_mw"
            name="Forecast"
            stroke="#0f9b8e"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="actual_generation_mw"
            name="Actual"
            stroke="#2f8f4e"
            strokeWidth={2}
            strokeDasharray="4 2"
            dot={false}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
