# GherProof Phase 7 — Controlled Regional Inference and Optical Comparison

**Overall status: COMPLETE for the requested exploratory workflow; quantitative/event conclusions NOT APPROVED.** This phase did not train a model, modify frontend code, change checkpoints or claim a confirmed flood, village impact, cause or breach. It used the Phase 6B provisional regional AOI only.

## Work completed

- Reconstructed and documented training-to-inference preprocessing in [model input provenance](GHERPROOF_MODEL_INPUT_PROVENANCE.md).
- Confirmed the four selected RTC arrays are linear Gamma0; converted positive values once to dB, retained source inputs unchanged, compared actual distributions with the project Sen1Floods11 training subset and recorded the domain gap in [radiometric compatibility](GHERPROOF_RADIOMETRIC_COMPATIBILITY.md).
- Added test-covered conversion, channel-order, mask, normalization and tiling helpers. The new NumPy test module passed **14/14** tests.
- Loaded both existing checkpoints with pinned hashes and ran each separately over the four acquisition scenes using 256×256 overlapping tiles. Eight probability/mask/entropy outputs, four model-specific pre/post comparisons, and separate disagreement layers were produced. Smoke checks passed: tensor channels/order, valid-pixel finiteness, invalid-channel zeroing, complete tile coverage, stable output shape, finite [0,1] scores and exact repeated-tile agreement.
- Retrieved and used exact SAFE product/granule metadata for the Sentinel‑2 pair. Converted stored values using offset/quantification metadata, preserved native reflectance grids, generated NDWI and 20 m MNDWI plus sensitivity statistics.
- Compared Sentinel‑1 candidate outputs to optical index candidates without fusing them. The SAR/optical output is explicitly a spatial agreement/disagreement coding layer, not a ground-truth evaluation.
- Reopened and independently checked **80 Phase 7 GeoTIFFs** with Rasterio. All reopened; no NaN/Inf values; scene probability rasters stayed within [0,1]. Full checksums/statistics are in `data/gherproof/manifests/phase7_raster_qc_manifest.json`.

## Selected data

| Stream | Acquisitions | Exact geometry | Status |
|---|---|---|---|
| Sentinel‑1 RTC pair 1 | Jan 12 and Jan 24, 2026 | S1A IW, rel 12 ascending, VV/VH | Pixel-validated, 6,475,371 common valid pixels |
| Sentinel‑1 RTC pair 2 | Jan 9 and Jan 21, 2026 | S1A IW, rel 150 descending, VV/VH | Pixel-validated, 6,475,371 common valid pixels |
| Sentinel‑2 L2A | Jan 10 and Jan 20, 2026 | S2B, tile 45QYF, rel 133, baseline 05.11 | Phase 6B SCL clear support; offsets read from exact metadata |

The earlier orbit‑114 Jan 7/19 pair remains unusable due to the Jan 7 VV asset failure. It was not substituted or inferred.

## Interpretation and gate

The input gate passed for **experimental inference**: linear RTC intensity was converted into the dB representation expected by the trained pipelines, exact checkpoint normalization was applied, and invalids were masked. The sensor measurement reference remains different: local RTC terrain-corrected Gamma0 is not equivalent to the benchmark's GRD dB. Benchmark metrics are not local accuracy. The two models also disagree considerably in predicted class footprint and cross-sensor overlap.

Thus the outputs are **model-predicted water-like class and change candidates** only. Do not treat their area totals as flood extent, new inundated land, affected cropland, village-specific estimates, or proof of a breach. No authoritative permanent water, aquaculture, cropland or village boundary layer was available to support those deductions. Field labels remain necessary before a local water-likelihood model can be evaluated.

## Deliverables and reproduction

- [Model input provenance](GHERPROOF_MODEL_INPUT_PROVENANCE.md)
- [Radiometric compatibility](GHERPROOF_RADIOMETRIC_COMPATIBILITY.md)
- [Regional inference](GHERPROOF_REGIONAL_INFERENCE_REPORT.md)
- [Optical corroboration](GHERPROOF_OPTICAL_CORROBORATION.md)
- Scripts: `scripts/gherproof/phase7/`
- Inputs and output manifests: `data/gherproof/manifests/phase7_*.json`
- Processed rasters/figures: `data/gherproof/processed/phase7/`

```powershell
Push-Location backend
.venv/Scripts/python.exe -m pytest tests/test_gherproof.py tests/test_gherproof_boundary.py tests/test_gherproof_boundary_api.py tests/test_gherproof_cdse_auth.py tests/test_gherproof_event_imagery.py tests/test_gherproof_planetary_computer.py tests/test_gherproof_phase7_inputs.py -q
Pop-Location
python scripts/gherproof/phase7/audit_radiometric_compatibility.py
backend/.venv/Scripts/python.exe scripts/gherproof/phase7/process_optical.py
python scripts/gherproof/phase7/run_experimental_inference.py
python scripts/gherproof/phase7/validate_outputs.py
```

The audit/inference commands require system Python with PyTorch, and add the backend virtual environment's Rasterio packages. Neither output represents locally validated model performance. No final classifier training was performed.
