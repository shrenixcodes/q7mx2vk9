# WindLens demo runbook

Target total length: **~9 minutes**, leaving a margin under the 10-minute limit. Two
unlisted-YouTube-ready parts, recorded as one continuous take or two clips stitched
together -- either works for submission as long as the combined video is one URL.

Before recording, re-read `docs/demo-feature-audit.md`: it tells you exactly what is
genuinely implemented and what is not. Don't describe anything beyond that list.

**If no public URL exists yet when you record:** use `localhost` (via
`docker compose up`, or `uvicorn`/`vite dev` run directly) and say on camera that
you're demoing the local development build pending deployment. Do not imply it's the
production deployment if it isn't. Swap in the real URL once it exists -- nothing else
in this runbook changes.

---

## Part 1 -- Customer-facing pitch (~4:30)

Audience: a UK energy utility's day-ahead electricity procurement team. No invented
customer names, endorsements, or financial savings anywhere in this part.

**0:00-0:30 -- Introduction**
- State the problem: wind generation forecasts drive day-ahead purchasing decisions,
  and forecast error directly creates procurement risk.
- Introduce WindLens by name and its intended user (a procurement/trading analyst).

**0:30-1:20 -- Dashboard overview**
- Open the Overview view. Point out the January 2026 analysis period shown in the top
  bar.
- Read the actual MAE, RMSE, bias, and coverage KPI cards off the screen -- don't
  recite numbers from memory or from this script.

**1:20-2:30 -- Forecast analysis**
- Switch to Forecast Analysis. Let the chart load with real data.
- Point at a specific delivery interval's forecast line vs. actual line and explain
  what the gap means.
- Open the interval table, point at the "Published" column, and explain that this is
  when that specific forecast number became available -- not the delivery time.
- Change the date range or analysis mode in the filter form and show the chart/table
  update to a new real result (this is a genuine feature, not staged).

**2:30-3:30 -- Forecast accuracy**
- Switch to Accuracy & Backtesting.
- Explain MAE and RMSE in plain terms using the actual values on screen.
- Explain bias's sign: if it's positive, say forecasts have been running high (an
  overestimation risk -- the "wind shortfall" case, where less wind showed up than
  planned for).

**3:30-4:30 -- Business value and limitations**
- Explain how a quantified, auditable error history lets a procurement team weight a
  given day's forecast appropriately, instead of treating every forecast as equally
  reliable.
- State clearly: this measures a generation deviation, not a verified electricity
  purchase volume or a financial savings figure -- no price or demand data is in scope.
- Close on the value of a transparent, data-driven methodology over a black box.

---

## Part 2 -- Technical lead walkthrough (~4:30)

Audience: a technical reviewer assessing architecture, methodology, and code quality.

**4:30-5:10 -- Repository structure**
- Show the repo root: `frontend/`, `backend/`, `docs/`, `docker-compose.yml`,
  `render.yaml`, `README.md`.
- Briefly open `backend/app/` (ingestion / analytics / api / services) and
  `frontend/src/` (api / components / views) to show the module boundaries.

**5:10-6:00 -- Architecture and data flow**
- Walk through the README's architecture diagram: Elexon -> ingestion/normalization ->
  in-memory `AnalysisService` -> FastAPI -> React/Recharts.
- Mention the file cache is a performance optimization only, never a system of record
  (point at `backend/app/ingestion/cache.py` and the README's wording on this).

**6:00-7:00 -- Forecast-vintage methodology**
- Open `backend/app/analytics/selection.py`.
- Explain `startTime` (delivery) vs. `publishTime` (vintage) using the real field
  names.
- Point at `select_latest_eligible_forecast` and explain the `publish_time <= cutoff`
  guard -- this is what prevents look-ahead bias in decision-time backtests.
- Mention the real resolution mismatch you found: WINDFOR is hourly, FUELHH is
  half-hourly, handled via `hour_bucket` alignment in
  `backend/app/core/time_grid.py`.

**7:00-7:50 -- Accuracy and data quality**
- Open `backend/app/analytics/metrics.py` and `exposure.py`.
- Explain MAE/RMSE/bias definitions and the MAPE near-zero-denominator exclusion
  policy.
- Explain why wind shortfall/surplus are deviation metrics, not cost estimates.

**7:50-8:40 -- Engineering practices**
- Show one backend test file (e.g. `tests/analytics/test_backtest.py`, the
  look-ahead-bias test) and one frontend test file (e.g.
  `src/hooks/useApiResource.test.tsx`, the stale-response test).
- Show `docker-compose.yml` and `.github/workflows/ci.yml`.
- Mention the startup-ingestion-as-background-task fix, and why `/health` must never
  depend on a live upstream call.

**8:40-9:00 -- Conclusion**
- State the main tradeoff: this is a single-analyst MVP (no auth, no database, no paid
  services) built for a 16-hour budget, not a multi-tenant production system.
- Name one real next step: verified production deployment with the public URLs filled
  in, and (if true at recording time) that it's still pending.

---

## Recording, uploading, and publishing

Nothing in this section has been performed for you. These are the exact manual steps.

1. **Record with OBS Studio.** Add a "Display Capture" or "Window Capture" source for
   your browser/editor, and an "Audio Input Capture" source for your microphone. Start
   Recording, run through the runbook, then Stop Recording.
2. **Save locally.** OBS writes to its configured recording folder (Settings ->
   Output -> Recording Path) as an `.mkv` or `.mp4`. Note the file path.
3. **Review before uploading.** Play the full file back. Confirm the runtime is under
   10 minutes, audio is audible throughout, and the screen is legible throughout (see
   `docs/demo-checklist.md`).
4. **Upload to YouTube Studio.** Go to studio.youtube.com -> Create -> Upload videos
   -> select your file.
5. **Set visibility to Unlisted** on the Visibility step of the upload wizard (not
   Public, not Private).
6. **Wait for processing.** YouTube Studio shows a processing progress bar; wait until
   it says the video is fully processed, not just "uploaded."
7. **Open the video's URL in an incognito/private window** (signed out of any Google
   account) to confirm it plays without requiring sign-in or an invite.
8. **Confirm link-only access works** -- an Unlisted video should be viewable by
   anyone with the URL, and should not appear in search or on your channel page.
   Verify both in that same incognito window.

Once you have the real video URL, add it to `docs/submission-manifest.md` and to the
README, replacing the `PENDING` placeholder.
