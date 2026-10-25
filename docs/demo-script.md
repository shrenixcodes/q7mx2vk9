# WindLens demo script

A complete spoken script for the two-part demo video. Bracketed text is a screen
action, not something to say out loud. Wherever a metric value appears as a
placeholder like `[read MAE from screen]`, read the real number visible on your
screen at that moment -- never recite a number from this document, since it may not
match what the live data shows on the day you record.

Target: ~1,000-1,100 spoken words, paced for roughly 9 minutes with natural pauses for
screen actions.

---

## Part 1 -- Customer-facing pitch

[Open the dashboard. Overview view. No sign-in screen should appear.]

Hi -- I'm going to walk you through WindLens, a forecast accuracy tool built for
day-ahead wind procurement.

Every day, a UK electricity buyer has to decide how much power to purchase, based on a
wind generation forecast. But forecasts aren't perfect, and when they're wrong, that
error becomes real procurement risk. WindLens doesn't try to improve the forecast --
it measures exactly how wrong it's been, so a procurement team can make a better
informed decision.

[Make sure you're on the Overview view, January 2026 period visible.]

This is the Overview for January 2026. At the top you can see the analysis period, and
here are four key numbers: mean absolute error is [read MAE from screen], root mean
squared error is [read RMSE from screen], bias is [read bias from screen], and data
coverage is [read coverage percent from screen]. Coverage matters because it tells you
how many delivery intervals actually have both a forecast and an actual reading to
compare -- you're never looking at a number quietly built on incomplete data.

[Switch to the Forecast Analysis view. Let the chart finish loading.]

This chart plots forecast generation against actual generation, half-hour by
half-hour, across the month. [Point at a visible gap between the two lines.] Right
here, the forecast ran well above what actually happened -- that's exactly the kind of
gap that matters to a buyer.

[Scroll to the interval table. Point at the Published column.]

Every row also shows a Published time -- when that specific forecast number became
available. That's different from the delivery time it applies to, and it matters: we
only ever use a forecast that existed before the relevant decision point. No forecast
from the future ever leaks into this analysis. You'll also notice some rows are
labeled differently -- "forecast not available" or "actual not yet available" -- rather
than just showing a blank or a zero. That distinction matters for a procurement team:
a missing number and a true zero reading mean very different things, and this tool
never quietly conflates the two.

[Change a filter -- the date range, or the analysis mode -- and let the page reload.]

And it's interactive. If I change the date range here, the chart and the table
recalculate live, from the real backend.

[Switch to the Accuracy & Backtesting view.]

On the Accuracy page: mean absolute error is the average size of the forecast miss, in
megawatts. RMSE is similar, but it penalizes large misses more heavily. And bias tells
you the direction -- [read the sign and meaning from screen] means forecasts have
tended to run high, which is the shortfall scenario a buyer needs to plan for, where
less wind shows up than the forecast promised.

I want to be upfront about scope. These numbers describe a generation deviation. They
are not a verified purchase volume, and they are not a financial savings figure --
that would require market price and demand data, which isn't part of this tool. What
WindLens gives a procurement team is something more foundational: an honest, auditable
record of how reliable a given forecast actually was, so they can weight it
accordingly, instead of treating every forecast as equally trustworthy.

That's the product side. Now let's look at how it's built.

---

## Part 2 -- Technical lead walkthrough

[Switch to the GitHub repository or your code editor, repo root visible.]

From an engineering standpoint, this is a small monorepo: a React and TypeScript
frontend, a FastAPI Python backend, a Docker Compose setup for local development, and
a GitHub Actions pipeline that runs both test suites on every push.

[Open backend/app in the editor.]

On the backend, the folder structure follows the actual data pipeline: an ingestion
layer that talks to Elexon's public API, an analytics layer that does the forecast
evaluation, and a thin API layer on top of both.

[Open the README's architecture section.]

Data flows from two Elexon datasets -- FUELHH for actual wind generation, filtered to
the WIND fuel type, and WINDFOR for forecasts -- through normalization, into an
in-memory store the API reads from. There's a small file cache for performance, but
it's explicitly not the system of record -- if it's wiped on a restart, the app just
re-fetches from Elexon.

[Open backend/app/analytics/selection.py.]

The core methodology question is forecast-vintage selection. Elexon's forecast data
carries two timestamps: startTime, the delivery interval a number applies to, and
publishTime, when that forecast was actually published. For every delivery interval,
this function finds the latest forecast whose publish time is before a decision
cutoff -- and it's structurally incapable of returning anything published after that
cutoff. That's what keeps a backtest honest: no future information leaking into a
decision meant to represent the past.

One thing I found while verifying this against the live API: WINDFOR forecasts are
published hourly, while the actual generation data is half-hourly. So two half-hour
readings share one hourly forecast value -- that mismatch is handled explicitly in the
code, not glossed over.

[Open a backend test file, e.g. tests/analytics/test_backtest.py.]

On testing: there's a dedicated test asserting that a forecast published after the
cutoff is never selected -- that's the look-ahead-bias guard, enforced by an automated
test, not just a comment.

[Open frontend/src/hooks/useApiResource.test.tsx.]

On the frontend, there's a test confirming a slow, stale API response never overwrites
a newer one if the user changes filters quickly -- so you never see a result that
doesn't match your current selection.

In total there are sixty-eight backend tests and twenty-eight frontend tests, all
passing, and they run in CI on every push alongside a production frontend build -- so
a broken build can't merge silently.

[Show docker-compose.yml and .github/workflows/ci.yml briefly.]

A couple of smaller decisions worth calling out: the health endpoint never depends on
a live Elexon call, so the service reports healthy even while data is still loading in
the background -- that matters on a free hosting tier that sleeps and has to wake up
cold. And the one endpoint that forces a fresh data refresh is rate-limited, so it
can't be used to hammer the upstream API even though it requires no login to call.

Docker Compose runs both services locally end to end, and CI runs the backend and
frontend test suites plus a production build on every push.

[Return to any dashboard view for the closing shot.]

To wrap up: this is a focused build, done to a sixteen-hour budget -- no database, no
authentication, no paid services, because none of those were actually needed to solve
this problem. The main thing still outstanding is finishing public deployment
verification. Thanks for watching.
