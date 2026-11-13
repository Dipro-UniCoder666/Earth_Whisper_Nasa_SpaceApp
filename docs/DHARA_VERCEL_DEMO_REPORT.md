# DHARA Vercel Frontend Demo Preparation

**Date:** 2026-11-13  
**Status:** Implemented locally and production-build tested. No commit, push, or deployment was performed.

## Root cause

Vercel serves a static Vite frontend and has no FastAPI functions or `/api/gherproof` service. The DHARA results page still required 14 backend endpoints before rendering, and requested raster preview PNGs dynamically from that same absent API. This left direct `/dhara/pallimangal` navigation loading or showing an API error.

Vite preview also inherited the development API proxy. That made a production-like local preview connect to a FastAPI process on the PC, masking the Vercel behavior. Preview mode now has no API proxy unless `DHARA_PREVIEW_API_PROXY_TARGET` is explicitly set.

## Implementation

- Added `DHARA_DATA_MODE`: local development defaults to `backend`; production defaults to `demo`. `VITE_DHARA_DATA_MODE` can explicitly override either mode.
- Demo mode loads a prepared JSON snapshot and static PNG previews without requesting `/api/gherproof`.
- Added `scripts/gherproof/build_vercel_demo_data.py`, which reads the local evidence registry, existing fisheries services, provisional AOI GeoJSON and registered rasters. It runs no satellite processing or model inference.
- Generated a static package with 217 evidence records, 47 layer choices and 51 raster preview variants, plus existing case screening, report, observation metadata, provenance and limitations.
- Previews use the existing backend display renderer. The frontend package does not contain source GeoTIFFs, model files, HDF5 products, training data or the backend directory.
- Map layer selection, map controls, opacity, NISAR HHHH/HVHV selection, evidence previews, report dialog and evidence JSON link use static prepared assets where available.
- Boundary review is read-only in demo mode and reports that the enclosure boundary is unavailable. Local boundary editing still uses FastAPI.
- A failed direct result-page load no longer triggers automatic repeated retries.
- Added Vite build/output configuration in `app/vercel.json`. Existing explicit SPA rewrites cover `/dhara`, `/dhara/pallimangal` and the other app routes without rewriting static assets or API paths.

## Scientific provenance preserved

- Sentinel-2 comparisons on January 10 and January 20 identify 671 possible-new-water candidate cells and 1,316 possible-water-loss candidate cells on a 20 m grid. These are candidates, not flood area or confirmed observations.
- The Pallimangal event and date remain reported/inferred, not independently confirmed.
- The enclosure boundary remains not delineated; exposure is not assessable.
- Model predictions remain separate exploratory outputs without local human-label validation.
- NISAR scenes from October 23 and November 4, 2026 remain a separate later regional series, not evidence for the January incident.
- The map uses the existing provisional regional search extent, not an official village or enclosure boundary.

The JSON snapshot includes evidence metadata and relative source-path provenance, not the referenced local raster files. Generated map PNGs are display-only. No large scientific raster/model inputs were copied into the frontend package.

## Verification

| Check | Result | Details |
|---|---|---|
| TypeScript and Vite production build | PASS | `npm run build` completed; Vite 8.3.0 transformed 1,987 modules. Existing main-JS advisory: about 757 kB minified. |
| `/dhara?stage=select` in built preview | PASS | HTTP 200; SPA document served, query string retained by the browser URL. |
| `/dhara/pallimangal` in built preview | PASS | HTTP 200; SPA document served on direct request. |
| Static demo JSON and report | PASS | HTTP 200; demo JSON 821,768 bytes and report JSON 7,994 bytes. |
| Static map PNG | PASS | HTTP 200, `image/png`. |
| Production preview API isolation | PASS | `/api/gherproof/screening/status` resolves to SPA fallback HTML, not FastAPI JSON. Demo mode does not call it. |
| Local development backend proxy | PASS | Through `npm run dev`, `/api/health` and `/api/gherproof/screening/status` returned existing backend JSON. |
| Raster preview generation | PASS | 47 layer choices, 51 preview variants, zero render failures. SHA-256 and source-raster provenance are recorded in `app/public/data/dhara-demo-manifest.json`. |
| Built output | PASS | 77.35 MiB across 77 files, including existing Earth Whisper public media. New DHARA preview images total about 17.5 MB; demo JSON about 0.8 MB. |
| Heavy source files in `dist` | PASS | No `.tif`, `.tiff`, `.pt`, `.pth`, `.h5` or training-data files. |
| Browser interactions / console | NOT VERIFIED | The desktop browser surface was unavailable in this session. Build and HTTP checks were completed; no deployed browser test is claimed. |
| Vercel dashboard settings / live deployment | NOT VERIFIED | Project settings cannot be read from this workspace; nothing was deployed. |

## Reproduction

From `app/`:

```powershell
npm run build
npm run preview -- --host 127.0.0.1
```

Check `/dhara?stage=select` and `/dhara/pallimangal` on the preview server. Preview intentionally does not proxy `/api` unless `DHARA_PREVIEW_API_PROXY_TARGET` is configured.

To rebuild prepared assets from repository root:

```powershell
$env:GHERPROOF_FISHERIES_DB = Join-Path $env:TEMP 'dhara-vercel-demo.sqlite3'
.\backend\.venv\Scripts\python.exe scripts/gherproof/build_vercel_demo_data.py
```

The generator writes only under `app/public/data/` and `app/public/images/dhara-demo/`.

## Vercel project settings to confirm

Set the Vercel **Root Directory** to `app`. Use Vite auto-detection, build command `npm run build`, output directory `dist`, and npm install detection from `package-lock.json`. Leave `VITE_DHARA_DATA_MODE` unset in production (it defaults to demo) or set it to `demo`. Do not set a production `VITE_API_BASE_URL` for the static demo. The FastAPI backend remains local. Dashboard configuration and live deployment were not changed or verified.

## Files changed

- `app/.env.example`, `app/vercel.json`, `app/vite.config.ts`
- `app/src/features/gherproof/services/gherproofApi.ts`
- `app/src/features/gherproof/GherProofPage.tsx`
- `app/src/features/gherproof/GherProofWorkspace.tsx`
- `app/src/features/gherproof/GherProofMap.tsx`
- `app/src/features/gherproof/BoundaryReviewMap.tsx`
- `scripts/gherproof/build_vercel_demo_data.py`
- `app/public/data/dhara-demo.json`
- `app/public/data/dhara-demo-manifest.json`
- `app/public/data/dhara-evidence-report.json`
- `app/public/images/dhara-demo/*.png`
- `docs/DHARA_VERCEL_DEMO_REPORT.md`

The pre-existing API timeout change in `gherproofApi.ts` was preserved. Backend source, local raster data, model files, Sandhya, Monda and the DELTAQ archive were not changed.

## Git commands for review

No files were staged or committed. After reviewing `git diff` and `git status`, commit and push from the current branch to `main` with:

```powershell
git add app/.env.example app/vercel.json app/vite.config.ts app/src/features/gherproof/BoundaryReviewMap.tsx app/src/features/gherproof/GherProofMap.tsx app/src/features/gherproof/GherProofPage.tsx app/src/features/gherproof/GherProofWorkspace.tsx app/src/features/gherproof/services/gherproofApi.ts scripts/gherproof/build_vercel_demo_data.py app/public/data/dhara-demo.json app/public/data/dhara-demo-manifest.json app/public/data/dhara-evidence-report.json app/public/images/dhara-demo docs/DHARA_VERCEL_DEMO_REPORT.md
git commit -m "Prepare static DHARA Vercel demo"
git push origin HEAD:main
```

This task did not perform the push. Verify Vercel's project root is `app` and approve deployment separately.
