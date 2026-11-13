# GherProof event-scene suitability assessment

**Phase 4 update (2026-11-12): `not_evaluated`.** The current run found no CDSE credentials in the process environment, no repository `.env.cdse.local`, and no configured `GHERPROOF_CDSE_ENV_FILE`. The recovery script followed its no-credentials branch: it made no authentication or product request, and verified 0/4 assets. Therefore no actual raster coverage, alignment, pixel-validity, radiometry, calibration, or terrain-correction assessment is possible. The Jan 7/19 metadata remains a plausible catalogue pair only. The enclosure remains `not_delineated`.

**Phase 4B update:** the same acquisition dates were subsequently found and accessed as Microsoft Planetary Computer RTC alternatives; see `docs/GHERPROOF_PHASE4B_REPORT.md`. This does not change the historical CDSE asset statuses. The RTC pair is conditionally suitable for backscatter comparison only over 18.13% common valid coverage of the provisional locality window. Target-enclosure coverage remains unknown because no verified enclosure location/boundary exists.

**Assessment: BLOCKED; no validated pre/post raster pair is currently available.** The January 7 and January 19 records are catalogue assets only. The local manifest contains four CDSE OData COG measurements with `authentication_blocked`, and `verify_event_imagery.py` reports 0 verified assets. No local VV/VH event rasters were present at audit time. This document therefore makes no claim about their measured CRS, coverage, pixel grid, nodata, calibration, noise masks, or terrain correction.

## Catalogue scene identities

| Role | Acquisition UTC | Product identifier | Platform | Mode/product | Relative orbit | Direction | Polarizations | Timing to reported Jan 14 |
|---|---|---|---|---|---:|---|---|---|
| Candidate pre-event | 2026-01-07 12:04:28.028694 | `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_6998_COG` | S1A | IW / GRDH, catalogue processing level L1 | 114 | Ascending | VV, VH | 7 days before |
| Candidate post-event | 2026-01-19 12:04:27.012308 | `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_E3D6_COG` | S1A | IW / GRDH, catalogue processing level L1 | 114 | Ascending | VV, VH | 5 days after |

Each scene has two separate COG measurement links. Catalogue lengths total 2,472,781,521 bytes across four assets. Their 36-character hex checksum strings are not identified standard digests. Downloaded-file SHA-256 and local raster reads do not exist yet.

## Scientific suitability

### What appears favorable in catalogue metadata

- Both candidate acquisitions use the same Sentinel‑1 platform, IW GRD High Resolution product family, relative orbit 114, ascending pass and dual VV/VH polarizations.
- The acquisition dates bracket the reported event, with one scene 7 days before and one 5 days after.
- Relative-orbit consistency makes similar incidence/viewing geometry plausible.

### What remains unverified

- Authenticated download and successful content/raster decoding.
- Whether all four footprints cover the actual enclosure and surrounding agricultural area; the only locality extent is broad and the enclosure point/polygon is unknown.
- CRS, raster resolution, affine alignment, valid-data overlap, edge/no-data and quality masks.
- Exact radiometric quantity/units, scaling, calibration provenance, thermal-noise handling, border-noise removal, terrain correction and DEM/geocoding baseline.
- Whether COG values are calibrated/terrain-normalized to a common quantity. A GRDH label or COG filename alone does not establish analysis-ready radiometry.
- Pixel-level co-registration and stable target geometry after preprocessing.

The two dates are a plausible catalogue pair, but **they cannot yet support a scientific pre/post change result**. If downloaded assets prove to be comparable calibrated measurements and adequately cover a reviewed AOI, process both with the same documented SNAP/ESA-compatible chain, apply identical masks, and resample to a common projected grid. If the COGs do not expose adequate calibration provenance or correction support, retrieve original SAFE GRD products or a consistently generated RTC pair from the same orbit. Do not compare raw digital numbers as water evidence.

Even a valid pair would show a change in radar backscatter, not prove a breach. Rainfall, crop phenology, soil moisture, irrigation, aquaculture management, wind/water roughness and tidal/regional water-level changes remain alternative explanations. Local boundary and reference data are required before area accounting.

## Reproduction

With local CDSE variables configured, run:

```powershell
py scripts/gherproof/recover_event_imagery.py
py scripts/gherproof/verify_event_imagery.py
```

The machine-readable outputs are `data/gherproof/manifests/event_imagery_manifest.json` and `event_imagery_validation.json`. The validator updates an asset to `verified` only after catalogue byte-length validation, Rasterio open, georeferencing checks and a real pixel read. Pair-level suitability remains false until radiometry/processing metadata and adequate coverage are verified.
