# GherProof Phase 5 — Sentinel-1 coverage assessment

**Enclosure coverage: NOT EVALUATED.** Reporting places Pallimangal in Sujatpur mouza in Beel Kedaria, Bhavadah area, but provides no defensible coordinate, cadastral plot, or polygon. Coverage percentages over the enclosure and its surrounding agricultural land cannot be calculated from toponyms alone.

## What was measured

The existing Phase 4B January 7/19 Sentinel-1 RTC products were retained. They share an EPSG:32645 10 m grid and an identical common mask requiring valid VV and VH observations on both dates. Rasterio read the mask and its AOI band directly; the count and area were independently rechecked while producing the Phase 5 package.

| Measurement | Result |
|---|---:|
| Common-valid pixels in provisional search window | 463,292 |
| Pixel area | 100 m² |
| Common-valid area | 46.3292 km² |
| Provisional-window pixel count | 2,555,756 |
| Fraction of provisional window | 18.1274% |
| Valid support arrangement | Eastern strip of broad search window |
| Enclosure area / common-valid pixels / coverage % | Unknown / unknown / not evaluated |
| 250 m, 500 m, 1 km buffer coverage | Not calculated: no supportable site geometry |
| Surrounding cropland coverage | Not calculated: no enclosure geometry or cropland reference |

The 18.1274% fraction is a measured property of the analyst-selected broad raster window. It is not coverage of the administrative village, the fish enclosure, the reported breach, or cropland. Missing support pixels are unknown data, not evidence of dry land.

## Pair interpretation gate

The pair remains conditionally suitable only for cautious, co-registered gamma-naught backscatter comparison on common-valid pixels. Both are Sentinel-1A, relative orbit 114, ascending, IW, VV/VH RTC products. These facts do not prove the target falls inside the support. The eastern-strip constraint could completely exclude the enclosure; the direction cannot be resolved without a target point/polygon.

No alternate Sentinel-1 acquisitions were selected in Phase 5. The site's coordinates are unresolved, so scene footprint checks cannot be run against the actual target and choosing a different footprint would invite selection by coverage rather than geographic evidence. Once a GPS point or polygon exists, search January 1–13 and January 15–31 using the same RTC collection and preferably orbit 114 ascending; inspect exact footprints and common per-pixel coverage before replacing or supplementing the preserved pair.

## Cropland and permanent water

No target-level cropland or permanent-water reference is available. I inspected the archived Clark Labs 2022 Bangladesh land-cover class raster and made a 15 m EPSG:32645 cutout for QGIS context. Nominal projected class areas in the **provisional search window** are 5.68575 km² pond aquaculture, 0.911475 km² water, and 248.97645 km² other landcover. In the **S1 common-valid support**, the 2022 layer assigns 1.814625 km² to pond aquaculture and 44.512875 km² to other landcover, with no pixels assigned to class 4 water. These are summaries of a 2022 categorical reference after nearest-neighbor reprojection; they do not measure January 2026 target land use. Class 5 is generic “other landcover,” not cropland, and class 4 is not proof of permanent water. Class 3 cannot distinguish Pallimangal from neighboring ponds. No site-specific reference was generated.

January 13 Sentinel-2 remains visual context, not a validated land-cover classification; scene-level cloud metadata does not replace pixel cloud/shadow screening. Existing OSM search returned no unique Pallimangal feature; OSM absence is not conclusive. No field-validated reference is available. The local Clark raster's source, legend, CRS and limitations are recorded in `data/gherproof/manifests/phase5_site_coverage_assessment.json` and raster tags.

The machine-readable result is `data/gherproof/manifests/phase5_site_coverage_assessment.json`. Null target coverage values are intentional and represent unknown, not zero. A QGIS GeoPackage contains only the provisional search-window raster footprint and actual common-valid footprint, both clearly flagged as non-site reference layers.

## Phase 5B update — target geometry still unavailable

The J.L. 143 Sujatapur/Sujatpur listing provides a better request key, but it is a secondary source and no official cadastral map or plot geometry was recovered. No Pallimangal coordinate, Beel Kedaria polygon, southern embankment or khal geometry has been added. Accordingly, all target-specific coverage values remain **unknown / not evaluated**. The Jan 7/19 pair's 463,292 common-valid pixels, 46.3292 km² and 18.1274% still describe only the provisional broad raster window. They must not be reported as Pallimangal coverage.

The same common-support count applies to the actual January pair; no new satellite acquisition was requested because selecting dates before an independently supported site location could bias selection to a broad search window. Once an official sheet or local GPS point is available, locate the site independently first, then compute enclosure and 250 m/500 m/1 km buffer support. Search additional Sentinel-1 acquisitions if that spatial test shows inadequate coverage. Current state remains `not_delineated`; experimental inference remains blocked. See `docs/GHERPROOF_PHASE5B_REPORT.md` for source results and required cadastral/GPS request.

## Phase 5C update — official sheets catalogued; site coverage remains unknown

The official DLRS portal's read-only catalogue confirms Sujatpur / J.L. 143 for Manirampur, with two digitized/available CS sheets and two RS sheets (sheets 1 and 2). Full map originals require purchase, so no cadastral geometry was obtained. Public preview thumbnails and a 2014 Beel Bakar locality schematic do not provide target geometry or alignment control. The historic schematic is not a Beel Kedaria or Pallimangal boundary.

No additional Sentinel-1 acquisitions were queried or selected; site location must precede acquisition selection. January 7/19 target overlap remains **not evaluated**, not zero. The measured 463,292 common-valid pixels, 46.3292 km² and 18.1274% still apply only to the broad provisional search window. The 250 m / 500 m / 1 km buffer and cropland coverages are uncomputed. Inference readiness remains `not_ready` pending full-sheet/plot inspection, independent farm-to-parcel or landmark identification, reviewed site geometry, and a target-specific mask intersection. See `docs/GHERPROOF_PHASE5C_REPORT.md` and `data/gherproof/manifests/phase5c_official_map_search.json`.

## Phase 5D update — free-source checks did not establish target geometry

One third-party BS/RS J.L. 143 sheet-1 listing was found; its public thumbnail was compared with the four official DLRS previews, but no content match was confirmed. No full-resolution copy or geometry was recovered. The Ministry of Land public Khulna location query returned Bagerhat and Khulna but not Jashore, so its public selector path did not reach Sujatpur. MowjaBD's public Drive route was unavailable during the check. No candidate was created and no coverage calculation was changed. Enclosure and buffer coverage remain **unknown**, while 46.3292 km² / 18.1274% continues to describe only the broad provisional window. See [Phase 5D report](GHERPROOF_PHASE5D_REPORT.md), [free-source findings](GHERPROOF_FREE_CADASTRAL_SOURCES.md), and `data/gherproof/manifests/phase5d_free_source_search.json`.
