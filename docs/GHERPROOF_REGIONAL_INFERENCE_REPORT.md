# GherProof Phase 7 — Controlled Regional Inference

## Status and scope

**Status: COMPLETE for exploratory inference; NOT APPROVED for validated event or village-impact conclusions.** Inference ran only after the dB conversion, normalization, validity-mask and model-load gates passed. The footprint is the provisional 647.537 km² Phase 6B regional AOI, not verified village boundaries.

Two exact same-geometry Sentinel‑1A RTC pairs were used and kept separate:

| Pair | Exact scene identifiers | Geometry | Relative offsets from Jan 14 event date | Common valid pixels |
|---|---|---|---|---:|
| Jan 12→24 | `S1A_IW_GRDH_1SDV_20260112T121234_20260112T121259_062734_07DDE0_rtc` → `S1A_IW_GRDH_1SDV_20260124T121233_20260124T121258_062909_07E438_rtc` | Ascending, rel 12, IW, VV/VH | -2 / +10 d | 6,475,371 |
| Jan 9→21 | `S1A_IW_GRDH_1SDV_20260109T235606_20260109T235631_062697_07DC80_rtc` → `S1A_IW_GRDH_1SDV_20260121T235605_20260121T235630_062872_07E2FF_rtc` | Descending, rel 150, IW, VV/VH | -5 / +7 d | 6,475,371 |

## Model outputs

The scratch Attention U-Net (`fcb244de…f5a040`) and pretrained-initialized/fine-tuned ResNet50-SAR U-Net (`084b41f0…8d9f0`) were run as distinct models. Each emitted one probability raster, fixed-0.5 mask and entropy proxy per acquisition. Pair-level post-minus-pre probability, new-water-like candidate and separate model disagreement products were generated. Threshold sensitivity at 0.4/0.5/0.6 is reported; 0.5 remains the benchmark-fixed primary threshold. These are model classes and candidate changes, not validated water masks.

| Pair/model | Pre model-class area (km²) | Post model-class area (km²) | Post class not in pre (km²) |
|---|---:|---:|---:|
| Jan 12→24 scratch | 128.12 | 151.95 | 45.18 |
| Jan 12→24 pretrained | 56.45 | 57.64 | 14.66 |
| Jan 9→21 scratch | 70.27 | 95.49 | 41.37 |
| Jan 9→21 pretrained | 8.87 | 11.47 | 5.43 |

Areas are pixel counts × 100 m² inside the common valid source mask. They are exploratory model-predicted class area on a provisional regional extent; not flood extent, affected cropland, village totals, or confirmed new water. The substantial differences between architectures demonstrate model uncertainty: binary pre-event disagreement was 13.41% (ascending pair) and 9.75% (descending pair); post-event disagreement was 16.34% and 13.44%, respectively. No model averaging was done.

The outputs do not remove permanent water or aquaculture ponds because no suitable authoritative reference mask was available. The detected post/pre class transitions cannot be attributed to the incident or an embankment breach. Crop state, irrigation, aquaculture, moisture, rainfall, tide, speckle and RTC/training domain differences remain plausible alternatives.

## Quality and reproducibility

All 80 Phase 7 GeoTIFFs reopened with Rasterio. QC recorded CRS, transforms, bounds, resolution, sizes, dtype, band description, nodata, checksums and valid-value statistics. No NaN or infinity pixels were found; per-acquisition probability rasters remained in [0,1]. 256×256 tiles with 64-pixel overlap covered the full 3,111×2,156 rectangular raster. Input validity was retained (6,475,371 AOI valid pixels per scene); invalid normalized pixels were zero and excluded from output masks/counts. Repeat-forward smoke difference was 0.0 for all scene/model runs.

Primary machine-readable record: `data/gherproof/manifests/phase7_inference_manifest.json`. Full output paths and hashes are in that manifest; independent raster QC is in `data/gherproof/manifests/phase7_raster_qc_manifest.json`.

```powershell
python scripts/gherproof/phase7/audit_radiometric_compatibility.py
python scripts/gherproof/phase7/run_experimental_inference.py
python scripts/gherproof/phase7/validate_outputs.py
```

The first step requires local PyTorch, Rasterio available via the backend virtual environment, the Sen1Floods11 training data and the existing pinned checkpoints. No model was trained or changed in Phase 7.
