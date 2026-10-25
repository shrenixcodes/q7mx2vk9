# WindLens

WindLens is a UK energy procurement analytics tool. It compares Elexon's published
day-ahead wind generation forecasts against actual metered wind generation for January
2026, so an electricity procurement analyst can see how reliable a given forecast
vintage was *before* a purchasing decision, not with hindsight.

This project was built with assistance from Claude Code (Anthropic). All Elexon API
integration described below was verified against the live API during development.

## What it actually does

- Pulls **actual** generation from Elexon's `FUELHH` dataset, filtered to `fuelType = WIND`.
- Pulls **forecast** generation from Elexon's `WINDFOR` dataset, keeping every publish
  vintage.
- For a chosen decision cutoff, selects the latest forecast that was published *before*
  that cutoff for each delivery interval -- never a forecast from the future relative to
  the decision being evaluated.
- Computes MAE, RMSE, bias, and wind shortfall/surplus over the matched intervals, and
  reports coverage so incomplete data is visible rather than hidden.
- Serves this through a FastAPI backend and a React dashboard.

It does **not** estimate a financial cost, does not require a database, and does not
use any paid API -- Elexon's Insights Solution API is public and unauthenticated.

## Architecture

```
frontend (React + Vite)  --->  backend (FastAPI)  --->  Elexon BMRS API
     |                              |                    (FUELHH, WINDFOR)
     |                              v
     |                     in-memory analysis +
     |                     local JSON file cache
     v                     (performance only, not
  Recharts dashboard        a durable store)
```

The backend fetches and normalizes Elexon data once (on startup, or via `/refresh`),
holds the normalized actuals/forecasts in memory, and computes backtests on demand from
that in-memory data. Dashboard filter changes (date range, mode) never trigger a new
Elexon request.

## Repository structure

```
frontend/   React + TypeScript + Vite + Tailwind dashboard
backend/    FastAPI service: ingestion, analytics, API
docs/       (reserved for future design/architecture notes)
docker-compose.yml
.env.example
```

### Backend (`backend/app`)

```
core/        settings, time-grid utilities
ingestion/   Elexon HTTP client, actuals/forecasts retrieval, normalization, file cache
analytics/   forecast vintage selection, matching, accuracy metrics, exposure, backtest
services/    AnalysisService -- the one in-memory holder of normalized data
api/         FastAPI routers: health, v1/{overview,forecasts,accuracy,metadata,refresh}
```

### Frontend (`frontend/src`)

```
api/         typed fetch client + response types matching the backend schemas
hooks/       useApiResource -- shared loading/error/abort state machine
components/  layout, kpi, charts, filters, accuracy, table, status
views/       Overview, Forecast Analysis, Accuracy & Backtesting, Data & Methodology
```

## Running it locally

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

The backend fetches real Elexon data for January 2026 on startup (and the forecast
history needed to evaluate early-January decisions). This requires outbound internet
access to `data.elexon.co.uk`. Health check (`/health`) never depends on this fetch
succeeding.

### Frontend

```bash
cd frontend
cp .env.example .env   # set VITE_API_BASE_URL if not using the default
npm install
npm run dev
```

Open http://localhost:5173.

### Docker Compose

```bash
docker compose build
docker compose up
```

`docker-compose.yml` was validated with `docker compose config` during development.
**Image builds and container-to-container networking were not verified in this
environment** -- the Docker CLI was present but the Docker Desktop engine was not
running, so `docker compose build` could not complete here. Please verify
`docker compose up` on a machine with a running Docker daemon before relying on it.

## Environment variables

See `.env.example` (root, for Compose) and `frontend/.env.example` (for `vite dev`
outside Docker).

| Variable | Where | Purpose |
|---|---|---|
| `CORS_ALLOWED_ORIGINS` | backend | Comma-separated allow-list of origins. No wildcard default. |
| `VITE_API_BASE_URL` | frontend | Base URL the browser uses to call the backend. |
| `ELEXON_CACHE_DIR` | backend | Where the performance-only JSON cache is written. |

## API (`/api/v1`)

| Endpoint | Purpose |
|---|---|
| `GET /health`, `GET /api/v1/health` | Liveness only; never calls Elexon. |
| `GET /api/v1/overview` | Summary KPIs for a date range + mode. |
| `GET /api/v1/forecasts` | Paginated per-interval forecast/actual records. |
| `GET /api/v1/accuracy` | MAE/RMSE/bias/MAPE + coverage. |
| `GET /api/v1/metadata` | Units, timezone, methodology, known limitations. |
| `POST /api/v1/refresh` | Re-fetches the configured range from Elexon. Rate-limited to one attempt per 60s. |

All four analysis endpoints take `start_date`, `end_date`, `mode`
(`decision_time`/`as_of`), and `as_of` (required when `mode=as_of`).

## Methodology

- **Decision-time mode**: for each delivery interval, selects the latest WINDFOR
  forecast published before an assumed cutoff of **11:00 Europe/London the day before
  delivery**. This is a stated assumption for this assignment, not a verified official
  market rule -- it approximates a UK day-ahead procurement decision point.
- **As-of mode**: applies one caller-supplied cutoff timestamp to every interval in the
  range, for reconstructing "what was known by time X" across a whole period.
- Forecasts are never selected from after the applicable cutoff, in either mode.
- **Resolution mismatch (verified live, 2026-10-25)**: WINDFOR forecasts are hourly;
  FUELHH actuals are half-hourly. The two half-hour actual intervals inside a clock hour
  are compared against that hour's single forecast value.
- **Wind shortfall/surplus** (`max(forecast-actual, 0)` / `max(actual-forecast, 0)`)
  describe a generation deviation only. They are not a verified additional electricity
  purchase volume and not a financial cost estimate -- no price or demand data is in
  scope.
- Missing actuals or missing eligible forecasts are reported as such, never
  substituted with zero or a later value.

## Tests

```bash
# backend
cd backend && pytest -q
# 68 tests: ingestion normalization/client/cache/retrieval, analytics
# selection/matching/metrics/backtest, API endpoints with mocked ingestion.

# frontend
cd frontend && npm test
# 28 tests: components, the shared data-fetching hook (including stale-response
# rejection), and view-level loading/empty/error states with mocked API responses.
```

Both suites were executed during development and passed. Backend tests never call the
live Elexon API (HTTP is mocked with `httpx.MockTransport` / stub clients, and fixtures
under `backend/tests/fixtures/` are small real samples captured from the live API on
2026-01-10, clearly separate from synthetic edge-case data used for negative tests).

Production build:

```bash
cd frontend && npm run build   # tsc -b && vite build -- verified, succeeds
```

## Known limitations

- Decision-time cutoff is an explicit assumption (see Methodology), not a verified
  market rule.
- WINDFOR/FUELHH resolution mismatch is handled by hour-bucket alignment, not native
  half-hourly forecasts (Elexon does not publish those for WINDFOR).
- The local JSON cache is a performance optimization only; it is not durable and is not
  relied upon as the system of record. A Render-style ephemeral filesystem is fine --
  the cache just starts empty again.
- MAPE excludes intervals where actual generation is below 50 MW to avoid a
  near-zero-denominator blowup; this is a documented, not hidden, exclusion.
- Docker Compose was validated for syntax only in this environment (see above).

## Deployment (planned, not yet done)

- Frontend: Vercel -- URL: _not yet deployed_.
- Backend: Render -- URL: _not yet deployed_.

## Implementation status

Ingestion, the backtesting engine, the FastAPI API, and the React dashboard described
above are implemented and tested against live Elexon data. Not yet built: CI-driven
deployment, and any analysis beyond wind generation forecast accuracy (no price, demand,
or other-fuel-type analytics).
