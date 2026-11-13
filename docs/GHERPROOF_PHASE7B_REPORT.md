# GherProof Phase 7B — Independent Validation and Model-Readiness Report

## Executive decision

**Model readiness: `exploratory_only`. Phase 8 impact quantification: NOT APPROVED.** The work completed the requested evidence audit, found exact same-acquisition Sentinel-1 GRD catalog records, measured the existing RTC/training distribution and texture differences, audited all eight model probability rasters, rebuilt cross-sensor comparison rasters on the correct 20 m grid, and prepared a blind 450-point optical annotation package. No human labels have been entered, so independent local evaluation and model selection were not possible. No new model was trained and no affected-area result was generated.

## Existing Phase 7 model outputs audited

Two unchanged checkpoint files were re-hashed and matched their manifests:

| Model | Architecture | SHA-256 | Threshold | Input normalization |
|---|---|---|---:|---|
| Scratch | AttentionUNet | `fcb244de72d51da9760d089ed5909d0cfdfda41af2e8def76aae203aadf5a040` | 0.5 | VV/VH means [-10.2318, -17.2022], std [4.1367, 4.9157] |
| Pretrained | ResNet50SARUNet | `084b41f06ea0f1049b53c6708fed0a78e081a38704677dce7e172e67e2b8d9f0` | 0.5 | VV/VH means [-12.5485, -20.1924], std [5.2570, 5.9115] |

Both use VV then VH, positive finite linear RTC Gamma0 converted once with `10*log10`, clipped to [-60,20] dB, model-specific z-score normalization, 256-pixel patches and 64-pixel overlap. The common valid mask is applied and invalid output pixels remain nodata. All eight outputs are float32 probability rasters on the same EPSG:32645 grid (10 m; 3,111 × 2,156), with 6,475,371 valid pixels and 231,945 rectangular-grid invalid pixels (96.54% valid-grid fraction). This is the provisional regional AOI raster coverage, not verified village-boundary coverage.

The four acquisition dates and geometry-specific comparisons are:

| Geometry pair | Before | After | Event offsets | Interpretation |
|---|---|---|---|---|
| Ascending, relative orbit 12 | Jan 12, 2026 | Jan 24, 2026 | -2 d / +10 d | Pre image is closer to Jan 14; temporal offsets are asymmetric. |
| Descending, relative orbit 150 | Jan 9, 2026 | Jan 21, 2026 | -5 d / +7 d | More balanced interval, but different view geometry from ascending pair. |

Each pair has 6,475,371 common valid pixels in the Phase 6B pair mask. They must remain separate geometry series; neither pair alone establishes event causality.

### Probability outputs and model disagreement

All model probabilities were finite on valid pixels and within [0,1]. The output-audit manifest provides complete per-scene min/max/mean/standard deviation/percentiles and checksums. At threshold 0.5, model class disagreement (XOR among common valid pixels) is material:

| Pair | Date | Disagreement fraction |
|---|---|---:|
| Ascending rel 12 | Jan 12 | 13.41% |
| Ascending rel 12 | Jan 24 | 16.34% |
| Descending rel 150 | Jan 9 | 9.75% |
| Descending rel 150 | Jan 21 | 13.44% |

The 4×4 grid diagnostic shows disagreement is spatially heterogeneous, with tile fractions approximately 2.9%–21.0% across the displayed blocks. These are model-vs-model differences, not error rates. The side-by-side probability distribution also differs materially between models; no winner is selected without local reference labels.

![Phase 7 model disagreement audit](../data/gherproof/processed/phase7/figures/phase7b_model_disagreement_audit.png)

## Exact GRD counterparts and domain shift

All four RTC acquisitions have exact `sentinel-1-grd` item counterparts, each with VV and VH assets. Header inspection opened all eight assets, and seven of eight sample windows were readable. The one failed sample was Jan 12 VH. All carry no CRS/meaningful geotransform, `uint16` type, and Level 1 GRD TIFF tags. SAFE manifests plus polarization-specific calibration LUT and noise XMLs exist and are checksummed. A STAC asset description says terrain correction was applied, but the TIFF metadata and Level 1 sidecars conflict. No full GRD scene was downloaded or processed to analysis-ready calibrated/geocoded backscatter; the current environment lacks SNAP/GPT and GDAL Python bindings. Thus GRD did not yet improve demonstrated compatibility.

For the Sen1Floods11 training sample versus RTC dB inputs, the P02/median/P98 values are:

| Channel | Training dB | RTC dB | Median shift (RTC−training) | Wasserstein-1 | KS D |
|---|---|---:|---:|---:|---:|
| VV P02 / median / P98 | -22.309 / -9.614 / -3.479 | -21.034 / -9.305 / -2.803 | +0.309 dB | 0.764 dB | 0.0872 |
| VH P02 / median / P98 | -31.267 / -16.174 / -10.306 | -25.736 / -16.418 / -9.987 | -0.244 dB | 0.860 dB | 0.0756 |

These are descriptive pooled distributions, not proof of equivalence or classifier validity. Spatial adjacent-difference RMSE also differs; VH’s low-end tail is notably less negative in RTC. GRD raw DN was excluded from comparison. Details and fixed-scale visual are in [domain-shift validation](GHERPROOF_DOMAIN_SHIFT_VALIDATION.md).

## Independent optical annotation package

A QGIS-compatible GeoPackage was prepared with 450 points (150 calibration, 150 validation, 150 held-out test) in EPSG:32645. Ten blind-coded proxy strata have up to 15 samples per stratum per split. Selection uses seed 20261113, retained inclusion probabilities/inverse-probability weights, complete 5 km spatial block columns, and nominal 1 km guards between west/center/east split bands. The package has blank independent pre/post label fields and includes no prediction probabilities or model names. A separate gallery provides Jan 10 and Jan 20 false-color optical context with no model overlay.

**Human labels completed: 0 of 900 pre/post slots.** Therefore `local_validation_status = human_review_pending`, metrics are null, thresholds are not locally calibrated, and neither model is selected. The test strip is only representative of its designated spatial domain; the guard does not eliminate long-range spatial autocorrelation. Optical review is a reference interpretation, not absolute ground truth.

See [annotation guide](GHERPROOF_OPTICAL_REFERENCE_LABELING.md), GeoPackage `data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg`, and public sampling design `data/gherproof/reference/phase7b/sampling_design_manifest.json`. The internal mapping of blind stratum codes is stored separately in `data/gherproof/manifests/phase7b_sampling_design_manifest.json` and must not be supplied to a blinded annotator.

## Cross-sensor raster correction

Audit found that original Phase 7 NDWI agreement/change rasters were written using a 10 m profile although their arrays were evaluated at 20 m. The previously recorded array counts were based on 20 m values, but those raster files are incorrectly georeferenced/resized. They remain untouched for provenance. A new independent Phase 7B build produced 48 corrected GeoTIFFs covering 24 comparisons on the selected-pair native 20 m EPSG:32645 grid. Every output’s grid and class codes were checked. This fixes raster alignment only; optical indices are still not reference truth, and agreement is not confirmation of flood.

Manifest: `data/gherproof/manifests/phase7b_cross_sensor_validation.json`; outputs: `data/gherproof/processed/phase7b/cross_sensor/`.

## Tests, reproducibility, and blockers

Completed outputs and verification:

- Phase 7B output audit passed: eight probability rasters reopened, hashes, masks, dimensions, nodata and valid counts checked.
- Exact GRD STAC matching and metadata extraction completed for four items; asset header inspection partial (8/8 headers, 7/8 sample reads, 0 full scenes processed).
- Domain distribution/texture analysis ran on 210 training chips and four RTC scenes; deterministic manifest and fixed-range figure created.
- Blind sampling package contains 450 features and 900 blank label slots; split design and context chips verified in the package-generation checks.
- Corrected cross-sensor build contains 24 comparisons/48 GeoTIFFs aligned to the 20 m grid; outputs were reopened and checked.
- Focused test suite: `tests/test_gherproof_phase7b.py` and `tests/test_gherproof_phase7_inputs.py` — **22 passed**.
- GeoPackage integrity: SQLite tables and GeoPackage feature/geometry registrations present; `samples` has 450 EPSG:32645 POINT features, and all 450 pre-label plus all 450 post-label slots are blank. Nine Phase 7B Python scripts compile successfully.

No GRD calibration/terrain-correction workflow was run, no human labels exist, and no independent local evaluation was performed. These are scientific prerequisites, not merely software gaps.

### Reproduction commands

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase7b/audit_phase7_outputs.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase7b/domain_shift_metrics.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase7b/rebuild_cross_sensor_layers.py
Push-Location backend
.venv/Scripts/python.exe -m pytest tests/test_gherproof_phase7b.py tests/test_gherproof_phase7_inputs.py -q
Pop-Location
```

### Required next evidence before reconsidering Phase 8

1. Complete blinded human labels for both optical dates, with confidence, annotator, review date, source and notes; review ambiguous wet soil, turbid/shallow water, ponds, shadows and vegetation as uncertain when necessary.
2. Evaluate both models on the exact same spatially held-out references with sampling weights; tune thresholds only on calibration data and keep the final test untouched.
3. Obtain independent field/GIS references and authoritative village/enclosure boundaries before attributing any mapped water to an incident or calculating affected area.
4. If investigating GRD compatibility, run a pinned SNAP processing chain and validate calibration, geocoding, masks and output grid before model inference.
5. Resolve the Phase 7 NDWI raster defect by using the newly generated corrected Phase 7B files for any future map display or pixel inspection.

**Final:** exploratory predictions only; no locally validated water map; no affected-area or other impact estimate approved.
