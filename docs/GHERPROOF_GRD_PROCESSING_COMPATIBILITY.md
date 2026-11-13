# GherProof Phase 7C — Sentinel-1 GRD Processing Compatibility

## Finding

**The four exact GRD counterparts are discoverable, but they have not been converted into analysis-ready rasters. GRD has not demonstrated a compatibility improvement over the Phase 7 RTC Gamma0 inputs. Keep current predictions exploratory.**

The assets were identified in Microsoft Planetary Computer `sentinel-1-grd` by exact scene ID, matching the four RTC dates, Sentinel-1A platform, IW mode, dual VV/VH polarization, relative orbit and direction. This confirms catalogue identity, not equivalent radiometry or geocoding.

| Acquisition | Relative orbit / direction | STAC measurement assets | Pixel data read | Result |
|---|---|---|---|---|
| 2026-01-09 | 15 / descending | VV + VH | Both 16×16 windows readable | Header is uint16, no CRS/meaningful transform, Level 1 GRD tags |
| 2026-01-12 | 12 / ascending | VV + VH | VV readable; VH failed sample decode | Same metadata; VH sample read error recorded |
| 2026-01-21 | 15 / descending | VV + VH | Both 16×16 windows readable | Same metadata |
| 2026-01-24 | 12 / ascending | VV + VH | Both 16×16 windows readable | Same metadata |

All eight remote COGs returned HTTP 206 for 16 KiB header ranges and opened for Rasterio metadata inspection. Seven small center windows were read successfully; one VH window failed. No complete asset was downloaded. The inspection values are native unsigned integer amplitude-like DN counts (sample ranges vary by polarization/date; e.g. Jan 9 VV sample p50=177 and VH p50=74). The TIFF headers list `uint16`, scale 1, offset 0, nodata 0, no units, no CRS, and an identity index-space affine. Thus their displayed resolution of `1` is not a physical metre resolution. No raster footprint or AOI-clipped geographic window can be computed from these TIFF headers.

## Product representation and conflicting metadata

The returned STAC asset descriptions call the VV/VH assets amplitudes with radiometric terrain correction applied. In contrast, the TIFF tags say `Sentinel-1A IW GRD HR L1` and identify IPF 004.02; the companion SAFE manifest says GRD; separate per-polarization calibration LUT and noise XML files are present. This combination does **not** substantiate an analysis-ready terrain-corrected product. The conflict could reflect catalog metadata reuse or an unconventional serialization; it was not resolved by the remote headers. Do not infer terrain correction from the STAC prose alone.

The recovered metadata files provide 27 calibration vectors per polarization per scene and lists sigma-nought, beta-nought, gamma and DN lookup tables with an absolute calibration constant of 1.0. Noise XML files are present, though the extracted noise vector count is zero in these documents. A zero vector count does not by itself prove that thermal-noise or border-noise treatment is unnecessary. Raw integer values must not be interpreted as calibrated backscatter, gamma-0, sigma-0, dB or water probability.

## Comparison with Sen1Floods11 benchmark inputs

The local Sen1Floods11 v1.1 `S1Hand` chips are 2-band, georeferenced 512×512 values in dB (VV,VH) with hand masks. The project training loader applies the declared [-60,20] dB clip, event-grouped split and checkpoint-specific normalization. The four RTC products are linear Gamma0 converted once to dB for inference, then clipped and normalized with checkpoint-specific constants. That conversion does not remove the product-domain distinction.

No exact GRD sample was calibrated into sigma0/gamma0 and dB, geocoded, terrain corrected, or resampled onto the benchmark grid. Consequently there is no valid numerical GRD-vs-training distribution result, no same-location or AOI-clipped comparison, and no evidence that replacing RTC with GRD improves domain compatibility.

## What is required to settle compatibility

Use a pinned ESA SNAP/S1TBX or independently validated processor on the exact source data. At minimum, record and apply the appropriate orbit auxiliary file, border-noise handling, thermal-noise handling, radiometric calibration target, DEM, terrain correction, geocoding CRS, resampling, pixel spacing, no-data/layover masks, and linear-to-dB transformation. Save the processing graph/version and input/output hashes. Clip the outputs to the same project AOI only after geocoding. Then compare exact spatial pixels and distributions with the selected Sen1Floods11 benchmark inputs, while accounting for acquisition/incidence-angle and land-cover differences.

The current environment has no QGIS, SNAP GPT/command, `osgeo` Python bindings or SNAP bridge. This phase therefore stops at non-destructive remote header/sample inspection. The original RTC products and all checkpoints remain untouched.

Reproducible sources:

- `data/gherproof/manifests/phase7b_grd_counterpart_manifest.json`
- `data/gherproof/manifests/phase7b_grd_raster_inspection.json`
- `data/gherproof/manifests/phase7b_grd_metadata_summary.json`
- Scripts in `scripts/gherproof/phase7b/assess_grd_counterparts.py`, `inspect_grd_assets.py`, `summarize_grd_metadata.py`
- ESA [SNAP Calibration operator](https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.microwavetbx.sar.op.calibration.ui/operators/CalibrationOp.html) and [Sentinel-1 time-series tutorial](https://step.esa.int/docs/tutorials/S1TBX%20Time-series%20analysis%20with%20Sentinel-1.pdf)

**Conclusion:** exact GRD assets exist, but no defensible processed alternative input domain was established. Do not switch the models from RTC to these GRD assets in their current form.
