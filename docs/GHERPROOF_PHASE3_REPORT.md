# GherProof Phase 3 — Recovery, benchmark model comparison and event readiness

**Overall: PARTIAL.** The authenticated retrieval and verification pipeline, separate pretrained fine-tuning/evaluation experiment, provenance-controlled human boundary workflow, honest application workflow states, and retired-project cleanup are implemented. Actual event imagery, a verified enclosure boundary, and local reference labels are still unavailable, so event inference and affected-area analysis remain blocked.

## Status by workstream

| Workstream | Status | Evidence |
|---|---|---|
| Repository/data audit and protection | COMPLETE | `docs/GHERPROOF_PHASE3_AUDIT.md`; initial working tree was extensively dirty and was not reset/stashed/staged/committed. |
| CDSE authentication implementation | COMPLETE | `scripts/gherproof/cdse_auth.py`; no secrets entered chat or written to manifests. |
| Recover four event assets | BLOCKED | 0/4 downloaded; current process has no CDSE credentials. Recovery script performs no identity/download request when credentials are missing. |
| Verify actual event rasters | BLOCKED | 0/4 raster assets available; no CRS/coverage/units/no-data measurements can be reported. Validator and manifest are ready. |
| Scene suitability | PARTIAL / NOT ESTABLISHED | Catalogue metadata is same S1A IW GRDH family, relative orbit 114 ascending, VV/VH; Jan 7 is −7 days and Jan 19 +5 days from the reported Jan 14 date. Radiometry, terrain correction, actual overlap/alignment and masks are unknown. This is a plausible pair, not yet a scientifically validated comparison. |
| Pretrained model experiment | COMPLETE for benchmark | Encoder-only direct inference was rejected as task-incompatible; a separate strictly initialized ResNet50 encoder-decoder was fine-tuned and evaluated on the same event split. Results below. |
| Pallimangal geometry | PARTIAL | A reviewer map/API workflow exists, but current status remains `not_delineated`; no geometry was created or implied. |
| Sujatpur inference / area | NOT STARTED (gated) | No event rasters, verified enclosure, permanent-water reference or cropland reference. No inference maps or area totals were generated. |
| GherProof application status/integration | PARTIAL | The app displays asset counts, explicit workflow gate, boundary status, review map, and comparison download when results exist. No event prediction layer is shown. |
| Retired-project cleanup | COMPLETE | See dedicated section below. |

## Sentinel‑1 recovery and validation

The source URLs are CDSE OData node `$value` COG measurements on `zipper.dataspace.copernicus.eu`, not ASF/NASA Earthdata URLs. The four exact COG links/product IDs and local statuses are in `data/gherproof/manifests/event_imagery_manifest.json`.

| Date/time UTC | Scene ID (short) | Orbit/direction | Polarization | Catalogue bytes | Outcome |
|---|---|---|---|---:|---|
| 2026-01-07 12:04:28.028694 | S1A…062661…COG | 114 ascending | VV | 664,403,282 | `authentication_blocked` |
| 2026-01-07 12:04:28.028694 | S1A…062661…COG | 114 ascending | VH | 572,402,839 | `authentication_blocked` |
| 2026-01-19 12:04:27.012308 | S1A…062836…COG | 114 ascending | VV | 662,506,694 | `authentication_blocked` |
| 2026-01-19 12:04:27.012308 | S1A…062836…COG | 114 ascending | VH | 573,468,706 | `authentication_blocked` |

The 36-hex-character provider strings do not identify a standard digest. The script therefore records them as `unidentified` and will record local SHA‑256 after complete retrieval. It validates response status/ranges, expected content length, TIFF open, single-band georeferencing and a decoded pixel sample before asset verification. The separate validator records CRS, affine transform, WGS84 bounds, resolution, NoData/mask flags, units/scale/tags, finite values and bounded-memory percentile samples, plus broad provisional-box overlap. It never labels catalogue presence as processing success.

Current authentication state is blocked because `CDSE_USERNAME`, `CDSE_PASSWORD`, `CDSE_TOTP_CODE` / `CDSE_TOTP_SECRET` are missing. Setup instructions are in `docs/GHERPROOF_CDSE_SETUP.md`. No passwords need to be sent in chat. CDSE documents a password token flow using `cdse-public`, optional current one-time `totp` code, and refresh-token renewal; our code also supports local TOTP-secret code generation. Authentication and product requests do not log tokens or response bodies. One 401 refresh is allowed before further downloads stop.

**Pre/post scientific judgement:** dates/metadata make the scene pair a reasonable candidate for investigation, but without the files this phase cannot establish compatible calibrated measurement units, processing baseline, pixel-level alignment, valid coverage or masks. Do not interpret values or publish a change/water map until those checks pass. Full assessment is `docs/GHERPROOF_EVENT_IMAGERY_VALIDATION.md`.

## Pretrained comparison

The TorchGeo/SSL4EO-S12 checkpoint is a two-channel ResNet50 MoCo self-supervised encoder (318 tensors, strict key match), not a water segmentation model. Direct inference is marked `not_applicable_task_incompatible`; no direct outputs were fabricated. A ResNet50 encoder-decoder was trained using the same 210/41/15 event-separated chips and fixed 0.5 threshold. The ResNet50's final encoder stages and decoder were fine-tuned; early stages were frozen for the CPU runtime. CUDA and mixed precision were unavailable.

| Model | Event 11 validation IoU / P / R / F1 / PR-AUC | Bolivia test IoU / P / R / F1 / PR-AUC | CPU ms per 256² patch | Parameters / checkpoint bytes |
|---|---|---|---:|---:|
| Scratch attention U-Net | 0.5088 / 0.6469 / 0.7044 / 0.6744 / 0.72684 | 0.6276 / 0.7423 / 0.8023 / 0.7712 / 0.74693 | 49.3 | 509,564 / 2,064,496 |
| Pretrained MoCo encoder, fine-tuned | 0.5505 / 0.6849 / 0.7371 / 0.7101 / 0.74123 | 0.5942 / 0.8905 / 0.6410 / 0.7454 / 0.84058 | 158.3 | 37,244,737 / 149,316,323 |

The fine-tuned model improves event-11 validation; Bolivia has a precision/PR-AUC gain but markedly lower recall and lower IoU/F1. The Bolivia test is 15 chips from one event. This benchmark does not support a local accuracy claim. No model is approved for quantitative Sujatpur impact reporting. Full comparisons, confusion matrices, source/licence, hashes and interpretation are in `docs/GHERPROOF_PRETRAINED_MODEL_COMPARISON.md` and `docs/GHERPROOF_TRAINING_REPORT.md`.

## Human boundary workflow

The map at the GherProof route overlays the broad Jan 13 Sentinel‑2 crop with an explicit contextual-only warning. Users can create/edit a candidate polygon, enter evidence/reviewer/date/confidence, save/reload versioned GeoJSON, and advance only through `candidate → under_review → verified`. Invalid polygons, missing evidence and review metadata, and direct candidate-to-verified transitions are rejected by the API. Each version gets a separate GeoJSON file and provenance record. There is no current geometry. The reviewer text is user-entered (not an authenticated identity), and `verified` means reviewed with recorded evidence, not independently surveyed ground truth. Details: `docs/GHERPROOF_BOUNDARY_PROVENANCE.md`.

## Event reconstruction gate and result

The current workflow is `imagery_unavailable`, with 0/4 assets recovered, 0/4 verified, and boundary `not_delineated`. Since required event inputs do not exist locally, the phase does **not** generate pre/post probability maps, masks, new-water masks, cropland impact rasters, hectares/bighas, or a breach diagnosis. These are withheld, not estimated. The Jan 13 Sentinel‑2 crop and 2022 Clark class remain context only.

## Licensing and data protection

- CDSE Sentinel products: Copernicus Sentinel data terms are free/full/open; cite source and follow the Sentinel Data Legal Notice.
- Clark Labs aquaculture layer: provider lists CC BY 4.0 plus non-commercial use only; permission is required for other applications. Not used as an exact boundary.
- Sen1Floods11 v1.1 hand imagery/labels: official collection metadata says proprietary, with no verified permissive license in the source README; do not redistribute data or fine-tuned weights pending written terms.
- TorchGeo/SSL4EO-S12 weights: CC BY 4.0; source and SHA recorded.
- OpenStreetMap tiles: OpenStreetMap contributor attribution / ODbL; no OSM geometry is used as the enclosure.

Machine-readable source decisions are in `data/gherproof/manifests/license_provenance.json`. Current data rights do not permit claiming the app's benchmark artifacts are freely redistributable.

## DELTAQ COMPLETE REMOVAL

**COMPLETE for the working repository.** The archive was inventoried before deletion: it contained 182 files, 63 directories and 47,825,247 bytes (about 45.6 MiB), not the 194 files/8.48 GiB claimed in the cleanup instructions. The measured total is the actual storage reclaimed by this deletion; no additional data tree existed at `data/deltaq/`. The dedicated `archive/deltaq_legacy/` directory is gone. The earlier 8.48 GiB bulk is therefore not counted as part of this phase's measured deletion.

The archive held the dedicated app feature, API/schema/service/tests, datasets, scripts, manifests and project reports; reference checks found no active GherProof/Sandhya/Monda dependency. The old `/deltaq` redirect and route constant were removed. Active navigation had no DELTAQ entry; no backend DELTAQ endpoint or exclusive dependency remained. `docs/PROJECT_AUDIT.md` and stale archive claims were removed/updated. No other shared assets were removed. No git add, commit, history rewrite or broad cleanup was performed. There is no `/deltaq` route, API or archive directory. Sandhya, Monda and shared Earth Whisper source/data were not modified.

## Verification

- GherProof backend tests: **19 passed** across existing status, CDSE auth/refresh/TOTP/redirect, raster metadata/range resume, boundary state/geometry, and boundary API-handler tests (2 expected Rasterio not-georeferenced warnings from a deliberately invalid test raster).
- Frontend production build: **passed**; Vite reports the existing >500 kB bundle advisory.
- Oxlint (`npx oxlint src`): **exit 0 with warnings** for existing fast-refresh/state-in-effect/effect-dependency patterns in investigation/navigation source; no GherProof boundary component warning and no unrelated fixes were made.
- CDSE recovery script with no secrets: ran and reported 0/4 recovered without attempting authentication. Raster validator ran and reported 0 verified / pair unsuitable pending metadata.
- ResNet50 strict state loading and 256×256 output-shape smoke check passed. Fine-tuning and independent evaluation actually completed (not a smoke test).
- No event imagery or local boundary validation could be executed because those inputs are absent. Sandhya/Monda regression suites were not available as dedicated commands and their source/data were not modified.

See `docs/GHERPROOF_PHASE3_AUDIT.md` for initial repository state and inspected-file list. Pre-existing staged/unstaged/untracked changes remain unstaged and uncommitted.
