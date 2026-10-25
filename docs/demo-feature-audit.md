# WindLens feature audit

Compiled 2026-10-25, at the end of Phase 8, for demo preparation. "Verified" means I ran
something and observed the result in this session (a test, a live API call, or a
browser interaction) -- not that the source code merely exists.

## Commands run for this audit

```bash
cd backend && pytest -q
# -> 68 passed

cd frontend && npx tsc -b && npm test && npm run build
# -> tsc: no errors
# -> vitest: 8 files, 28 passed
# -> vite build: succeeds, dist/index.html + dist/assets/*.{js,css} produced,
#    no "localhost" string present in the built JS bundle

docker compose config
# -> valid YAML, resolves both services correctly
```

## Feature-by-feature status

| Feature | Status | Evidence |
|---|---|---|
| FUELHH actual wind generation ingestion | **Verified** | Live call to `data.elexon.co.uk` during this session normalized 1,489 `WIND`-only records for Jan 2026; `tests/ingestion/test_normalize_actuals.py` covers filtering, invalid timestamps, nonnumeric generation, and duplicate-revision handling. |
| WINDFOR forecast ingestion + vintage preservation | **Verified** | Same live run normalized 44,384 forecast records across the Jan-2026 + lookback window; `tests/ingestion/test_normalize_forecasts.py::test_retains_multiple_vintages_for_same_delivery_interval` asserts two distinct `publishTime` vintages survive for one delivery hour. |
| January 2026 delivery-period analysis | **Verified** | `/api/v1/overview?start_date=2026-01-01&end_date=2026-02-01` returned `expected_intervals: 1488` (the correct half-hour count for a 31-day month) against live data. |
| Forecast selection by decision cutoff | **Verified** | `tests/analytics/test_backtest.py::test_decision_time_mode_never_leaks_future_forecast` and `test_selection.py` assert a forecast published after cutoff is never selected; live table output showed a consistent `09:30` publish time preceding every delivery interval's default 11:00-the-day-before cutoff. |
| MAE, RMSE, bias | **Verified** | `tests/analytics/test_metrics_and_exposure.py::test_exact_mae_rmse_bias` asserts exact arithmetic; live `/api/v1/accuracy` for the first week of Jan 2026 returned `mae: 2157.5`, `rmse: 2594.6`, `bias: 1983.7` (MW) against real data. |
| Data coverage / missing-interval reporting | **Verified** | `CoverageStats` fields (`expected_intervals`, `matched_intervals`, `coverage_percent`) are populated correctly in both unit tests and the live `/overview` response; the UI renders "Coverage" and per-row status badges (`Matched`, `Actual not yet available`, etc.). |
| Forecast-vs-actual chart | **Verified** | `GenerationChart` rendered real data in-browser during this session (confirmed via accessibility-tree text extraction of the rendered SVG/legend and the chart's screen-reader summary text, not just that the component file exists). |
| Forecast publication timestamps | **Verified** | Visible in the interval table's "Published" column and in the API's `forecast_publish_time` field; confirmed in the live browser session. |
| Delivery interval table + filters | **Verified** | Live session showed "Page 1 of 3 - 1488 intervals" with working pagination, sorting, and the start/end/mode/as-of filter form submitting real new requests. |
| Methodology and limitations view | **Verified** | Live session rendered the full methodology text (FUELHH/WINDFOR description, cutoff assumption disclosure, the hourly-vs-half-hourly resolution-mismatch limitation) from `/api/v1/metadata`. |
| Docker Compose setup | **Partially verified** | `docker compose config` validates the YAML and both Dockerfiles' build contexts. **`docker compose build`/`up` have not been executed** in any session so far -- the Docker CLI is present on this machine but the Docker Desktop engine itself is not running here. This is an environment limitation, not a code defect; it should be re-run on a machine with a live Docker daemon before the demo if Docker is to be shown running. |
| Backend automated tests | **Verified** | `pytest -q` -> 68 passed, just now, in this session. |
| Frontend automated tests | **Verified** | `npm test` (vitest) -> 28 passed, just now, in this session. |
| Public deployment | **Not verified** | The GitHub repository is confirmed public (`GET https://api.github.com/repos/shrenixcodes/q7mx2vk9` returned `"private": false`, checked in this session). **No Vercel frontend URL or Render backend URL has been confirmed** -- this environment has no Vercel CLI, Render CLI, or dashboard access, and none has been supplied. |

## Critical issue for the demo

**There is currently no confirmed public deployment.** This is the one issue that would
make a "show the live product" demo misleading if not handled honestly: there is no
verified public URL to point a camera at yet.

This cannot be fixed from within this repository or this session -- it requires someone
with Vercel/Render dashboard access to complete the deployments described in the
README's Deployment section and report back the two URLs.

**Workaround, not a fix:** the demo can be recorded against the local development
environment (`docker compose up`, or `uvicorn` + `vite dev` directly) instead of a
public URL, as long as the presenter says so on camera rather than implying it's the
production deployment. The runbook and script in this `docs/` folder are written so
they work either way -- substitute the real public URL in for `localhost` once it
exists, nothing else in the script changes.

No other critical issues were found. All analytical and UI features above are
genuinely implemented and were exercised, not merely present as unused code.
