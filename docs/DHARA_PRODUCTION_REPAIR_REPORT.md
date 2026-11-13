# DHARA Production Repair and Deployment Review

**Review date:** 2026-11-13
**Working branch:** `feature/gherproof`
**Production URL checked:** <https://earth-whisper.vercel.app/dhara>

## Findings

The live Vercel deployment serves the application shell at `/` (`200 text/html`), but a direct request to `/dhara` returns Vercel `404 NOT_FOUND`. The same-origin `/api/health`, `/api/gherproof/evidence?limit=1`, and `/api/gherproof/layers` paths also return Vercel `404 NOT_FOUND`. This confirms two separate deployment failures:

1. The Vite single-page application has no Vercel route fallback for React Router deep links.
2. The production frontend has no working same-origin FastAPI route, and the checked-in API client previously hard-coded relative `/api/gherproof` URLs. The Vite proxy in `vite.config.ts` is development-only. No separate backend hostname or Vercel project environment configuration is present in this repository, so the correct production API host cannot be established from code or the tested public routes.

The landing image and Pallimangal card both requested `/api/gherproof/context/sentinel2`, so they failed with the unavailable API. The actual pre-incident contextual image is present locally: a Sentinel-2B true-colour preview acquired `2026-01-13T04:40:39.024Z`, item `S2B_MSIL2A_20260113T044039_R033_T45QYF_20260113T070956`. It is a broad provisional locality view, not an enclosure boundary. The asset remains unchanged in the original data folder; a byte-identical copy is included in the frontend public directory. SHA-256 equality was verified.

## Repairs prepared

- Added `app/vercel.json` with explicit SPA rewrites for the routes implemented by React Router. The rules do not capture `/api/*`, so a missing API cannot appear as a successful HTML response. This file is read only if the Vercel project root is configured as `app`; the repository does not contain Vercel account settings to confirm that root directory.
- Added the real Sentinel-2B preview as `app/public/images/dhara-sentinel2-context-2026-01-13.png`, used on the DHARA landing and Pallimangal selection card, and reused in the boundary review map. A visible image fallback appears if the local asset fails.
- Updated DHARA JSON, raster-preview, boundary, and evidence-report requests to use `VITE_API_BASE_URL` when configured, while retaining same-origin `/api` behavior for local Vite proxy use.
- Improved the screening error to include the observed HTTP status when available and point to API base URL/routing, backend availability, and CORS configuration.
- Added `app/.env.example` with the frontend setting name and documented the production setup below.
- Preserved existing evidence IDs, API paths, boundary data, raster assets, model outputs, and scientific interpretation. The image caption identifies its acquisition and provisional locality scope.

## Required deployment configuration

The live deployment still needs the existing FastAPI service to be made reachable. No service URL could be verified; do not substitute an invented URL.

1. In Vercel, confirm **Root Directory** is `app`, framework is Vite, build command is `npm run build`, and output directory is `dist`. The app-root setting is required for `app/vercel.json` and the `app` package build to apply.
2. Set Vercel's production environment variable `VITE_API_BASE_URL` to the real HTTPS origin of the already-hosted FastAPI service, with no trailing slash and no `/api` suffix. For example, the value should have the shape `https://<existing-api-host>`; this is a format illustration, not a real endpoint. Rebuild/redeploy after setting it. If production instead has an existing same-origin API proxy, keep this variable empty and configure that proxy to the actual backend.
3. In the FastAPI host environment, set `CORS_ORIGINS=https://earth-whisper.vercel.app` (add the actual Vercel preview origins if preview deployments need browser access). The backend's checked-in default only allows localhost origins.
4. Confirm the API host responds successfully to `/api/health`, `/api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/screening`, `/api/gherproof/evidence?limit=1`, `/api/gherproof/layers`, `/api/gherproof/context/sentinel2`, and layer preview requests. Confirm response content types and that the backend has the project's prepared evidence files mounted at their expected paths.

These account-level settings cannot be changed or verified from the checked-out repository. The current live site therefore remains API-blocked until the verified existing backend URL and production settings are supplied/configured.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Production root | PASS | `200 text/html` from Vercel. |
| Production `/dhara` deep link | FAIL before this unpushed change | Vercel `404 NOT_FOUND`; SPA rewrite repair is prepared but not deployed. |
| Production same-origin API | FAIL before this unpushed change | `/api/health`, evidence, and layers returned Vercel `404 NOT_FOUND`. |
| Frontend TypeScript + production build | PASS | `npm run build`; Vite 8.3.0 transformed 1,987 modules and emitted `app/dist`. Existing large-chunk advisory remains (754.23 kB JS minified). |
| Focused lint of changed frontend files | PASS with warning | `npx oxlint` exit 0; one existing `react(set-state-in-effect)` warning in `BoundaryReviewMap.tsx`. |
| Full frontend lint | PASS with noisy existing warnings | `npm run lint` exit 0; oxlint traversed existing generated build-output files and reported thousands of warnings. No lint configuration changes were made. |
| Vercel rewrite JSON | PASS | Parses as JSON; nine app-route rewrites; no `/api` rewrite conflict. |
| Static image | PASS locally | Source and public copy are both 5,440,663 bytes and SHA-256 hashes match; generated `dist/images/dhara-sentinel2-context-2026-01-13.png` exists. |
| Backend import | PASS | Local backend virtual environment imported `app.main`. |
| Local backend HTTP smoke | BLOCKED | Bounded Uvicorn start did not produce a reachable health endpoint within 12 seconds; the process was terminated. No startup diagnostic was emitted by the managed shell. Do not treat local fisheries API responses as verified. |
| Git whitespace check | PASS | `git diff --check` returned no errors. |
| Production verification after repair | BLOCKED | Changes have not been committed/deployed; no Vercel account settings or verified API host are available in this checkout. |

## Remaining scientific and production limits

- A static Sentinel-2 preview restores contextual imagery only. It does not make the incident screening, raster maps, evidence catalog, or report API available.
- The January 13 preview is not a cadastral or verified gher boundary, current land-cover label, or proof of incident impact.
- No model inference or science outputs were changed.
- Route rewrites, image loading, API response schemas, map tiles, CORS, and browser console behavior still require a deployed preview check after the Vercel root/environment settings and existing API host are configured.

## Git and deployment state

This report was first prepared while the repair files were still local. The user subsequently requested direct publication of the full local codebase to GitHub `main`; the reviewed repair files are included in that update. The user-provided untracked `gherproof-file-list.txt` remains untouched and is excluded. The pretrained model and S1GFloods archive are already Git LFS-tracked; the new Sentinel-2 context preview is 5.44 MB.

The live Vercel project still needs a verified FastAPI origin configured as `VITE_API_BASE_URL`, or an existing same-origin API proxy. This repository does not contain a production API hostname or deployment account settings, so publishing the frontend cannot by itself make the screening API reachable. No API host has been invented.

## Post-deployment smoke check — 2026-11-13

After the direct push to GitHub `main` (commit `00eb277`), the live Vercel project returned:

| Request | Result |
|---|---|
| `/dhara` | **PASS** — HTTP 200 HTML |
| `/images/dhara-sentinel2-context-2026-01-13.png` | **PASS** — HTTP 200 PNG, 5,440,663 bytes |
| `/api/health` | **FAIL** — HTTP 404 |
| Pallimangal `/api/gherproof/.../screening` | **FAIL** — HTTP 404 |

The SPA route and contextual image are deployed. Analyze Now is still blocked in production because Vercel has no `/api` backend route and no verified FastAPI origin was found in the repository. Configure Vercel production `VITE_API_BASE_URL` to the actual FastAPI HTTPS origin (without `/api`), or deploy a same-origin proxy to that service; then redeploy and recheck `/api/health` and screening. This repository contains no verified API hostname, so none is supplied here.

## Named results route — 2026-11-13

Added `/dhara/pallimangal` as the direct, named results URL for the Pallimangal investigation. Analyze Now navigates to this path, and the existing `/dhara?stage=results` remains a supported link. The Vercel SPA rewrite and React Router both serve the named route. The frontend build passed after this change. In the latest live smoke check, the frontend route and image were available while `/api/health` and the screening endpoint returned 404; this route update does not resolve the missing production FastAPI connection.
