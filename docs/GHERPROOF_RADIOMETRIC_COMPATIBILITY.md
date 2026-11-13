# GherProof Phase 7 — Radiometric Compatibility

## Findings

The four Phase 6B Sentinel‑1 rasters are Microsoft Planetary Computer RTC products. STAC asset descriptions and raster tags identify terrain-corrected Gamma0; samples are stored as **linear intensity**, not dB. Raster source files were preserved. For the 6,475,371 common AOI pixels per scene, both channels had positive finite support in the audited set; zero and negative samples were absent in these four regional clips. The model-input pipeline converts positive samples once with `10*log10(x)` and masks source nodata/nonpositive/nonfinite pixels.

Training data are Sen1Floods11 `S1Hand` dual-polarization GRD inputs in dB, channel order VV,VH. The local code clips to [-60,20] dB and uses model-specific z-score parameters (see [model input provenance](GHERPROOF_MODEL_INPUT_PROVENANCE.md)).

## Distribution comparison

The project training subset contained 210 chips and 46,968,696 valid pixels. Deterministic per-chip samples were used for plotted/percentile distributions; training normalization statistics were calculated exactly over all valid training pixels. RTC scene percentiles are calculated from actual valid scene pixels.

| Scene | VV median dB | VH median dB | VV above 20 dB | VH above 20 dB | below -60 dB |
|---|---:|---:|---:|---:|---:|
| S1A, Jan 9, descending rel 150 | -9.3003 | -16.3382 | <0.001% | 0% | 0% |
| S1A, Jan 12, ascending rel 12 | -9.5722 | -16.5637 | <0.001% | 0% | 0% |
| S1A, Jan 21, descending rel 150 | -8.9587 | -16.1742 | <0.001% | 0% | 0% |
| S1A, Jan 24, ascending rel 12 | -9.3886 | -16.6030 | <0.001% | 0% | 0% |

Training sampled medians were VV −9.614 dB and VH −16.174 dB. Thus the central distributions are numerically near these medians and the checkpoint clipping fraction is negligible for the regional samples. The full sampled distributions and percentile tables are in `data/gherproof/manifests/phase7_radiometric_compatibility.json`; the reproducible comparison plot is shown below.

![Training and RTC dB distributions](../data/gherproof/processed/phase7/figures/phase7_radiometric_distributions.png)

| Pair | Band | Median post-pre dB | 2nd–98th percentile dB |
|---|---|---:|---:|
| Jan 12→24, rel 12 ascending | VV | +0.200 | -6.272 to +6.880 |
| Jan 12→24, rel 12 ascending | VH | +0.041 | -6.139 to +5.646 |
| Jan 9→21, rel 150 descending | VV | +0.280 | -6.166 to +6.843 |
| Jan 9→21, rel 150 descending | VH | +0.221 | -5.789 to +5.768 |

![Experimental post-event probability overview](../data/gherproof/processed/phase7/figures/phase7_experimental_probability_overview.png)

## Decision

**Compatibility gate: exploratory inference only.** Physically defensible linear-to-dB conversion and exact checkpoint preprocessing were applied; smoke tests passed. Similar numeric distributions do not resolve measurement baseline, terrain normalization, incidence-angle, speckle, resolution and preprocessing differences between benchmark GRD and regional RTC Gamma0. No local labels exist to test calibration or accuracy. Model output must not be reported as measured water extent or as probability of flood occurrence.
