import { useCallback, useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { TopBar } from "./components/layout/TopBar";
import { OverviewView } from "./views/OverviewView";
import { ForecastAnalysisView } from "./views/ForecastAnalysisView";
import { AccuracyView } from "./views/AccuracyView";
import { MethodologyDataView } from "./views/MethodologyDataView";
import type { AnalysisFiltersValue } from "./components/filters/AnalysisFilters";
import { getMetadata, postRefresh } from "./api/endpoints";
import { useApiResource } from "./hooks/useApiResource";
import { formatLondonDate } from "./lib/format";

export type ViewKey = "overview" | "forecast-analysis" | "accuracy" | "methodology";

const DEFAULT_QUERY: AnalysisFiltersValue = {
  startDate: "2026-01-01",
  endDate: "2026-02-01",
  mode: "decision_time",
  asOf: "",
};

export default function App() {
  const [activeView, setActiveView] = useState<ViewKey>("overview");
  const [query, setQuery] = useState<AnalysisFiltersValue>(DEFAULT_QUERY);
  const [refreshToken, setRefreshToken] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const { data: metadata } = useApiResource((signal) => getMetadata(signal), [refreshToken]);

  const handleReset = useCallback(() => setQuery(DEFAULT_QUERY), []);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await postRefresh();
    } catch {
      // The refresh cooldown/unavailability is surfaced by the next
      // metadata/overview fetch's own error state, not here.
    } finally {
      setRefreshing(false);
      setRefreshToken((token) => token + 1);
    }
  }

  const periodLabel = `${formatLondonDate(`${query.startDate}T00:00:00Z`)} – ${formatLondonDate(
    `${query.endDate}T00:00:00Z`
  )} (${query.mode === "decision_time" ? "Decision-time" : "As-of"} analysis)`;

  return (
    <div className="flex h-screen flex-col bg-[var(--color-canvas)] md:flex-row">
      <Sidebar activeView={activeView} onSelectView={setActiveView} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          periodLabel={periodLabel}
          sourceLoadedAt={metadata?.source_loaded_at ?? null}
          sourceLoadError={metadata?.source_load_error ?? null}
          onRefresh={handleRefresh}
          refreshing={refreshing}
        />
        <main className="flex-1 overflow-y-auto p-6">
          {activeView === "overview" && <OverviewView query={query} refreshToken={refreshToken} />}
          {activeView === "forecast-analysis" && (
            <ForecastAnalysisView
              query={query}
              onQueryChange={setQuery}
              onReset={handleReset}
              refreshToken={refreshToken}
            />
          )}
          {activeView === "accuracy" && (
            <AccuracyView query={query} onQueryChange={setQuery} onReset={handleReset} refreshToken={refreshToken} />
          )}
          {activeView === "methodology" && <MethodologyDataView />}
        </main>
      </div>
    </div>
  );
}
