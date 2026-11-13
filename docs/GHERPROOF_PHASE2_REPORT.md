# GherProof Phase 2 — Event imagery recovery and incident reconstruction

**Status: PARTIAL / EVENT RECONSTRUCTION BLOCKED.** The reproducible Sen1Floods11 benchmark training run completed, but the January 7/19 Sentinel‑1 assets were not downloaded because no Copernicus Data Space credentials are configured in this runtime. No local incident inference, spillover area, water probability map, or embankment diagnosis was produced.

## 1. Sentinel‑1 event imagery

The saved catalogue identifies the four assets as Copernicus Data Space (CDSE) Sentinel‑1 GRD measurement COGs, served through the CDSE OData product-node `$value` route. They are not ASF/NASA Earthdata assets. Both scenes are S1A IW, relative orbit 114, ascending, dual VV/VH: 2026‑01‑07 and 2026‑01‑19.

| Acquisition | Polarization | Catalogue bytes | Local result |
|---|---|---:|---|
| 2026‑01‑07 | VV | 664,403,282 | Not downloaded: missing CDSE credentials |
| 2026‑01‑07 | VH | 572,402,839 | Not downloaded: missing CDSE credentials |
| 2026‑01‑19 | VV | 662,506,694 | Not downloaded: missing CDSE credentials |
| 2026‑01‑19 | VH | 573,468,706 | Not downloaded: missing CDSE credentials |

Total catalogued payload: 2,472,781,521 bytes. The complete asset URLs, product identity, status, and checksum metadata are in `data/gherproof/manifests/event_imagery_manifest.json`. Catalogue checksum strings are 36 hexadecimal characters and do not identify a standard digest; they are deliberately not misrepresented as MD5. No local SHA‑256 exists for an undownloaded asset. CRS, resolution, nodata, coverage, and georeferencing therefore remain unverified for these four rasters.

The current recovery script supports OAuth refresh, safe bounded redirect handling, resumable byte ranges, expected-size checks, local SHA‑256 and a real Rasterio open/sample read before marking a COG verified. These four catalogue assets are individual measurement GeoTIFF COGs, not ZIP archives, so ZIP validation/extraction is not applicable. **No RTC jobs were resubmitted.**

### Authentication setup

CDSE OData access uses an OAuth2 access token from the official CDSE identity service with public client ID `cdse-public`, then a bearer-authenticated product download. Register/sign in through the Copernicus Data Space Ecosystem and provide credentials only as local environment variables (`CDSE_USERNAME`, `CDSE_PASSWORD`; `CDSE_TOTP` only if account TOTP is enabled). Do not put credentials in source, manifests, command-line arguments, or chat. The provided recovery script reads those environment variables and does not log their values. This does not require creating a custom OAuth client. See [CDSE OData API documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html) and [CDSE token authentication documentation](https://documentation.dataspace.copernicus.eu/APIs/Token.html).

## 2. Enclosure boundary and context imagery

No reliable Pallimangal enclosure geometry was established. The provenance manifest records a null geometry and exact missing inputs. OSM name searches did not return a corresponding feature. Secondary news reporting locates Pallimangal in Sujatpur mouza near Beel Kedaria and describes a south-side breach, but provides no georeferenced boundary. January 14 is inferred from reports published January 15–17 describing a Wednesday incident; it is not an official timestamp.

A real Sentinel‑2B L2A scene from 2026‑01‑13 was retrieved via Microsoft Planetary Computer. A 10 m true-colour crop covers the analyst-selected broad locality window (about 15.6 × 16.9 km), not a target polygon. It contains many pond-like and agricultural-looking parcels; none can be attributed to Pallimangal without a verified point or parcel ID. This is context imagery only, not a classification. The Clark Labs 2022 aquaculture layer is historical regional context and is explicitly not an exact 2026 gher boundary. No cropland or permanent-water geometry was inferred.

**Required to delineate:** a GPS point or cadastral/official fisheries ID, a locally reviewed boundary on dated imagery or official polygon, and field confirmation separating enclosure, permanent water, neighboring ponds, and fields.

## 3. Supervised benchmark recovered and audited

The selected reproducible baseline is the official Cloud to Street Sen1Floods11 v1.1 hand-labelled Sentinel‑1 subset. 446 paired S1Hand/LabelHand chips, all four published split lists, and the event metadata were retrieved. The official S1Hand inputs have two VV/VH dB bands; labels are `-1` no-data, `0` non-water, `1` water. All 446 pairs were opened and checked for dimensions, CRS, alignment, label codes and event-polygon assignment. Six chips have no usable labeled pixels. The remaining usable mask contains 100,821,804 pixels (10,644,793 water; 90,177,011 non-water); 15,932,910 pixels are label no-data. All chip footprints overlap a single official event polygon with at least 100% of chip footprint area by the validation method.

The official random chip validation/test lists share the same event groups as training, so they are not used as independent event tests. Instead, event ID 11 (41 usable chips) from the official train pool was withheld as validation; the 210 remaining usable official-train chips were used for fitting. The separate 15-chip Bolivia group was held out as the test event and not used for selection. This is an actual completed training run; metrics and confusion matrices are in the training report and evaluation manifest.

### Licensing

Official Sen1Floods11 v1.1 source collection metadata declares the hand imagery and labels `proprietary`; the GitHub README does not provide a clear permissive dataset license. Data are retained locally for this requested research run. Do not redistribute the imagery, labels, or derived checkpoint without written permission from Cloud to Street. Ask the data owner for written terms before any public or commercial deployment. The separate SSL4EO/TorchGeo Sentinel‑1 encoder weights are CC‑BY‑4.0, but were retrieved after the completed scratch training run and are **not** the weights used in this model.

## 4. Event reconstruction result

| Requirement | Actual result |
|---|---|
| Same-orbit pre/post S1 VV/VH files | Catalogue only; 0/4 downloaded |
| Verified local S1 CRS/resolution/nodata/coverage | Not available |
| Exact enclosure boundary | Not available |
| Independent local water/cropland/permanent-water references | Not available |
| Pre/post local model masks or probabilities | Not generated |
| New-water hectares/bighas | Not calculated |
| Embankment-failure diagnosis | Not made |

The generic benchmark model must not be used to imply January event conditions. Spatial adjacency alone would not establish a breach even if imagery became available. A future analysis needs validated local radiometry/geometry, a defensible enclosure and land-cover reference, permanent-water exclusion, uncertainty reporting, and field corroboration.

## Reproduction and source records

- Event asset recovery: `py scripts/gherproof/recover_event_imagery.py` (after setting local CDSE variables).
- Public pre-event optical context: `py scripts/gherproof/recover_pre_event_sentinel2.py`.
- Dataset preparation and checks: `py scripts/gherproof/prepare_sen1floods11.py`; `py scripts/gherproof/validate_sen1floods11.py`.
- Training: `py scripts/gherproof/train_sen1floods11.py --epochs 15 --patience 4 --patch 256 --batch-size 4 --seed 42`.
- Independent metrics: `py scripts/gherproof/evaluate_sen1floods11_checkpoint.py`.
- Machine-readable records: `data/gherproof/manifests/event_imagery_manifest.json`, `enclosure_boundary_provenance.json`, `sen1floods11_download_manifest.json`, `sen1floods11_qc_manifest.json`, `sen1floods11_training_results.json`, and `sen1floods11_independent_evaluation.json`.

### Sources

- [CDSE OData API](https://documentation.dataspace.copernicus.eu/APIs/OData.html) and [CDSE token authentication](https://documentation.dataspace.copernicus.eu/APIs/Token.html).
- [Official Sen1Floods11 repository](https://github.com/cloudtostreet/Sen1Floods11) and its [v1.1 imagery collection metadata](https://storage.googleapis.com/sen1floods11/v1.1/catalog/sen1floods11_hand_labeled_source/collection.json) / [label collection metadata](https://storage.googleapis.com/sen1floods11/v1.1/catalog/sen1floods11_hand_labeled_label/collection.json).
- [TorchGeo Sentinel‑1 pretrained model](https://huggingface.co/torchgeo/resnet50_sentinel1_all_moco) and [SSL4EO‑S12 source](https://github.com/zhu-xlab/SSL4EO-S12).
- [Samakal report](https://samakal.com/whole-country/article/334020/%E0%A6%AA%E0%A6%BE%E0%A7%9C-%E0%A6%AD%E0%A7%99%E0%A6%99%E0%A7%87-%E0%A6%A2%E0%A7%81%E0%A6%95%E0%A6%B2-%E0%A6%AA%E0%A6%BE%E0%A6%A8%E0%A6%BF-%E0%A7%A7%E0%A7%AB%E0%A7%AE-%E0%A6%B9%E0%A7%87%E0%A6%95%E0%A7%8D%E0%A6%9F%E0%A7%87%E0%A6%B0-%E0%A6%9C%E0%A6%AE%E0%A6%BF%E0%A6%B0-%E0%A6%95%E0%A7%8D%E0%A6%B7%E0%A6%A4%E0%A6%BF), [Dhaka Post](https://www.dhakapost.com/country/424238), and [Daily Country Today](https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded%2C-over-500-families-homeless-in-jashore).
