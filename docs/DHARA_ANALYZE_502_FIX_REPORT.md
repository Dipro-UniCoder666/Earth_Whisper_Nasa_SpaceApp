# DHARA Analyze Now HTTP 502 — Diagnosis and Local Verification

**Checked:** 2026-11-13
**Requested checkout:** `D:\Earth_Whisper_Nasa\Earth_Whisper_GitHubClean`
**Source-control note:** This report records local diagnosis and verification; the fix is being published on a separate branch so `origin/main` remains untouched.

## Request flow

1. `app/src/features/gherproof/GherProofPage.tsx` handles **Analyze Now** in `analyze()`, which calls `loadAnalysis()`.
2. `loadAnalysis()` calls `loadGherProofData()` in `app/src/features/gherproof/services/gherproofApi.ts`; selection state is preserved if a request fails.
3. The service issues parallel **GET** requests. The required screening request is `/api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/screening`; it has no request payload. The other GETs load status, evidence, layers, scenes, predictions, weak reference, comparisons, coverage, provisional geography, summary, findings, priorities, and report. Screening is required; failures in other resources are optional/partial.
4. The frontend uses same-origin `/api/gherproof` unless `VITE_API_BASE_URL` is configured. Vite development forwards `/api` through `server.proxy`.
5. FastAPI mounts `backend/app/api/gherproof_fisheries.py` at `/api/gherproof`. Its screening route calls `gherproof_fisheries_service.screening_for_incident()` and returns the existing response model. The service reads stored incident, asset, and prepared evidence through project-root paths; it does not run live model inference.

## Root cause

Two local configuration failures combined to produce the 502:

- The Vite proxy targeted `http://127.0.0.1:8000`, but the stated backend port is `8001`. The running Vite app at `localhost:5173` returned HTTP 502 for the exact screening GET while its configured upstream was unavailable.
- The process occupying port 8001 was not serving HTTP. Its command was `uvicorn backend.app.main:app --reload --port 8001` from the repository root. TCP inspection showed a bound socket but no listener. Reproducing that command on a separate port failed at `backend/app/main.py` with `ModuleNotFoundError: No module named 'app.api'`. The reloader parent had reserved the socket while its application child failed to import.

This was not a CORS failure. With the correct import path and Vite proxy, the same-origin request succeeded.

## Changes made

- `app/vite.config.ts`: made the development proxy configurable using `DHARA_API_PROXY_TARGET`, defaulting to `http://127.0.0.1:8001`. This is a Vite development server setting and is not embedded in production builds. The equivalent config change was applied in the active `Earth_Whisper` checkout because that checkout owns the running port-5173 Vite process.
- `backend/app/api/gherproof.py` in GitHubClean: a registered optional GeoJSON whose file is missing now logs a warning and returns a structured HTTP 404 (`status: unavailable`) instead of an unhandled 500. Unexpected exceptions remain logged by the ASGI server and do not produce fabricated success responses.

The frontend API route, method, incident ID, evidence records, model outputs, and scientific interpretation were not changed.

## Verification results

| Check | Status | Result |
|---|---|---|
| Exact pre-fix request | **PASS (reproduced)** | The Pallimangal screening GET through `localhost:5173` returned HTTP 502 while the configured upstream was unavailable. |
| Wrong backend launch diagnosis | **PASS** | Reproduced `uvicorn backend.app.main:app --reload` from repository root on a separate port; captured `ModuleNotFoundError: No module named 'app.api'`. The confirmed malformed port-8001 reloader (PID 19352) was stopped. |
| Correct FastAPI startup | **PASS** | GitHubClean application code started on isolated port 8002 from its `backend/` directory with `app.main:app`, using the sibling checkout's installed Python environment because GitHubClean has no `backend/.venv`. Startup completed. |
| Health and OpenAPI | **PASS** | `/api/health` returned HTTP 200; the Pallimangal screening GET route is registered in OpenAPI. |
| Pallimangal screening | **PASS** | HTTP 200; incident ID matched; 8 observations returned; asset exposure remained `not_assessable`. |
| Full Analyze Now API set through port 5173 | **PASS** | After starting the corrected backend on 8001, all 14 GET endpoints used by `loadGherProofData()` returned HTTP 200, including screening, evidence, layers, geography, summary, findings, priorities, and report. `/dhara` also returned the SPA shell. |
| Context image and representative previews in active checkout | **PASS** | Context image and Sentinel-2 Jan 10, scratch/pretrained model, model disagreement, optical comparison, and separate NISAR Oct 23/Nov 4 preview requests returned HTTP 200 `image/png`. |
| GitHubClean missing optional GeoJSON | **PASS after fix** | Its absent regional GeoJSON now returns HTTP 404 with structured `status: unavailable` and emits a warning with evidence ID. Before the fix, reading this missing file returned HTTP 500. |
| GitHubClean imagery/raster files | **BLOCKED / absent** | The GitHubClean checkout lacks the Sentinel-2 context PNG, provisional AOI GeoJSON, and the tested registered raster files; those specific image/preview requests return HTTP 404 there. The sibling active checkout contains the corresponding tested files. No substitute data was generated or copied. |
| Proxy override | **PASS** | A temporary Vite server on port 5174 with `DHARA_API_PROXY_TARGET=http://127.0.0.1:8002` returned HTTP 200 for health, screening, evidence, layers, and `/dhara`. |
| Frontend production build | **PASS (active checkout)** | `npm run build` passed with 1,987 modules. Existing 754.28 kB minified JavaScript chunk advisory remains. GitHubClean has no `app/node_modules`, so its own build was not run. |
| Browser Analyze Now click / console review | **NOT VERIFIED** | DHARA route and investigation selection screen loaded in the browser. The click itself and browser console were not verified; all exact requests made by the click were exercised successfully through the actual port-5173 proxy. |
| Test process/service state | **PASS** | Temporary servers on 8002 and 5174 and the reproduction on 8003 were stopped. The corrected backend is now running on `127.0.0.1:8001` (PID 888; `/api/health` returns 200); Vite on 5173 remains running. |

## Correct backend startup

Run from the backend directory with an environment where the backend requirements are installed:

```powershell
Set-Location D:\Earth_Whisper_Nasa\Earth_Whisper_GitHubClean\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Do not use `backend.app.main:app` from the repository root. Restart Vite after the config change; its proxy defaults to port 8001. `DHARA_API_PROXY_TARGET` can override the local proxy target. Production API configuration remains separate through `VITE_API_BASE_URL` or an explicitly configured production proxy.

## Remaining limits

- The corrected backend is now running from the active `Earth_Whisper/backend` checkout on port 8001. Its process uses `app.main:app` and passes the health and screening requests.
- Port 5173 currently serves the sibling `Earth_Whisper` checkout, not GitHubClean. It passed the default proxy test after the config update. Restart Vite from GitHubClean if that is the intended working tree.
- GitHubClean contains evidence manifests but is missing several registered rasters and its context/AOI files. Its screening JSON works, but its map previews cannot be fully accepted until the original assets are made available in that checkout.
- No model was trained, no event inference was run, and no scientific outputs were changed.
- At the time this report was first prepared, the fix had not yet been staged, committed, or pushed.
