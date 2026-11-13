# GherProof Optical Weak-Reference Methodology — Phase 8B

## Purpose and interpretation

This pipeline creates automated optical reference *indicators* to compare against already-produced Sentinel-1 model outputs. The labels are derived only from Sentinel-2 L2A reflectance, its Scene Classification Layer (SCL), NDWI, and MNDWI. No SAR prediction, model mask, checkpoint, or model disagreement product is used to assign the optical classes or choose their thresholds.

The result is not human ground truth, field validation, proof of flood extent, or a local model-accuracy estimate. SCL class 6 can include permanent water and aquaculture ponds. A class-6 pixel is only retained as `weak_water` if both optical indices support it. These indicators cannot distinguish incident-related floodwater from ordinary surface water.

## Input products and radiometry

The selected products are the Sentinel-2B L2A items on MGRS tile 45QYF, relative orbit 133:

| Date | Exact acquisition time (UTC) | Item | Processing baseline |
|---|---|---|---|
| 2026-01-10 | 04:30:49.024Z | `S2B_MSIL2A_20260110T043049_R133_T45QYF_20260110T065859` | 05.11 |
| 2026-01-20 | 04:30:09.024Z | `S2B_MSIL2A_20260120T043009_R133_T45QYF_20260120T062559` | 05.11 |

Both acquisitions precede/follow the reported January 14 date, but neither is contemporaneous with the incident. Per-product SAFE metadata recorded `BOA_QUANTIFICATION_VALUE = 10000` and `BOA_ADD_OFFSET = -1000` for the selected B03, B08, and B11 bands in each product. The source stacked rasters were inspected for their band descriptions/order and masks. B03 and B08 are 10 m; B11 is 20 m. Source DN 0 and source masks are invalid.

The output is computed from the existing original stored-value rasters using `(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE`. The prior Phase 7 reflectance outputs were not converted again or overwritten. Their values were independently cross-checked against the source DN conversion: for B03, B08, and B11 on both dates, the maximum absolute difference over overlapping valid pixels was **0.0** and every comparison was within `1e-6`.

## Common comparison grid

All primary optical weak-reference labels, indices, optical-change candidates, and SAR/optical comparisons use the native B11 grid: **EPSG:32645, 20 m, 1556 × 1079 pixels**. B03 and B08 reflectance are area-averaged from their 10 m source grids to that grid. A 20 m destination cell is accepted only when all contributing 10 m source pixels are valid. MNDWI uses B11 on its native grid. NDWI is recomputed from the 20 m averaged Green and NIR reflectances, so it is also correctly represented on the 20 m comparison grid. Existing 10 m reflectance and NDWI products remain untouched.

Normalized-difference calculations require finite, nonnegative reflectances and a denominator of at least **0.02**. This avoids unstable ratios for near-zero illumination and excludes negative offset-corrected reflectance from water-index decisions. Clear SCL context with valid source bands but unusable low-signal indices remains `uncertain`; source NoData stays `invalid`.

## Fixed thresholds and label rules

The primary index thresholds were fixed before loading or comparing any Sentinel-1 predictions: **NDWI ≥ 0.0 and MNDWI ≥ 0.0** for positive support. Zero is the neutral sign threshold for normalized differences. It is combined with SCL rather than used as a stand-alone water test. The thresholds were not tuned to maximize model agreement.

| Optical class | Rule |
|---|---|
| `weak_water` | SCL 6 and both NDWI and MNDWI are at least 0.0. |
| `weak_nonwater` | SCL 4 or 5 and both NDWI and MNDWI are below 0.0. |
| `uncertain` | SCL 2 or 7; contradictory SCL/index evidence; or clear SCL context with source bands valid but unusable low-signal index values. |
| `invalid` | SCL 0, 1, 3, 8, 9, 10, or 11; source NoData/invalid pixels; or no valid observation. |

SCL class 3 (cloud shadow), 8/9 (cloud), 10 (cirrus), and 11 (snow/ice) are not treated as clear evidence. Class 2 is a dark-area class and class 7 is unclassified; neither is forced into a binary label. The SCL class raster is retained separately for inspection.

### Sensitivity

The same dual-index sign threshold is shifted together to **−0.05** and **+0.05**, without model feedback. Resulting weak-water counts were:

| Date | Threshold −0.05 | Threshold 0.00 (primary) | Threshold +0.05 |
|---|---:|---:|---:|
| Jan 10 | 190,155 | 175,119 | 157,425 |
| Jan 20 | 167,861 | 154,536 | 139,038 |

Changing the threshold by 0.05 changes the water-candidate count by +15,036/−17,694 pixels on Jan 10 and +13,325/−15,498 on Jan 20. The resulting weak-water counts are threshold-sensitive; they are not estimates of flooded area. Full water/nonwater/uncertain/invalid counts for all six threshold-date combinations are in `data/gherproof/manifests/phase8b_weak_reference_manifest.json`.

## Temporal change categories

The January 10 and January 20 classes are compared only where both dates contain valid clear observations. The change raster uses:

| Code | Meaning |
|---:|---|
| 1 | `persistent_water_candidate` |
| 2 | `possible_new_water_candidate` (Jan 10 weak-nonwater → Jan 20 weak-water) |
| 3 | `possible_water_loss_candidate` |
| 4 | `stable_nonwater_candidate` |
| 5 | `uncertain_change` (either date is uncertain) |
| 0 / NoData | Invalid or unavailable observation |

With these rules the observed pixel counts were 144,170 persistent-water candidates, 671 possible-new-water candidates, 1,316 possible-water-loss candidates, 900,758 stable-nonwater candidates, 570,341 uncertain changes, and 61,668 invalid. The low count of possible new-water candidates is not a flood estimate. Two-date optical differences can reflect crop/vegetation state, aquaculture/pond operation, irrigation, wet soil, rainfall, tide, turbidity, illumination, or classification errors.

## Sentinel-1 comparison

The four actual Phase 7 RTC acquisitions are matched to the closest of the two optical acquisitions by UTC time, without implying simultaneity. The same 20 m B11 comparison grid is used. Each 10 m probability raster is area-averaged to 20 m, and a cell is valid only when all four contributing 10 m SAR pixels are valid. The existing model threshold is held at 0.5. Optical `uncertain` classes are retained in the uncertainty layer and excluded from binary comparison metrics.

Metrics use exact names `weak_reference_agreement`, `weak_reference_positive_agreement`, and `weak_reference_negative_agreement`. A “positive” is an optical `weak_water` candidate, not verified floodwater. These are consistency measures against the selected optical rules, not accuracy, precision, recall, or F1 against ground truth.

The comparison manifest provides confusion counts, common-valid counts, optical uncertain/excluded counts, invalid coverage counts, 5 km block summaries, and SCL context breakdowns for each model and acquisition. Block ranges are descriptive spatial variation only; adjacent pixels are spatially dependent, and no pixel-independent confidence interval is calculated.

## Reproduction

From the repository root using the project environment:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase8b/run_weak_reference_pipeline.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase8b/prepare_demo_scenario.py
```

The first script reads existing Phase 6B source rasters and Phase 7 products/manifests and writes only under `data/gherproof/processed/phase8b/` and `data/gherproof/manifests/phase8b_*`. The second builds the static demonstration scenario from current registry records and Phase 8B manifests. Neither script trains or alters model weights, changes the Phase 7 annotation package, or writes frontend code.
