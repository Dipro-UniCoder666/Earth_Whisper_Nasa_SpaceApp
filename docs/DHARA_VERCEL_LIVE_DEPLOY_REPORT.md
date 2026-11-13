# DHARA Pallimangal Vercel Production Deployment

**Verified:** 2026-11-13 (Asia/Dhaka)  
**Production commit:** `a59b8cab1e97eb2ae8c0c592a64f0aab224e1b24` (`Prepare complete DHARA Vercel investigation demo`)  
**Production branch:** `main`

## Deployment result

The frontend-only DHARA release was pushed to the existing GitHub `main` branch. The existing Vercel Git integration published the update at the existing domain. The production page and the previously missing prepared JSON and preview assets now return successfully.

- Home: https://earth-whisper.vercel.app/
- DHARA: https://earth-whisper.vercel.app/dhara
- Pallimangal investigation: https://earth-whisper.vercel.app/dhara/pallimangal

The working branch had substantial project-data differences from production `main`. To avoid adding those data files to the deployment commit, the release was prepared in a clean worktree based on the fetched production branch. The release commit changed only frontend code, prepared JSON/PNG preview assets, the local demo-data generator, and documentation. No raster source, model checkpoint, training dataset, HDF5 product, or FastAPI source change was included in this release commit.

## Root cause and fix

The route itself already returned the React SPA, but the deployed static frontend had no FastAPI `/api/gherproof` service. The results page depended on that absent API for its case data and raster previews. Consequently, the route rendered its shell while the investigation could remain loading or report an API error.

Production now selects the prepared static demo provider by default. It loads the checked-in JSON snapshot and static image previews without requesting `/api`. Local development continues to select the FastAPI provider and retains the Vite `/api` development proxy. The production preview server does not inherit that proxy.

## Vercel configuration

The deployed Vercel build uses the frontend under `app/`:

- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Static SPA routes: `/dhara`, `/dhara/pallimangal`, and the existing application routes in `app/vercel.json`
- Production data mode: `demo` by default
- Production API requirement: none

The `app/vercel.json` build configuration was used by the successful production build, and the new `app/public` assets are available on the live domain. Vercel CLI/dashboard access was unavailable, so the project settings page itself was not inspected. The deployed output verifies that the existing project is building the frontend configuration and serving its static package.

## Live production checks

| Check | Result | Observation |
|---|---|---|
| `/` | PASS | HTTP 200, SPA document. |
| `/dhara` | PASS | HTTP 200, SPA document. |
| `/dhara?stage=select` | PASS | Direct request returns SPA document; query parameter remains in the URL. |
| `/dhara/pallimangal` | PASS | HTTP 200 on direct navigation and refresh. |
| Demo data | PASS | HTTP 200, 821,768-byte JSON; prepared mode, 217 evidence records, 47 layer choices. |
| Evidence report JSON | PASS | HTTP 200. |
| Prepared raster previews | PASS | All 51 manifest-listed preview URLs returned HTTP 200. |
| HTML, JS, CSS | PASS | Production bundle and styles returned HTTP 200. |
| Browser console | PASS | No page console errors or uncaught runtime exceptions in the headless Chrome production session. |
| Browser API calls | PASS | No `/api` requests during the hosted demonstration page load or exercised controls. |
| Image loading | PASS | 26 page images loaded; zero broken image URLs. All prepared preview assets separately returned HTTP 200. |
| Map tiles | PASS | OpenStreetMap tile service returned HTTP 200 and the page displayed loaded tiles. During initial Leaflet extent settling, 10 obsolete tile requests were cancelled; 15 current tiles loaded and none remained broken. |
| Model/raster source files | PASS | No GeoTIFF, model weights, HDF5, or training data was added by the production commit. |

## Full page and interactions

The production DOM contains the investigation title, all four KPI cards (671 candidate cells, 1,316 candidate cells, 2.32 km² historical pond-aquaculture class, two exploratory models), screening findings, historical context, suggested inspection steps, Key Evidence, Additional NISAR Regional Observations, limitations, and report access.

Headless Chrome interaction checks passed for:

- Historical Context and AI Screening tabs.
- Sentinel-1 observation/layer selection.
- Map zoom controls and opacity slider.
- Evidence preview lightbox.
- Investigation report dialog.
- NISAR Frequency A observation and HHHH/HVHV band selection; the HV preview switched to its packaged `--b2.png` file.
- JSON report link and static report asset.

At a 390 CSS-pixel mobile viewport, `document.documentElement.scrollWidth` was 390 px, with no horizontal page overflow. A 1,422 px desktop CSS viewport measured a 1,412 px document width. Both layouts rendered the result view; no deployed mobile-specific functional failure was observed.

The displayed satellite values and limitations are unchanged. Sentinel-2 candidate counts remain grid-cell counts, the exact enclosure boundary remains unresolved, the AI products remain exploratory, and NISAR remains a separate later regional observation stream.

## Build and local mode

`npm run build` passed in the isolated production worktree using the same Vite/TypeScript configuration and prepared assets. Vite emitted its existing advisory that the main JavaScript bundle is about 757 kB minified; build succeeded.

Local `npm run dev` was separately verified to retain the FastAPI proxy: `/api/health` and the DHARA screening endpoint returned backend JSON. Production does not rely on that proxy.

## Remaining limitations

- The deployment is a static prepared demonstration, not live satellite processing or live AI inference.
- The exact Pallimangal enclosure boundary is not established; no enclosure-specific exposure is claimed.
- Map basemap tiles are supplied by OpenStreetMap and require browser internet access. The prepared evidence overlays themselves are included in the frontend deployment.
- Vercel CLI and private dashboard settings were unavailable for direct inspection; live HTTP response checks confirmed that the expected application build and assets are deployed on the existing domain.
