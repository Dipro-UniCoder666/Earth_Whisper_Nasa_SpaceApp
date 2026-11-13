# GherProof data provenance

> **Update:** The Phase 2 acquisition, Sen1Floods11 dataset QC, license check, and training provenance are recorded in [GHERPROOF_PHASE2_REPORT.md](GHERPROOF_PHASE2_REPORT.md) and the linked machine-readable manifests. Existing entries below describe earlier work and are retained as history.

**As of:** 2026-11-11 UTC. Source downloads are retained locally for research and are not committed as redistributed datasets.

## Event and locality

| Record | Provenance | Treatment |
|---|---|---|
| Reported embankment event | Daily Country Today, published 2026-01-17, reports a failure at the south side of Sujatpur Pallimangal Fisheries Enclosure and flooding in nearby villages. | Secondary news report only. January 14 is inferred from the article's “Wednesday” wording and publication date. No independent incident verification. [Source](https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore) |
| Locality query geometry | WGS84 bbox `[89.15,22.93,89.30,23.08]` in the saved Copernicus STAC search. | Broad provisional locality window only; not a boundary, field GPS point, or authoritative geometry. It must not be used for local area reporting. |
| Event acquisition catalogue | Copernicus Data Space STAC `/v1/search`, Sentinel‑1 GRD and Sentinel‑2 L2A, time window 2026-01-01 to 2026-01-30. | Complete result set saved in `data/gherproof/manifests/event_satellite_catalogue.json`; scene count is catalogue metadata, not processed imagery. The same-orbit S1 Jan 7/19 COG URL byte-range probes returned 401 without an authenticated session. |

## Public machine-learning dataset

| Field | Value |
|---|---|
| Dataset | S1GFloods, Tamer‑Saleh |
| Source | [Hugging Face dataset](https://huggingface.co/datasets/Tamer-Saleh/S1GFloods); source implementation/research [official GitHub repository](https://github.com/Tamer-Saleh/S1GFlood-Detection) |
| Download | `data/gherproof/raw/S1GFloods.rar`, 673,724,972 bytes |
| SHA‑256 | `4f1b57c342c661853dec0d7384709ce4bb9e53097ab31cd060cd4a3f915e3e67` |
| Integrity | UnRAR archive test exit 0; one paired A/B/Label sample opened successfully |
| Observed sample | A and B: 256×256 RGB PNG; Label: 256×256 grayscale PNG; observed label codes 0 and 255 |
| Archive organization | 5,360 files each under `A`, `B`, and `Label`; no split folders, event IDs, geography, or split manifest in the downloaded archive |
| Author-published description | 5,360 pairs, 46 events, 2015–2022; claimed train/validation/test sizes 4,300/530/530. These assignments could not be matched to local archive filenames. |
| Rights | Hugging Face card says CC-BY-4.0; author repository README says non-commercial/research only. Applied stricter non-commercial/research treatment pending clarification. |

The archive has been retained but not fully extracted into a training tree. A local sample-only extraction is under `data/gherproof/inspection/`; it is not used as an independent train/test split.

## Historical aquaculture land cover

| Field | Value |
|---|---|
| Dataset | Clark Labs Bangladesh Land Cover and Change Maps |
| Source page | [Clark University download page](https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/) |
| Archive | `data/gherproof/raw/Clark_Bangladesh_Aquaculture_1999_2022.zip`, 46,943,637 bytes |
| SHA‑256 | `5c070d8e06d73a79d282b99047f096174701106291a25b012e573c1bb742ee5a` |
| Years included | 1999, 2014, 2018, 2020, 2022; source archive also includes change-persistence maps |
| Inspected layer | 2022 categorical GeoTIFF, 27,672 × 24,088, 15 m, uint8, WGS84 Normal Aspect Cylindrical Equal Area, nodata 0 |
| Legend | 1 mangrove; 2 coastal wetland; 3 pond aquaculture; 4 water; 5 other land cover; 6 missing. The opened Bangladesh 2022 raster contained values 0, 1, 3, 4, 5. |
| Rights | Clark page says free for non-commercial use only; archive metadata says CC-BY-4.0. Preserve attribution; non-commercial restriction governs until clarified. Do not redistribute archive. |
| Local use | No Sujatpur gher polygons/area were extracted because the incident enclosure geometry and exact location have not been verified. 2022 class 3 is not a verified 2026 fish-farm enclosure boundary. |

The inspected 2022 raster and required metadata sidecars are held in `data/gherproof/processed/clark/`. This is a source classification copy for local research, not a derived incident result.

## Not acquired

- Sen1Floods11: the full bucket is about 14 GB; no event/label-quality-aware subset was downloaded.
- Dynamic World: Earth Engine credentials and AOI processing were not configured.
- January 2026 Sentinel‑1/2 measurement assets: catalogue entries exist, but measurement assets were not successfully read/downloaded in this run.
- NISAR event imagery: unavailable for January 2026; later NISAR dates post-date the reported event and are not event-reconstruction observations.
- Field labels, verified enclosure/cropland polygons, official breach coordinates, local gauge/rainfall records, fish loss records: none acquired.

## Manifests and checksums

- Catalogue query: [`event_satellite_catalogue.json`](../data/gherproof/manifests/event_satellite_catalogue.json)
- COG access checks: [`event_scene_access_checks.json`](../data/gherproof/manifests/event_scene_access_checks.json)
- Public dataset audit: [`public_dataset_audit.json`](../data/gherproof/manifests/public_dataset_audit.json)
- S1GFloods acquisition record: [`public_dataset_downloads.json`](../data/gherproof/manifests/public_dataset_downloads.json)
- Source archives are not suitable for web-serving. The API exposes the metadata catalogue and an evidence-status JSON only.
