# GherProof Phase 7C — Independent Evaluation Protocol

## Current status

The label slots are blank. This document specifies the evaluation that may run after real human annotation is returned; it does not report model results. The script returns `human_review_pending` without computing accuracy while labels are blank.

## Submission checks

Use the Phase 7C editable copy or a submitted copy of it. Before evaluation, the script:

1. Confirms all 450 original sample IDs occur exactly once and match the untouched Phase 7B baseline.
2. Checks sample coordinates, stratum, block, split, inclusion probability and sample weight are unchanged.
3. Validates labels (`water`, `non_water`, `uncertain`, `invalid`), confidence (`high`, `medium`, `low`) and review status.
4. Reports blanks, uncertain/invalid, low confidence, annotator count, paired second-review exact agreement and `needs_second_review` counts.
5. Requires both dates to be reviewed and no unresolved second-review flag before metric computation.

For CSV editing, use `scripts/gherproof/phase7c/merge_annotation_csv.py`; it validates the frozen design and writes a separate GPKG rather than modifying source files. Separate second-review labels and date-specific agreement fields are available; the first reviewer’s labels remain unchanged.

## Frozen spatial roles

The Phase 7B assignment is frozen before review and represented in `data/gherproof/manifests/phase7c_fixed_spatial_split_manifest.json`:

| Role | Existing split | Use |
|---|---|---|
| Calibration | `calibration` | Choose model-specific, geometry-specific probability threshold by sampling-weighted F1 only. |
| Validation | `validation` | Examine stability and subgroup behavior; do not tune against final test. |
| Final independent evaluation | `test` | One-time held-out performance report after choices are frozen. |

There are 150 points per role, across the two dates (up to 300 date-specific labels per role). Existing block-column assignment and 1 km guards are unchanged. These mitigate local leakage but do not remove broader spatial autocorrelation. If a reviewer has viewed model outputs before labeling, mark this in the annotation provenance and do not describe labels as blinded.

## Minimum computation gate

The evaluator requires every date slot to have an explicit label, every sample pair to have `reviewed_status=reviewed`, no invalid category or identity/design mismatch, and at least 30 binary references in each split × date cell with both classes represented. The 30-reference gate is a minimum software guard, not a claim of adequate statistical power or representativeness. Insufficient cells keep status `insufficient_valid_reference_labels` and do not yield a readiness approval.

## Metrics and interpretation

- Sample both existing models at the same sample coordinates from each corresponding Jan 9/12 pre and Jan 21/24 post probability raster, separately for each relative-orbit pair.
- Select a per-model/per-geometry threshold on calibration points using inverse-inclusion-probability weighted F1. Never tune on the test set.
- Report weighted confusion matrices, IoU, precision, recall, F1 and average precision/PR-AUC for calibration, validation and final test. The test split is the primary independent evidence.
- Break down performance by scene/date, blind sampling stratum, and annotator confidence. Report uncertain/invalid and low-confidence proportions separately; do not coerce them to binary labels.
- Record false-positive/false-negative sample IDs and their strata/confidence for review, not as diagnoses.
- Compare the two models on identical held-out references. Do not select a model from benchmark metrics or overall IoU alone. Consider precision/recall tradeoffs, PR-AUC, sampling uncertainty and spatial generalization.

The evaluator implements point sampling and weighted metric summaries in `scripts/gherproof/phase7c/evaluate_optical_reference.py`; unit metric functions are in `scripts/gherproof/phase7b/reference_evaluation.py`. Run after annotation:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/evaluate_optical_reference.py
# Optional: evaluate a returned, validated submission copy
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/evaluate_optical_reference.py `
  data/gherproof/reference/phase7c/gherproof_optical_annotations_submitted.gpkg
```

Outputs are written to `data/gherproof/manifests/phase7c_model_evaluation_manifest.json` and `phase7c_model_readiness.json`. The latter never automatically approves Phase 8: a model may support regional water classification yet remain unsuitable for event attribution or impact quantification. These optical references are not field-verified truth. Attribution requires independent field and infrastructure evidence.
