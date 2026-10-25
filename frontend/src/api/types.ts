export type AnalysisMode = "decision_time" | "as_of";

export type IntervalStatus =
  | "matched"
  | "forecast_unavailable"
  | "actual_unavailable"
  | "both_unavailable";

export interface AnalysisQuery {
  startDate: string; // YYYY-MM-DD, UTC, inclusive
  endDate: string; // YYYY-MM-DD, UTC, exclusive
  mode: AnalysisMode;
  asOf?: string; // ISO 8601 UTC, required when mode === "as_of"
}

export interface OverviewResponse {
  mode: AnalysisMode;
  as_of: string | null;
  delivery_range_start: string;
  delivery_range_end: string;
  expected_intervals: number;
  matched_intervals: number;
  coverage_percent: number;
  unit: string;
  mae: number | null;
  rmse: number | null;
  bias: number | null;
  total_wind_shortfall: number | null;
  total_wind_surplus: number | null;
  source_loaded_at: string | null;
  warnings: string[];
}

export interface ForecastIntervalResponse {
  delivery_start: string;
  forecast_generation_mw: number | null;
  actual_generation_mw: number | null;
  forecast_publish_time: string | null;
  error_mw: number | null;
  wind_shortfall_mw: number | null;
  wind_surplus_mw: number | null;
  status: IntervalStatus;
}

export interface ForecastsResponse {
  mode: AnalysisMode;
  as_of: string | null;
  total_count: number;
  limit: number;
  offset: number;
  records: ForecastIntervalResponse[];
}

export interface AccuracyResponse {
  mode: AnalysisMode;
  as_of: string | null;
  sample_count: number;
  unit: string;
  mae: number | null;
  rmse: number | null;
  bias: number | null;
  mape_percent: number | null;
  mape_excluded_low_actual_count: number;
  coverage_percent: number;
  warnings: string[];
}

export interface MetadataResponse {
  datasets: string[];
  analysis_range_start: string;
  analysis_range_end: string;
  generation_unit: string;
  actual_interval_resolution_minutes: number;
  forecast_interval_resolution_minutes: number;
  timezone_note: string;
  decision_cutoff_methodology: string;
  source_loaded_at: string | null;
  source_load_error: string | null;
  limitations: string[];
}

export interface RefreshResponse {
  status: string;
  loaded_at: string | null;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}
