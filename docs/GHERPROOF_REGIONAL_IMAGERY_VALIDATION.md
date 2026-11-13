# GherProof Phase 6 — Regional Imagery Validation

## Scope and validation states

The regional search uses the provisional envelope documented in [GHERPROOF_REGIONAL_AOI_PROVENANCE.md](GHERPROOF_REGIONAL_AOI_PROVENANCE.md), not administrative village geometries. “Catalog match” means a STAC item exists and its metadata matches the stated criteria. “Local raster validated” means actual downloaded/local pixels were opened and checked. Those statuses are kept separate throughout.

## Sentinel-1 RTC discovery

Microsoft Planetary Computer anonymous STAC was queried for Sentinel-1 RTC in the provisional AOI for 2026-01-01 through 2026-01-13 and 2026-01-15 through 2026-01-31. Seven IW VV/VH scenes were returned. All scenes below are Sentinel-1A. Approximate footprint overlap is a polygon-intersection ratio in longitude/latitude coordinates, **not** a pixel-valid coverage fraction.

| Date (UTC) | Relative orbit | Direction | Mode / polarizations | Footprint overlap (approx.) | Pixel status |
|---|---:|---|---|---:|---|
| 2026-01-07 | 114 | Ascending | IW, VV/VH | 90.3% | Existing local clipped raster validated; new full regional pixels not checked |
| 2026-01-09 | 150 | Descending | IW, VV/VH | 100% | Catalog only |
| 2026-01-12 | 12 | Ascending | IW, VV/VH | 100% | Catalog only |
| 2026-01-19 | 114 | Ascending | IW, VV/VH | 90.1% | Existing local clipped raster validated; new full regional pixels not checked |
| 2026-01-21 | 150 | Descending | IW, VV/VH | 100% | Catalog only |
| 2026-01-24 | 12 | Ascending | IW, VV/VH | 100% | Catalog only |
| 2026-01-31 | 114 | Ascending | IW, VV/VH | 90.6% | Catalog only |

The scene footprints expose VV and VH assets in the RTC collection. Three clean pre/post geometry groups are catalogued: Jan 7/19 on relative orbit 114 ascending; Jan 9/21 on relative orbit 150 descending; Jan 12/24 on relative orbit 12 ascending. The January 7/19 pair remains the preferred first comparison because it brackets the reported January 14 incident closely and is the only full pair already represented by local pixels. The Jan 12/24 and Jan 9/21 pairs must remain separate orbit series. Jan 7/31 is also orbit 114 ascending but is a later, less event-proximate post observation. These are catalogue comparisons; alternate scenes have not been downloaded or processed.

The Jan 7 and Jan 19 catalogue items match Sentinel-1A, IW, VV/VH, relative orbit 114, ascending. Their actual local clips are 2-band float32 GeoTIFFs in EPSG:32645 at 10 m, with nodata -32768 and `VV`/`VH` band descriptions. The Phase 4B raster validation identifies RTC gamma-nought (gamma0) linear backscatter. It is backscatter evidence, not water probability.

### Existing Jan 7/19 coverage within the regional envelope

| Measure | Result |
|---|---:|
| Regional 10 m mask pixels | 6,475,371 |
| Common pixels valid in VV and VH on both dates | 463,292 |
| Common valid area at 10 m | 46.3292 km² |
| Common valid fraction of provisional regional envelope | 7.1547% |
| Part of regional mask intersecting existing local raster grid | 1,060,319 pixels (16.38%) |
| Common valid fraction in western reporting sector | 14.31% |
| Common valid fraction in eastern reporting sector | 0% |

The existing local raster bounds are EPSG:32645 `[720240, 2537380, 735880, 2554240]`. The source raster clip predates this larger Phase 6 envelope and was made for the western provisional locality. The 0% eastern-sector result means **no existing local clip coverage there**, not no water. A 10 m common-validity raster and PNG overview are provided; color indicates data availability, not flood status.

No newly discovered regional RTC asset completed a pixel-window read in this phase. A bounded remote COG-window run was attempted but did not complete within the working session and was stopped; it produced no successful expanded-coverage validation. Therefore the footprint percentages must not be substituted for per-pixel coverage.

## Sentinel-2 L2A discovery and local imagery

Planetary Computer STAC returned 14 Sentinel-2 L2A items on tile 45QYF, seven before and seven after January 14. The STAC `eo:cloud_cover` values are catalogue metadata percentages, not local cloud masks.

| Date | STAC cloud cover (%) | Status |
|---|---:|---|
| Jan 03 | 0.227472 | Catalog only |
| Jan 05 | 99.938488 | Catalog only; poor catalog-level candidate |
| Jan 07 | 0.046010 | Catalog only |
| Jan 08 | 0.002496 | Catalog only |
| Jan 10 (S2A) | 0.649180 | Catalog only |
| Jan 10 (S2B) | 1.005260 | Catalog only |
| Jan 13 (S2B) | 0.000384 | Existing local RGB clip; no pixel-level cloud/shadow mask |
| Jan 15 | 0.182911 | Catalog only |
| Jan 18 | 0.000315 | Catalog only; closest low-cloud post-event candidate |
| Jan 20 | 0.001854 | Catalog only |
| Jan 23 | 0.000469 | Catalog only |
| Jan 25 | 0.000510 | Catalog only |
| Jan 28 | 0.000068 | Catalog only; lowest reported post-event catalogue cloud value |
| Jan 30 | 40.004286 | Catalog only; poor catalog-level candidate |

The existing January 13 product is a three-band RGB visual crop, EPSG:32645, 10 m, nodata 0. It contains 1,057,992 non-nodata pixels inside the Phase 6 envelope (16.34%); it does not include a regional Sentinel-2 classification/SCL mask. No post-event optical asset was downloaded or pixel-QA checked. Consequently Sentinel-2 does **not yet provide independently validated regional corroboration**. Jan 18 is the logical first post-event scene to inspect at pixel level; Jan 28 is a later backup, not a substitute for the near-event observation.

## Retrieval, provenance and outputs

- `data/gherproof/manifests/phase6_sentinel1_regional_manifest.json` — RTC scene metadata, footprints, candidate geometry groups, and local pair coverage.
- `data/gherproof/manifests/phase6_sentinel2_regional_manifest.json` — L2A catalogue records and local pre-event clip status.
- `data/gherproof/manifests/phase6_regional_valid_coverage.json` — source raster metadata, pixel counts, checksums and coverage raster record.
- `data/gherproof/regional/processed/sentinel1/existing_jan07_jan19_common_valid_coverage_10m_utm45n.tif` — 0=not locally valid, 1=common valid, 255=outside AOI.
- `data/gherproof/regional/phase6_existing_s1_coverage.png` — visual coverage summary.
- `scripts/gherproof/phase6/regional_discovery.py` — reproducible STAC catalogue discovery; `--check-pixels` enables optional remote RTC pixel-window checks, which remain unverified and may be slow.
- `scripts/gherproof/phase6/validate_existing_coverage.py` — local-only remap and coverage summary for already existing Jan 7/19 and Jan 13 files.

`regional_discovery.py` uses the Planetary Computer STAC API and SAS endpoint; it does not persist SAS tokens. A successful catalogue query is not a download. Only the pre-existing Jan 7/19 and Jan 13 local clips were used as actual regional pixels in this phase.

## Inference and area decision

Regional model inference is **not justified on the currently validated image coverage**: the existing matched Jan 7/19 rasters provide only 7.15% common support in the provisional envelope and zero support in the eastern reporting sector; alternative tracks are not processed; and no village polygons are available. The existing Sen1Floods11 model scores remain independent benchmark results and are not evidence of performance in Jashore. No new model was trained, and no event water mask or inundation estimate was generated.

There is no defensible regional or cropland inundation area from the assets validated here. January reports give approximately 1,500 bighas in the [Dhaka Post report](https://www.dhakapost.com/country/424238) and approximately 158 hectares in [Samakal's report](https://samakal.com/whole-country/article/334020). These are separate, independently reported context figures with different units and reporting methods. Neither was used as a model label, raster threshold, validation target, or area constraint.

No result localizes the breach, establishes that all detected water originated at Pallimangal, or confirms the reported event footprint. Rainfall, irrigation, crop phenology, aquaculture operations, soil moisture and drainage timing remain plausible alternative causes of radar change.
