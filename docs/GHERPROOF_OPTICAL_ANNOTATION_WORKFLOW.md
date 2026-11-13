# GherProof Phase 7C — Human Optical Annotation Workflow

## Package status

**Workflow package prepared; human labeling remains pending.** The untouched Phase 7B GeoPackage remains the baseline. The Phase 7C working copy preserves all 450 IDs and geometries, coded sampling strata, spatial blocks, fixed split assignments, inclusion probabilities and weights. No label was filled automatically.

| Artifact | Path |
|---|---|
| Editable GeoPackage | `data/gherproof/reference/phase7c/gherproof_optical_reference_samples_editable.gpkg` |
| Untouched Phase 7B baseline | `data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg` |
| QGIS project (XML generated; app load not verified) | `data/gherproof/reference/phase7c/gherproof_optical_annotation.qgs` |
| CSV template | `data/gherproof/reference/phase7c/gherproof_optical_annotations_template.csv` |
| Image annotation guide | `data/gherproof/reference/phase7c/GHERPROOF_OPTICAL_ANNOTATION_GUIDE.png` |
| Progress | `data/gherproof/reference/phase7c/annotation_progress.md` and `.json` |
| Fixed split | `data/gherproof/manifests/phase7c_fixed_spatial_split_manifest.json` |
| Workflow manifest | `data/gherproof/manifests/phase7c_annotation_workflow_manifest.json` |

## Open the QGIS project

Open `gherproof_optical_annotation.qgs` in QGIS. It references eight sources: the Jan 10 and Jan 20 S2B false-colour stacks, both date-specific SCL class rasters, both clear-pixel masks, the editable sample GeoPackage, and the provisional regional search extent. The Jan 10 composite is initially visible; the Jan 20 image can be toggled on. SCL and clear masks start hidden and can be toggled for context. The sample layer appears as yellow points. **No Sentinel-1 prediction or disagreement layer is part of this project.**

The false-colour stacks are R=B08/NIR, G=B04/red, B=B03/green, with stored surface reflectance values and fixed display stretch 0.0–0.4. They are not true-colour photographs. The SCL classes and masks are context for cloud/shadow/validity, not reference labels. The AOI is explicitly provisional and is not a set of village boundary polygons. No local roads or authoritative water-reference GIS layer was found in the project assets; none has been fabricated.

QGIS and PyQGIS are not installed in the current environment. The QGS XML parses, all eight layer sources resolve on disk, and no prediction source is included, but project opening, renderer appearance, forms and editing behavior could not be smoke-tested in QGIS. Validate on a machine with QGIS before a reviewer begins.

## Label fields and review process

For Jan 10, fill `pre_label`, `pre_confidence`, `pre_notes`, plus `pre_reviewer`, `pre_review_date`, and `pre_label_source`. For Jan 20, fill the `post_` equivalents. Optional second-review fields (`pre_second_label`, `post_second_label`, associated confidence/notes, reviewer/date and date-specific disagreement fields) preserve the first label while recording an independent review. Use one label per date:

| Label | Meaning |
|---|---|
| `water` | Surface water is discernible at the sample point. |
| `non_water` | Water is not discernible and the observed surface supports a non-water label. |
| `uncertain` | Mixed, ambiguous, shadowed, turbid, vegetated or otherwise not classifiable with confidence. |
| `invalid` | Point is outside valid imagery or obscured/corrupted such that review is not possible. |

Confidence values are `high`, `medium`, `low`. `reviewed_status` applies to the paired pre/post record: `not_reviewed`, `reviewed`, or `needs_second_review`. If either date needs another opinion, use `needs_second_review` and document the reason. Do not turn uncertain or invalid into a binary class. The GeoPackage rejects invalid label/confidence/review-status values and prevents edits to design fields (IDs, coordinates, weights, strata and splits).

The CSV is an alternative editing template, not a separate sampling design. It includes optional second-review fields. Preserve every ID and frozen field. Enter confidence, reviewer, review date, and label source for every assigned date label. Validate and merge an edited copy to a **new** GeoPackage (never overwrite the baseline):

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase7c/merge_annotation_csv.py `
  path\to\completed_annotations.csv `
  --output data/gherproof/reference/phase7c/gherproof_optical_annotations_submitted.gpkg
```

The script rejects duplicate/missing/unknown IDs, altered sampling design, invalid categories, and incomplete rows marked reviewed. A QGIS-edited GeoPackage may be evaluated directly by passing its path to the evaluator.

## Optical interpretation guidance

- Open water may appear spectrally dark or have coherent water-like texture, but reflectance varies with depth, turbidity, sun/view geometry and adjacency. Assess surrounding spatial continuity.
- Aquaculture ponds can be regular water surfaces separated by embankments. A pond label describes optical surface water, not whether it flooded or lost fish.
- Turbid/shallow water may resemble wet soil or exposed sediment; use `uncertain` when unresolved.
- Vegetated water and emergent vegetation may mask the water signal. Do not infer water beneath vegetation from model predictions.
- Wet soil can look dark or water-like; inspect texture, field boundaries and neighborhood, but do not guess.
- Dry soil and agricultural vegetation are `non_water` only if no visible water occupies the sampled location. Do not assign crop type or growth stage from assumption.
- Shadows from cloud, buildings or other objects can resemble water. Inspect the SCL and context; choose `uncertain` or `invalid` if the point cannot be judged.
- Cloud-affected observations should be `invalid` when the sample is not visually assessable. A partially ambiguous but observable surface is `uncertain`.
- A 10 m pixel can mix water, crop, soil, road or pond edge. Choose `uncertain` if the dominant visible condition is not clear.

Do not expose the model maps or infer labels from the blind-coded stratum. Keep the two dates separate. A second independent reviewer is recommended for ambiguous samples and a shared subset. These remain optical interpretations, not field-verified ground truth.

## Spatial independence and progress

The Phase 7B spatial blocks and assignments were retained unchanged: 150 calibration, 150 validation and 150 test points, with existing contiguous 5 km block-column grouping and 1 km guard bands. The final test assignment is hashed in the split manifest and must not be changed after inspecting model performance. Long-range spatial autocorrelation can remain beyond the guard. Sampling weights are inverse inclusion probabilities; preserve them for weighted population-oriented measures.

Current progress: **0/450 samples reviewed, 0/450 pre labels complete, 0/450 post labels complete.** Evaluation correctly reports `local_validation_status = human_review_pending`; no local metrics exist.
