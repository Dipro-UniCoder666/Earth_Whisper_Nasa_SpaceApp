# GherProof Phase 7C — Annotation Workflow and Independent Validation Readiness

## Decision

**Model readiness remains `exploratory_only`; Phase 8 impact quantification is NOT APPROVED.** The Phase 7C annotation workflow and validation code are prepared, but no human labels were supplied. Consequently there are no independent local performance metrics, no model winner, and no basis to convert model probabilities into a confirmed flood or impact result.

## Annotation package audit

The original Phase 7B GeoPackage was read and preserved unchanged. It contains **450 unique sample IDs**, the original point geometries, blind-coded strata, spatial blocks/splits, sample weights and inclusion probabilities, plus **900 blank pre/post label slots**. The Phase 7C working copy was copied from that baseline, checked for the same IDs/count, and remains blank: 450 pre and 450 post labels. Sampling IDs, coordinates, strata, weights and split values are protected against edits by SQLite triggers in the working copy. The immutable baseline checksum is recorded in the Phase 7C workflow manifest.

No label was inferred from Sentinel-1 model outputs, strata, indices, or automated rules. Current evaluator result is `local_validation_status = human_review_pending`, with 900 blank slots and zero metrics.

## Offline QGIS annotation workflow

Created:

- An editable Phase 7C GeoPackage with separate `pre_label`, `pre_confidence`, `pre_notes`, `post_label`, `post_confidence`, `post_notes`, and `reviewed_status` fields, plus reviewer, date, source and second-review metadata.
- Controlled vocabulary triggers for labels, confidence and review status. Protected sample identity/design fields cannot be edited in this copy.
- A UTF-8 CSV template with all frozen assignment fields and blank annotation fields.
- Jan 10 and Jan 20 three-band false-colour GeoTIFFs (R=B08/NIR, G=B04/red, B=B03/green), generated from the existing reflectance layers on matching EPSG:32645 10 m grids. Display guidance is a fixed 0.0–0.4 reflectance stretch; files retain reflectance values.
- A QGIS project XML with eight sources: two false-colour composites, two matching-date S2B SCL rasters, two SCL clear masks, editable sample points and the provisional regional search extent. No model probability, prediction or disagreement source is included. SCL/masks start hidden and can be toggled for context.
- Optional second-review labels, confidence, notes, reviewer/date and per-date agreement fields preserve independent annotations without overwriting the first reviewer’s entries.
- An image-based annotation guide and a progress summary.

QGIS/PyQGIS are not installed in this environment. The project XML parses, all eight layer source paths resolve, source raster grids and composite metadata were checked, and the project source list was audited to confirm predictions are absent. **Opening the project in QGIS and testing its attribute form/edit behavior is blocked**, so the generated QGS must be opened and visually checked in QGIS before use. Roads and water-reference GIS were not found among the local project assets; none were fabricated or added.

Progress currently shows 0/450 samples reviewed, 0/450 pre labels and 0/450 post labels complete. Ambiguous observations should remain `uncertain`, and cloud/invalid data should be `invalid` only when the sample cannot be judged. The optical labels are interpretations, not field-verified truth.

## Frozen independent split

The original Phase 7B assignments were retained, not regenerated: 150 calibration, 150 validation and 150 test points. The fixed manifest records all sample IDs and the SHA-256 hash of their assignment mapping. Original 5 km block-column groups and 1 km guards remain unchanged. Calibration is for per-model/per-geometry threshold choice; validation is for stability checks; test is the held-out final evidence. The nearest sampled points across role boundaries are 2,667.5 m apart (calibration/validation), 2,401.5 m (validation/test) and 12,228.9 m (calibration/test); unique spatial block IDs are disjoint across all three roles. No split can be changed after a reviewer or analyst inspects model results. The split reduces nearby point leakage but does not remove long-range spatial autocorrelation.

## GRD processing compatibility

All four exact acquisition GRD catalogue counterparts have VV/VH asset URLs and match the RTC source identifiers, platform, orbit, direction and IW mode. Remote inspection returned 8/8 COG headers (HTTP 206) and decoded 7/8 small sample windows. The eighth (Jan 12 VH) failed to read a sample. TIFFs report uint16, nodata zero, scale 1, offset 0, no units, no CRS and identity pixel-index transforms; their TIFF tags say Sentinel-1 IW GRD HR L1. Separate SAFE manifest, calibration LUTs (27 vectors per polarization) and noise XML metadata were recovered and checksummed. STAC prose says RTC was applied, but the actual raster tags, missing map transform and Level 1 sidecars do not establish terrain-corrected geocoded backscatter.

No complete scene was downloaded or processed. This environment lacks SNAP GPT/bridge and GDAL Python bindings. Without physical coordinates, the remote GRD COGs could not be clipped to the AOI. Native uint16 samples are not calibrated gamma/sigma backscatter or dB and were not compared with Sen1Floods11 dB chips. Therefore GRD compatibility is unresolved and **no improvement over RTC was demonstrated**. See [GRD processing compatibility](GHERPROOF_GRD_PROCESSING_COMPATIBILITY.md).

## Independent evaluation implementation

The Phase 7C evaluator now checks exact sample-ID preservation, duplicates, coordinates, strata, spatial blocks, split roles, inclusion probabilities and weights; validates label/confidence/review categories; and summarizes blanks, uncertain/invalid, low-confidence and second-review flags. It does not compute metrics while labels are blank or a review is unresolved. After review, it applies a minimum software gate of 30 binary labels per date and split with both classes represented. This is only a guard against nearly empty evaluation subsets, not a statistical-power guarantee.

For eligible submissions it evaluates both existing models on the same sample points, separately by geometry/date; selects thresholds using calibration weighted F1, never the final test; reports weighted confusion matrices, IoU, precision, recall, F1 and average precision with scene, stratum and confidence breakdowns; and records held-out errors. The local evaluation and readiness manifests remain pending/exploratory. No checkpoints were changed.

## Verification and blockers

- Phase 7C, Phase 7B and Phase 7 input tests: **29 passed**.
- CSV blank-template round trip to a temporary new GeoPackage: passed; IDs/weights remain unchanged and labels remain blank.
- Invalid category and duplicate CSV record rejection: passed.
- Editable GeoPackage rejects invalid label categories and changes to frozen sample design: passed.
- QGS XML parses; all eight source paths resolve; no model outputs are referenced. QGIS application smoke test: **blocked (QGIS unavailable)**.
- Optical composites: both reopened as 3-band EPSG:32645, 10 m rasters; source grids match.
- Evaluator run against the current blank working package: `human_review_pending`; 450 points, 900 blank slots, 0 metrics; no ID/design errors.
- GRD: 4 exact catalogue matches; 8/8 headers; 7/8 small reads; 0 fully processed scenes. Terrain correction and calibrated backscatter remain unverified.

Reproduce workflow generation and validation:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/prepare_annotation_workflow.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/build_qgis_project.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/evaluate_optical_reference.py
Push-Location backend
.venv/Scripts/python.exe -m pytest tests/test_gherproof_phase7c.py tests/test_gherproof_phase7b.py tests/test_gherproof_phase7_inputs.py -q
Pop-Location
```

See the [annotation workflow](GHERPROOF_OPTICAL_ANNOTATION_WORKFLOW.md) and [evaluation protocol](GHERPROOF_INDEPENDENT_EVALUATION_PROTOCOL.md). The no-label condition is the present blocker to determining which model, if any, can support further regional water analysis. Even successful optical validation would not by itself approve Pallimangal attribution, drainage diagnoses, or affected-area quantification.
