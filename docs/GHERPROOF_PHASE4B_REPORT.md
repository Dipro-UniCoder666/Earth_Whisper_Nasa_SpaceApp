# GHERPROOF PHASE 4B — Planetary Computer Sentinel-1 recovery

**Outcome: PARTIAL / CONDITIONALLY SUITABLE for an aligned historical backscatter comparison over the measured common-valid portion of the provisional locality. Event interpretation remains blocked.**

## Summary

The anonymous Microsoft Planetary Computer STAC API was reachable. Exact-date searches found the corresponding January 7 and January 19 acquisitions in both Sentinel-1 RTC and GRD; each search returned one item. Anonymous SAS signing and bounded HTTP Range access to all four RTC COG assets succeeded. Four source-polarization windows were read and validated; the full ~1.8 GB source COG files were not downloaded. Two AOI-clipped analysis-ready products and one validity-mask stack were written and independently checked.

The alternative-provider items correspond to the CDSE acquisition candidates through matching Sentinel-1 platform/mode, sensing start and stop times, relative orbit, and datatake fields. MPC item identifiers omit CDSE-specific trailing product-instance suffixes and use `_rtc`; these are **alternative RTC representations of the same acquisitions**, not the CDSE COG files. The unchanged CDSE manifest still truthfully records its four assets as `authentication_blocked`.

The local clips provide a conditionally comparable backscatter pair over **463,292 common-valid 10 m pixels (about 46.33 km²; 18.13% of the provisional locality box)**. Valid observations form an eastern strip. Because the search window is broad and no Pallimangal point or boundary is verified, we cannot confirm that the enclosure or reported breach location falls inside this strip. The pair is not sufficient to claim an event detection, water extent, breach, crop impact, or loss. No ML inference or training ran.

## Public collection and search results

The official STAC collection list returned 139 collections. The collections used were:

| Collection | Current metadata | Asset format | Used? |
|---|---|---|---|
| `sentinel-1-rtc` | RTC gamma-naught product; CC BY 4.0; Catalyst processor; Microsoft host/licensor; STAC contains `msft:requires_account: true` | VV/VH separate cloud-optimized GeoTIFFs, Float32, nodata `-32768`, 10 m | Yes |
| `sentinel-1-grd` | GRD amplitude products; collection licence field is `proprietary` (ESA/Copernicus data terms also linked) | VV/VH separate COGs plus SAFE, noise, product, and calibration metadata assets | Searched as fallback; not processed |

The public Planetary Computer SAS documentation states that STAC is public and that SAS tokens can be requested anonymously; the current RTC token endpoint returned HTTP 200 without an account key, despite the collection metadata flag. Each COG byte-range check returned HTTP 206. No token or signed URL was logged or persisted. The SDK packages `planetary-computer` and `pystac-client` were not installed, so the reproducible implementation uses the same official STAC/SAS REST endpoints via `requests` and keeps SAS material in memory.

Every query used bbox `[89.15, 22.93, 89.30, 23.08]` and a single exact UTC date window. No neighboring dates were substituted.

| Search | Results | Selected item |
|---|---:|---|
| RTC, 2026-01-07 | 1 | `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_rtc` |
| RTC, 2026-01-19 | 1 | `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_rtc` |
| GRD, 2026-01-07 | 1 | `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B` |
| GRD, 2026-01-19 | 1 | `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9` |

Collection metadata and full unsigned STAC items are stored in `data/gherproof/manifests/planetary_computer_event_imagery.json` and `data/gherproof/raw/event_sentinel1/planetary_computer/stac_items/`. No SAS query strings appear in these files.

### Individual polarization-asset outcomes

`verified` here means the source COG range/header and AOI pixel window were read, then the corresponding local clipped band passed independent raster QC. The complete scene-sized blob was **not** downloaded, so no full-source-file checksum is claimed; the SHA-256 below belongs to the local two-band clip.

| Date | Pol | MPC asset | Access result | Full scene downloaded | Local verified output / SHA-256 |
|---|---|---|---|---|---|
| 2026-01-07 | VV | `vv` RTC COG | HTTP 206 + Rasterio window read | No | Jan 7 clip; `5fd8836464deed7935ef838fb47028bec19393dbe09c33f20ce51c5d4bc336e0` |
| 2026-01-07 | VH | `vh` RTC COG | HTTP 206 + Rasterio window read | No | Jan 7 clip; `5fd8836464deed7935ef838fb47028bec19393dbe09c33f20ce51c5d4bc336e0` |
| 2026-01-19 | VV | `vv` RTC COG | HTTP 206 + Rasterio window read | No | Jan 19 clip; `47781c5af46fc7a2fa688489f30f07281997e9261e5091c614972eaad79e538b` |
| 2026-01-19 | VH | `vh` RTC COG | HTTP 206 + Rasterio window read | No | Jan 19 clip; `47781c5af46fc7a2fa688489f30f07281997e9261e5091c614972eaad79e538b` |

## Acquisition crosswalk and source metadata

| Date | CDSE reference product identifier | MPC RTC item | MPC STAC datetime | Scene start/end (UTC) | Orbit / direction | Mode / pols | Timeliness / orbit source |
|---|---|---|---|---|---|---|---|
| 2026-01-07 | `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_6998_COG` | `S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_rtc` | 12:04:40.528434Z | 12:04:28Z–12:04:53Z | 114 / ascending | IW / VV,VH | Fast-24h / RESORB |
| 2026-01-19 | `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_E3D6_COG` | `S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_rtc` | 12:04:39.512002Z | 12:04:27Z–12:04:52Z | 114 / ascending | IW / VV,VH | Fast-24h / RESORB |

Both items identify Sentinel-1A, product type GRD, processing level 1, C-band, IW mode, right-looking, and both polarizations. Provider STAC time is a scene timestamp and differs from the CDSE acquisition timestamp by about 12 seconds; the product sensing start/end, orbit and datatake provide the crosswalk. MPC IDs omit the CDSE suffix (`6998` / `E3D6` and `_COG`), so the crosswalk is acquisition-level rather than file identity. RTC processing datetimes were 2026-01-07 14:46:18Z and 2026-01-19 14:42:58Z. Both use `Fast-24h` timeliness and `RESORB`; `s1:processing_version` is absent. Collection-level processing is consistent, but an explicit software/version/DEM baseline is not provided in item properties.

## Actual COG access and raster QC

All four assets passed an actual byte-range response (HTTP 206), TIFF header check, Rasterio/GDAL open, metadata read, and locality-window pixel read. Raster values are Float32 with `-32768` nodata, scale 1 and offset 0. Original source grids use EPSG:32646 at 10 m. VV and VH align exactly within each scene. The native grid origins differ between dates: Jan 7 is at easting 103,610 m / northing 2,673,290 m with 28,349 × 21,066 pixels; Jan 19 is at 103,670 m / 2,673,280 m with 28,348 × 21,065 pixels. Thus the source dates do not share an identical transform; they were warped onto a common 10 m target grid using nearest-neighbour resampling.

The collection describes RTC values as gamma-naught. Actual band metadata tags `SARPixelContent=intensity` and `Scale=linear`; the GeoTIFF `units` field itself is blank. Values were preserved without dB conversion or independent per-date normalization. They are radar backscatter measurements, not water probabilities.

| Date | Pol | Source dims / CRS / resolution | Nodata | Valid in provisional AOI | Fraction | Min / p02 / median / p98 / max (stored values) |
|---|---|---|---:|---:|---:|---|
| Jan 7 | VV | 28,349×21,066 / EPSG:32646 / 10 m | -32768 | 472,974 | 18.51% | 0.001724 / 0.009053 / 0.122171 / 0.725775 / 87.168396 |
| Jan 7 | VH | 28,349×21,066 / EPSG:32646 / 10 m | -32768 | 472,974 | 18.51% | 0.000928 / 0.005188 / 0.025956 / 0.122183 / 4.572379 |
| Jan 19 | VV | 28,348×21,065 / EPSG:32646 / 10 m | -32768 | 463,292 | 18.13% | 0.001486 / 0.008925 / 0.101974 / 0.727395 / 98.928436 |
| Jan 19 | VH | 28,348×21,065 / EPSG:32646 / 10 m | -32768 | 463,292 | 18.13% | 0.001230 / 0.004908 / 0.023141 / 0.128210 / 5.448867 |

The stored source tags record `ProductType=ORTHO`, `ProjectionId=Ground Range`, `Scale=linear`, `SARPixelContent=intensity`, the acquisition timestamp, ascending orbit, and incidence near/far angles of 30.7765°/46.2817° (Jan 7) and 30.7783°/46.2827° (Jan 19). Source COGs expose per-dataset masks plus nodata. The pipeline respects masked/nodata reads; pixels outside common validity remain nodata and are masked, not set to non-water.

The maxima (VV 87–99 and VH 4.6–5.4) are much higher than the 98th-percentile values; this long upper tail is retained and reported without clipping. It should be reviewed if later analyses use means or thresholds; no data-driven outlier removal was applied.

## Spatial coverage and common-grid products

The target grid is EPSG:32645 (UTM zone 45N, containing the locality), 10 m, 1,564 × 1,686 pixels, transform origin easting 720,240 m / northing 2,554,240 m. Nearest-neighbour reprojection was used to preserve stored sample values. Each date's VV/VH clip has a common mask requiring both polarizations for both dates and the provisional AOI polygon. This strict shared support contains 463,292 pixels of 2,555,756 AOI pixels: **18.1274%**, approximately **46.3292 km²** at 100 m² per target pixel. Jan 7 dual-pol coverage is 472,974 pixels (18.5062%); Jan 19 is 463,292 pixels (18.1274%).

The valid-data footprint lies along the eastern strip of the broad locality box. Its approximate common-valid envelope is 89.2545–89.3025° E and 22.9299–23.0806° N; the envelope is not an enclosure polygon. The exact Pallimangal boundary and event location are not known at pixel level, so whether the enclosure is inside the covered strip is **not evaluated**.

![Sentinel-1 RTC valid-data coverage over provisional search window](../data/gherproof/processed/sentinel1/planetary_computer/coverage_validity.png)

## Pre/post suitability decision

**`conditionally_suitable` for a cautious, co-registered gamma-naught backscatter comparison only over the common-valid footprint.** Supporting evidence: same Sentinel-1A platform, relative orbit 114, ascending direction, IW mode, matching VV/VH, acquisition-level CDSE crosswalk, same RTC collection, compatible 10 m measurement product family, both COGs readable, and actual common valid pixels. Same date products have identical VV/VH grids; the source date grids were aligned to EPSG:32645.

The suitability is conditional because only 18.13% of the broad locality window has common valid data and the enclosure's location within that strip is unknown. Item-level RTC processing version/DEM baseline is not explicit, although both scenes use the same collection, Fast-24h timeliness, and RESORB orbit source. Seasonal/rainfall/soil-moisture/irrigation/crop/aquaculture and radar-surface-roughness differences remain plausible causes of backscatter variation. The pair is not evidence of water, a flood, a broken embankment, causation, damages, or an affected area. The paper/reported incident date remains secondary-media based; the scene pair alone cannot confirm it.

## Files created

- `data/gherproof/manifests/planetary_computer_event_imagery.json` — searches, selected metadata, license/attribution, source URLs without SAS, statuses, access and output provenance.
- `data/gherproof/manifests/planetary_computer_scene_validation.json` — source raster QC and independent output QC.
- `data/gherproof/raw/event_sentinel1/planetary_computer/stac_items/` — four unsigned original STAC item metadata documents.
- `data/gherproof/processed/sentinel1/planetary_computer/2026-01-07_sentinel1_rtc_vv_vh_10m_utm45n.tif` — 3,174,576 bytes; SHA-256 `5fd8836464deed7935ef838fb47028bec19393dbe09c33f20ce51c5d4bc336e0`.
- `data/gherproof/processed/sentinel1/planetary_computer/2026-01-19_sentinel1_rtc_vv_vh_10m_utm45n.tif` — 3,173,668 bytes; SHA-256 `47781c5af46fc7a2fa688489f30f07281997e9261e5091c614972eaad79e538b`.
- `data/gherproof/processed/sentinel1/planetary_computer/2026-01-07_2026-01-19_rtc_validity_masks_10m_utm45n.tif` — per-date VV/VH, common validity, and provisional AOI mask bands; checksum in the alternative-provider manifest.
- `data/gherproof/processed/sentinel1/planetary_computer/coverage_validity.png` — map of actual data availability, not water.
- `docs/GHERPROOF_PLANETARY_COMPUTER_SETUP.md` and updated `data/gherproof/processed/README.md`.

The first exploratory clip in EPSG:32646 was superseded by the final local-zone 45N products. It is retained as a separately named intermediate in the output directory and is not referenced by the final manifests.

## Tests and reproducibility

- Live anonymous API discovery, all four exact-date searches, anonymous RTC/GRD SAS endpoints, and four COG byte-range reads succeeded.
- Each source COG opened in Rasterio and its AOI window was read. The full scene file was not downloaded; no full-source SHA-256 is claimed.
- No full-scene download interruption was injected because retrieval uses bounded COG range/window reads. Local clips are written to temporary `.part` files then atomically renamed; rerunning regenerates an incomplete clip. The mock suite covers 429 backoff, but the live service did not rate-limit this run.
- Independent local QC verified both output GeoTIFFs, checksums, CRS, transform, dimensions, bands, nodata, finite values, common internal masks, validity-mask stack alignment and AOI containment. Both output grids and masks are identical.
- Full focused GherProof suite, including Planetary Computer request, pagination, rate-limit retry, identifier crosswalk and signed-URL-sanitization tests: **26 passed**, with two expected Rasterio warnings from an intentionally invalid fixture.
- Python compilation passed for the retrieval and independent validation scripts.
- Reproduction commands are in `docs/GHERPROOF_PLANETARY_COMPUTER_SETUP.md`.

## Remaining blockers

1. A GPS location or authoritative GIS polygon for the actual Pallimangal enclosure/breach is required to establish that the observed swath covers the target.
2. Only 18.13% of the provisional locality window is common-valid; missing pixels are not evidence of dry land.
3. An enclosure boundary, permanent-water context, agricultural references, and local field observations are missing.
4. This analysis has not run either benchmark model and makes no local accuracy claim.
5. Backscatter changes require hydrological/context evidence and cannot diagnose a breach or damage.

Event inference and affected-area calculation remain prohibited until geometry and validation requirements are met. Sandhya/Monda and the pre-existing project changes were left untouched; no DELTAQ functionality was restored.
