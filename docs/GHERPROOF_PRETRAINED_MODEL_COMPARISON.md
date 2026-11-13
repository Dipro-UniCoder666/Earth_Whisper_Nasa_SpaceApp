# Pretrained Sentinel‑1 checkpoint comparison

## Checkpoint audit

The downloaded 94,349,125-byte file is TorchGeo's `resnet50_sentinel1_all_moco`, derived from the SSL4EO‑S12 Sentinel‑1 GRD MoCo model. Its pinned SHA-256 is `906e4356da0ff06ce0388cba50dd4f310ba6abbee706c5303c129d8aead98082`; the TorchGeo model card states CC BY 4.0. The upstream model is a self-supervised ResNet-50 backbone trained with Sentinel‑1 dual-polarization data, not a supervised water segmentation model.

Inspection found 318 tensor entries, a 2-input-channel first convolution of shape `[64,2,7,7]`, ResNet50 bottleneck stages, no classification `fc` layer, and no segmentation decoder/head. The checkpoint has no water/non-water output convention. The implementation's encoder loaded all keys strictly and unchanged. Fine-tuning uses Sen1Floods11's VV then VH channel order, dB inputs, and SSL4EO-S12 per-channel mean/std. The convolutional model supports variable raster size; this run used 256×256 training patches. The pretrained weights are CC BY 4.0, but the separate Sen1Floods11 training labels are proprietary/unclear; this fine-tuned checkpoint remains non-redistributed pending data-owner permission.

## Experiments

| Experiment | Status | Interpretation |
|---|---|---|
| 1. Scratch attention U-Net | Evaluated | Phase 2 checkpoint, same frozen event split; baseline. |
| 2. Direct pretrained encoder inference | Not applicable | Encoder-only representation cannot emit a water class/probability. No fabricated output or metric was produced. |
| 3. Pretrained initialization plus fine-tuning | Completed | Matching ResNet50 encoder initialized strictly; final two stages and decoder fine-tuned; early stages frozen for CPU feasibility. |

Both segmentation experiments use 210 train chips excluding the full event-11 validation group, 41 event-11 validation chips, and the separate 15-chip Bolivia test. The threshold is fixed at 0.5 for both. No metric, threshold, or checkpoint selection used Bolivia. Scratch normalization is derived from its training chips; pretrained normalization uses the upstream S1 means/stds. Split, rasters, spatial sizes, labels, and metrics are otherwise fixed.

## Results by held-out event

| Model | Group | IoU | Precision | Recall | F1 | PR-AUC | AP | False positives | False negatives |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Scratch | Event 11 validation | 0.5088 | 0.6469 | 0.7044 | 0.6744 | 0.72684 | 0.72684 | 222,504 | 171,036 |
| Pretrained fine-tune | Event 11 validation | 0.5505 | 0.6849 | 0.7371 | 0.7101 | 0.74123 | 0.74123 | 196,232 | 152,099 |
| Scratch | Bolivia test | 0.6276 | 0.7423 | 0.8023 | 0.7712 | 0.74693 | 0.74693 | 125,851 | 89,332 |
| Pretrained fine-tune | Bolivia test | 0.5942 | 0.8905 | 0.6410 | 0.7454 | 0.84058 | 0.84058 | 35,633 | 162,211 |

Confusion matrices (true rows `[non-water, water]`, predicted columns `[non-water, water]`):

- Event 11 scratch: `[[9,509,438,222,504],[171,036,407,583]]`.
- Event 11 fine-tuned: `[[9,535,710,196,232],[152,099,426,520]]`.
- Bolivia scratch: `[[2,246,682,125,851],[89,332,362,569]]`.
- Bolivia fine-tuned: `[[2,336,900,35,633],[162,211,289,690]]`.

The fine-tuned model improves all listed event-11 metrics. On Bolivia it has much higher precision and PR-AUC but lower IoU, recall and F1; it misses more benchmark water pixels while reducing false positives. Validation and test each represent just one event, and the test has 15 chips. Water prevalence is approximately 5.6% in validation and 16.0% in Bolivia. These results are not sufficient to assert generalization to Bangladesh.

One 256×256 CPU forward pass measured 49.3 ms for the scratch model and 158.3 ms for the fine-tuned ResNet50 model. The checkpoints have 0.51M versus 37.24M parameters (2,064,496 vs 149,316,323 bytes). This runtime uses CPU-only PyTorch; GPU latency and memory are unmeasured.

## Event-model decision

**No model is approved for quantitative Sujatpur reconstruction now.** The fine-tuned model is a follow-up benchmark candidate because it wins the validation event and has stronger Bolivia PR-AUC, but its reduced Bolivia recall and higher model cost are material. Retain the scratch model as the small baseline. Do not run either on event scenes as operational evidence until the imagery, boundary and local reference gates in `GHERPROOF_EVENT_IMAGERY_VALIDATION.md` and `GHERPROOF_BOUNDARY_PROVENANCE.md` are met. If used earlier for exploratory visualization after gates, mark all predictions unvalidated and do not calculate impact area.

Machine-readable results: `data/gherproof/manifests/pretrained_model_comparison.json`. Fine-tuning result history: `sen1floods11_pretrained_finetune_results.json`. Reproduce evaluation with `py scripts/gherproof/evaluate_pretrained_model.py`.
