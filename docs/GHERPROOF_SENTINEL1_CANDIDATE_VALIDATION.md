# GherProof Phase 6B — Sentinel‑1 Candidate Pixel Validation

**Validation date:** 2026-11-12 UTC
**Provider:** Microsoft Planetary Computer `sentinel-1-rtc` COG assets
**AOI:** provisional regional search envelope only; not official village boundaries
**Grid for clipped products:** EPSG:32645, 10 m, 3,111 × 2,156; 6,475,371 AOI pixels (about 647.537 km²)

## Method and scope

The seven exact item IDs saved by Phase 6 discovery were re-fetched from the STAC item API. The source VV and VH assets were accessed as remote Cloud Optimized GeoTIFFs with Microsoft Planetary Computer SAS URLs held in memory only. Bounded HTTP range requests returned HTTP 206 and a GeoTIFF header before Rasterio/GDAL read the AOI windows. Only regional analysis clips and pair masks were written locally; source assets were not downloaded in full. The Phase 6 catalogue manifest remains intact and now points to the additional pixel validation manifest.

The clipped output keeps the source RTC samples in their linear intensity representation. Source metadata describes each layer as calibrated and terrain corrected and its band tags report `SARPixelContent=intensity` and `Scale=linear`; the raster has no physical units field. These values are not water probabilities. No water mask, event inference, or area estimate was generated.

For every asset that read successfully, valid pixels were computed from the source nodata/masked read, finite-value check, and the provisional AOI. Clipped VV/VH bands were written on one common grid. A scene is marked complete only when both polarizations passed. Pair masks require common valid pixels for both polarizations at both dates.

## Candidate results

| Acquisition (UTC) | Relative orbit / pass | VV valid in AOI | VH valid in AOI | Result |
|---|---:|---:|---:|---|
| 2026-01-07 12:04 | 114 / ascending | Failed read | 89.961% | Partial; VV unavailable |
| 2026-01-09 23:56 | 150 / descending | 100.000% | 100.000% | Complete |
| 2026-01-12 12:12 | 12 / ascending | 100.000% | 100.000% | Complete |
| 2026-01-19 12:04 | 114 / ascending | 89.771% | 89.771% | Complete, with a northwest/west-side coverage gap |
| 2026-01-21 23:56 | 150 / descending | 100.000% | 100.000% | Complete |
| 2026-01-24 12:12 | 12 / ascending | 100.000% | 100.000% | Complete |
| 2026-01-31 12:04 | 114 / ascending | 90.303% | 90.303% | Complete, with a similar northwest/west-side coverage gap |

There are seven unique acquisition dates. Six scenes are fully pixel-verified and one is partial. Thirteen of fourteen candidate polarization assets were read successfully. On Jan 7, the VH asset was read and reprojected from source EPSG:32646 to the common EPSG:32645 grid. The VV read raised a RasterioIOError (“Read failed”). One isolated retry did not finish within the extended wait and was stopped; the scene remains partial. The failed layer is not counted as a zero-valued or no-water observation.

Source asset values below are the actual linear intensity samples in the AOI; the table gives median and p02–p98 to show the robust range. Per-band min and max are also preserved in the manifest. Maxima are far above p98 in several scenes, so raw extrema should not be used as representative backscatter values.

| Date | VV p02 / median / p98 | VH p02 / median / p98 |
|---|---:|---:|
| Jan 7 | — / — / — | 0.004569 / 0.025221 / 0.114243 |
| Jan 9 | 0.010302 / 0.117481 / 0.549065 | 0.003638 / 0.023237 / 0.096145 |
| Jan 12 | 0.006925 / 0.110353 / 0.490237 | 0.002233 / 0.022061 / 0.098337 |
| Jan 19 | 0.008305 / 0.112055 / 0.755930 | 0.004528 / 0.024707 / 0.118385 |
| Jan 21 | 0.008440 / 0.127094 / 0.578431 | 0.003678 / 0.024131 / 0.105231 |
| Jan 24 | 0.006859 / 0.115116 / 0.488863 | 0.002234 / 0.021862 / 0.102243 |
| Jan 31 | 0.009000 / 0.126557 / 0.785172 | 0.004901 / 0.025705 / 0.123332 |

Source RTC rasters report 10 m resolution, float32 values, and nodata `-32768`. Source asset extents are much larger than the regional AOI (reported COG object lengths are about 1.86 GB per band). The six complete regional products are the AOI clips, not full source archives.

## Compatible temporal pairs

The discovery catalogue matched exact platform, relative orbit, pass direction, IW mode and VV/VH polarization. Two complete pairs also passed actual raster-mask intersection over the entire provisional AOI:

| Pair | Relative orbit / pass | Offset from Jan 14 event date | Pixels valid in all four VV/VH rasters | Area | AOI fraction |
|---|---|---:|---:|---:|---:|
| Jan 9 → Jan 21 | 150 / descending | 5 days before; 7 days after | 6,475,371 | 647.537 km² | 100.000% |
| Jan 12 → Jan 24 | 12 / ascending | 2 days before; 10 days after | 6,475,371 | 647.537 km² | 100.000% |

The pairs must remain separate geometry series. Jan 9/21 has more balanced temporal offsets around the incident date; Jan 12/24 gives the closest pre-date but a later post-date. This is an imagery availability comparison, not evidence that an event occurred in any particular pixel. The relative-orbit-114 series cannot be paired across Jan 7/19 because the Jan 7 VV asset failed. Jan 19 and Jan 31 have approximately 10% spatial gaps and are not substitutes for full-support pairs.

The valid-pixel maps show the partial coverage wedge for Jan 19 and Jan 31. The maps depict only raster availability against the provisional envelope; they do not depict village boundaries.

![Sentinel-1 pair coverage and selected Sentinel-2 clear masks](../data/gherproof/regional/processed/phase6b/figures/phase6b_pixel_validity_maps.png)

## Local raster products and quality checks

Complete-scene clipped products are under `data/gherproof/regional/processed/phase6b/sentinel1/`; two pair masks are under `pair_masks/`. Every product has SHA-256, byte size, grid metadata and valid-pixel counts in [`phase6b_sentinel1_pixel_validation.json`](../data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json). The independent local Rasterio audit is in [`phase6b_raster_qc_manifest.json`](../data/gherproof/manifests/phase6b_raster_qc_manifest.json).

The six two-band clips have common EPSG:32645 alignment, 10 m resolution, float32 bands named VV and VH, and nodata `-32768`. Rasterio reopened all 40 Phase 6B GeoTIFF outputs in the combined sensor dataset. No NaN or infinite values were found. Pair-mask raster values are `1=common valid`, `0=invalid/missing within AOI`, `255=outside AOI`.

## Limitations

- The envelope spans about 647.5 km² and is a provisional rectangular regional search extent, not validated boundaries for the six named villages, Pallimangal, fields, or an enclosure.
- Full raster coverage only means that usable source pixels were present; it does not identify water or explain a change.
- The Jan 7 VV read remains unresolved; no matched orbit-114 Jan 7/19 comparison is available.
- RTC is linear intensity while the existing Sen1Floods11 model was trained using VV/VH in dB with checkpoint-specific channel normalization. The required conversion, input-order check, nodata handling, and model preflight have not been run in Phase 6B.
- Relative orbits 12 and 150 are independent acquisitions and must not be mixed in a single temporal composite.
- No exact village polygons, field reference labels, or event-specific local accuracy assessment are present in this validation.

## Reproduction

From the repository root, with network access to Planetary Computer:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel1
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/build_report_assets.py
```

Use `--resume` to keep complete products and retry incomplete candidates. Use `--only-item <exact STAC item ID>` for one candidate. SAS query tokens are never written to manifests. `build_report_assets.py` performs local QC and figure generation; it does not access the network or run model inference.
