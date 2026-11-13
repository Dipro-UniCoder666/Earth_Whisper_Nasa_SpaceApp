# GherProof Phase 7B — Sensor-Domain Shift Validation

## Scope and conclusion

This comparison uses the project’s Sen1Floods11 v1.1 hand-labelled training subset and the four already validated Planetary Computer RTC acquisitions. It quantifies numerical distribution and adjacent-pixel texture differences after the documented conversion of positive linear RTC Gamma0 to dB. It does not establish measurement equivalence or local classification skill.

**RTC input domain remains exploratory.** The central VV/VH distributions overlap, but distribution tails and texture differ, RTC Gamma0 is not the training product representation, and all exact GRD counterparts inspected are ungeocoded Level 1 DN rather than calibrated products. No evidence yet shows that switching to GRD would improve compatibility because no GRD processing was completed.

## Reproducible comparison

The script reconstructs the 210-chip project training subset from the official training split, excluding the event held out in the Phase 2 benchmark. It reads both VV and VH in dB, clips to the model-input range [-60, 20], samples 2,500 valid pixels per chip and channel with a fixed random seed, and computes pooled empirical distribution summaries. RTC samples use up to 250,000 valid pixels per scene and channel, also seeded. Existing masks are respected. Adjacent-pixel lag-1 correlation and adjacent difference RMSE describe spatial texture. No per-scene min-max stretch is used for quantitative results; the visual uses one fixed -30..0 dB display range.

| Channel | Training median dB | RTC median dB | RTC − training median | Wasserstein-1 dB | Empirical KS D | Training / RTC adjacent RMSE (horizontal, dB) |
|---|---:|---:|---:|---:|---:|---:|
| VV | -9.614 | -9.305 | +0.309 | 0.764 | 0.0872 | 1.642 / 1.961 |
| VH | -16.174 | -16.418 | -0.244 | 0.860 | 0.0756 | 1.988 / 1.828 |

| Channel | Training P02 / P98 dB | RTC P02 / P98 dB | Interpretation |
|---|---:|---:|---|
| VV | -22.309 / -3.479 | -21.034 / -2.803 | RTC has a narrower central 96% interval in this pooled sample, with different spatial texture. |
| VH | -31.267 / -10.306 | -25.736 / -9.987 | RTC low-end tail is substantially less negative; the training and RTC tails differ. |

The KS statistic is descriptive only. A conventional p-value is intentionally omitted because spatial observations are autocorrelated and nominal pixel sample sizes would overstate independence. A distribution distance also depends on the sampled landscape composition and does not account for acquisition geometry or radiometric calibration. Values are pooled over four scenes and a geographically different training set.

Training medians, RTC per-scene percentiles, valid counts and all distribution metrics are in `data/gherproof/manifests/phase7b_domain_shift_statistics.json`. The plot is `data/gherproof/processed/phase7b/figures/phase7b_radiometric_domain_shift.png`.

![Fixed-scale training and RTC dB comparison](../data/gherproof/processed/phase7b/figures/phase7b_radiometric_domain_shift.png)

## Why comparable medians do not resolve domain shift

- The Sen1Floods11 training chip values and event RTC Gamma0 values pass through different product and processing chains. Logging linear Gamma0 once is numerically valid for the RTC representation but does not make it equivalent to the training representation.
- Training samples and the local AOI differ in geography, land cover, incidence-angle distribution, acquisition conditions, resampling and likely speckle texture.
- VV medians differ by about 0.31 dB and VH by about -0.24 dB in the current pooled sample, but VH low percentiles differ by more than 5 dB (P02). Spatial texture also differs: horizontal adjacent-difference RMSE is 1.64 vs 1.96 dB for VV and 1.99 vs 1.83 dB for VH (training vs RTC).
- The probability outputs show meaningful model disagreement; matching input medians cannot be used to select one model.
- GRD values are not included in this comparison. Their remote COG headers identify ungeocoded `uint16` Level 1 GRD data with calibration/noise sidecars. DN is not backscatter power or dB. See [GRD assessment](GHERPROOF_GRD_COUNTERPART_ASSESSMENT.md).

## Figure interpretation

Both panels use a single fixed display stretch, not per-image normalization. The side-by-side chips are representative examples, not a statistically controlled pixel-by-pixel comparison because source regions differ. Brighter pixels indicate stronger backscatter within the -30 to 0 dB display range; clipped high and low values and invalid pixels are not separately encoded. Brightness is not a confidence or water class. No predictions are shown.

## Readiness

The two existing models and their Phase 7 probability maps remain exploratory. The current statistics support the claim that RTC inputs have measurable distribution/texture differences from benchmark training data, not the claim that those differences caused any particular prediction. Exact GRD records exist, but no compatible GRD product has been generated or tested. Independent optical references remain unlabeled, so no local accuracy, threshold selection, model winner, or Phase 8 impact estimate is approved.

Reproduce with:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase7b/domain_shift_metrics.py
```
