# GherProof Phase 4 — Actual Sentinel-1 event data recovery and validation

**Run date:** 2026-11-12
**Outcome:** BLOCKED AT AUTHENTICATION; no Sentinel-1 event product was downloaded or assessed as a raster.

This report records the CDSE-only recovery attempt at that phase. The alternative public Planetary Computer RTC retrieval, actual clips, and current scene suitability are documented separately in `docs/GHERPROOF_PHASE4B_REPORT.md`; the original CDSE records remain unchanged.

## Executive result

The Phase 3 CDSE recovery implementation and validation scripts were inspected and exercised. On the user's follow-up run, the process environment, Windows user-level variables, and machine-level variables had no `CDSE_USERNAME`, `CDSE_PASSWORD`, `CDSE_TOTP_CODE`, `CDSE_TOTP_SECRET`, or legacy `CDSE_TOTP` values. The configured alternate dotenv path was unset, and the repository `.env.cdse.local` did not exist. Consequently, the recovery script took its explicit no-credentials branch and made **no identity-provider or product request**. Its exact per-asset blocker is `CDSE credentials are not configured; no request attempted`. It recorded the four exact assets as `authentication_blocked`; raster validation found 0/4 verified assets.

The acceptance criteria requiring actual product recovery and raster-based scene-compatibility assessment are not met. Independent preparation, manifest refresh, no-credentials behavior, current suitability assessment, and the local GherProof test suite were completed. There is no responsible way to claim actual coverage or compare rasters in this run.

## Authentication findings

`CDSEAuth._read_values()` reads allowed variables from process environment and `.env.cdse.local` (or a path named by `GHERPROOF_CDSE_ENV_FILE`), then environment values take precedence. No values were printed or persisted. `credentials_available` requires username and password.

The implementation resolves the `CDSE_TOTP` ambiguity as follows:

- `CDSE_TOTP_CODE` is a current short-lived authenticator code submitted as OAuth `totp`.
- `CDSE_TOTP_SECRET` is a Base32 seed; the code generates a current TOTP locally.
- Legacy `CDSE_TOTP` is treated as a current one-time code and copied to `CDSE_TOTP_CODE`; it is **not** treated as a persistent secret.
- Supplying both the code and seed raises a safe error.

Authentication **did not succeed and was not attempted** because username/password were absent from all checked scopes. No invalid-credential or external CDSE response occurred, so there is no OAuth failure code to report. The existing PowerShell recovery and raster-validation workflows ran once in their no-credentials mode and produced 0 recovered / 0 validated assets. The exact local PowerShell configuration steps are in `docs/GHERPROOF_CDSE_SETUP.md`; credentials must be entered locally and never pasted in chat.

The prior `event_scene_access_checks.json` records unauthenticated 1 KiB Range probes on both VV assets returning HTTP 401 (zero body bytes); VH URLs were not independently probed. This is an authorization result, not evidence that CDSE products are unavailable. Phase 4 did not repeat those unauthenticated requests.

## Asset recovery outcomes

All four records below are separate polarization-specific COG measurement assets. Catalogue metadata identifies Sentinel-1A, IW, GRDH, L1, relative orbit 114, ascending. Each date has the same scene identifier across VV and VH. Catalogue sizes/checksum strings are not local-file integrity checks; no local SHA-256 exists because no download occurred.

| Product identifier | Acquisition UTC | Orbit / direction | Polarization | Catalogue bytes | Download status | Checksum / raster status |
|---|---|---|---|---:|---|---|
| `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_6998_COG` | 2026-01-07 12:04:28.028694Z | 114 / ascending | VV | 664,403,282 | `authentication_blocked` | No local checksum; raster not inspected |
| `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_6998_COG` | 2026-01-07 12:04:28.028694Z | 114 / ascending | VH | 572,402,839 | `authentication_blocked` | No local checksum; raster not inspected |
| `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_E3D6_COG` | 2026-01-19 12:04:27.012308Z | 114 / ascending | VV | 662,506,694 | `authentication_blocked` | No local checksum; raster not inspected |
| `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_E3D6_COG` | 2026-01-19 12:04:27.012308Z | 114 / ascending | VH | 573,468,706 | `authentication_blocked` | No local checksum; raster not inspected |

The provider checksum values are 36-character hex strings and remain algorithm `unidentified`; they are not relabelled as MD5/SHA. The actual raw event acquisition directory contains no Jan 7/19 VV/VH product. Other raw files under `data/gherproof/raw/` belong to Sen1Floods11 training data and are not event imagery.

## Pre/post compatibility decision

**Classification: `not_evaluated`.** Catalogue identity supports a candidate pairing: both are S1A, relative orbit 114, ascending, IW/GRDH, with VV and VH records; Jan 7 is seven days before and Jan 19 five days after the reported Jan 14 incident. These are catalogue-level facts only.

Actual CRS, dimensions, resolution, geotransform, footprint, VV/VH grids, valid-data masks, study-window overlap, radiometric quantity/units, calibration, noise correction, terrain correction, co-registration, and processing baselines remain unknown. The existing validation manifest correctly records `suitable_for_change_inference: false`; false here means suitability is not established, not that measured raster incompatibility was found. No common-grid outputs were created.

## Study-area coverage

The only available search extent is a **provisional broad locality box**, not a verified enclosure boundary. With no local event rasters, scene coverage of the locality, enclosure, or surrounding agricultural land is **not measurable**. Valid-pixel fraction is also **not measurable**. The available Sentinel-2B context is a visual 10 m crop acquired 2026-01-13, with scene-level cloud fraction 0.000384; pixel-level cloud/shadow screening is not documented, and this optical image is not evidence of SAR coverage. It was not used to infer an enclosure polygon. No precise Pallimangal boundary is asserted.

## Outputs and provenance

- Updated catalogue-derived asset status: `data/gherproof/manifests/event_imagery_manifest.json`.
- Refreshed machine-readable raster/scene assessment: `data/gherproof/manifests/event_imagery_validation.json` (classification `not_evaluated`).
- Existing provenance/setup: `docs/GHERPROOF_CDSE_SETUP.md`.
- No new event raster, checksum, pre/post composite, aligned grid, water mask, or affected-area product was created. Existing model checkpoints were not modified; no inference or training ran.

The raw files are still expected under `data/gherproof/raw/event_sentinel1/<date>/{VV,VH}.tif` after authenticated retrieval. The current downloader preserves already verified products, resumes `.part` files using HTTP Range when supported, checks byte counts, computes SHA-256, opens each COG with Rasterio and reads a pixel sample. A successful HTTP response alone does not mark a product verified.

## Remaining requirements before inference

1. Configure CDSE username/password and, only when the account requires it, a current `CDSE_TOTP_CODE` (or a locally protected `CDSE_TOTP_SECRET`) using the setup guide.
2. Rerun `py scripts/gherproof/recover_event_imagery.py`; confirm all four assets individually reach a truthful status and preserve raw products/checksums.
3. Run `py scripts/gherproof/verify_event_imagery.py`; inspect actual metadata, VV/VH consistency, scene overlap and valid-pixel coverage against the provisional area.
4. Establish the input radiometry and processing baseline. If the COG metadata does not demonstrate compatible calibrated measurements, retrieve/use a consistently processed Sentinel-1 product pair rather than comparing raw values.
5. Decide pair suitability from those measurements. Only if appropriate, make reproducible, identically processed analysis-ready grids with explicit masks and provenance.
6. Obtain and review a defensible enclosure boundary plus permanent-water and agricultural references before any local inference or impact-area accounting. The benchmark models remain unapproved for quantitative Sujatpur reporting.

Even a suitable radar pair would indicate backscatter differences, not establish breach cause or operational failure. Rainfall, crop stage, soil moisture, irrigation, aquaculture management, wind/water roughness, tidal or local water-level conditions remain alternative explanations.

## Verification

| Check | Result |
|---|---|
| Current process/user/machine credential check | Passed safely: all required values absent; no secret values printed |
| Missing-credential recovery path | Passed: 4 exact records preserved, 0 verified, authentication blocked; no authentication/product request |
| Raster validation | Passed as a no-data assessment: 0 validated assets; pair suitability false/not established |
| Authentication and event-imagery tests (follow-up run) | 11 passed; 2 expected Rasterio `NotGeoreferencedWarning` warnings from a deliberately invalid test raster |
| External authentication / download | Not attempted; credentials absent (not an authentication rejection) |
| Actual raster metadata / footprint / alignment / masks | Blocked; no event products downloaded |
| Processing / event inference / model training | Not run; correctly gated |

Reproduce local checks from the repository root (after creating the backend environment if needed):

```powershell
py scripts/gherproof/recover_event_imagery.py
py scripts/gherproof/verify_event_imagery.py
Push-Location backend
.venv\Scripts\python.exe -m pytest tests/test_gherproof.py tests/test_gherproof_cdse_auth.py tests/test_gherproof_boundary.py tests/test_gherproof_boundary_api.py tests/test_gherproof_event_imagery.py -q
Pop-Location
```

## Repository safety

The Phase 4 event-imagery manifest and validation manifest were refreshed; `scripts/gherproof/verify_event_imagery.py` now records explicit `not_evaluated` / conditional / unsuitable scene classifications based on available raster checks. Added this report and updated `docs/GHERPROOF_EVENT_IMAGERY_VALIDATION.md` and `docs/GHERPROOF_CDSE_SETUP.md` to clarify the legacy TOTP alias. No authentication implementation defect was found, so the authentication code was not rewritten. No destructive Git command or staging operation was used. Pre-existing staged, unstaged and untracked work was preserved. Sandhya and Monda were not modified; DELTAQ was not reintroduced.
