# GherProof benchmark training and evaluation

**Status: benchmark experiments completed; local Sujatpur model validation not possible.** Both models were trained/evaluated on Sen1Floods11 hand-labelled water/non-water masks. Neither reports Sujatpur performance.

## Data split and evaluation protocol

Sen1Floods11 v1.1 contains 446 paired 512×512 VV/VH dB chips with hand labels (`-1` no-data, `0` non-water, `1` water). Six chips have no usable pixels. Official random validation/test lists share event footprints with training and were not used as independent scores. Both experiments used the same 210 usable chips from official train after holding out all 41 usable event-11 chips for validation. The separate published 15-chip Bolivia event was test-only and was not used to select a checkpoint or threshold. Threshold was fixed at 0.5, as in the Phase 2 scratch run; no threshold was tuned on Bolivia.

The official v1.1 hand imagery and label collection metadata declare `proprietary`; obtain written terms from Cloud to Street before redistributing data or derived model weights. Both checkpoints remain local. See `data/gherproof/manifests/sen1floods11_license_check.json` and `license_provenance.json`.

## Experiments

1. **Scratch baseline:** four-scale residual attention U-Net, 509,564 parameters, random initialization, 2-channel VV/VH dB input. Trained 13 epochs with early stopping, seed 42, 256×256 random patches, batch 4. CPU-only PyTorch 2.12.1; CUDA and mixed precision were unavailable. Checkpoint: `models/gherproof/sen1floods11_attention_unet.pt` (SHA-256 `fcb244de72d51da9760d089ed5909d0cfdfda41af2e8def76aae203aadf5a040`).
2. **Direct pretrained inference:** not applicable. TorchGeo/SSL4EO-S12 supplies an encoder-only self-supervised ResNet50 backbone. It has no segmentation decoder, water output layer, or water-mask label convention. Applying it directly cannot produce water probabilities, so no direct-inference scores or masks were created.
3. **Pretrained initialization/fine-tuning:** custom encoder-decoder whose ResNet50 encoder state loaded **strictly** with all checkpoint keys matching; the 2-channel stem accepts VV/VH. Fine-tuned encoder layers 3–4 and decoder; stem and layers 1–2 were frozen due CPU constraints. Seed 42, same train/validation/test chips, patches, labels and fixed threshold. Eight epochs with early stopping; best checkpoint at epoch 4. Pretraining normalization used `S1_MEAN=[-12.54847273,-20.19237134]`, `S1_STD=[5.25697717,5.91150917]` dB from SSL4EO-S12. The scratch baseline retains its training-set normalization; inputs and split remain identical while normalization follows each model's documented training setup. Checkpoint: `models/gherproof/sen1floods11_resnet50_moco_unet.pt` (SHA-256 `084b41f06ea0f1049b53c6708fed0a78e081a38704677dce7e172e67e2b8d9f0`).

The pretrained source is [TorchGeo ResNet50 Sentinel‑1 GRD MoCo](https://huggingface.co/torchgeo/resnet50_sentinel1_all_moco), derived from [SSL4EO‑S12](https://github.com/zhu-xlab/SSL4EO-S12). It is a self-supervised remote-sensing representation, not a flood model. Its 318 encoder tensors were loaded without dropping/reshaping keys. The weights manifest records CC BY 4.0 attribution and artifact SHA-256. The original ResNet-50 is convolutional and supports variable spatial sizes; SSL4EO S1 sample patches are about 264×264, and fine-tuning used 256×256 crops.

## Results

| Model | Event-11 validation | Bolivia event test | 256×256 CPU latency | Parameters | Checkpoint bytes |
|---|---|---|---:|---:|---:|
| Scratch attention U-Net | IoU 0.5088; precision 0.6469; recall 0.7044; F1 0.6744; PR-AUC 0.72684; AP 0.72684 | IoU 0.6276; precision 0.7423; recall 0.8023; F1 0.7712; PR-AUC 0.74693; AP 0.74693 | 49.3 ms | 509,564 | 2,064,496 |
| MoCo ResNet50 encoder + decoder, fine-tuned | IoU 0.5505; precision 0.6849; recall 0.7371; F1 0.7101; PR-AUC 0.74123; AP 0.74123 | IoU 0.5942; precision 0.8905; recall 0.6410; F1 0.7454; PR-AUC 0.84058; AP 0.84058 | 158.3 ms | 37,244,737 | 149,316,323 |

Confusion matrices use rows true non-water/water and columns predicted non-water/water:

- Scratch event 11: `[[9,509,438, 222,504], [171,036, 407,583]]`; Bolivia: `[[2,246,682, 125,851], [89,332, 362,569]]`.
- Fine-tuned event 11: `[[9,535,710, 196,232], [152,099, 426,520]]`; Bolivia: `[[2,336,900, 35,633], [162,211, 289,690]]`.

On validation, the fine-tuned model improves each listed metric. On the one-event Bolivia test, it sharply raises precision and PR-AUC but lowers recall and IoU relative to scratch. Thus fewer false positives accompany more missed labeled water pixels in Bolivia. The two holdout groups have only 41 and 15 chips, respectively; event composition and water prevalence differ (5.6% vs 16.0%). No confidence intervals, probability calibration, stratified error review, or multi-event average were calculated. Benchmark scores are not transferable accuracy estimates for Bangladesh.

Latency is a single 256×256 CPU forward pass on this environment, not a production throughput benchmark. The fine-tuned model has about 73× as many parameters and a 72× larger checkpoint; this tradeoff matters on the available CPU. No CUDA memory result exists because this PyTorch build is CPU-only.

## Recommendation

**Do not select either model for quantitative Sujatpur event reporting.** The fine-tuned checkpoint is the stronger candidate for a controlled, non-operational follow-up because of its higher event-11 validation metrics and Bolivia PR-AUC, but Bolivia's much lower recall and only 15 chips make that evidence insufficient to establish superiority or local suitability. Keep the scratch model as a small baseline. Before local inference is considered, recover and validate the same-orbit scenes, verify the enclosure and land references, collect representative local standing-water/non-water field labels, and compare error patterns/calibration without changing the held-out event protocol.

The exact evaluation is reproducible with `py scripts/gherproof/evaluate_pretrained_model.py`. Training is `py scripts/gherproof/train_pretrained_sen1floods11.py --epochs 15 --patience 4 --patch 256 --batch-size 4 --seed 42`. Machine-readable source records are `data/gherproof/manifests/sen1floods11_pretrained_finetune_results.json`, `pretrained_model_comparison.json`, and `sar_pretrained_weights_manifest.json`.
