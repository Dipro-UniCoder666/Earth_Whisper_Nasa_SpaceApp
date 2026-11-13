# GherProof Weak-Reference Comparison Results — Phase 8B

## Result semantics

These results quantify how existing Sentinel-1 model outputs agree with independently generated optical weak-reference classes. They are **not local accuracy, field validation, flood detection, or proof of incident causality**. The optical labels are automated SCL + NDWI + MNDWI candidates on the provisional regional raster footprint.

## Exact temporal matching

| Sentinel-1 scene | Relative orbit / direction | Closest optical observation (UTC) | S1 minus S2 time |
|---|---|---|---:|
| 2026-01-09 23:56:06Z | 150 / descending | Jan 10 04:30:49.024Z | −4.579 h |
| 2026-01-12 12:12:34Z | 12 / ascending | Jan 10 04:30:49.024Z | +55.696 h |
| 2026-01-21 23:56:05Z | 150 / descending | Jan 20 04:30:09.024Z | +43.432 h |
| 2026-01-24 12:12:33Z | 12 / ascending | Jan 20 04:30:09.024Z | +103.707 h |

These are the nearest available optical dates, not simultaneous acquisitions. The 12/24 ascending observations and the 9/21 descending observations are evaluated per scene; opposite directions and relative orbits are never pooled into one time series.

## Comparison grid and common support

The comparison grid is EPSG:32645, 20 m, 1556 × 1079, aligned to native Sentinel-2 B11. Existing Sentinel-1 probability rasters are area-averaged from 10 m to 20 m; cells require all four 10 m input cells to be valid. Threshold 0.5 is unchanged from the existing model outputs. The comparison uses the joint SAR/optical observation mask and evaluates only the optical `weak_water` and `weak_nonwater` classes.

| Optical date | Weak-water pixels | Weak-nonwater pixels | Uncertain pixels | Invalid pixels | Clear observed pixels | Valid weak-reference coverage of clear observations |
|---|---:|---:|---:|---:|---:|---:|
| Jan 10 | 175,119 | 973,193 | 469,098 | 61,514 | 1,618,843 | 70.93% |
| Jan 20 | 154,536 | 963,888 | 498,946 | 61,554 | 1,618,843 | 69.09% |

“Coverage” here is the fraction of clear observations assigned one of the two conservative binary weak-reference classes. It is not geographic or flood coverage. Each acquisition has 1,617,525 jointly observed comparison pixels including uncertain optical observations. The comparable binary weak-reference subset is 1,148,312 pixels for Jan 10 and 1,118,424 for Jan 20; the remaining optical-uncertain pixels are excluded from agreement scores.

## Per-model/per-acquisition results

| S1 date / geometry | S2 date | Model | Common labeled pixels | Weak-reference agreement | Positive agreement (weak water) | Negative agreement (weak nonwater) |
|---|---|---|---:|---:|---:|---:|
| Jan 09 / 150 descending | Jan 10 | Scratch | 1,148,312 | 83.62% | 15.96% | 95.80% |
| Jan 09 / 150 descending | Jan 10 | Pretrained | 1,148,312 | 85.54% | 6.17% | 99.83% |
| Jan 12 / 12 ascending | Jan 10 | Scratch | 1,148,312 | 88.70% | 60.60% | 93.76% |
| Jan 12 / 12 ascending | Jan 10 | Pretrained | 1,148,312 | 92.42% | 53.06% | 99.50% |
| Jan 21 / 150 descending | Jan 20 | Scratch | 1,118,424 | 84.76% | 19.99% | 95.15% |
| Jan 21 / 150 descending | Jan 20 | Pretrained | 1,118,424 | 87.13% | 8.18% | 99.78% |
| Jan 24 / 12 ascending | Jan 20 | Scratch | 1,118,424 | 89.57% | 67.74% | 93.07% |
| Jan 24 / 12 ascending | Jan 20 | Pretrained | 1,118,424 | 93.68% | 57.69% | 99.45% |

Confusion counts below are ordered **weak-water hit / weak-water miss / weak-nonwater match / weak-nonwater predicted water**:

| S1 date | Scratch | Pretrained |
|---|---|---|
| Jan 09 | 27,955 / 147,164 / 932,310 / 40,883 | 10,802 / 164,317 / 971,510 / 1,683 |
| Jan 12 | 106,128 / 68,991 / 912,447 / 60,746 | 92,918 / 82,201 / 968,324 / 4,869 |
| Jan 21 | 30,891 / 123,645 / 917,130 / 46,758 | 12,637 / 141,899 / 961,793 / 2,095 |
| Jan 24 | 104,687 / 49,849 / 897,124 / 66,764 | 89,150 / 65,386 / 958,611 / 5,277 |

## Interpretation and spatial variation

The pretrained model has higher overall weak-reference agreement on all four comparisons, but it also has much higher weak-nonwater agreement and lower weak-water positive agreement on all four. The scratch model matches more of the optical weak-water candidates but predicts water more often on the weak-nonwater subset. This is a class-dependent trade-off; it does **not** establish a validated winner. Scores are sensitive to the chosen optical rules and the non-water-heavy reference mix.

SCL-context breakdown shows the same pattern. On the weak-water subset (SCL 6 plus both optical indices nonnegative), positive agreement ranges from 15.96–67.74% for scratch and 6.17–57.69% for pretrained. Weak-nonwater agreement on SCL 4/5 is generally higher. The SCL 6 group itself contains 100,248 uncertain pixels on Jan 10 and 107,676 on Jan 20 where both optical indices do not support a binary weak-water label. Class 5 also has many uncertain pixels because the dual-index evidence conflicts or fails the fixed rule.

Each comparison has 35 populated coarse 5 km spatial blocks. The per-comparison 10th-to-90th percentile range of block-level weak-reference agreement spans:

| S1 date | Scratch block p10–p90 | Pretrained block p10–p90 |
|---|---:|---:|
| Jan 09 | 61.80–94.90% | 61.06–98.26% |
| Jan 12 | 77.10–94.56% | 78.02–98.59% |
| Jan 21 | 65.56–94.39% | 64.06–99.02% |
| Jan 24 | 78.81–93.94% | 81.99–98.93% |

These are descriptive block summaries, not confidence intervals; spatial autocorrelation remains and blocks are not a formal independent validation sample. The machine-readable manifest includes block windows and EPSG:32645 centroids. The pixels are not assigned to village or land-use groups.

No authoritative crop/aquaculture/pond map or field labels are available to test whether disagreement corresponds to ponds, vegetation type, wet soil, irrigation, permanent water, mixed pixels, or shadow. Cloud and cloud-shadow classes are excluded or unavailable; SCL 2/7 are retained as uncertain and not compared. The large class-specific difference in weak-water agreement is a clear focus for future human review, not evidence of any particular land-use cause.

## Optical pre/post candidate changes

On the joint observed Jan 10/Jan 20 comparison grid: 671 pixels are `possible_new_water_candidate`, 1,316 are `possible_water_loss_candidate`, 144,170 are persistent-water candidates, 900,758 are stable-nonwater candidates, 570,341 are uncertain changes, and 61,668 are invalid. These are raw candidate pixel counts only; no conversion to hectares/bighas or impact extent is made. The two-date interval cannot attribute a change to the reported incident or a breached embankment.

## Products and reproducibility

Machine-readable per-model, per-scene confusion matrices, comparison masks, threshold sensitivity, time matching, block summaries, raster provenance and checksums are in `data/gherproof/manifests/phase8b_weak_reference_comparison.json` and `data/gherproof/manifests/phase8b_raster_qc_manifest.json`. Separate GeoTIFFs for optical weak-water, weak-nonwater, uncertainty, possible optical new-water, each model’s 20 m probability/binary prediction, SAR/optical agreement, SAR/optical disagreement, model disagreement, multi-source candidate agreement, and joint coverage are in `data/gherproof/processed/phase8b/`.

Every Phase 8B GeoTIFF was reopened with Rasterio. CRS, transform, dimensions, resolution, nodata, dtype, valid-pixel count and SHA-256 are recorded; the QC validation found no unmasked NaN/Inf values. Existing model predictions/checkpoints, Phase 7 products, and the 450-point human annotation workflow were not overwritten. The human reference status remains `human_review_pending` and local model readiness remains `exploratory_only`.
