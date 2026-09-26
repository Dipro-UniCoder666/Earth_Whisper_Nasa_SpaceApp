# Step 3 — NISAR Temporal Fingerprint

## Objective

Identify spatially connected areas within the Sandhya River AOI that exhibit significant temporal changes in NISAR interferometric coherence.

## AOI

Sandhya River, Babuganj, Barishal, Bangladesh.

AOI:
POLYGON((90.15 22.47,90.22 22.47,90.22 22.51,90.15 22.51,90.15 22.47))

## NISAR observations

| Product | Acquisition interval | Polarization |
|---|---|---|
| GUNW_023_091 | 20 Jun 2026 → 2 Jul 2026 | HH |
| GUNW_025_091 | 14 Jul 2026 → 31 Aug 2026 | VV |
| GUNW_026_091 | 26 Jul 2026 → 19 Aug 2026 | VV |
| GUNW_029_091 | 31 Aug 2026 → 12 Sep 2026 | HH |

All four observations use Track 91 / Frame 77 descending geometry.

## AOI extraction

The GUNW products were remotely accessed from NASA/ASF Earthdata Cloud.

The common GUNW grid was used for extraction.

- Columns: 5584:5948
- Rows: 9928:10157
- Resolution: 20 m
- Rectangular extraction: 83,356 pixels
- Exact AOI pixels retained: 79,874
- Exact AOI retention: 95.82%

A polygon mask was applied to exclude pixels outside the actual AOI.

## Coherence change

Two same-polarization comparisons were calculated.

### HH comparison

GUNW_023 → GUNW_029

20 Jun–2 Jul → 31 Aug–12 Sep

### VV comparison

GUNW_025 → GUNW_026

14 Jul–31 Aug → 26 Jul–19 Aug

Change was calculated as:

Δcoherence = later coherence − earlier coherence

## Candidate-region detection

Candidate pixels were defined using:

Δcoherence ≤ −0.20

Connected components were identified using 8-connectivity.

Minimum region size:

10 pixels.

Each GUNW pixel represents:

20 m × 20 m = 400 m².

A total of 211 candidate regions were identified within the exact AOI.

## Region-level temporal fingerprint

For each candidate region, coherence statistics were extracted from all four GUNW observations.

The resulting table is:

`data/step2_region_temporal_fingerprint.csv`

This provides the temporal behavior of each candidate region across the available NISAR observations.

## Sentinel-1 independent radar cross-check

Sentinel-1 GRD data were used as an independent radar observation.

The first comparison used Sentinel-1 D observations from:

- 3 Jul 2026
- 15 Jul 2026

Sigma0 VV was calibrated using the available sigmaNought calibration LUT.

A Sentinel-1 dB-change layer was generated.

Candidate regions were sampled using candidate-pixel-centered Sentinel-1 neighborhoods.

The resulting screening table is:

`data/step2_nisar_s1_ranked.csv`

## Candidate geographic output

The geographically corrected candidate-region table is:

`data/step2_candidate_regions_geographic.csv`

## Important limitations

1. The four GUNW observations do not form one continuous four-point coherence time series.

2. GUNW_023 and GUNW_029 are HH, while GUNW_025 and GUNW_026 are VV.

3. The interferograms have different temporal baselines.

4. Therefore, coherence changes are treated as change indicators rather than direct measurements of erosion, deposition, or deformation.

5. A decrease in coherence does not uniquely identify a physical process.

6. Sentinel-1 backscatter change is also not uniquely diagnostic of erosion because radar backscatter can change due to moisture, vegetation, water extent, surface roughness, and other factors.

7. Sentinel-1 candidate sampling used candidate-pixel-centered neighborhoods rather than strict polygon intersection.

8. The Step 3 candidates therefore represent areas requiring independent verification rather than confirmed Earth-surface events.

## Step 3 conclusion

Step 3 produced 211 spatially connected NISAR coherence-change candidate regions within the Sandhya River AOI.

These candidates were temporally characterized using four GUNW observations and independently screened against Sentinel-1 radar backscatter change.

The candidates are carried forward to Step 4 for independent optical and environmental verification.
