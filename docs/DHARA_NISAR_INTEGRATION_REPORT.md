# DHARA NISAR Integration Report

**Status: integrated for separate regional radar evidence; no January incident NISAR evidence exists.**

## Summary

The official ASF DAAC search found no NISAR L2 GCOV footprint matches for the provisional Sujatpur/Manirampur/Jashore search extent in either January 2026 incident window (January 1–13 and January 15–31). The archive did return later observations. Two matching **VALIDATED** L-band GCOV products from ascending relative orbit 170, acquired October 23 and November 4, 2026, were selected. Both have dual-H polarization (HH/HV) on two native grids: Frequency A (40 MHz, 10 m) and Frequency B (5 MHz, 80 m). They share processing release P05036 and EPSG:32645.

The two scenes were read by authenticated HTTP byte range. The full source HDF5 products (about 6.6 GB each) were not downloaded; only metadata and regional chunks for the provisional search envelope were fetched. Both frequency grids were processed separately, with HH/HV views, raw quality layers and a non-classificatory signed temporal gamma0 ratio for each grid. **These later products do not observe or substantiate the reported January incident.** No NISAR values were passed to Sentinel-1-trained models.

## Archive search and scene selection

Search used the official ASF DAAC NISAR product archive and the existing six-village regional search extent at `data/gherproof/regional/six_village_regional_search_extent.geojson`. That polygon is an approximate study/search envelope, not a verified village, site or fisheries-enclosure boundary.

| Search period | Collection/maturity | AOI GCOV matches | Result |
|---|---|---:|---|
| Jan 1–13, 2026 | BETA | 0 | No matching pre-event GCOV product |
| Jan 15–31, 2026 | BETA | 0 | No matching post-event GCOV product |
| Jun 17–part of Oct 23, 2026 | PROVISIONAL | 40 | Later matching catalogue footprints; not selected for this integration |
| Oct 21–Nov 13, 2026 | VALIDATED | 6 | Two same-geometry, same-polarization orbit-170 acquisitions selected |

The January search result means **no catalogued GCOV footprint matching this AOI and date window was found**; it does not mean NISAR collected no observations elsewhere. The archive release guide says January/February BETA data were pre-calibration samples, PROVISIONAL products begin with acquisitions from June 17, and the first VALIDATED L0–2 collection was released November 6 for acquisitions from October 21. Product maturity is therefore not inferred from acquisition date alone: the selected product IDs resolve to the `NISAR_L2_GCOV_V1` VALIDATED collection, release P05036. See the [ASF availability guide](https://nisar-docs.asf.alaska.edu/availability-overview/) and [product maturity overview](https://nisar-docs.asf.alaska.edu/products-overview/).

| Acquisition (UTC) | Product ID | Maturity / CRID | Cycle / relative orbit / pass | Polarizations and terms | Product size |
|---|---|---|---|---|---:|
| 2026-10-23 23:29:18 | `NISAR_L2_PR_GCOV_033_170_A_013_4005_DHDH_A_20261023T232918_20261023T232952_P05036_N_F_J_001` | VALIDATED / P05036 | 033 / 170 / ascending | Frequency A: 40 MHz, 10 m; Frequency B: 5 MHz, 80 m; both HH/HV | 6,593,445,888 bytes |
| 2026-11-04 23:29:18 | `NISAR_L2_PR_GCOV_034_170_A_013_4005_DHDH_A_20261104T232918_20261104T232952_P05036_N_F_J_001` | VALIDATED / P05036 | 034 / 170 / ascending | Frequency A: 40 MHz, 10 m; Frequency B: 5 MHz, 80 m; both HH/HV | 6,568,280,064 bytes |

The two acquisitions are 12 days apart and share orbit direction, relative orbit, maturity and polarization. The corresponding A grids align with each other, as do the corresponding B grids; A and B remain separate native resolutions. Their similar acquisition times and matching product geometry make them a defensible **within-NISAR regional comparison**, but not an event-period comparison. The original products were accessed through ASF DAAC using locally configured Earthdata credentials; no credentials were printed or embedded in code.

## HDF5 inspection and processing

Actual data were inspected and read from both `/science/LSAR/GCOV/grids/frequencyA` and `frequencyB`. Product mode `4005` identifies 40 MHz primary and 5 MHz secondary bands; `DHDH` identifies HH/HV dual polarization for both, as defined in the [ASF GCOV naming convention](https://nisar-docs.asf.alaska.edu/gcov/). Both HDF5 arrays are float32, gzip-compressed in 512×512 chunks, with separate coordinate and quality datasets. Frequency A is 33,912×34,632 at 10 m. Frequency B is 4,239×4,329 at 80 m. Both are EPSG:32645. The two grids were retained at native resolution and were not resampled or compared to each other.

| Grid | Bandwidth | Regional output dimensions | Approximate AOI pixels | Valid pixels per channel/date | Valid fraction |
|---|---:|---:|---:|---:|---:|
| Frequency A | 40 MHz | 3,111×2,155 at 10 m | 6,475,371 | 6,475,371 | 100% |
| Frequency B | 5 MHz | 388×270 at 80 m | 101,170 | 101,170 | 100% |

The Frequency A pixel count corresponds to approximately 647.54 km² at nominal pixel area. Frequency B has its own AOI rasterization and pixel count; its cells are not interchangeable with Frequency A.

| Layer | HDF5 term | Interpretation and units |
|---|---|---|
| HH | `HHHH` | Real diagonal covariance power for HH; dimensionless linear gamma0 power (units `1`) |
| HV | `HVHV` | Real diagonal covariance power for HV; dimensionless linear gamma0 power (units `1`) |
| Focused-data mask | `mask` | GCOV subswath mask; zero is invalid/partially focused, 255 is outside scene |
| Input exception / validity | `inputDataExceptionMask` | Raw bits retained; per-channel focused-valid bits HH=256 and HV=512; exception bit 2 describes qFSP-H1 sample slip |
| Number of looks | `numberOfLooks` | Retained in source metadata; mean within AOI approximately 4.394 for A and 35.155 for B |
| RTC factor | `rtcGammaToSigmaFactor` | Preserved as source metadata; not applied, so outputs remain gamma0 |

For each frequency/channel, the exported valid mask requires an AOI pixel to have a GCOV `mask` in 1–254 and the matching focused-valid bit in `inputDataExceptionMask`; invalid raster values are nodata, not zero backscatter. Raw masks and exception values are preserved in separate quality GeoTIFFs. All four frequency/date groups had 100% valid AOI pixels under this explicit mask rule. The qFSP-H1 exception bit was present in 0 focused-valid AOI pixels in all groups. These coverage statements describe only the provisional envelope.

No gamma0-to-sigma0 adjustment was made, and no Sentinel-1 calibration workflow was applied. NISAR GCOV is documented as calibrated, radiometrically and terrain corrected gamma0 power. The [ASF GCOV guide](https://nisar-docs.asf.alaska.edu/gcov/) describes the real-valued diagonal terms as per-polarization backscatter intensity, explains the masks and RTC factor, and documents the bandwidth-dependent spacing. These are radar measurements, **not water probability**.

## Regional measurements and temporal comparison

| Date | Channel | Valid AOI pixels | Min | P05 | Median | P95 | Max | Units |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Oct 23 | HHHH | 6,475,371 | 0.000849 | 0.011038 | 0.131243 | 0.703964 | 775.156250 | Linear gamma0 power (1) |
| Oct 23 | HVHV | 6,475,371 | 0.000308 | 0.003006 | 0.022279 | 0.125998 | 13.804321 | Linear gamma0 power (1) |
| Nov 4 | HHHH | 6,475,371 | 0.001051 | 0.010303 | 0.127135 | 0.685181 | 978.054688 | Linear gamma0 power (1) |
| Nov 4 | HVHV | 6,475,371 | 0.000283 | 0.002966 | 0.021939 | 0.125982 | 19.657959 | Linear gamma0 power (1) |

| Date | Frequency B channel | Valid AOI pixels | Min | P05 | Median | P95 | Max | Units |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Oct 23 | HHHH | 101,170 | 0.009827 | 0.030678 | 0.239766 | 0.621323 | 22.957764 | Linear gamma0 power (1) |
| Oct 23 | HVHV | 101,170 | 0.002823 | 0.006424 | 0.032498 | 0.094136 | 1.044632 | Linear gamma0 power (1) |
| Nov 4 | HHHH | 101,170 | 0.008199 | 0.029004 | 0.226210 | 0.604008 | 33.219727 | Linear gamma0 power (1) |
| Nov 4 | HVHV | 101,170 | 0.002493 | 0.006052 | 0.030744 | 0.091315 | 1.067596 | Linear gamma0 power (1) |

The two change rasters are calculated per channel/grid as `10 × log10(Nov 4 linear gamma0 / Oct 23 linear gamma0)` over the corresponding common validity masks. These are signed, like-for-like ratios in dB; they are **not** water, flood, drainage, fishery-damage or probability maps.

| Channel | Common valid AOI pixels | P05 change | Median change | P95 change | Units |
|---|---:|---:|---:|---:|---|
| Frequency A · HHHH | 6,475,371 (100%) | −4.654 dB | −0.154 dB | +4.449 dB | dB ratio |
| Frequency A · HVHV | 6,475,371 (100%) | −4.657 dB | −0.051 dB | +4.607 dB | dB ratio |
| Frequency B · HHHH | 101,170 (100%) | −2.079 dB | −0.123 dB | +1.847 dB | dB ratio |
| Frequency B · HVHV | 101,170 (100%) | −2.138 dB | −0.189 dB | +1.755 dB | dB ratio |

The robust middle of the change distribution is small compared with its broad spatial spread. That may reflect real surface change, but the two scenes alone cannot distinguish moisture, crop/vegetation, roughness, irrigation/aquaculture, rainfall, tidal influence, speckle or other acquisition/environmental effects. No field labels or land-use grouping were used to attribute those changes.

## DHARA application integration

Six records were added to the active evidence registry:

1. Four validated NISAR observation layers: October 23 and November 4, each with Frequency A (10 m) and Frequency B (80 m), and HHHH/HVHV bands.
2. Two derived Oct 23 → Nov 4 signed gamma0 change layers (one per frequency grid), kept distinct from the acquired observations.

The existing DHARA **Satellite View** map selector now includes all four observation layers and both temporal-change layers. Selecting a NISAR layer exposes the HHHH/HVHV channel selector and shows the date, VALIDATED maturity, ascending relative orbit 170, native gamma0 units and grid resolution. A short explanation states that NISAR L-band and Sentinel-1 C-band have different wavelengths and provide complementary observations. Signed-change previews use a blue/neutral/red display stretch; the legend explicitly says that the layer is not a water probability. The application does not route any NISAR raster into either Sentinel-1-trained model.

The evidence listing and metadata service were exercised directly: four observation IDs and two comparison IDs appeared, and raster metadata resolved for each. Direct calls to the existing preview handler generated image/png responses with status 200 for HHHH, HVHV and both frequency-grid comparisons. A full live-server/TestClient request did not finish within the bounded smoke check, so transport-level HTTP verification remains unconfirmed. The UI production build passed.

## Data files and reproducibility

Regional rasters and masks are under `data/gherproof/processed/nisar/validated/` (about 117.5 MB total). Source query and processing details are in `data/gherproof/manifests/nisar_integration_manifest.json`; per-acquisition manifests are beside the rasters. The evidence registry is `data/gherproof/manifests/evidence_registry.json`, and independent Rasterio checksums/metadata/statistics for 16 output rasters are in `data/gherproof/manifests/nisar_raster_qc_manifest.json`. Alignment was checked within each frequency grid; the 10 m and 80 m products are not aligned to one another by design.

From the repository root, with local NASA Earthdata credentials available to Requests (for example `.netrc`):

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/inspect_nisar_remote_gcov.py --date 2026-10-23 --extract-dir data/gherproof/processed/nisar/validated --aoi data/gherproof/regional/six_village_regional_search_extent.geojson
backend/.venv/Scripts/python.exe scripts/gherproof/inspect_nisar_remote_gcov.py --date 2026-10-23 --frequency B --extract-dir data/gherproof/processed/nisar/validated --aoi data/gherproof/regional/six_village_regional_search_extent.geojson
backend/.venv/Scripts/python.exe scripts/gherproof/inspect_nisar_remote_gcov.py --date 2026-11-04 --extract-dir data/gherproof/processed/nisar/validated --aoi data/gherproof/regional/six_village_regional_search_extent.geojson
backend/.venv/Scripts/python.exe scripts/gherproof/inspect_nisar_remote_gcov.py --date 2026-11-04 --frequency B --extract-dir data/gherproof/processed/nisar/validated --aoi data/gherproof/regional/six_village_regional_search_extent.geojson
backend/.venv/Scripts/python.exe scripts/gherproof/build_nisar_temporal_comparison.py
backend/.venv/Scripts/python.exe scripts/gherproof/register_nisar_evidence.py
backend/.venv/Scripts/python.exe scripts/gherproof/validate_nisar_outputs.py
backend/.venv/Scripts/python.exe scripts/gherproof/smoke_nisar_map_preview.py
cd app; npm run build
```

Each source HDF5 is about 6.6 GB. Across frequency grids, AOI extraction read about 115.3 MB from October 23 and 114.3 MB from November 4 using HTTP Range requests. **The complete ASF source-product checksums were not independently recomputed because the full HDF5 files were not downloaded.** SHA-256 values for every local TIFF are recorded in the QC manifest and registry; source product identifiers and URLs are retained for provenance.

## Limitations and conclusion

- There is no NISAR pre/post pair for the January 14, 2026 reported fisheries incident; the two data windows returned zero AOI-matching BETA GCOV products.
- The October/November observations are later than the incident and cannot confirm or refute it.
- The provisional regional study extent is not an authoritative Pallimangal, Sujatpur or enclosure boundary.
- Gamma0 values and their temporal differences are not a water classification and do not establish inundation, drainage failure, fish escape, fish mortality or economic loss.
- NISAR and Sentinel-1 are separate sensor evidence streams; model transfer or combined inference was not performed.
- No field-reference labels were introduced. A water-likelihood model is not validated or supplied by this integration.
- Earlier provisional products were not mixed with the selected VALIDATED pair; this avoids maturity-baseline confounding.

**Decision:** NISAR is integrated as a genuine, validated, separate regional radar evidence stream and is visible through the DHARA map layer selector. It improves multi-frequency mission representation and provides a same-track 12-day L-band comparison. It contributes no direct January-event evidence, no water label, and no confirmed fisheries impact.

## Authoritative references

- [ASF NISAR data availability and maturity timeline](https://nisar-docs.asf.alaska.edu/availability-overview/)
- [ASF NISAR product maturity overview](https://nisar-docs.asf.alaska.edu/products-overview/)
- [ASF NISAR GCOV product, masks, units and resolution](https://nisar-docs.asf.alaska.edu/gcov/)
- [ASF Search API documentation](https://docs.asf.alaska.edu/api/basics/)
- [ASF Search API keywords and endpoints](https://docs.asf.alaska.edu/api/keywords/)
- [NASA Earthdata data use policy](https://www.earthdata.nasa.gov/engage/open-data-services-software/data-use-policy)
