# GherProof Phase 7B — Optical Reference Annotation Guide

## Status

**Package prepared; human labels pending.** The 450 point samples are intentionally unlabeled. The package contains no model probabilities, prediction masks, model identifiers or prefilled water/non-water classes. No local validation metrics have been computed.

## Review package

- GeoPackage: `data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg`, layer `samples`, EPSG:32645.
- Blind image gallery: `data/gherproof/reference/phase7b/annotation_review_gallery.html`.
- Context chips: `data/gherproof/reference/phase7b/context_chips/`.
- Sampling manifest: `data/gherproof/manifests/phase7b_sampling_design_manifest.json` (project provenance; do not give the internal stratum-key mapping to the blind annotator).

The gallery shows paired Jan 10 and Jan 20 Sentinel‑2 false-color chips, with the sample center marked in yellow. The display is fixed-stretched reflectance composite **R=NIR B08, G=red B04, B=green B03**; it is not true color. It contains no Sentinel‑1 model layer or prediction. For broader inspection, open the original Jan 10/20 reflectance and index rasters from `data/gherproof/processed/phase7/sentinel2/` in QGIS, alongside the GeoPackage. Do not add the Phase 7 inference rasters to the blind review map.

## Labels and fields

Record `pre_label` for Jan 10 and `post_label` for Jan 20 independently using exactly one of:

| Value | Use |
|---|---|
| `water` | Surface water is discernible at the sample location in the image/context. |
| `non_water` | Water is not discernible and the surface context supports a non-water label. |
| `uncertain` | Evidence is ambiguous, mixed, shadowed, turbid, vegetated, or otherwise not confidently classifiable. |
| `invalid` | The sample is unusable because it is outside valid imagery, invalid/cloud-obscured, or context is corrupted. |

Enter `high`, `medium` or `low` in the corresponding confidence field when a binary or uncertain label is assigned. Include `annotator`, `review_date`, `label_source` and explanatory `notes`. Keep uncertain and invalid distinct; do not force them into the binary evaluation.

Consider whether water is turbid, shallow, wet soil, shadow, aquaculture pond, submerged crop, vegetated/partially obscured water or a mixed pixel. Record this in notes rather than creating unreviewed classes. NDWI/MNDWI and SCL values are provided as context only; they are not reference labels. The samples are concentrated in sampling strata by design, so retain the provided `sample_weight` when calculating population-weighted metrics.

## Sampling and split design

The reproducible seed is 20261113. Ten exclusive blind-coded strata were sampled with up to 15 points per stratum in each split. The internal mapping includes optical proxies, possible optical change, and same-acquisition model agreement/disagreement strata; that mapping is held outside the review package to reduce reviewer bias. The exact eligible candidate count, selected count, inclusion probability and inverse-probability sample weight are stored in the project manifest.

Groups use complete 5 km projected block columns in west (calibration), middle (validation) and east (final test) strips, with a 1 km guard on both sides of split boundaries. A block column is assigned wholly to one split. This reduces neighboring-pixel leakage but cannot eliminate spatial autocorrelation beyond the guard. The test sample supports only the designated eastern test domain unless a broader independently designed sample is later collected.

## Evaluation protocol

The evaluator is `scripts/gherproof/phase7b/evaluate_optical_reference.py`. It refuses to produce metrics while labels are blank/invalid. Once reviewed labels are entered in the GeoPackage:

1. Validate label and confidence values; summarize uncertain, invalid and blank records.
2. Use calibration labels only to select a per-model/per-geometry threshold by inverse-inclusion-probability weighted F1.
3. Keep threshold/model decisions separate from the spatial validation and final-test blocks.
4. Report weighted IoU, precision, recall, F1, average precision, confusion matrix, per-stratum and per-scene results for both models on identical samples.
5. Exclude uncertain/invalid labels from primary binary metrics and report their counts/proportions.

Jan 10/20 optical observations are independent reference context, not absolute ground truth. The Sentinel‑1 acquisitions do not coincide exactly: Jan 9/12 are compared with Jan 10 pre-event context, and Jan 21/24 with Jan 20 post-event context. Turbidity, shallow water, vegetation, wet soil, shadow, ponds, mixed pixels, tidal/agricultural change and temporal offset remain sources of disagreement. One reviewer is currently planned; inter-annotator agreement is unavailable until a second independent labeler reviews a shared sample subset.
