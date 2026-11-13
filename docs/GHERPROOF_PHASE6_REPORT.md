# GherProof Phase 6 — Six-Village Regional Satellite Flood Evidence

**Status: regional evidence acquisition is in progress; event inference is not ready.** This phase produced a provisional regional search AOI, actual local-clip coverage accounting, and expanded Microsoft Planetary Computer STAC manifests. It did not produce a regional flood/water map, a village-level inundation estimate, or an enclosure boundary.

## Executive decision

**NO-GO for experimental regional water-change inference or an inundation-area estimate using the evidence currently validated in the regional AOI.** The local Jan 7/19 Sentinel-1 clips provide only 7.1547% common valid support across the approximately 650 km² provisional search envelope, with no existing local clip coverage in the eastern reporting sector. Alternative same-orbit candidates are present in the catalogue but their pixels have not yet been validated. Only a pre-event visual Sentinel-2 clip exists locally; no post-event optical pixels or cloud/shadow masks were checked.

**CONDITIONAL GO for continuing retrieval, geospatial refinement and data preparation.** A water-change screening workflow can be reconsidered after expanded RTC acquisitions pass pixel-level coverage/QC and official or locally surveyed village reference geometries are obtained. Any future model output must be described as experimental and independently field-checked; existing benchmark scores are not local validation.

## Results at a glance

| Question | Phase 6 finding |
|---|---|
| Could all six villages be geographically constrained? | No. Official village/mouza polygons and reliable coordinates are absent. Names and some union/upazila associations are supported; the regional AOI is a search envelope only. Moshiahati jurisdiction/spelling is inconsistent across sources. |
| Were suitable pre/post Sentinel-1 scenes found? | Yes in the RTC catalogue, with same-platform/orbit/direction/IW/VV-VH candidates. Full regional pixel suitability is **not** validated for newly found scenes. |
| Were alternative relative orbits needed? | Candidate groups exist at relative orbits 12 ascending and 150 descending in addition to orbit 114 ascending. They remain separate geometry groups and are not yet proven necessary or sufficient by pixel coverage. |
| What is common valid coverage? | Existing Jan 7/19 local clips: 463,292 common 10 m pixels, 46.3292 km², or 7.1547% of the provisional regional raster mask. No existing clip pixels were found in the eastern reporting sector. |
| Does Sentinel-2 independently corroborate? | Not yet. Catalog has low-cloud pre/post candidates, but actual post-event imagery and SCL/cloud-shadow masks were not checked. The local Jan 13 RGB crop covers 16.34% of the regional mask and has no local pixel-level cloud QA. |
| Is experimental regional inference justified now? | No, given current valid support and unresolved regional geometry. |
| Is any defensible regional inundation area available? | No. No event classifier inference or cropland overlay was produced. |
| Is Pallimangal exactly identified? | No. Existing Phase 5 boundary status remains `not_delineated`; the broad regional incident does not locate a parcel or breach. |

## Geographic scope and source assessment

The delivered GeoJSON/GeoPackage covers `[89.24, 22.92, 89.54, 23.11]` in WGS84. The envelope is roughly 650.13 km² by a latitude-adjusted degree approximation. The 10 m projected grid is EPSG:32645, 3,111 × 2,156 cells, with 6,475,371 cells in the rasterized AOI. This is search area only and must never be reported as flooded area.

The [Dhaka Post incident report](https://www.dhakapost.com/country/424238) lists Sujatpur, Hatgachha, Kultia, Moshiahati, Bedbhita and Bolarabad as affected village names. The official [DPHE village geo-code table](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqpryl/g/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf) associates Sujatpur, Hatgachha and Kultia with Kultia Union, Manirampur, but provides codes rather than spatial boundaries. Published regional work associates Bolarabad with Chalisia Union, Abhaynagar. Local reports describe Bedbhita in Abhaynagar. Moshiahati is assigned to Abhaynagar in the incident report but alternate administrative/address records associate similarly spelled Mashiahati with Manirampur. We retain the discrepancy rather than resolve it by assumption.

No authoritative six-village polygon layer was found in the repository or in the examined public sources. The rectangle is a provisional analyst-defined search extent guided by reported administrative contexts and publicly mapped locality references; it is not a digitized boundary and has no quantified positional accuracy. The per-village coverage question therefore cannot be answered from this phase’s geometries. See [regional AOI provenance](GHERPROOF_REGIONAL_AOI_PROVENANCE.md).

## Sentinel-1 acquisition review

Planetary Computer STAC discovery for the requested pre/post date windows returned seven Sentinel-1 RTC acquisitions. Every candidate is Sentinel-1A, IW, VV/VH. Scene catalog coverage by footprint suggests the listed scenes intersect the provisional envelope; those ratios use lon/lat polygon area and must not be interpreted as raster coverage.

| Date | Relative orbit | Direction | Approx. footprint overlap | Role/status |
|---|---:|---|---:|---|
| Jan 07 | 114 | Ascending | 90.3% | Existing local pre-event clip; preferred existing geometry |
| Jan 09 | 150 | Descending | 100% | Alternate pre-event candidate, catalog only |
| Jan 12 | 12 | Ascending | 100% | Alternate pre-event candidate, catalog only |
| Jan 19 | 114 | Ascending | 90.1% | Existing local post-event clip; same geometry as Jan 07 |
| Jan 21 | 150 | Descending | 100% | Alternate post-event candidate, catalog only |
| Jan 24 | 12 | Ascending | 100% | Alternate post-event candidate, catalog only |
| Jan 31 | 114 | Ascending | 90.6% | Later post-event orbit-114 candidate, catalog only |

The preferred pair for first expanded pixel validation remains **Jan 7/19, relative orbit 114 ascending**, because both local clips already exist and the acquisition timing brackets the reported Jan 14 incident. The alternate matched pairs are Jan 9/21 (orbit 150 descending) and Jan 12/24 (orbit 12 ascending). Keep each as a separate time series; do not merge descending and ascending observations or different relative orbits into one unadjusted comparison. Jan 7/31 is another orbit-114 option but later than Jan 19.

The existing Jan 7/19 local rasters are two-band float32 GeoTIFFs, EPSG:32645, 10 m, nodata -32768, with VV and VH band descriptions. The prior Phase 4B processing and QC identify Sentinel-1 RTC gamma0 linear backscatter. The existing local clips are co-registered with matching bounds and valid masks in the saved files. The Phase 6 coverage script separately remapped them to the larger AOI grid and counted common VV/VH-valid pixels across both dates.

The existing clips contain 463,292 pixels valid in both polarizations and both dates. The source local grid intersects 1,060,319 pixels in the new regional envelope; only 43.69% of those intersection pixels are common valid across all assets. On the full regional grid, common valid support is 7.1547%. The west/east split at 89.39 E is only a reporting aid: the western provisional sector has 46.3292 km² valid common support (14.31%); the eastern provisional sector has zero valid pixels because existing clips do not extend there. Zero coverage is unknown, not dry.

**New regional RTC scenes were not pixel-validated or retrieved into local files.** The optional remote COG window validation was attempted but did not complete in the available session and was stopped without recording successful pixels or an error-coded data result. Thus all alternative relative-orbit scenes remain catalogue candidates, not processed observations.

## Sentinel-2 review

Fourteen Sentinel-2 L2A catalog items were returned on tile 45QYF: seven pre-event, seven post-event. The lowest post-event STAC cloud-cover value is 0.000068% on Jan 28; the closest low-cloud post scene is Jan 18 at 0.000315%. These are catalogue fields only. Full pixel-level cloud/shadow QA is not present in the data inspected here.

The existing Jan 13 Sentinel-2 product is a 3-band RGB visual crop in EPSG:32645 at 10 m. Its 1,057,992 valid pixels cover 16.34% of the proposed regional mask. No SCL band accompanies this crop, and no post-event L2A raster was recovered/processed in this phase. A low scene cloud statistic cannot replace pixel-level cloud, cirrus and shadow screening. Sentinel-2 corroboration therefore remains **unestablished**.

## Model and quantification safeguards

No model was run or trained in Phase 6. The existing attention U-Net benchmark evaluations reported in the GherProof training documentation remain benchmark results only; they do not establish local accuracy over the six-village region. Existing event model inference would be particularly misleading where the eastern region has no validated S1 pixels.

The [Dhaka Post report](https://www.dhakapost.com/country/424238) reports about 1,500 bighas; [Samakal reports 158 hectares](https://samakal.com/whole-country/article/334020/%E0%A6%AA%E0%A6%BE%E0%A7%9C-%E0%A6%AD%E0%A7%99%E0%A6%99%E0%A7%87-%E0%A6%A2%E0%A7%81%E0%A6%95%E0%A6%B2-%E0%A6%AA%E0%A6%BE%E0%A6%A8%E0%A6%BF-%E0%A7%A7%E0%A7%AB%E0%A7%AE-%E0%A6%B9%E0%A7%87%E0%A6%95%E0%A7%8D%E0%A6%9F%E0%A6%B0-%E0%A6%9C%E0%A6%AE%E0%A6%BF%E0%A6%B0-%E0%A6%95%E0%A7%8D%E0%A6%B7%E0%A6%A4%E0%A6%BF). The two figures are retained as separate reports with different units and not reconciled or converted. Neither was used as a label, ground truth, threshold, inference constraint or calibration value. No affected-cropland area, escaped-fish quantity, damage estimate, exact breach position or source attribution is provided.

Radar differences in this low-lying setting could reflect standing water, antecedent soil moisture, rice/crop phenology, irrigation, aquaculture water management, rainfall, drainage timing, or processing differences. Without field observations and broader valid coverage, a water-change claim is premature. Even a later regional water mask cannot prove that every wet pixel came from Pallimangal or pinpoint its breach.

## Deliverables and reproduction

| Deliverable | Path |
|---|---|
| This report | `docs/GHERPROOF_PHASE6_REPORT.md` |
| AOI/source provenance | `docs/GHERPROOF_REGIONAL_AOI_PROVENANCE.md` |
| Imagery validation | `docs/GHERPROOF_REGIONAL_IMAGERY_VALIDATION.md` |
| Regional AOI | `data/gherproof/regional/six_village_regional_search_extent.geojson` and `.gpkg` |
| S1/S2 discovery manifests | `data/gherproof/manifests/phase6_sentinel1_regional_manifest.json`; `phase6_sentinel2_regional_manifest.json` |
| Valid coverage statistics | `data/gherproof/manifests/phase6_regional_valid_coverage.json` |
| Coverage data raster/overview | `data/gherproof/regional/processed/sentinel1/existing_jan07_jan19_common_valid_coverage_10m_utm45n.tif`; `data/gherproof/regional/phase6_existing_s1_coverage.png` |
| Scripts | `scripts/gherproof/phase6/regional_discovery.py`; `scripts/gherproof/phase6/validate_existing_coverage.py` |

Run from repository root:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase6/regional_discovery.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase6/validate_existing_coverage.py
```

The discovery script queries Planetary Computer STAC and records catalog metadata without retaining SAS tokens. It does not claim that catalog matches are processed products. The coverage script operates only on the existing local clips, writes a 10 m common-valid raster, and saves a checksum and actual counts. No full-scene downloads, model runs, frontend changes or checkpoint modifications were made.

## Verification performed

- Python syntax compilation passed for both Phase 6 scripts.
- Catalogue discovery completed successfully: 7 S1 RTC candidates, 4 compatible same-geometry catalog pairings, and 14 S2 L2A items.
- Existing local S1 coverage validation completed successfully: 463,292 common-valid pixels; 7.1547% regional support; 0% existing coverage in the eastern provisional sector.
- Existing local S2 clip check completed: 1,057,992 non-nodata pixels in the proposed regional envelope; RGB only, no SCL QA.
- The coverage raster and overview were generated. No inference output was generated because readiness gates failed.

## Next evidence needed

1. Replace or refine the provisional extent using authoritative BBS/DLRS village/mouza polygons or community/field-surveyed polygons, with source dates and CRS.
2. Open the Jan 7/19 source RTC COGs over the entire approved AOI and validate VV, VH, masks and exact four-layer common coverage; preserve original local files.
3. Test the Jan 9/21 and Jan 12/24 candidate pairs at pixel level, separately by geometry, and select based on actual shared valid area and observation timing.
4. Retrieve Jan 18 post-event Sentinel-2 L2A (plus SCL) and evaluate clouds, cirrus, shadows, valid coverage and co-registration; Jan 13 pre-event data needs comparable pixel-QA or a replacement pre scene.
5. Collect contemporaneous field observations and reference labels, including known water, cropland, aquaculture ponds and dry controls, before any local performance claim.
6. Obtain a verified Pallimangal gher boundary and independent breach/incident documentation before enclosure-level analysis.
