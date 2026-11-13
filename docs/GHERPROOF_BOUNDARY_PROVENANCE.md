# GherProof Pallimangal boundary provenance and review workflow

## Current geographic evidence

**Status: `not_delineated`; geometry is null.** No enclosure polygon is committed or inferred. The place-name searches and OpenStreetMap query in the provenance record produced no unique Pallimangal feature. The reviewed secondary news accounts describe a farm in Sujatpur mouza near Beel Kedaria and a south-side embankment failure, but they do not provide coordinates or a parcel polygon. January 14 is a date inference from reporting, not a georeferenced observation.

The available Sentinel‑2B L2A visual crop was acquired 2026‑01‑13 at 10 m in EPSG:32645 and spans a broad analyst-selected locality box. Its extent contains numerous pond-like and agricultural-looking parcels; appearance alone cannot identify Pallimangal. Clark Labs' 2022 Bangladesh aquaculture class is historical context, not the exact January 2026 farm boundary. No cropland, permanent-water or neighboring-pond polygons are currently asserted.

## Implemented reviewer workflow

The GherProof case page now includes a Leaflet map that overlays the available context crop on OpenStreetMap. Users can add polygon vertices, edit the displayed latitude/longitude pairs, clear/reload the shape, enter evidence, reviewer, review date, confidence, and save a GeoJSON version. Styling differentiates candidate (orange dashed), under-review (amber dashed), and verified (green solid) states. A warning states that the broad crop is not an enclosure boundary.

API operations:

- `GET /api/gherproof/boundary` — status, current feature, provenance and context extent; defaults to `not_delineated` without creating a fake feature.
- `PUT /api/gherproof/boundary` — validate and persist a GeoJSON polygon and its evidence/review metadata.
- `GET /api/gherproof/context/sentinel2` — serve only the already-downloaded context PNG.

Allowed progression is `not_delineated → candidate → under_review → verified`. A candidate requires at least one evidence item and confidence. Review states require a named reviewer and ISO-8601 review timestamp. Verification additionally requires that the current version already be under review; skipping review is rejected. Invalid/self-intersecting geometries, missing evidence, invalid timestamps, and invalid coordinate ranges are rejected. Each saved geometry is stored in `data/gherproof/boundaries/versions/` and the active version is stored in `pallimangal_enclosure.geojson`; `data/gherproof/manifests/boundary_provenance.json` records the version path, evidence, reviewer and status.

The application does not currently authenticate reviewer identity; the reviewer field is an auditable user-entered attribution, not a cryptographically verified identity. A locally saved polygon is human-delineated and must not be called authoritative unless its source evidence is authoritative. `verified` records completion of the stated review workflow, not ground survey truth.

## Feature separation and area gate

The enclosure, agriculture, permanent water, other aquaculture, and any new-inundation mask remain separate thematic layers. Only enclosure boundary editing is implemented now. Area/inference processing remains disabled until actual calibrated pre/post images, an evaluated segmentation model, a reviewed boundary, and suitable reference layers are present. Candidate/under-review geometry must never be treated as verified in area calculations.

## Source/licence notes

- CDSE Sentinel products are made available under the Copernicus Sentinel free/full/open data terms; attribute source as Copernicus Sentinel data and follow the [CDSE terms](https://dataspace.copernicus.eu/terms-and-conditions).
- Clark Labs states its aquaculture maps are CC BY 4.0 and for non-commercial use only; other applications require permission. See the [official data page](https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/). The layer remains historical contextual material.
- OpenStreetMap base map requires attribution to OpenStreetMap contributors and is subject to ODbL; no OSM feature is currently used as the farm boundary.
- Sen1Floods11 source catalogues declare the imagery/label collections proprietary; no dataset/checkpoint redistribution is authorized by this report pending written clarification.
- SSL4EO/TorchGeo encoder weights are CC BY 4.0; preserve attribution and source/hash records.

## Phase 5 geographic evidence update (2026-11-12)

The administrative record is supported by the official Bangladesh DPHE geographic-code table: Jessore 41 / Manirampur 61 / Kultia 473 / Sujatpur 368 (PDF p.72), and an official Kultia Union Parishad representative address listing Sujatpur. Samakal adds the textual setting “Sujatpur mouza in Beel Kedaria” and a south-side breach beside an adjacent khal; Dhaka Post and Daily Country Today independently corroborate the named farm/event and affected-village context. This improves toponymic identification (moderate confidence) but supplies no coordinates, plot ID or parcel geometry. The LGED Manirampur map adds roads, embankments, khals and water bodies at upazila scale; the map itself disclaims authority outside LGED, and it does not identify Pallimangal. The official Ministry of Land portal describes georeferenced mouza/plot sheets, but a specific Sujatpur sheet/plot was not acquired. See [site evidence](GHERPROOF_SITE_LOCATION_EVIDENCE.md).

The January 13, 2026 Sentinel-2 visual image was inspected; the broad crop contains many pond-like and field-like features. No individual parcel is assigned to Pallimangal. The saved review package is `data/gherproof/review/phase5/`: its GeoPackage contains only a provisional raster search-window layer and actual S1 common-valid support footprint. The high-resolution map deliberately has no site marker or enclosure outline. Roads, canals, administrative boundaries, named water bodies, candidate boundary and target cropland/permanent-water polygons were not extracted as georeferenced GIS in Phase 5; the available LGED map is a PDF context reference, not a supplied vector layer.

Status remains **`not_delineated`** and geometry remains null. No candidate has been created, so no status transition was attempted. `data/gherproof/manifests/phase5_boundary_candidates.json` records zero candidates and the precise missing evidence. Enclosure coverage and buffer coverage are **not evaluated**, not zero; the measured 46.3292 km² / 18.1274% applies only to the broad Phase 4B provisional raster search window. Refer to `docs/GHERPROOF_COVERAGE_ASSESSMENT.md`.

The official [Jessore Settlement Office village/mouza map index](https://www.zsojessore.gov.bd/maps.html) is a promising next source; the specific Sujatpur sheet was not acquired. Obtain a georeferenced cadastral sheet/JL number and plot reference or a field GPS point before local imagery digitization. The review package build is reproducible with `backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5_review_package.py`.
