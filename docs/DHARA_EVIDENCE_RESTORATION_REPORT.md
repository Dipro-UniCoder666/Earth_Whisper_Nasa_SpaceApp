# DHARA Evidence Restoration and API Repair

**Date:** 2026-11-13
**Repository:** `D:\Earth_Whisper_Nasa\Earth_Whisper`

## Outcome

The DHARA results screen now receives the complete registered evidence catalogue and raster-layer list from the repository backend. The four January evidence cards use registered Sentinel-2, model, optical-change and disagreement outputs. Later NISAR evidence is presented in a separate section. No imagery or observations were synthesized.

The live Pallimangal record still reports enclosure exposure as `not_assessable` because its geometry is `not_delineated`.

## Root cause and API routing

The frontend proxy in `app/vite.config.ts` and the backend development default both use `127.0.0.1:8000`. Port 8001 was not in use during this check. The active backend was started from this repository's `backend` directory; no unrelated process was stopped.

`GET /api/gherproof/evidence?limit=500` returned HTTP 500 because the evidence response schema rejected two real registry states:

- NISAR change products use `derived_exploratory`, which was not in the response status enum.
- Four NISAR source-product records use `original_file: {availability: "not_downloaded", ...}` with no local `path`; the schema incorrectly required a path and disallowed that availability value.

The schema now represents both states without weakening validation of other fields. The catalogue returns all **217** registry records. `GET /api/gherproof/layers` returns **211** available raster references, including all **six** NISAR layers.

The UI reported both “evidence catalogue” and “map evidence” when only the catalogue request failed: its combined-registry fallback treated either missing response as a combined map failure. The fallback now appears only when both evidence and layers are absent without an individual request failure. The actual map layers endpoint returned HTTP 200 throughout the live smoke checks.

## Live HTTP verification

All requests below were made against the running local FastAPI server, not direct handler calls.

| Endpoint | Result |
|---|---:|
| `/api/health` | 200 |
| `/api/gherproof/screening/status` | 200 |
| `/api/gherproof/evidence?limit=500` | 200; 217 records |
| `/api/gherproof/layers` | 200; 211 raster references |
| `/api/gherproof/geography/geography-provisional-regional-aoi` | 200 |
| `/api/gherproof/scenes` | 200 |
| `/api/gherproof/predictions` | 200 |
| `/api/gherproof/weak-reference` | 200 |
| `/api/gherproof/comparisons` | 200 |
| `/api/gherproof/coverage` | 200 |
| Pallimangal screening, summary, findings, priorities and report | 200 each |
| Clark, WorldCover, NISAR observation and NISAR change metadata | 200; available raster metadata returned |
| Frontend Vite proxy to a NISAR preview | 200 `image/png`; 51,191 bytes |

The fisheries screening response still reports `asset_exposure.status = "not_assessable"` and `geometry_status = "not_delineated"`; this remains an honest limitation, not a zero-exposure result.

## Restored January Key Evidence

The gallery now contains four independently source-linked cards. Each has a real image preview, period, evidence category, short interpretation and click-to-enlarge view. A failed individual image is shown as unavailable in its own card rather than suppressing the gallery.

| Card | Registered evidence IDs | Actual preview check |
|---|---|---|
| Before the reported incident · Jan 10, 2026 | `s2-true-colour-2026-01-10` | HTTP 200 `image/png`, 69,792 bytes |
| After the reported incident · Jan 20, 2026 | `s2-true-colour-2026-01-20` | HTTP 200 `image/png`, 70,349 bytes |
| AI screening comparison · Jan 12, 2026 | `prediction-scratch-2026-01-12-probability`; `prediction-pretrained-2026-01-12-probability` | HTTP 200 `image/png` for both, 68,789 and 56,113 bytes |
| Water changes and model disagreement · Jan 10–20 / Jan 12–24 | `optical-weakref-temporal-temporal_change`; `disagreement-disagreement_2026-01-12_2026-01-24_rel12_ascending-xor` | HTTP 200 `image/png` for both, 9,788 and 5,368 bytes |

The model outputs remain separate and exploratory. The optical layer represents candidate indicators, not confirmed flood extent. The XOR layer indicates disagreement between models, not an error rate.

## Clark historical aquaculture context

The local derived raster exists at `data/gherproof/reference/clark_2022_locality_context_15m_utm45n.tif`; the original compressed source archive is not served or redistributed. Its checksum matches the manifest. Raster inspection found EPSG:32645, 15 m pixels and NoData value 0. After transforming the provisional regional AOI into the raster CRS and masking to that geometry, the raster contains **454,374 valid pixels (102.23415 km²)**; **10,299** are class 3 (**2.317275 km²**). These figures match `fisheries_context_manifest.json` and the registry. Counts from the full raster footprint are larger and are not used as AOI statistics.

Class 3 means pond aquaculture in the source legend. It is a 2022 land-cover class, not a current farm inventory, site boundary or January 2026 observation. The UI displays **2.32 km²** with its valid-coverage denominator and a historical-context qualification. Clark is the default Historical Context map layer; ESA WorldCover 2021 remains selectable as general land-cover context.

Clark Labs' source page states that the maps are ©2024 Clark Labs, Clark University, licensed under CC BY 4.0, and available for non-commercial use only; other applications require permission. This app presentation is treated as a non-commercial NASA Space Apps research demonstration. Any commercial deployment requires permission. The local raster is an AOI subset/derived display product, not the raw source archive. [Clark Labs aquaculture data terms](https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/).

## NISAR presentation

The separate **Additional NISAR Regional Observations** section contains two actual previews: the 2026-10-23 validated-maturity Frequency A observation (10 m) and the 2026-10-23 to 2026-11-04 Frequency A gamma0 comparison. Its text states that both dates postdate the reported January incident and are regional L-band context, not January incident evidence. It also states that gamma0 intensity/change are not water probability.

All six registered NISAR layer IDs remain available in the map selector:

- Oct 23 and Nov 4 validated-maturity Frequency A (10 m) observations.
- Oct 23 and Nov 4 validated-maturity Frequency B (80 m) observations.
- Frequency A and Frequency B Oct 23 → Nov 4 exploratory gamma0 change layers.

The map's polarization control selects HHHH or HVHV for the observation rasters. NISAR values are not routed into the Sentinel-1 models. All six NISAR preview routes returned non-empty HTTP 200 `image/png` responses in the live check; the representative Vite-proxied preview also returned HTTP 200.

## Frontend changes

- Kept the Earth Whisper navigation and DHARA route.
- Restored the four January evidence cards and retained the existing click-to-enlarge provenance dialog.
- Separated later NISAR context from January evidence and limited the additional strip to one acquisition preview plus one temporal-change preview.
- Kept all six NISAR layers and the HH/HV control in the map selector; 80 m Frequency B remains available there.
- Kept the January Sentinel-2 true-colour layer as the map default.
- Corrected the API client's duplicate “map evidence” fallback when a single individual request fails.
- Kept Clark's raster, map, historical statistic and attribution visible for this non-commercial demonstration; WorldCover remains available as broader land-cover context.

No model was retrained, no satellite scenes were searched for, and no scientific output or registry record was rewritten.

## Testing

| Check | Result |
|---|---|
| Live FastAPI routes and registered previews | **PASS** — HTTP checks listed above |
| Frontend proxy raster request | **PASS** — valid non-empty PNG |
| Focused registry/schema regression | **PASS** — 1 test passed; covers schema maturity, all six NISAR IDs, January card sources and Clark context statistics |
| Python compile check | **PASS** |
| `npm run build` (TypeScript + Vite) | **PASS** — build completed; existing >500 kB bundle-size advisory remains |
| Targeted Oxlint for changed frontend files | **PASS** — no diagnostics |
| Repository-wide `npm run lint` | **PASS with warnings** — command exited 0; it emitted many pre-existing warnings across unrelated/generated paths |
| Full `test_gherproof_phase9_preview.py` | **BLOCKED** — the Windows Python 3.14 `TestClient` request stalls while AnyIO starts a blocking portal; faulthandler showed the thread waiting in asyncio's Windows `_fallback_socketpair`/`accept`. This was not represented as a passing suite. The live HTTP tests above passed independently. |
| Browser screen smoke check | **PASS with limitation** — local `/dhara?stage=results` rendered real registered records without the generic optional-content warning; the final grouping was also confirmed by the production build and live route checks. The browser capture showed Leaflet controls but a blank external basemap; evidence PNG routes and the Vite proxy returned valid images. Basemap tile reachability/visual rendering remains to be rechecked in the user's normal browser/network. |

## Files changed

- `backend/app/schemas/gherproof_evidence.py`
- `backend/tests/test_gherproof_phase9_preview.py`
- `app/src/features/gherproof/GherProofWorkspace.tsx`
- `app/src/features/gherproof/gherproof-phase9.css`
- `app/src/features/gherproof/services/gherproofApi.ts`
- `docs/DHARA_EVIDENCE_RESTORATION_REPORT.md`

The backend and Vite dev servers are available locally at `127.0.0.1:8000` and `127.0.0.1:5173`. This task did not stage files; existing staged and unstaged changes were preserved. No DELTAQ, Sandhya or Monda project data was changed. `npm run build` updated the tracked compiler cache `app/.tmp/tsconfig.app.tsbuildinfo`.
