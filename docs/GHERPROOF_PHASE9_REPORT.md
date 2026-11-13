# GherProof Phase 9 — Frontend Implementation Report

## Delivered

Integrated the fisheries incident results experience into the existing Earth Whisper application and retained its shared navigation and route structure. The GherProof route now opens an investigation introduction, selection step and data-backed results page. The results page uses the supplied dark visual reference as a guide while keeping all incident claims tied to the existing evidence services.

The page includes four API-backed summary cards, a Leaflet map with selectable evidence layers and opacity controls, three interpretation/next-step panels, four registered evidence previews, an evidence provenance lightbox, and a report dialog populated from the fisheries report endpoint. Missing data remains explicitly unavailable. The page labels the regional extent provisional and does not draw an invented Pallimangal boundary.

Sentinel-2 previews are identified as B08/B04/B03 false colour. The map defaults to the registered Sentinel-1 observation layer and states that its display stretch is not water probability. Temporal change categories use distinct colors for possible increases, possible decreases, persistent-water candidates, stable indicators, uncertain change and invalid coverage. All are described as exploratory indicators.

## API integration and backend correction

The page loads the existing GherProof status, evidence, layer, scene, prediction, weak-reference, comparison, coverage and provisional-geography routes together with the Phase 8C incident screening, summary, findings, priorities and report routes. Partial failures are shown as partial evidence status rather than replaced by fabricated values. Only registered raster records are offered as layer choices.

Live inspection of the already-running service on port 8000 found `/api/gherproof/screening/status` returning HTTP 500. The underlying screening status included model names, label counts and other non-integer values, while its response schema incorrectly restricted `model_outputs` to integers and omitted label-count fields. Updated the schema to preserve those actual fields and added a regression test. A fresh application instance on port 8001 returned HTTP 200 for status, evidence, layers, provisional geography and all five incident screening/report endpoints. The pre-existing process on port 8000 was not stopped; it must be restarted to load the schema fix.

The report dialog is read-only and renders the actual generated JSON report. No PDF, event boundary, flood classification or incident-area estimate is fabricated. The evidence preview API remains a bounded visualization endpoint; source units and evidence limitations remain in the UI.

## Verification

- `npm run build` — **PASS**. TypeScript and Vite production build completed. Vite reported the existing large-bundle advisory (742.52 kB minified JavaScript).
- `npm run lint` — **PASS** (exit code 0). Repository-wide output contains extensive existing warnings, including warnings on generated `.vite-build-investigate` assets. Targeted Oxlint on the changed GherProof components, API service and shared layout files — **PASS**, no warnings.
- Focused backend preview and status tests — **PASS**, 6 tests. Includes registered raster previews, category colors, input validation and the screening-status response schema. The sandboxed Windows test-client run stalled; the same command completed outside the sandbox using the approved local socket access.
- Fresh FastAPI runtime on port 8001 — **PASS** for all nine GET requests tested: screening status, evidence, layers, provisional geography, incident screening, summary, findings, priorities and report. The temporary server was stopped after the checks.
- Service on port 8000 — **BLOCKED for current-process verification**: status still returns 500 because that already-running process predates the schema correction. Its owner/process was not interrupted. Restart it before browser use.
- Requested screenshot review at 1440×900, 1024×768 and 390×844 — **NOT VERIFIED**. The browser-control connector was unavailable, and the desktop automation detected active user input in Chrome and did not proceed. Responsive breakpoints exist, but no screenshot-based visual claim is made.

## Scientific and operational limits

- The 671 possible-increase and 1,316 possible-decrease values are candidate grid-cell counts on a 20 m grid, not hectares, confirmed flood pixels or affected area.
- The exact Pallimangal enclosure boundary remains unresolved and exposure remains `not_assessable`.
- The incident date is reported/inferred. Model layers are exploratory; no local human reference labels or field confirmation are represented.
- The interface makes no claim of fish escape, mortality, breach, production loss or financial damage.
- OSM tiles require network access in the user's browser. The page remains usable with the evidence API even if tiles cannot load.

## Files changed for Phase 9

- `app/src/features/gherproof/GherProofPage.tsx`
- `app/src/features/gherproof/GherProofWorkspace.tsx`
- `app/src/features/gherproof/GherProofMap.tsx`
- `app/src/features/gherproof/gherproof-phase9.css`
- `app/src/features/gherproof/services/gherproofApi.ts`
- `app/src/components/layout/AppLayout.tsx`
- `app/src/components/layout/SecondaryPageLayout.tsx`
- `backend/app/api/gherproof.py` (temporal preview palette)
- `backend/app/schemas/gherproof_evidence.py` (screening-status schema)
- `backend/tests/test_gherproof_phase9_preview.py`
- `docs/GHERPROOF_PHASE9_REPORT.md`

Other staged, unstaged and untracked repository changes were preserved and not staged or cleaned up.

## Run locally

Start the backend from `backend/` using its documented command, then start Vite from `app/` with `npm run dev`. If an older backend process is already on port 8000, restart that process so it loads the corrected response schema. Open `/gherproof`, select the Pallimangal reported investigation, then choose **Analyze Now**. Run the focused preview tests from `backend/` with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_gherproof_phase9_preview.py -q
```
