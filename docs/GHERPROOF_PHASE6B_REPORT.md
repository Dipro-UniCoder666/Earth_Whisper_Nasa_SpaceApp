# GherProof Phase 6B — Final Alternative Imagery Pixel Validation

**Run date:** November 12, 2026 UTC
**Result:** **CONDITIONALLY READY** for a controlled, experimental regional inference preflight; **not ready for quantitative or village-specific analysis**.
**No model inference, training, UI work, or checkpoint changes were made.**

## Decision

The actual candidate pixels show that useful, same-geometry alternatives exist. Six of seven Sentinel‑1 scenes are complete VV/VH reads, and two matched pre/post pairs have valid coverage across all 6,475,371 pixels in the provisional AOI. All 14 Sentinel‑2 SCL candidates were pixel-read; the selected Jan 10/20 pair shares Sentinel‑2B, tile 45QYF, relative orbit 133, and baseline 05.11, with 99.9839% common clear support.

The readiness status is **`conditionally_ready`**. Raster availability passes the regional experimental-data gate, but model input compatibility still needs a non-inference preflight: Sentinel‑1 RTC values are tagged linear intensity, while the existing GherProof segmentation checkpoints were trained with VV/VH in dB and checkpoint-specific normalization. That conversion, channel order, mask handling, and normalization have not been exercised against these RTC products. The AOI is also a provisional regional extent, not authoritative village boundaries. Thus this phase does not authorize quantitative or site-specific claims. The model benchmark metrics in previous reports remain benchmark-only and were not tested here.

## What was validated

| Sensor | Catalogue items | Unique acquisition dates | Pixel result | Selected evidence |
|---|---:|---:|---|---|
| Sentinel‑1 RTC | 7 | 7 | 6 complete scenes; one partial (Jan 7 VV read failed); 13/14 candidate VV/VH assets read | Jan 9→21, relative orbit 150 descending; Jan 12→24, relative orbit 12 ascending; each has 100% common valid VV/VH support |
| Sentinel‑2 L2A | 14 | 13 | All 14 SCL rasters read; 12 have ≥99.62% clear SCL support; Jan 5 has 0%, Jan 30 has 0.8436% | Jan 10→20, same Sentinel‑2B/orbit 133/tile/baseline; 99.9839% common clear support; B03/B04/B08 and native 20 m B11 read for both dates |

The acquisition-date chart reports data coverage per item as independent points. It does not join unlike Sentinel‑1 orbits or interpolate between observations.

![Per-acquisition coverage and regional support cells](../data/gherproof/regional/processed/phase6b/figures/phase6b_candidate_coverage.png)

![Actual valid-pixel footprints for matched pairs and clear SCL support](../data/gherproof/regional/processed/phase6b/figures/phase6b_pixel_validity_maps.png)

The Sentinel‑1 Jan 19 and Jan 31 products each retain a similar northwest/west-side missing wedge, at 89.771% and 90.303% valid pixels respectively. Jan 7 VH covers 89.961%; Jan 7 VV is unreadable, so that acquisition remains partial. The Jan 9/21 and Jan 12/24 pair masks are full-coverage on the chosen regional envelope. This is sensor-data coverage only; no village or field boundary is drawn.

## Coverage area and map grid

The Phase 6 AOI is the provisional search extent from [`GHERPROOF_REGIONAL_AOI_PROVENANCE.md`](GHERPROOF_REGIONAL_AOI_PROVENANCE.md), approximately 89.24–89.54°E and 22.92–23.11°N. It is a broad regional envelope (about 647.5 km²), not the legally or locally verified polygons for six villages. No spatial claim at named-village scale is supported by this phase.

| Product | CRS and grid | AOI pixels | Approximate AOI area |
|---|---|---:|---:|
| Sentinel‑1 clips and pair masks | EPSG:32645, 10 m, 3,111 × 2,156 | 6,475,371 | 647.537 km² |
| Sentinel‑2 SCL and selected B11 | EPSG:32645, 20 m, 1,555 × 1,078 | 1,618,843 | 647.537 km² |
| Selected Sentinel‑2 B03/B04/B08 | EPSG:32645, 10 m, 3,111 × 2,156 | 6,475,371 | 647.537 km² |

The rectangular bounds/grid include pixels outside the provisional AOI geometry; valid fractions use the AOI mask, not the full rectangular array. Area values are pixel-area summaries over that provisional mask and should not be treated as administrative area measurements.

## Sentinel‑1 findings

All seven saved item IDs were examined; orbit and pass are kept separate. Two exact same-platform, relative-orbit, direction, IW-mode, and VV/VH pairs passed a common valid-pixel intersection:

| Pair | Pre/post offsets from Jan 14 | Common valid support |
|---|---|---:|
| Jan 9→Jan 21, relative orbit 150 descending | −5/+7 days | 6,475,371 pixels; 647.537 km²; 100.000% |
| Jan 12→Jan 24, relative orbit 12 ascending | −2/+10 days | 6,475,371 pixels; 647.537 km²; 100.000% |

Jan 9/21 offers a more balanced pair of temporal offsets; Jan 12/24 has the closest pre-event acquisition. The orbit-114 Jan 7/19 pair is not complete because the Jan 7 VV COG did not read successfully. Jan 19/31 are each individually readable but have a roughly 10% wedge missing in the AOI and do not repair the incomplete Jan 7 comparison. Alternative geometries are not combined.

Source RTC metadata reports 10 m float32 linear intensity samples, nodata `-32768`, and a “calibrated and terrain corrected” band description. It does not provide a physical units field. The outputs are clipped source RTC values; no dB conversion or intensity normalization was performed. They are not probability values, flood labels, or direct measures of water depth.

See [`GHERPROOF_SENTINEL1_CANDIDATE_VALIDATION.md`](GHERPROOF_SENTINEL1_CANDIDATE_VALIDATION.md) for every candidate date, valid fraction, the Jan 7 asset-read failure and pair-level coverage details.

## Sentinel‑2 findings

All 14 SCL COGs are pixel-verified. The dates cover Jan 3–30 with two distinct Jan 10 acquisitions (relative orbits 033 and 133), giving 13 unique dates. A conservative clear mask uses SCL classes 2/4/5/6, excluding cloud, shadow, snow, unclassified, defective and nodata classes. This only reports whether input pixels pass the selected data-quality mask; class 6 is retained as an SCL class, not treated as an event label.

Jan 5 has no clear-class pixels in the AOI, and Jan 30 has only 0.8436% clear support. The remaining 12 acquisitions range from 99.6242% to 99.9968%. Twenty-four same-tile/relative-orbit pre/post combinations were evaluated; Jan 10→Jan 20 was selected because it is a same-platform Sentinel‑2B pair on orbit 133, tile 45QYF, and baseline 05.11. Its common clear area is 647.4332 km² at 20 m. B03/B04/B08 at 10 m and B11 at 20 m were extracted for each selected date.

The extracted band assets are stored integer samples retained as float32 with nodata support. Rasterio reports scale 1 and offset 0; no reflectance rescaling was applied. Do not interpret the values as normalized reflectance without an explicit scale step. Sentinel‑2 remains a separate optical evidence stream and is not numerically interchangeable with Sentinel‑1 RTC intensity.

See [`GHERPROOF_SENTINEL2_PIXEL_VALIDATION.md`](GHERPROOF_SENTINEL2_PIXEL_VALIDATION.md) for all 14 SCL coverages, class counts, the selected pair, band grids and value interpretation.

## Independent raster QC

`scripts/gherproof/phase6b/build_report_assets.py` reopened all 40 GeoTIFFs written in Phase 6B using Rasterio and recorded checksums, CRS, transform, bounds, dimensions, resolutions, dtype, nodata, band descriptions, valid/nodata counts, min/p02/median/p98/max, and NaN/infinite counts. All 40 files opened successfully, all are EPSG:32645, the set uses expected 10 m and 20 m grids, and no NaN or infinite pixel values were found.

The 40 outputs comprise six two-band Sentinel‑1 scene clips, two Sentinel‑1 pair masks, fourteen SCL rasters, fourteen SCL clear masks, and four selected-pair Sentinel‑2 band products (two 10 m three-band files and two 20 m B11 files). Checksum and metadata records are in [`phase6b_raster_qc_manifest.json`](../data/gherproof/manifests/phase6b_raster_qc_manifest.json). Pixel-validity outputs are in `data/gherproof/regional/processed/phase6b/`.

Both original Phase 6 catalogue manifests retain their discovery records and include additive `phase6b_pixel_validation` summaries. `phase6_regional_valid_coverage.json` likewise keeps the earlier local-only evidence and adds Phase 6B regional results; no previous coverage result was replaced.

## Readiness and next step

**Gate: `conditionally_ready`.** The images support a controlled experimental regional inference preflight, after a separately documented check that converts positive Sentinel‑1 RTC intensity values to dB, applies the exact checkpoint VV/VH order and normalization, masks nodata consistently, and confirms the raster input range. Keep relative orbits separate. Do not call preflight success a water detection or validation result.

Quantitative/event conclusions still require validated local boundaries, independent field or authoritative reference labels, event-level accuracy evaluation, and review of the Sentinel‑1 RTC versus training-data domain shift. The Jan 7 VV read failure remains a blocker only for the orbit-114 Jan 7/19 pair; it does not block the two fully covered alternative pairs. No final model accuracy or event-specific performance was measured here.

## Files and reproduction

| Artifact | Purpose |
|---|---|
| [`phase6b_sentinel1_pixel_validation.json`](../data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json) | Seven exact S1 candidates, source raster metadata, per-band pixel statistics and compatible pairs |
| [`phase6b_sentinel2_pixel_validation.json`](../data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json) | Fourteen S2 candidates, SCL class counts, clear masks and selected band provenance |
| [`phase6b_regional_coverage_assessment.json`](../data/gherproof/manifests/phase6b_regional_coverage_assessment.json) | AOI, per-scene and pair coverage summary |
| [`phase6b_raster_qc_manifest.json`](../data/gherproof/manifests/phase6b_raster_qc_manifest.json) | Independent local Rasterio metadata, statistics, validity and checksums for all Phase 6B GeoTIFFs |
| `scripts/gherproof/phase6b/validate_candidates.py` | Remote STAC/range/COG validation and local product generation |
| `scripts/gherproof/phase6b/build_report_assets.py` | Local raster QC, additive manifest updates, temporal coverage and validity figures |

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel1
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel2
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/build_report_assets.py
```

The first two commands require network access to Planetary Computer; SAS query tokens are held in memory and omitted from saved manifests. `--resume` preserves completed Sentinel‑1 clips and retries incomplete scenes. `--only-item <item-ID>` limits a retry to one known STAC item. The report-assets command is local and performs no inference. Phase 6B did not modify existing checkpoints, pre-Phase-6B raster products, frontend features, Sandhya/Monda work, or the archived DELTAQ project.
