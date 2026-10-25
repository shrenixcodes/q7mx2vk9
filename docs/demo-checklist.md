# Pre-recording checklist

Work through this top to bottom, in order, right before you hit record.

## Environment setup

- [ ] Decide now whether you're demoing the public deployment or `localhost`. If
      public, confirm both URLs load in a fresh private/incognito window first (see
      `docs/submission-manifest.md` for the actual URLs and their verification
      status).
- [ ] If demoing the Render backend, open it and wait for it to finish waking up
      *before* you start recording -- hit `/health` once, wait for a `200`, then give
      it another 10-20 seconds for the background data load to finish before you open
      the dashboard (see "Backend wake-up" below).
- [ ] If demoing locally: `docker compose up` (or `uvicorn` + `npm run dev`), then
      confirm `http://localhost:5173` loads and shows real data, not an error state.
- [ ] Browser zoom at 100%, window sized so nothing is cut off or overlapping at
      1280x800 or your recording resolution.
- [ ] Resize the browser window once and confirm the layout doesn't break (sidebar,
      KPI cards, chart, table all still legible).

## Backend wake-up time

- [ ] Render's free tier sleeps after inactivity. Budget at least 30-60 seconds after
      your first request before the app is fully responsive with real data. Don't
      start recording until you've done a cold hit yourself and timed it.
- [ ] If it's still loading when you open the dashboard, you should see an honest
      loading or "not yet loaded" state -- not a crash and not fabricated numbers. If
      you see anything else, stop and fix it before recording.

## Browser and screen hygiene

- [ ] Close every tab except the one you're demoing. No email, no chat apps, no
      unrelated bookmarks bar entries visible.
- [ ] Turn off OS and browser notifications (Do Not Disturb / Focus mode).
- [ ] Clear or hide your browser history/autofill if the address bar will be visible.
- [ ] No personal information, API keys, tokens, or `.env` file contents visible on
      screen at any point -- double-check if you're going to show a terminal or editor.
      (This app has no API key to begin with, but check your own shell history/prompt
      anyway.)
- [ ] If showing the code editor, close any unrelated open files or terminals first.

## Rehearsal

- [ ] Click through every interaction you plan to demo at least once before
      recording: switching views, changing the date filter, switching analysis mode,
      sorting the table, paging the table.
- [ ] Note the actual MAE/RMSE/bias/coverage values you'll read on screen -- don't
      plan to say a number from the script; the script uses placeholders on purpose.
- [ ] Confirm the units you'll say out loud (MW) match what's on screen.
- [ ] Time yourself once, informally, against the runbook's minute marks. Part 1
      should land near 4:30, Part 2 near 4:30, total near 9:00.

## Recording setup

- [ ] Test your microphone levels with a few spoken sentences before the real take --
      listen back for clipping or background noise.
- [ ] Test screen recording for a few seconds and confirm both video and audio were
      captured together.
- [ ] Pick a recording resolution that's readable on YouTube at normal viewing size
      (1080p recommended).

## After recording

- [ ] Watch the full recording back, start to finish, before uploading anything.
- [ ] Confirm total runtime is **under 10 minutes**.
- [ ] Confirm audio is audible throughout and the screen is legible throughout.
- [ ] If anything is wrong, re-record rather than upload a flawed take -- budget time
      for at least one backup take.
