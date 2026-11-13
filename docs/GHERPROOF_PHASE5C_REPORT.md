# GherProof Phase 5C — Official DLRS cadastral recovery and remote geolocation

**Review date:** 2026-11-12
**Official map status:** `official_map_requires_purchase`
**Site status:** `site_unresolved`
**Boundary status:** `not_delineated`
**Experimental inference:** NOT READY

## Executive result

The official DLRS map portal's public location and catalogue APIs resolve the requested jurisdiction to Khulna Division → Jashore District → Manirampur Upazila → Sujatpur mouza, J.L. 143. For this exact mouza, the survey-type endpoint returned **CS and RS only**. Search returned **four digitized records marked AVAILABLE**: CS sheets 1 and 2, and RS sheets 1 and 2. No SA, BRS or BDS record was returned for this mouza. This upgrades J.L. 143 from a secondary listing to an official catalogue-confirmed association. The printed title block on a full original sheet has not been inspected because the full-resolution maps require purchase.

The portal lists **BDT 500 per map record**, BDT 70 delivery and BDT 20 court fee. The public result does not specify whether delivery/court fees are per order or per sheet; no total is inferred. Portal registration requires personal account details and verification; no account, cart, order or payment was initiated. The four publicly served preview thumbnails were downloaded and visually inspected, but their small 227 × 320 pixel size is insufficient for reliable reading of plot numbers, scale, date or legend. They must not be georeferenced or used for parcel tracing.

An independent 2014 USS/Oxfam *Beel Bakar Study* map provides regional orientation. Its schematic Figure 2 labels Sujatpur, Moshihati, Bhaba Daha, Kultia Union, Mukteswari River, roads and sluice/bridge symbols. The associated report places Beel Bakar mostly north of Moshihati Bazar and south of the Manirampur–Abhaynagar road. The figure has no CRS, coordinate grid, scale or surveyed boundary, and it does not identify Pallimangal. Recent incident reporting's Beel Kedaria/Bhavadah wording cannot be assumed to mean the same mapped feature as Beel Bakar. Thus the historic map adds a **locality context**, not a geospatial candidate or boundary.

No original cadastral map, georeferenced raster, boundary or candidate polygon was created. The existing Jan 7/19 Sentinel-1 common-valid coverage remains 463,292 pixels / 46.3292 km² / 18.1274% of the broad provisional search window only. Target-enclosure coverage remains unknown. The result is **`official_map_requires_purchase` + `site_unresolved`**; inference and affected-area analysis remain blocked.

## Official DLRS catalogue results

| Survey | Sheet | Catalogue status | Digitized | Listed map price | Delivery | Court fee | Public preview |
|---|---:|---|---|---:|---:|---:|---|
| CS | 1 | AVAILABLE | Yes | BDT 500 | BDT 70 | BDT 20 | Downloaded; not original |
| CS | 2 | AVAILABLE | Yes | BDT 500 | BDT 70 | BDT 20 | Downloaded; not original |
| RS | 1 | AVAILABLE | Yes | BDT 500 | BDT 70 | BDT 20 | Downloaded; not original |
| RS | 2 | AVAILABLE | Yes | BDT 500 | BDT 70 | BDT 20 | Downloaded; not original |
| SA | — | Not returned for this mouza | — | — | — | — | — |
| BRS | — | Not returned for this mouza | — | — | — | — | — |
| BDS | — | Not returned for this mouza | — | — | — | — | — |

The location API returned Sujatpur with J.L. 143 under the selected Manirampur jurisdiction; catalogue records repeat the same mouza and J.L. metadata. The portal as a whole advertises CS, SA, RS, BRS and BDS survey families, but the location-specific survey list returned only CS and RS. An empty response for another survey type means “not listed in this query,” not proof that no paper map exists in other offices or archives.

The DLRS portal describes a search → payment → digital download/printed delivery process and a scan request for maps that are not digitized. These target records are digitized and available, so a scan request is not indicated by the catalogue. Full map purchase would be required to inspect printed title blocks, survey dates, scales, legends and complete plot numbering. No registration or payment step was taken.

The four thumbnails and exact record IDs, fees, preview URLs, byte counts and SHA-256 hashes are recorded in `data/gherproof/manifests/phase5c_official_map_search.json` and preserved under `data/gherproof/reference/dlrs_portal_previews/`.

![DLRS low-resolution preview thumbnails](../data/gherproof/review/phase5/pallimangal_dlrs_preview_montage.png)

## J.L. 143 and original sheet verification

**Official catalogue finding:** Sujatpur J.L. 143 is confirmed in the public DLRS catalogue under Khulna / Jashore / Manirampur. This is authoritative catalogue metadata and supersedes the earlier secondary-only status. The CS and RS map result records independently carry the same mouza and J.L. fields.

**Still pending:** Visual confirmation from the original printed map title block, plus the full survey edition/date, scale, legend, sheet edges and plot IDs. The catalogue search is strong confirmation of the portal record, but not inspection of a cadastral sheet. Do not use it to assert plot ownership or that a particular plot belongs to Pallimangal.

## Remote locality evidence: Beel Bakar context

The 2014 report by Ulashi Sreejony Sangha (USS) and Oxfam labels its Figure 2 as “Beel Bakar covering the surrounding area of Mukteswari River.” The diagram labels Sujatpur on the southern/eastern side of its drawn beel context, near Moshihati and Bhaba Daha; it also depicts the river, roads, a bridge and sluice symbols. The same report's prose describes Beel Bakar as spanning Kultia and Haridaskati unions and crossing the Manirampur–Abhaynagar administrative context.

This helps orient a reviewer to a wider landscape around the reported Sujatpur locality. The figure is not a cadastral or engineering map: no coordinate grid, scale, CRS, source survey, date of field mapping or positional accuracy is supplied. Its drawn Beel Bakar fill cannot be treated as an exact beel boundary. It is not evidence that Beel Bakar and the incident reports' Beel Kedaria are identical, and it does not label Pallimangal, an enclosure parcel, or the January 2026 failure. The remote review therefore **does not identify a candidate site**.

![Historical schematic locality map from the 2014 Beel Bakar Study](../data/gherproof/reference/historical/beel_bakar_map_figure2_context.png)

## Georeferencing and satellite coverage

| Requirement | Result |
|---|---|
| Original CS/RS map available locally | No; only public 227 × 320 previews |
| Printed J.L., survey date, scale, plot labels legible | No; thumbnail resolution is inadequate |
| Map CRS / datum | Not returned / unknown |
| Georeferencing | Not attempted |
| Control points / transformation / RMS | None; not applicable |
| Georeferenced overlay with Sentinel-2/Sentinel-1 | Not made |
| Candidate mouza/beel/farm/khal/embankment geometry | None created |
| Sentinel-1 candidate enclosure coverage | Not evaluated; no independently supported target geometry |

The 2014 schematic was not aligned to the S2 or S1 raster. Existing common-valid support and its 18.1274% broad-window fraction are unchanged and must not be represented as target coverage. Since the location itself remains unresolved, no additional acquisition was selected; scene selection should follow, not determine, the target geometry.

## QGIS review package

The existing GeoPackage retains its two EPSG:32645 feature layers unchanged:

- `provisional_search_window`: broad raster window, not a mouza/site boundary.
- `common_valid_footprint`: actual Jan 7/19 common-valid S1 support, not water/flood extent.

Two non-spatial attribute tables were added:

- `phase5c_dlrs_records`: four official catalogue records, prices and preview paths.
- `phase5c_historical_context`: provenance and limitations of the 2014 schematic.

No point, polygon, line, or geospatial transform was added for Sujatpur, Beel Bakar/Kedaria, Pallimangal, the southern khal or embankment. See `data/gherproof/review/phase5/README.md` for loading the preserved rasters and the historical/preview context separately.

The Phase 5C review poster places the old diagram and current satellite context in separate panels and states that they are not spatially aligned:

![Phase 5C review map](../data/gherproof/review/phase5/pallimangal_phase5c_review_map.png)

## Decision and remaining blockers

**Official map classification:** `official_map_requires_purchase`
**Candidate site classification:** `site_unresolved`

Before even experimental event inference, obtain the original CS/RS map sheet(s) through an authorized purchase or other lawful official release; verify the printed title block and relevant sheet coverage; identify the Pallimangal plot(s) with a trustworthy operator/agency source; georeference only with documented controls; distinguish the fish enclosure from adjacent ponds, Beel Bakar/Kedaria, canals and agricultural parcels; obtain human review; then compute target and buffer validity against the preserved S1 mask. An original cadastral parcel boundary alone does not prove that a lease/operator farm uses that parcel.

Until those steps are satisfied, no ML inference, water/flood map, breach localization or area calculation is justified. See also [remote geolocation evidence](GHERPROOF_REMOTE_GEOLOCATION_EVIDENCE.md) and [updated coverage assessment](GHERPROOF_COVERAGE_ASSESSMENT.md).

## Reproduction

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5c_review_package.py
```

The local builder rebuilds the preview montage/review poster, idempotently adds non-spatial catalogue/context tables to the GeoPackage, validates the existing feature layers and SQLite integrity, and asserts four catalogue rows and one historical context record. It does not contact DLRS, make a purchase, or add coordinates.
