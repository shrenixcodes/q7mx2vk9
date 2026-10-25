# Submission manifest

Compiled 2026-10-25, end of Phase 8. Values are populated only where actually
verified in this session; everything else is explicitly `PENDING` or `NOT VERIFIED`.
Do not treat this file as final until every row says what it should.

| Item | Value | Incognito/private-window verification |
|---|---|---|
| GitHub repository | `https://github.com/shrenixcodes/q7mx2vk9` | **VERIFIED** -- confirmed public via an unauthenticated `GET https://api.github.com/repos/shrenixcodes/q7mx2vk9` returning `"private": false` in this session. Recommended: also open the repo URL itself in an incognito window before submitting, to visually confirm no sign-in prompt appears. |
| Vercel frontend URL | `PENDING` | **NOT VERIFIED** -- no Vercel URL has been supplied or discovered. This environment has no Vercel CLI or dashboard access. |
| Render backend URL | `PENDING` | **NOT VERIFIED** -- no Render URL has been supplied or discovered. This environment has no Render CLI or dashboard access. |
| Backend `/health` | `PENDING` (depends on backend URL above) | **NOT VERIFIED** |
| Backend `/api/v1/metadata` | `PENDING` (depends on backend URL above) | **NOT VERIFIED** |
| Demo video URL | `PENDING` | **NOT VERIFIED** -- no video has been recorded or uploaded. See `docs/demo-runbook.md` for the recording/upload steps. |
| Submission form | `https://forms.cloud.microsoft/r/FTX6K2bbnU` | Not applicable -- this is the destination form, supplied by you; I have not opened or submitted it. |

## Local-only verification already performed (not a substitute for the above)

These confirm the application itself works, but were run against `localhost`, not a
public URL:

- Backend test suite: 68/68 passed (`pytest -q`).
- Frontend test suite: 28/28 passed (`npm test`).
- Frontend production build: succeeds (`npm run build`); no `localhost` string present
  in the built bundle.
- `docker compose config`: valid.
- Live local run: `/health` responds immediately on a cold start; dashboard shows real
  January 2026 Elexon data across all four views; invalid date range returns a clean
  `400`; a disallowed CORS origin gets no CORS header.

## Outstanding tasks

1. Deploy the frontend to Vercel (dashboard settings are in the README's Deployment
   section) and record the resulting URL here.
2. Deploy the backend to Render (via `render.yaml` or the manual steps in the README)
   and record the resulting URL here.
3. Re-run the "Production verification checklist" in the README once both URLs exist.
4. Record the demo video per `docs/demo-runbook.md` and `docs/demo-script.md`.
5. Upload to YouTube as Unlisted, verify in an incognito window, and record the URL
   here.
6. Fill in the two deployment URLs and the video URL in this file and in the README.
7. Submit the form yourself at the URL above -- this has deliberately not been done
   for you.

## Final readiness status

**Not ready to submit.** The application, tests, and documentation are complete and
verified locally. The three externally-hosted artifacts required for submission --
the live frontend, the live backend, and the demo video -- do not yet exist in a form
this session can verify. Complete the outstanding tasks above, then this manifest
(and the README) just need their placeholders replaced with real, incognito-verified
URLs before submitting.
