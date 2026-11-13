# GherProof Phase 7B — Exact Sentinel-1 GRD Counterpart Assessment

## Decision

**Exact same-acquisition GRD records were found for all four Phase 7 RTC scenes, and both VV and VH assets are catalogued. None of the GRD scenes was fully processed into analysis-ready output.** The available PC assets opened as metadata but expose no CRS or meaningful map transform and identify themselves in TIFF tags as Sentinel-1 IW GRD HR Level 1. The STAC descriptions say “radiometric terrain correction applied,” which conflicts with the actual raster metadata and the separate Level 1 calibration/noise metadata. Therefore this assessment treats the files as unprocessed Level 1 measurements until a verified provider processing chain proves otherwise.

No GRD values were used as model inputs, compared numerically with dB training chips, or interpreted spatially. Current Phase 7 inference remains RTC-based and exploratory.

## Exact matches

The anonymous Microsoft Planetary Computer STAC `sentinel-1-grd` collection was queried by exact scene identifier and strict metadata matching. The GRD IDs are the RTC source IDs with the `_rtc` suffix removed.

| RTC acquisition | Exact GRD item | Relative orbit / direction | Mode / pols | Match |
|---|---|---:|---|---|
| 2026-01-09 23:56:19Z | `S1A_IW_GRDH_1SDV_20260109T235606_20260109T235631_062697_07DC80` | 15 / descending | IW / VV,VH | Exact scene identifier and metadata |
| 2026-01-12 12:12:47Z | `S1A_IW_GRDH_1SDV_20260112T121234_20260112T121259_062734_07DDE0` | 12 / ascending | IW / VV,VH | Exact scene identifier and metadata |
| 2026-01-21 23:56:17Z | `S1A_IW_GRDH_1SDV_20260121T235605_20260121T235630_062872_07E2FF` | 15 / descending | IW / VV,VH | Exact scene identifier and metadata |
| 2026-01-24 12:12:45Z | `S1A_IW_GRDH_1SDV_20260124T121233_20260124T121258_062909_07E438` | 12 / ascending | IW / VV,VH | Exact scene identifier and metadata |

Product start/end times, platform S1A, orbit, direction, IW mode and dual polarization agree with the corresponding RTC records. No substitute dates were used.

## Asset inspection

All eight COG assets (four dates × VV/VH) returned HTTP range status 206 and could be opened by Rasterio for header metadata. The assets are large remote COGs (approximately 568–670 MB per polarization in the inspected scenes). Seven of eight 16×16 sample reads completed; the 2026-01-12 VH sample failed with a Rasterio read error. No full assets were downloaded.

Common observed raster metadata: one `uint16` band; nodata 0; scale 1 and offset 0; no CRS, no band description, identity pixel-index transform, no map coordinates or physical resolution. TIFF tags identify `Sentinel-1A IW GRD HR L1`, software `Sentinel-1 IPF 004.02`, and dates matching the acquisitions. The displayed 1-unit “resolution” is a pixel-index default and must not be interpreted as one metre.

The SAFE manifest describes product type GRD. VV and VH calibration XMLs were recovered and checksummed for all four scenes; each lists 27 calibration vectors and LUTs (including sigma-nought, beta-nought, gamma and DN). Noise XMLs were also recovered. They report zero noise-vector entries in the inspected metadata; this is not evidence that noise treatment is unnecessary. The metadata includes a calibration constant of 1.0. Apply the product-specific LUT and noise/border-noise handling with a validated processor before treating DN as calibrated backscatter.

The STAC `description` field says the measurement asset has terrain correction applied, but the returned files carry raw Level 1 TIFF tags, no georeferencing, and have separate calibration/noise LUT metadata. This internal inconsistency remains unresolved. The raster itself and SAFE metadata take precedence over the descriptive text for this decision; do not assume STAC text establishes RTC processing.

## Processing decision and requirements

The project environment has Rasterio but no SNAP GPT, `osgeo`/GDAL Python bindings or SNAP Python bridge. Consequently no orbit correction, thermal/border-noise treatment, LUT calibration, terrain correction, geocoding, or comparable GRD dB raster has been produced. Full-scene coverage and spatial alignment of these GRD assets are unknown. `processed_full_scenes` remains zero.

For a defensible benchmark-domain comparison, process the four products with a pinned SNAP/S1TBX workflow (or an independently validated equivalent): apply orbit file, border-noise removal, thermal-noise removal where appropriate, calibration to a declared quantity, terrain correction to a fixed CRS/grid, consistent masks, and linear-to-dB conversion only after calibration. Record SNAP/S1TBX versions, orbit auxiliary file, DEM, resampling method, pixel spacing, calibration target, processing graph, input checksums and output QC. Then compare with the Sen1Floods11 training representation; GRD product-type matching alone does not establish equivalence.

ESA references: [SNAP Calibration operator](https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.microwavetbx.sar.op.calibration.ui/operators/CalibrationOp.html) and [Sentinel-1 time-series processing tutorial](https://step.esa.int/docs/tutorials/S1TBX%20Time-series%20analysis%20with%20Sentinel-1.pdf). The Planetary Computer collection documentation describes its GRD and RTC offerings: [Sentinel-1 collection](https://planetarycomputer.microsoft.com/dataset/group/sentinel-1).

## Reproducibility

- Exact STAC matches and item metadata: `data/gherproof/manifests/phase7b_grd_counterpart_manifest.json`.
- COG header/sample results: `data/gherproof/manifests/phase7b_grd_raster_inspection.json`.
- Downloaded SAFE/calibration/noise metadata and checksums: `data/gherproof/manifests/phase7b_grd_metadata_summary.json`.
- Scripts: `scripts/gherproof/phase7b/assess_grd_counterparts.py`, `inspect_grd_assets.py`, `summarize_grd_metadata.py`.

**Conclusion:** GRD counterpart availability is established, but no GRD compatibility improvement has been demonstrated. RTC remains the only input used for current exploratory inference, with domain mismatch unresolved.
