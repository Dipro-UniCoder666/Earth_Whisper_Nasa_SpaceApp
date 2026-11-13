# GherProof Phase 7 — Sentinel‑2 Optical Corroboration

## Selected pair and radiometry

The selected images are Sentinel‑2B, tile 45QYF, relative orbit 133, same processing baseline 05.11:

| Date | Item ID | BOA quantification | BOA offset |
|---|---|---:|---:|
| Jan 10, 2026 | `S2B_MSIL2A_20260110T043049_R133_T45QYF_20260110T065859` | 10000 | -1000 for all recorded band IDs |
| Jan 20, 2026 | `S2B_MSIL2A_20260120T043009_R133_T45QYF_20260120T062559` | 10000 | -1000 for all recorded band IDs |

The values come from the exact SAFE product and granule metadata assets saved under `data/gherproof/raw/phase7/sentinel2_metadata/`, with checksums in `phase7_sentinel2_radiometric_metadata.json`. Reflectance was calculated as `(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE`, i.e. `(DN-1000)/10000`; DN=0 was treated as NoData. No assumed scale or per-scene min-max stretch was used. Selected stack values were aligned to the Phase 6B EPSG:32645 grid. Clear SCL support used the exact matching item clear-mask raster (classes 2,4,5,6 as Phase 6B defined). Class 6 is retained because the prior mask policy explicitly includes it; this is not an independent label.

Green B03, red B04 and NIR B08 remain at native 10 m. NDWI is `(B03-B08)/(B03+B08)` at 10 m. SWIR1 B11 remains at native 20 m; B03 was averaged from 10 m to the B11 grid, explicitly, before MNDWI `(B03-B11)/(B03+B11)`. Index values are continuous. Candidate counts were tabulated at -0.05, 0 and +0.05 for sensitivity; these cutoffs are exploratory and not trained or validated water thresholds.

| Date/index | Valid pixels | Median | p02 | p98 | Candidate pixels at -0.05 / 0 / +0.05 |
|---|---:|---:|---:|---:|---:|
| Jan 10 NDWI 10 m | 6,472,354 | -0.3924 | -0.7402 | 0.3732 | 991,066 / 854,161 / 739,283 |
| Jan 20 NDWI 10 m | 6,472,158 | -0.3850 | -0.7291 | 0.3577 | 866,824 / 747,167 / 648,119 |
| Jan 10 MNDWI 20 m | 1,618,737 | -0.2044 | -0.5855 | 0.7596 | 663,992 / 615,482 / 564,675 |
| Jan 20 MNDWI 20 m | 1,618,688 | -0.1803 | -0.5965 | 0.6795 | 676,339 / 618,423 / 557,110 |

Counts are within the clear, valid source footprint but are not land-cover or water labels. Absolute index cutoffs are sensitive to turbidity, submerged/emergent vegetation, wet soil, shadows, aquaculture ponds, mixed pixels and surface reflectance conditions.

## SAR comparison

SAR prediction probability was area-averaged onto the optical native 20 m grid; candidate classes are compared at fixed SAR probability 0.5 and three optical index cutoffs. Categorical codes are 0 neither, 1 both, 2 SAR-only, 3 optical-only, with invalid pixels masked. Two Sentinel‑1 pairs × two separate models × two optical indices × three thresholds produced 24 comparison rasters. The SAR pair dates differ from the optical dates: Jan 12/24 are +2/+4 days relative to S2 Jan 10/20; Jan 9/21 are -1/+1 day.

At threshold 0 (the center sensitivity value), positive candidate overlap counts were:

| S1 geometry/model | Optical index | Both candidates | SAR-only | Optical-only |
|---|---|---:|---:|---:|
| Ascending rel 12 / scratch | NDWI | 119,230 | 257,703 | 59,015 |
| Ascending rel 12 / scratch | MNDWI | 305,217 | 71,716 | 312,905 |
| Ascending rel 12 / pretrained | NDWI | 97,122 | 45,585 | 81,123 |
| Ascending rel 12 / pretrained | MNDWI | 135,732 | 6,975 | 482,390 |
| Descending rel 150 / scratch | NDWI | 42,129 | 192,861 | 136,116 |
| Descending rel 150 / scratch | MNDWI | 184,662 | 50,328 | 433,460 |
| Descending rel 150 / pretrained | NDWI | 16,535 | 11,164 | 161,710 |
| Descending rel 150 / pretrained | MNDWI | 24,669 | 3,030 | 593,453 |

Agreement varies substantially by viewing geometry, model and index. That disagreement and the non-coincident dates prevent interpreting optical overlap as accuracy or independent ground truth. The layers are corroboration comparisons only; no fused confirmed flood map was created. See `data/gherproof/manifests/phase7_cross_sensor_manifest.json` for all thresholds/counts, and the inference report for limitations.
