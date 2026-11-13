# GherProof Phase 7 — Model Input Provenance

## Scope and source files

This record reconstructs the trained model inputs from `scripts/gherproof/train_sen1floods11.py`, its data loader, training/evaluation manifests and both checkpoint payloads. Regional inference used the four pixel-validated Phase 6B RTC products only. Source imagery and checkpoint files were not overwritten.

The benchmark inputs are Sen1Floods11 v1.1 `HandLabeled/S1Hand` chips. The project training code reads a two-band raster as float32, in **VV then VH** order. Its source chips are 512 × 512 pixels and georeferenced in EPSG:4326 with an approximate 8.983×10⁻⁵ degree affine spacing (about 10 m at the sampled latitude; local chip metadata reports geographic coordinates, so this is not a uniform projected metric grid). Values are dB according to the dataset README. The code does not calibrate or log-convert those chips.

## Exact training transformation

For a pixel with source channels `VV,VH`:

1. Read both source channels as float32; source nodata is excluded. Labels use `0=non-water`, `1=water`, `-1=ignore` (converted to 255 in the loader and excluded from loss/metrics).
2. Validity requires finite values in both channels, non-nodata inputs, and a non-ignore label.
3. Clip each channel in dB to **[-60, 20]**.
4. Apply per-channel z-score normalization `(clipped - mean) / std`.
5. Set both normalized channels to zero for any invalid pixel. Validity remains separately supplied to the loss/metrics.
6. During training only, sample random 256×256 windows from 512×512 chips, rotate by a random multiple of 90 degrees, and optionally flip horizontally. There is no padding. Validation evaluates full chips without cropping.

The scratch checkpoint's means/stds are population statistics recomputed over all valid pixels of the actual project training subset (210 chips; 46,968,696 valid pixels):

| Channel | Mean dB | Population std dB |
|---|---:|---:|
| VV | -10.23175049 | 4.13670397 |
| VH | -17.20221138 | 4.91571236 |

The fine-tuned pretrained encoder/decoder uses its recorded fixed SSL4EO-S12 statistics, not the local subset statistics:

| Channel | Mean dB | Population std dB |
|---|---:|---:|
| VV | -12.54847240 | 5.25697708 |
| VH | -20.19237137 | 5.91150904 |

Both models use threshold 0.5 from their benchmark evaluation. It was not tuned on the regional event. Checkpoint hashes are recorded in the Phase 7 inference manifest and are checked before loading.

## Regional inference transformation

Planetary Computer Phase 6B products contain two float32 RTC Gamma0 linear-intensity channels, tagged VV and VH, EPSG:32645, 10 m, 3,111×2,156, with nodata -32768. For finite positive non-nodata samples, the pipeline applies exactly once:

`dB = 10 * log10(linear Gamma0)`

Zero, negative, non-finite, source-nodata and invalid-band pixels are excluded. The converted dB values are clipped to [-60,20] and normalized with each checkpoint's own stored statistics. Invalid normalized input is zeroed, but the original common valid mask is preserved and excluded from exported predictions and area counts. There is no regional min-max normalization.

Inference uses overlapping 256×256 tiles with 64-pixel overlap and positive raised-cosine blending. Tiles cover the rectangular raster grid completely; predictions are masked back to 6,475,371 pixels valid in the source scene. Both models are applied independently. No logits, probabilities or masks are averaged. Probability output is finite and within [0,1]; repeat forward output differed by 0.0 in the smoke check.

## Compatibility limits

Numerical units are brought into the checkpoint's dB input contract, but Sentinel-1 GRD dB and RTC Gamma0 dB are not the same measurement reference. RTC terrain normalization, incidence-angle behavior, processing/resampling and speckle/texture differ, and training chip acquisition metadata is incomplete. Similar medians do not demonstrate distributional or semantic equivalence. The two local model outputs are therefore exploratory model classes, not calibrated water probabilities and not locally validated predictions.

Reproduction: `python scripts/gherproof/phase7/audit_radiometric_compatibility.py`, then `python scripts/gherproof/phase7/run_experimental_inference.py`. The latter verifies pinned hashes and refuses to run if either model/input contract fails.
