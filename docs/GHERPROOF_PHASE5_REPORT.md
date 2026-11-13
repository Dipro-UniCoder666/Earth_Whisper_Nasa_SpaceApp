# GHERPROOF PHASE 5 — Pallimangal site localization, boundary review and coverage

**Run date:** 2026-11-12
**Overall outcome:** PARTIAL
**Exact site:** NOT FOUND / NOT VERIFIED
**Boundary:** `not_delineated`
**Inference readiness:** `partially_ready` for geospatial/data preparation only; NOT ready for event inference or quantitative analysis.

## Executive result

The administrative village reference for Sujatpur is confirmed in an official DPHE geographic-code table as Jessore District / Manirampur Upazila / Kultia Union / Sujatpur village, and corroborated by the official Kultia Union Parishad representative page. Newer textual research improves the named geographic context: Samakal places Pallimangal in Sujatpur mouza in Beel Kedaria, Bhavadah area; it describes the southern embankment, water entering from an adjacent khal, and a leased operation reported to cover about 1,500 bigha. Dhaka Post and Daily Country Today corroborate the named farm, south-side incident and affected-village context. These reports still provide no coordinate, cadastral plot, identifiable georeferenced landmark or polygon. The place-name context is moderately supported; exact coordinates remain low confidence. Review of the official administrative sources and existing January 13 Sentinel-2 visual scene did not uniquely identify which of many pond-like parcels is Pallimangal.

No enclosure coordinate or polygon was fabricated. The existing boundary workflow remains unchanged and its status stays `not_delineated`. As a result, target enclosure overlap, buffer coverage, affected cropland coverage and January event location relative to the Sentinel-1 swath are **not evaluated**. The 46.3292 km² common-valid footprint and 18.1274% coverage are measurements of the broad provisional search window only. The eastern strip may exclude the target; without a site geometry, neither inclusion nor exclusion can be concluded.

## Evidence and location finding

| Finding | Evidence | Status / limitation |
|---|---|---|
| Sujatpur is under Kultia Union, Manirampur, Jessore | DPHE geo-code record: codes 41 / 61 / 473 / 368, PDF p.72 | Administrative village confirmed; no coordinate |
| Regional location context | LGED Monirampur upazila map; official Manirampur portal materials reference Sujatpur and Kultia | No Pallimangal parcel/farm geometry; PDF context is not a GIS layer |
| Named event site and textual setting | Samakal places the operation in Sujatpur mouza, Beel Kedaria, Bhavadah; reports south edge adjacent to a khal and a ~1,500-bigha lease; Dhaka Post and Daily Country Today corroborate site and village context | Moderate confidence in toponyms; secondary news reports, no coordinate, plot, or polygon; reported area is not GIS |
| Existing OSM search | Prior Nominatim/Overpass query recorded no matching enclosure feature | OSM incomplete; does not prove absence |
| January 13 visual scene | Sentinel-2B L2A crop visually inspected | Multiple pond-like/field-like features; none uniquely identified |
| Historical aquaculture reference | Clark Labs 2022 Bangladesh land-cover/aquaculture raster previously audited | Historical broad class only, not exact 2026 gher boundary |

Full source assessments and citations are in [GHERPROOF_SITE_LOCATION_EVIDENCE.md](GHERPROOF_SITE_LOCATION_EVIDENCE.md). Relevant sources include the [DPHE code document](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf), [Kultia Union Parishad](https://kultiaup.jessore.gov.bd/pages/leaders), [Samakal incident report](https://samakal.com/whole-country/article/334020/%E0%A6%AA%E0%A6%BE%E0%A7%9C-%E0%A6%AD%E0%A7%99%E0%A6%99%E0%A7%87-%E0%A6%A2%E0%A7%81%E0%A6%95%E0%A6%B2-%E0%A6%AA%E0%A6%BE%E0%A6%A8%E0%A6%BF-%E0%A7%A1%E0%A7%AB%E0%A7%AE-%E0%A6%B9%E0%A7%87%E0%A6%95%E0%A7%8D%E0%A6%9F%E0%A6%B0-%E0%A6%9C%E0%A6%AE%E0%A6%BF), [Dhaka Post](https://www.dhakapost.com/country/424238), [LGED upazila map](https://oldweb.lged.gov.bd/UploadedDocument/Map/KHULNA/jessore/monirampur/monirampur.pdf), and [Ministry of Land map portal](https://map.land.gov.bd/).

## Image and review package

January 13, 2026 Sentinel-2B visual data was inspected and placed on the same EPSG:32645 grid as the existing Sentinel-1 validity mask. The review map overlays the January 7/19 common-valid S1 support in blue. The map explicitly says this is valid measurement support, not water. It carries only an administrative-text reference to Sujatpur, not a map pin, because the village-level source does not give a coordinate.

![Phase 5 human review map](../data/gherproof/review/phase5/pallimangal_human_review_map.png)

The QGIS GeoPackage has two vector layers: `provisional_search_window` (raster-derived broad AOI; not an administrative or site boundary) and `common_valid_footprint` (derived from the measured common-valid raster mask). No candidate-boundary GeoJSON was created because no geometry met the evidence threshold. The GeoPackage does not contain administrative polygons, roads/canals, or water features: no corresponding georeferenced GIS layer was acquired. Use the existing context TIFF and validity mask as separate QGIS raster layers alongside the GeoPackage.

## Sentinel-1 coverage

| Metric | Actual result |
|---|---:|
| Jan 7/19 common-valid pixels (all VV/VH both dates) | 463,292 |
| Area at 10 m target pixel size | 46.3292 km² |
| Pixels in provisional raster search window | 2,555,756 |
| Search-window valid fraction | 18.1274% |
| Swath arrangement | Eastern strip |
| Pallimangal enclosure valid pixels / percent | Not evaluated: no site geometry |
| Surrounding area at 250/500/1,000 m | Not evaluated: no site geometry |
| Cropland coverage outside enclosure | Not evaluated: no target geometry or crop reference |

The Jan 7/19 pair remains conditionally suitable for a matched-orbit backscatter comparison only on its common support. Actual target coverage is unknown. The mapped eastern strip is a material limitation: if the enclosure is west of the supported pixels, this pair cannot answer the event question. `docs/GHERPROOF_COVERAGE_ASSESSMENT.md` and `data/gherproof/manifests/phase5_site_coverage_assessment.json` preserve the measured window results and null enclosure measures.

No additional scene search was represented as completed: with no actual target point/polygon, any “better-covered” scene selection would optimize against the broad search box rather than the named farm. Once the target is geolocated, search the requested pre-event (Jan 1–13) and post-event (Jan 15–31) windows, first matching orbit 114 ascending RTC, and inspect actual pixel coverage. Preserve the Jan 7/19 originals.

## Cropland and permanent-water references

No target-specific crop/permanent-water polygons were produced. I read the 2022 Bangladesh Clark Labs categorical GeoTIFF directly from the existing archive (15 m native grid), reprojected a local cutout to EPSG:32645 at 15 m with nearest-neighbor resampling, and preserved its class legend in `data/gherproof/reference/clark_2022_locality_context_15m_utm45n.tif`.

Within the broad provisional window, the projected 2022 classification contains nominally 5.68575 km² class 3 (pond aquaculture), 0.911475 km² class 4 (water), and 248.97645 km² class 5 (other landcover). Within the 2026 S1 common-valid footprint, class 3 covers nominally 1.814625 km² and class 5 44.512875 km²; class 4 has no pixels in this overlay. These are class summaries after reprojection, not current land cover, permanent water, farm boundaries, or target-site statistics. **Class 5 is not a cropland label**, class 4 is not persistence-validated, and class 3 cannot identify Pallimangal. Sentinel-2 remains context imagery without a documented pixel-level cloud/shadow mask. OSM remains an incomplete map reference. Detailed source, legend and limitations are in the coverage assessment and machine-readable manifest.

## Readiness decision

**State: `partially_ready`.** Administrative location and broad-window satellite data are documented, but prerequisites 1–6 are not satisfied for the enclosure:

1. Village administrative reference: met at village-name level, not site coordinate.
2. Enclosure boundary: not delineated or reviewed.
3. Pre/post imagery overlap: unknown at target.
4. Valid target pixels / surrounding coverage: unknown at target.
5. Cropland and permanent water references: not established locally.
6. Layer limitations: documented; substantial geographic uncertainty remains.

Do not run either model, generate water probabilities/new-water masks, calculate flooded area, or make a breach/impact statement from these data yet. No final ML inference was run. Quantitative and experimental event inference are blocked until exact-site geography, boundary review and target coverage are established.

## Exact evidence still needed

- GPS point / recognizable local landmark for Pallimangal and ideally the reported south-side breach.
- Sujatpur mouza name/sheet/JL number and cadastral plot number, or a Fisheries/BWDB/IWM/CEIP/CEGIS asset/farm identifier.
- Georeferenced boundary or a reviewer-drawn candidate with dated imagery references and named reviewer.
- Current cropland and permanent-water/aquaculture context polygons, with source dates and confidence, followed by field confirmation.
- After geometry arrives, measured S1 target intersection and buffer support, plus a separate scene search if needed.

## Files created or updated

- `docs/GHERPROOF_PHASE5_REPORT.md`
- `docs/GHERPROOF_SITE_LOCATION_EVIDENCE.md`
- `docs/GHERPROOF_COVERAGE_ASSESSMENT.md`
- `docs/GHERPROOF_BOUNDARY_PROVENANCE.md` (Phase 5 update; review workflow retained)
- `data/gherproof/manifests/enclosure_boundary_provenance.json` (added administrative evidence; null geometry/status preserved)
- `data/gherproof/manifests/phase5_boundary_candidates.json` (0 evidence-supported candidates)
- `data/gherproof/manifests/phase5_site_coverage_assessment.json`
- `data/gherproof/review/phase5/pallimangal_phase5_review.gpkg`
- `data/gherproof/review/phase5/pallimangal_human_review_map.png`
- `data/gherproof/review/phase5/README.md` (QGIS layer loading instructions and source limits)
- `data/gherproof/reference/clark_2022_locality_context_15m_utm45n.tif` (local historical class context)
- `scripts/gherproof/build_phase5_review_package.py`

The prior Phase 4B imagery, manifests, Sentinel-2 context source, model checkpoints and frontend were not changed. No Sandhya or Monda files were touched. No DELTAQ files were added or restored.

## Validation and reproduction

Executed `backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5_review_package.py`. The script reads the real common-valid and AOI mask bands, requires exactly 463,292 common pixels and no common-valid pixel outside the raster AOI mask, polygonizes both context layers, verifies 100 m² target pixels and the 46.3292 km² area, aligns the S2 RGB image to the S1 grid, writes the review PNG and a GeoPackage, and writes coverage JSON with null enclosure metrics.

Checks performed or pending:

| Check | Result |
|---|---|
| S1 validity/AOI mask count and containment | PASS (script assertions) |
| Pixel area and broad-window area arithmetic | PASS (script assertions) |
| S2-to-S1 CRS/grid warp for map | PASS (completed; output visually inspected) |
| GeoPackage integrity and layer creation | PASS (SQLite `integrity_check`; two feature layers written) |
| GeoJSON candidate validity | Not applicable; no candidate geometry created |
| Boundary status transition | Not performed; existing state remains `not_delineated` |
| GherProof API/regression tests | PASS: 19 passed; 2 expected `NotGeoreferencedWarning` warnings from a negative fixture |
| Enclosure intersection/buffers | Correctly not run; no geometry |

Run the review package rebuild from repository root:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5_review_package.py
```

The backend focused regression tests were run from `backend/`:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_gherproof.py tests/test_gherproof_boundary.py tests/test_gherproof_boundary_api.py tests/test_gherproof_planetary_computer.py tests/test_gherproof_event_imagery.py -q
```

Result: **19 passed**. The two Rasterio warnings are emitted by the intentional test that rejects a non-georeferenced product. A separate validation checked SQLite GeoPackage integrity, both feature tables, EPSG:32645 GeoPackageBinary headers, WKB geometry validity, and JSON parsing/null-boundary gates for all updated Phase 5 manifests; all passed.
