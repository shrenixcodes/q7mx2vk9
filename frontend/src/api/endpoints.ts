import { apiClient } from "./client";
import type {
  AccuracyResponse,
  AnalysisQuery,
  ForecastsResponse,
  MetadataResponse,
  OverviewResponse,
  RefreshResponse,
} from "./types";

function analysisParams(query: AnalysisQuery) {
  return {
    start_date: query.startDate,
    end_date: query.endDate,
    mode: query.mode,
    as_of: query.asOf,
  };
}

export function getOverview(query: AnalysisQuery, signal?: AbortSignal): Promise<OverviewResponse> {
  return apiClient.request<OverviewResponse>("/api/v1/overview", { params: analysisParams(query), signal });
}

export function getForecasts(
  query: AnalysisQuery,
  paging: { limit: number; offset: number },
  signal?: AbortSignal
): Promise<ForecastsResponse> {
  return apiClient.request<ForecastsResponse>("/api/v1/forecasts", {
    params: { ...analysisParams(query), limit: paging.limit, offset: paging.offset },
    signal,
  });
}

export function getAccuracy(query: AnalysisQuery, signal?: AbortSignal): Promise<AccuracyResponse> {
  return apiClient.request<AccuracyResponse>("/api/v1/accuracy", { params: analysisParams(query), signal });
}

export function getMetadata(signal?: AbortSignal): Promise<MetadataResponse> {
  return apiClient.request<MetadataResponse>("/api/v1/metadata", { signal });
}

export function postRefresh(signal?: AbortSignal): Promise<RefreshResponse> {
  return apiClient.request<RefreshResponse>("/api/v1/refresh", { method: "POST", signal });
}
