# GherProof machine-learning report

> **Historical report:** The “no training or inference performed” status below was true before Phase 2. A scratch-initialized benchmark model has since been trained and evaluated on event-held-out Sen1Floods11 chips. Current numbers and limitations are in [GHERPROOF_TRAINING_REPORT.md](GHERPROOF_TRAINING_REPORT.md). No Sujatpur inference has occurred.

**Status:** No training or inference performed. This report distinguishes benchmark-data readiness from local event readiness.

## Hardware and software

- `nvidia-smi` reports NVIDIA GeForce RTX 3050, 4,094 MiB VRAM, CUDA driver 12.8.
- The active Python environment has PyTorch `2.12.1+cpu`; `torch.cuda.is_available()` is false and `torch.version.cuda` is `None`.
- RAM reported by `psutil`: 15.64 GiB. The active PyTorch install is CPU-only; a compatible pretrained SAR checkpoint is available separately.
- No GherProof model checkpoint is present. No training run occurred.

The machine cannot use its GPU from the installed PyTorch build. Replacing the project environment with a CUDA wheel is not sufficient by itself: 4 GiB VRAM is restrictive for the official DAM‑Net configuration, and the local benchmark archive does not expose the event split needed for defensible evaluation.

## S1GFloods audit

The downloaded RAR passed an archive integrity test and the paired sample was decoded. Sample inputs are three-channel RGB 256×256 PNGs; the target is an 8-bit single-channel mask with values 0 and 255. No normalization/input-channel convention beyond this image representation has been inferred. The author's repository gives 5,360 pairs across 46 events and states 4,300/530/530 split sizes, but the downloaded archive itself has only flat `A`, `B`, and `Label` directories with generic `image_N` names. There is no local mapping from filename to event, region, year, or published split.

**Leakage conclusion:** Cannot verify geographic or event separation and cannot create an event-level holdout from the available archive alone. A random filename/pixel split is not an acceptable substitute. No final or exploratory reported metrics were computed.

### License check

The Hugging Face dataset card reports CC‑BY‑4.0. The official author repository says the dataset is for non-commercial and research purposes and commercial use requires contacting the authors. We have treated the data as restricted to non-commercial research pending author clarification. The official code page identifies its repository license as CC0, but this does not supersede the dataset-use terms stated in the README. [Dataset card](https://huggingface.co/datasets/Tamer-Saleh/S1GFloods) · [Author repository](https://github.com/Tamer-Saleh/S1GFlood-Detection)

## Candidate architecture and gating

The intended primary task remains pre/post temporal flood-change segmentation. The official DAM‑Net implementation is the first candidate because it is the author's Siamese pre/post system, but its dependencies are older and compatibility/checkpoint availability were not verified. A smaller Siamese U‑Net is supplied in the Colab notebook as a transparent baseline only; it is not trained or a claim of equivalent DAM‑Net performance.

The notebook is deliberately gated on a `split_manifest.csv` with columns `filename,event_id,split` and unique event membership across `train`, `validation`, and `test`. The current archive has no way to populate `event_id`, so a notebook run will stop before model training unless a curator supplies source-backed event assignments. This prevents invented grouping and leakage-prone random splits.

## Benchmark and local evaluation status

| Evaluation | Result |
|---|---|
| IoU / mIoU | Not measured |
| Precision / recall / F1 | Not measured |
| PR-AUC / confusion matrix | Not measured |
| Event-held-out benchmark | Not run; split mapping unavailable |
| Sujatpur inference | Not run; no local event imagery processed and no trained checkpoint |
| Field validation | Not available; no local reference labels |

The benchmark's published results, if cited externally, are not this project's reproduced metrics and do not establish transfer accuracy in Bangladesh.

## Exact prerequisites

1. Obtain author-provided file-to-event/region/year mapping and the official train/validation/test assignment or a documented event grouping.
2. Review benchmark input scale, bands/channel order, normalization, data augmentation, label meaning, and no-data policy from the author loader before training.
3. Confirm legal use terms, model-code dependencies, checkpoint existence and checkpoint licensing.
4. Use a Colab GPU or provision compatible CUDA software and suitable memory; log exact runtime/hardware, seeds, package versions, and checkpoint hash.
5. Freeze event-level holdout before any tuning. Evaluate the held-out test only once after model selection.
6. For Sujatpur, process actual same-orbit pre/post SAR with consistent radiometry/georeferencing/masks, acquire authoritative/provisional georeferenced enclosure/cropland context, and gather independent field observations.
7. Distinguish benchmark metrics from local inference and field-verified labels; report uncertainty and alternative causes.

No model accuracy or local flood/spillover result is claimed in this report.
