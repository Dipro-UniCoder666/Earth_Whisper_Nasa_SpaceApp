# GherProof Phase 3 — Read-only repository and data audit

**Audit baseline:** 2026-11-12 (local repository state, before Phase 3 implementation). This report records what was inspected and what was present. It is not a claim of recovered event data.

## Repository protection and initial state

`git status --short` was inspected at task start. The working tree already contained substantial staged and unstaged changes and untracked content across the Earth Whisper frontend/backend, GherProof, DELTAQ archive, and earlier reports. The inspected status included staged additions/deletions, `MM` paths, ordinary modifications and untracked `archive/`, `data/gherproof/`, `models/`, `notebooks/`, and `scripts/gherproof/`. No reset, clean, stash, restore, checkout, add, or commit was used. Sandhya and Monda source/data paths were not edited.

At the start, `archive/deltaq_legacy/` resolved inside the repository and contained 182 files, 63 directories and 47,825,247 bytes (45.6 MiB), not the 194-file/8.48-GiB estimate in the retirement note. `data/deltaq/` did not exist. The archive subtree was project-specific (its app feature, backend modules/tests, data tree, scripts, reports and figures); no active GherProof/Sandhya/Monda source referenced it. The explicit retirement request was then carried out; the archive is no longer present. See the removal record in the Phase 3 report.

## Files actually inspected

- Phase 2 and training reports: `docs/GHERPROOF_PHASE2_REPORT.md`, `docs/GHERPROOF_TRAINING_REPORT.md`.
- Earlier provenance and ML notes: `docs/GHERPROOF_DATA_PROVENANCE.md`, `docs/GHERPROOF_ML_REPORT.md`.
- Event and model manifests: `event_imagery_manifest.json`, `event_satellite_catalogue.json`, `pre_event_sentinel2_manifest.json`, `enclosure_boundary_provenance.json`, `sen1floods11_download_manifest.json`, `sen1floods11_qc_manifest.json`, `sen1floods11_training_results.json`, `sen1floods11_independent_evaluation.json`, `sen1floods11_license_check.json`, and `sar_pretrained_weights_manifest.json` under `data/gherproof/manifests/`.
- Processed-data note: `data/gherproof/processed/README.md`.
- Retrieval/processing/evaluation code: `recover_event_imagery.py`, `recover_pre_event_sentinel2.py`, `prepare_sen1floods11.py`, `validate_sen1floods11.py`, `train_sen1floods11.py`, `evaluate_sen1floods11_checkpoint.py`, and `download_sar_pretrained.py` under `scripts/gherproof/`.
- Model class/checkpoint metadata: `AttentionUNet` in `train_sen1floods11.py`; `models/gherproof/sen1floods11_attention_unet.pt`; two-channel ResNet50 MoCo weights at `data/gherproof/raw/pretrained_sar/resnet50_sentinel1_all_moco.pth`.
- Active product route/service: `app/src/router.tsx`, `app/src/lib/constants.ts`, `app/src/features/gherproof/GherProofPage.tsx`, `backend/app/main.py`, `backend/app/api/gherproof.py`, and `backend/app/services/gherproof_service.py`.

## Existing GherProof state

| Area | Audited state |
|---|---|
| CDSE event scenes | Four OData COG links: Jan 7/19, 2026 S1A IW GRDH, orbit 114 ascending, VV and VH. Every asset is `authentication_blocked`; no local S1 event measurement rasters exist. Catalog checksum strings are 36 hex characters and not an identified standard digest. |
| Authentication | The process has no `CDSE_USERNAME`, `CDSE_PASSWORD`, or CDSE TOTP value. No credential attempt was made in this audit. |
| Pair readiness | Jan 7 is seven days before the reported Jan 14 event; Jan 19 is five days after. Matching scene names alone do not establish calibration, terrain correction, unit compatibility, pixel alignment or valid AOI coverage. Those checks require actual assets. |
| Local optical context | A Jan 13 Sentinel‑2B L2A true-colour crop exists, 10 m, EPSG:32645, 1563×1685 pixels, cropped over the broad 15 km scale provisional locality window. It is not an enclosure boundary or land-cover classification. |
| Boundary | Provenance record is `not_delineated`, geometry null; no verified enclosure, cropland or permanent-water geometry exists. |
| Benchmark dataset | Sen1Floods11 v1.1 S1Hand/LabelHand has 446 paired chips, official split lists and event metadata. Six chips have zero usable labels. The official random val/test lists share event groups with train, so Phase 2 instead held out event 11 for validation and Bolivia as separate test. Licensing remains unclear/proprietary in official catalog metadata. |
| Scratch model | Four-scale attention U-Net, random initialization, two VV/VH dB inputs. 13 epochs, CPU-only PyTorch, event-11 validation IoU 0.5088, separate 15-chip Bolivia IoU 0.6276. These are benchmark metrics, not Sujatpur performance. |
| Pretrained weights | TorchGeo/SSL4EO-S12 two-band Sentinel‑1 ResNet50 MoCo encoder, 94,349,125 bytes, verified SHA-256 `906e4356…98082`, CC-BY-4.0. It is a self-supervised encoder with no water segmentation head; direct water-mask inference is not a valid task. It has not yet been fine-tuned in this project. |
| Existing app | GherProof route and read-only status/catalogue/evidence-report API exist. The current page explicitly states there is no local inference or affected-area estimate. Leaflet/React-Leaflet are installed and used elsewhere. |
| Existing project code | Sandhya/Monda investigation and shared application infrastructure are outside GherProof scope and must remain unchanged. |

## Phase 3 work order and hard blockers

1. Add secure CDSE authentication, resumable download, per-asset verification and an honest pair suitability assessment. Credentials must be supplied locally; there is no safe way to bypass that access control.
2. Inspect pretrained checkpoint against its source architecture and preprocessing. Direct water-segmentation inference is incompatible because the source weights are an encoder only. A separately named encoder-decoder fine-tuning experiment can be compared only on the Phase 2 event-level split; CPU/GPU runtime and label/data terms must be reported.
3. Provide a human-reviewed, versioned candidate-boundary workflow with required evidence and reviewer metadata before status can be verified. No boundary may be inferred automatically from the broad Sentinel‑2 crop.
4. Gate event inference and area estimation on validated pre/post scenes, suitable model, verified boundary, and reliable permanent-water/cropland references. If any gate is unmet, expose the blocker and produce no area map/value.
5. Remove the retired product’s dedicated archive, active redirect and stale references only after checking ownership and preserving unrelated project changes.
