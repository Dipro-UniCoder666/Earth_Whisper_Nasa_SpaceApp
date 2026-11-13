# GherProof Phase 8B — Automated Optical Weak-Reference Validation and Demonstration Preparation

**Completion:** Optical weak-reference products, existing-model comparison, evidence-registry updates, API integration, and Phase 9 demonstration data have been generated and tested. No new model was trained. No frontend code was changed.

## 1. Audit, preservation, and inputs

Reviewed the Phase 8 report, evidence methodology, Phase 7/7B/7C reports, optical corroboration and annotation workflow, domain-shift validation, evidence registry, inference and raster-QC manifests, reflectance/index products, SCL masks, eight existing probability rasters, and existing disagreement layers. Phase 7's 450 point IDs, frozen spatial splits, original annotation products, model checkpoints, source imagery, prior outputs, and frontend were preserved.

The source Sentinel-2 L2A products are S2B, baseline 05.11, MGRS tile 45QYF, relative orbit 133. Exact acquisition times from product metadata are Jan 10 **04:30:49.024Z** and Jan 20 **04:30:09.024Z**. For both products, selected B03/B08/B11 reflectance metadata specify quantification 10,000 and additive offset −1,000. Source DN zero/masked cells are treated as NoData. The formula `(DN + BOA_ADD_OFFSET)/BOA_QUANTIFICATION_VALUE` was applied to the source stored-value rasters for this derivation. A pixel-level cross-check against existing Phase 7 reflectance outputs found **zero difference** for B03, B08, and B11 on both dates; no original Phase 7 raster was overwritten or converted twice.

## 2. Optical weak-reference products

The primary comparison grid is the native B11 grid (**EPSG:32645, 20 m, 1556 × 1079**). B03/B08 reflectance were area-averaged from 10 m to 20 m; all four source pixels must be valid. NDWI was recalculated from the 20 m Green/NIR reflectances and MNDWI from 20 m Green plus native B11. Negative reflectance and normalized-difference denominators below 0.02 do not support a binary weak label.

Thresholds were fixed at NDWI ≥ 0 and MNDWI ≥ 0 before Sentinel-1 prediction files were read. Sensitivity thresholds are −0.05, 0, +0.05, selected without SAR feedback. Weak water requires SCL 6 plus positive support from both indices; weak non-water requires SCL 4/5 plus both indices below zero. SCL 2/7 and conflicting/low-signal evidence remain uncertain. SCL 0/1/3/8/9/10/11, source NoData, and invalid cells are invalid. This is a conservative automated reference rule, not human truth.

| S2 observation | Weak water | Weak non-water | Uncertain | Invalid | Clear observed | Weak binary coverage of clear observed |
|---|---:|---:|---:|---:|---:|---:|
| Jan 10 | 175,119 | 973,193 | 469,098 | 61,514 | 1,618,843 | 70.93% |
| Jan 20 | 154,536 | 963,888 | 498,946 | 61,554 | 1,618,843 | 69.09% |

Sensitivity changed weak-water counts from 190,155 → 175,119 → 157,425 on Jan 10 and 167,861 → 154,536 → 139,038 on Jan 20 as the dual-index threshold moved −0.05 → 0 → +0.05. All six full class-count rows are in the machine-readable manifest. This change demonstrates threshold sensitivity and is not a water-area estimate.

January 10 to January 20 optical transitions on jointly valid observations produced 144,170 persistent-water candidates, 671 possible-new-water candidates, 1,316 possible-water-loss candidates, 900,758 stable-nonwater candidates, 570,341 uncertain changes, and 61,668 invalid/unavailable cells. These are 20 m pixel counts only. Two optical observations cannot separate a reported incident from aquaculture/pond changes, crop or vegetation changes, irrigation, wet soil, rain, tide, turbidity, mixed pixels, or classification error.

## 3. Sentinel-1 temporal matching and model comparisons

All eight existing Phase 7 predictions were reused, with the model threshold fixed at 0.5. Sentinel-1 probability was area-averaged from 10 m to the same 20 m grid; all four contributing 10 m SAR cells must be valid. Comparisons use joint observation coverage and exclude uncertain optical classes. The exact nearest-observation differences were:

| S1 date/time | Orbit / pass | Matched S2 date/time | S1 minus S2 |
|---|---|---|---:|
| Jan 09 23:56:06Z | 150 / descending | Jan 10 04:30:49.024Z | −4.579 h |
| Jan 12 12:12:34Z | 12 / ascending | Jan 10 04:30:49.024Z | +55.696 h |
| Jan 21 23:56:05Z | 150 / descending | Jan 20 04:30:09.024Z | +43.432 h |
| Jan 24 12:12:33Z | 12 / ascending | Jan 20 04:30:09.024Z | +103.707 h |

All four scenes have 1,617,525 jointly observed cells including optical uncertainty. Binary labeled comparisons contain 1,148,312 cells for the Jan 10 optical scene and 1,118,424 for Jan 20.

| S1 date / geometry | Model | `weak_reference_agreement` | `weak_reference_positive_agreement` | `weak_reference_negative_agreement` |
|---|---|---:|---:|---:|
| Jan 09 / orbit 150 descending | Scratch | 83.62% | 15.96% | 95.80% |
| Jan 09 / orbit 150 descending | Pretrained | 85.54% | 6.17% | 99.83% |
| Jan 12 / orbit 12 ascending | Scratch | 88.70% | 60.60% | 93.76% |
| Jan 12 / orbit 12 ascending | Pretrained | 92.42% | 53.06% | 99.50% |
| Jan 21 / orbit 150 descending | Scratch | 84.76% | 19.99% | 95.15% |
| Jan 21 / orbit 150 descending | Pretrained | 87.13% | 8.18% | 99.78% |
| Jan 24 / orbit 12 ascending | Scratch | 89.57% | 67.74% | 93.07% |
| Jan 24 / orbit 12 ascending | Pretrained | 93.68% | 57.69% | 99.45% |

The pretrained model has higher overall weak-reference agreement in each of these four comparisons, while the scratch model has higher agreement on the weak-water subset each time. The pretrained model’s overall advantage is driven substantially by weak-nonwater agreement. This class trade-off, temporal mismatch, geometry dependence, and weak-reference uncertainty mean **no model winner is selected**. These percentages are not locally validated accuracy or field metrics.

Each result also contains the full weak-reference confusion matrix, valid/uncertain/excluded pixel counts, SCL-context breakdown, and 5 km spatial blocks. Each model/acquisition has 35 blocks with labeled support; p10–p90 block agreement ranges from roughly 61% to 99% depending on acquisition/model. These are descriptive spatial-variation summaries, not confidence intervals. No pixel independence assumption or naive pixel-level confidence interval is used.

Disagreement is most apparent in the weak-water class: positive agreement is much lower and varies strongly with orbit and acquisition than agreement on weak non-water pixels. The analysis cannot attribute disagreement to ponds, crops, wet soil, irrigation, permanent-water use, or specific villages because no authoritative land-use/pond labels or exact Pallimangal geometry exist. Ambiguous SCL/index evidence is retained rather than forced into a class.

## 4. Raster products and provenance

Outputs are under `data/gherproof/processed/phase8b/`:

- `optical/{date}/weak_reference.tif` (categorical states), plus separate `weak_water_mask.tif`, `weak_nonwater_mask.tif`, and `uncertainty_mask.tif`.
- `optical/{date}/ndwi_20m.tif`, `mndwi_20m.tif`, and `scl_class.tif`.
- `optical/temporal_change/2026-01-10_to_2026-01-20_change_candidates.tif` and `possible_new_water_candidate.tif`.
- `comparison/sar_optical/{date}_{model}/probability_20m_mean.tif`, `model_water_prediction_20m.tif`, `agreement_codes.tif`, separate SAR/optical agreement and disagreement masks, and joint coverage codes.
- `comparison/model_consensus/{date}/model_disagreement_codes.tif` and `multi_source_candidate_codes.tif`.

The 20 m binary/agreement products retain NoData and uncertain classes; no confirmed-flood mask is created. All 72 Phase 8B GeoTIFFs reopened successfully with Rasterio. The QC manifest records path, SHA-256, bytes, CRS, transform, bounds, resolution, dimensions, dtype, nodata, valid pixel count, and NaN/Inf counts. All comparison output rasters were checked for finite valid values. Phase 7 prediction rasters and model checkpoints are unchanged.

## 5. Evidence registry and API

Phase 8’s 135 evidence records were preserved, and Phase 8B products were added using `optical_weak_reference`, `model_comparison`, `uncertainty_layer`, `model_prediction`, or `derived_satellite_measurement` categories according to meaning. Current registry size is **207 records**; its file inventory reports **205 available file references**, no unavailable/invalid paths, and zero checksum mismatches. Each added layer has a deterministic ID, date(s), source/output references, checksum, CRS/resolution, threshold/algorithm, validity mask, status and limitations.

Added read-only endpoints:

- `GET /api/gherproof/weak-reference`
- `GET /api/gherproof/comparisons`
- `GET /api/gherproof/scenarios/january_2026_regional_screening_demo`

Existing evidence, scene, prediction, raster and report routes remain. The new metrics explicitly use `weak_reference_agreement`, not accuracy. Model readiness remains `exploratory_only`; human reference labels remain `human_review_pending`; impact quantification remains `not_approved`; Pallimangal location remains unresolved.

## 6. Demonstration scenario

`data/gherproof/scenarios/january_2026_regional_screening_demo.json` defines an evidence-linked, explicitly simulated 8-stage workflow for a hypothetical regional disaster-monitoring officer. It uses the saved news-event record, source-linked report claims/place names, existing scenes and predictions, Phase 8B outputs, and registry IDs. It contains no invented coordinates, boundaries, observations or operator actions. Source claims remain attributed and unverified. See `docs/GHERPROOF_DEMO_SCENARIO.md` for the Phase 9 user journey and endpoint contract.

## 7. Testing and reproduction

The new Phase 8B tests cover reflectance scaling and NoData, SCL logic, indices, fixed thresholds, class/change logic, grid/resampling semantics, common validity, weak-reference confusion metrics, spatial blocks, label leakage prevention, registry changes, scenario/API consistency, original annotation hashes, and all output raster reopen/checksum/numeric checks. The complete GherProof suite passed: **92 passed, 3 warnings**. Warnings are the existing Starlette/httpx deprecation and two intentional `NotGeoreferencedWarning` fixture notices. No prior assertions were weakened.

Reproduce:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase8b/run_weak_reference_pipeline.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase8b/prepare_demo_scenario.py
Push-Location backend
.venv/Scripts/python.exe -m pytest -q tests/test_gherproof*.py
Pop-Location
```

No final model training, external satellite/cadastral search, frontend work, village-specific summaries, affected-area conversion, or operational breach diagnosis was performed.

## 8. Readiness decision

**CONDITIONAL GO for Phase 9 frontend development** using the prepared demonstration scenario and evidence APIs. The frontend can build a clearly qualified evidence-review experience with separate observation, derived, weak-reference, prediction, uncertainty and provisional-geography layers. Keep the scientific statuses unchanged. Human labels, field checks and verified site boundaries are still prerequisites for local model validation or any operational impact claim.
