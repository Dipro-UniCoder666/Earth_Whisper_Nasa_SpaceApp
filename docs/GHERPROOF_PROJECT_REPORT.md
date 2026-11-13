# GherProof project report

> **Historical report, superseded by Phase 3 (2026-11-12):** Sections below record an earlier readiness stage. Statements such as “no model trained” and “no comparison” are no longer current. For the actual scratch and pretrained benchmark results, current authentication state, boundary workflow and event blockers, use [Phase 3 report](GHERPROOF_PHASE3_REPORT.md), [training report](GHERPROOF_TRAINING_REPORT.md), and [pretrained comparison](GHERPROOF_PRETRAINED_MODEL_COMPARISON.md). The Sujatpur event remains unreconstructed.

**Status date:** 2026-11-11 UTC
**Repository:** Earth Whisper, branch `feature/gherproof`
**Decision boundary:** Existing project retained; event reconstruction remains a data-readiness prototype. No local flood prediction or area estimate is published.

## Product and implementation

GherProof is the focused Sujatpur Pallimangal Fisheries Enclosure case experience: **Satellite Evidence for Aquaculture Flood Spillover**. It keeps Earth Whisper as the parent brand and leaves the existing Sandhya and Monda investigation routes/data at their original paths.

The primary navigation shows Home, Investigate, GherProof and About. `/gherproof` is the GherProof case route. Retired DELTAQ materials were removed from this working repository in Phase 3; see the phase report for the measured deletion scope. Sandhya/Monda files were not moved.

The GherProof frontend reads a small, read-only FastAPI contract. The page shows reported-event context separately from catalogue search records and explicitly shows zero processed observations, no inference, and no affected-area estimate. `/api/gherproof/evidence-report` produces a downloadable JSON status report with null model/area fields rather than made-up results.

## Reported event and target location

News coverage published January 17, 2026 reports that a south-side embankment at Sujatpur Pallimangal Fisheries Enclosure failed on Wednesday and flooding affected cropland/villages. The January 14 date is inferred from the article's publication date and “Wednesday”; it is treated as a reported date, not independently verified. The report is not a field survey or official incident record. [Daily Country Today report](https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore)

No authoritative enclosure polygon was found in the repository or public catalogue query. A broad search box was used only to locate candidate scenes; it is not the incident AOI. The current UI and manifests label that geometry provisional. No approximate point or Clark pixel was promoted to an enclosure boundary.

## Event-window satellite catalogue results

The Copernicus Data Space STAC API was queried for January 1–30, 2026 using the provisional WGS84 bounding box `[89.15, 22.93, 89.30, 23.08]`. This is a broad locality query and includes areas outside a surveyed enclosure. Results are recorded in [`event_satellite_catalogue.json`](../data/gherproof/manifests/event_satellite_catalogue.json).

| Collection | Catalogue matches | Acquisition dates found | Processing status |
|---|---:|---|---|
| Sentinel‑1 GRD | 6 | Jan 7, 9, 12, 19, 21, 24 | Catalogue only; none downloaded or processed |
| Sentinel‑2 L2A | 14 | Jan 3, 5, 7, 8, 10 (2), 13, 15, 18, 20, 23, 25, 28, 30 | Catalogue only; no cloud mask/clear observation confirmed |

The most temporally relevant same-geometry Sentinel‑1 catalogue pair is **2026-01-07 and 2026-01-19**, both Sentinel‑1A, relative orbit 114, ascending, IW, VV/VH. They are 12 days apart, with the acquisitions 7 days before and 5 days after the reported January 14 date. This establishes catalogue availability over the broad search box only. The two VV COG alternate URLs returned HTTP 401 during unauthenticated byte-range probes, so neither scene could be read or locally processed in this environment. VH assets were not independently probed. Exact access checks are in [`event_scene_access_checks.json`](../data/gherproof/manifests/event_scene_access_checks.json). No suitable pair is yet a processed image pair.

Sentinel‑2 catalogue results include nearby dates, but scene-level cloud/shadow assessment and target-footprint reading were not completed. A catalogue result does not establish usable optical pixels. NISAR began the relevant local archive after the event; later 2026 NISAR cannot observe or reconstruct the January event.

## Public data acquired and inspected

| Asset | Actual local result | Use and limitation |
|---|---|---|
| S1GFloods | Downloaded 673,724,972-byte RAR; SHA‑256 `4f1b57c342c661853dec0d7384709ce4bb9e53097ab31cd060cd4a3f915e3e67`; archive integrity test exit 0. One A/B/Label triplet opened. | 256×256 RGB pre/post PNGs and single-channel label with observed values 0 and 255. The archive has flat `A`, `B`, `Label` folders and generic `image_N` names; it contains no event IDs, geographies, or train/validation/test manifests. Event-level leakage cannot be audited from this copy. |
| Clark Bangladesh aquaculture maps | Downloaded 46,943,637-byte Bangladesh archive; SHA‑256 `5c070d8e06d73a79d282b99047f096174701106291a25b012e573c1bb742ee5a`. Extracted and opened the 2022 raster and legend metadata. | 15 m country-scale categorical raster; legend code 3 is pond aquaculture. It is a historical 2022 classification, not a surveyed 2026 gher boundary. No incident enclosure inventory was made without a verified location/polygon. |
| Sen1Floods11 | Not downloaded. | The complete bucket is about 14 GB; no focused subset was justified in this phase. Human labels and weak/reference labels must be kept distinct. |
| Dynamic World | Not queried. | Earth Engine credentials and a verified local AOI were not available. |

Exact download and inspection facts are recorded in [`public_dataset_audit.json`](../data/gherproof/manifests/public_dataset_audit.json). Clark University describes its Bangladesh rasters as 15 m and identifies year products through 2022; its download page states non-commercial-only usage. Its embedded README provides the class legend, including pond aquaculture class 3. [Clark aquaculture download page](https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/)

## Machine learning and local inference

No model was trained. The host has an NVIDIA GeForce RTX 3050 with 4 GiB VRAM, but the installed PyTorch 2.12.1 build is CPU-only (`torch.cuda.is_available() == False`). More importantly, S1GFloods' downloaded archive lacks the event/split assignments required to construct an honest event-level holdout. A random patch split would violate the stated leakage control. The `models/gherproof/` area contains no checkpoint and the application exposes no predictions.

The official DAM‑Net implementation is referenced and its published repository describes a Siamese pre/post architecture. The README documents 5,360 pairs from 46 events and its published split counts (4,300/530/530); however, those assignments are not present in the downloaded RAR. The official training entrypoint also sets a batch size of 8 and 100 epochs in its script, which is not suitable to assume on the local 4 GiB GPU even if a CUDA build were installed. [Official DAM‑Net repository](https://github.com/Tamer-Saleh/S1GFlood-Detection)

The package does not report benchmark accuracy, precision, recall, F1, IoU, local Sujatpur inference, or field validation. A Colab training notebook is supplied as a gated recipe: it downloads the archive and implements a Siamese U‑Net baseline, but stops until a lawful event-level split manifest is supplied. It does not silently create random splits. This is reproducible preparation, not training.

## Reproduction and tests

From the repository root:

```powershell
python scripts/gherproof/query_event_scenes.py
python scripts/gherproof/download_public_data.py
cd app
npm run build
cd ../backend
.\.venv\Scripts\python -m pytest tests/test_gherproof.py -q
```

Observed checks: Vite TypeScript/production build passed (with the existing >500 kB main-chunk advisory); GherProof API unit tests passed **3/3**. An unauthenticated Copernicus measurement COG range-read returned HTTP 401; no satellite raster processing was claimed. The frontend and API are a truthful readiness prototype, not an operational incident reconstruction.

## Remaining work

1. Obtain the official incident geometry or georeference a provisional polygon from independently reviewed, dated imagery with a documented positional uncertainty.
2. Obtain valid Copernicus access and download/read the Jan 7/19 same-orbit VV/VH data; verify product scaling, masks, alignment and AOI pixel coverage before comparison.
3. Inspect Sentinel‑2 cloud/shadow validity, and gather independent source imagery/context (including rainfall) around the event.
4. Obtain S1GFloods event and official split mapping from the authors, or construct a documented event-level grouping from source metadata before training.
5. Collect local labels/field observations and independently validate event-specific performance before estimating new inundation or cropland impacts.
6. Clarify dataset usage rights where published metadata conflicts. Do not redistribute Clark/S1GFloods source archives.

Until these gates pass, no claim of confirmed spillover extent, affected-area estimate, breach location/cause, fish loss or compensation eligibility is supported.
