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
render.yaml   Render blueprint for the backend (see Deployment below)
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
| `ENVIRONMENT` | backend | `development` (default) or `production`; informational, does not itself relax any check. |

None of these are secrets. The Elexon API requires no key, so there is no API credential
to configure anywhere in this stack.

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

## Deployment

**Current status: not yet deployed.** The GitHub repository has been connected to a
Vercel project through the Vercel website, but no production deployment has completed
or been verified from this environment -- no Vercel CLI, Render CLI, or `gh` CLI was
available here, so nothing below is a claim of a live URL.

- Frontend (Vercel): **`<VERCEL_URL_NOT_YET_VERIFIED>`**
- Backend (Render): **`<RENDER_URL_NOT_YET_VERIFIED>`**

Fill in the two placeholders above once each service is live, then re-run the
"Production verification checklist" at the end of this section.

### Vercel dashboard settings to verify

In the Vercel project's **Settings**:

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | Vite (should auto-detect once Root Directory is set) |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` (default) |

In **Settings -> Environment Variables**, add for Production (and Preview, if you want
previews to hit the same backend):

| Key | Value |
|---|---|
| `VITE_API_BASE_URL` | the Render backend URL, e.g. `https://windlens-backend.onrender.com` (no trailing slash) |

No `vercel.json` is committed: the app has no client-side routes needing a rewrite rule,
and every other setting above is expressible through the dashboard, so a repo-level
config file would just risk conflicting with it.

### Render: deploying the backend

A `render.yaml` blueprint is committed at the repo root. It was written against this
repository's actual module path (`app.main:app`) and `backend/requirements.txt`, but
**has not been exercised against a real Render deployment from this environment** --
treat it as a starting point and verify the first deploy manually.

**Via the blueprint:** Render dashboard -> New -> Blueprint -> select this repo. Render
will read `render.yaml` and propose a `windlens-backend` web service on the free plan
with root directory `backend`.

**Manual steps (equivalent), if you'd rather configure by hand:**

1. New -> Web Service -> connect this repo.
2. Root Directory: `backend`.
3. Runtime: Python 3.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   (Render injects `$PORT`; the Dockerfile and this command both honor it -- nothing in
   this app hardcodes port 8000 for production.)
6. Instance Type: Free.
7. Environment variable `CORS_ALLOWED_ORIGINS` = the exact Vercel origin, e.g.
   `https://windlens.vercel.app` (no trailing slash, no wildcard).
8. Health Check Path: `/health`.

Render's free tier sleeps after inactivity. The app's startup ingestion fetch runs as a
background task and does **not** block `/health` or any other route from responding on
a cold start -- this was verified locally by hitting `/health` immediately after
process start and confirming it returned `200` while the Elexon fetch was still
in flight in the background (dashboard endpoints returned a clean `503
{"detail": "ingestion data has not been loaded yet"}` until that fetch finished,
instead of hanging or fabricating data).

### Production verification checklist

Checks completed **locally** (not against a public URL, since none exists yet):

- [x] Backend starts and `/health` responds without waiting on Elexon.
- [x] `/api/v1/metadata`, `/api/v1/overview`, `/api/v1/accuracy` return real, correctly
      typed data for live January 2026 Elexon data.
- [x] `/api/v1/forecasts` paginates and respects `limit`/`offset`.
- [x] An invalid date range (`end_date <= start_date`) returns a clean `400`, no traceback.
- [x] CORS: an allowed origin gets `Access-Control-Allow-Origin`; a disallowed origin
      (`https://evil.example`) gets no CORS header at all.
- [x] Dashboard renders real KPIs, chart, and table from the live API, across all four
      views, in a browser pointed at `localhost`.
- [x] No `localhost` string appears in the built `frontend/dist` bundle.

Outstanding -- **cannot be completed without the two placeholder URLs above**, and
require you (or a future session with deployment access) to run them:

- [ ] Deployed frontend loads at the Vercel URL without sign-in.
- [ ] Deployed backend's `/health` responds at the Render URL.
- [ ] Deployed frontend successfully calls the deployed backend (check the Network tab
      for the actual request origin and response).
- [ ] CORS on the *deployed* backend allows the *deployed* frontend's exact origin and
      rejects others.
- [ ] Backend responds correctly after Render's free-tier sleep/wake cycle.
- [ ] January 2026 date filters work end-to-end on the public URLs.

If you can share the two URLs once they exist, the remaining checks can be completed in
a follow-up session.

## Implementation status

Ingestion, the backtesting engine, the FastAPI API, and the React dashboard described
above are implemented and tested against live Elexon data. Not yet built: CI-driven
deployment, and any analysis beyond wind generation forecast accuracy (no price, demand,
or other-fuel-type analytics).
