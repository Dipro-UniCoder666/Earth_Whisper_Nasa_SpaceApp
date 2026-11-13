# GherProof Phase 5B — Sujatpur cadastral recovery and Pallimangal geolocation

**Review date:** 2026-11-12
**Outcome:** PARTIAL — J.L. 143 is provisionally corroborated by a secondary Manirampur mouza listing; no authoritative Sujatpur cadastral sheet or Pallimangal geometry was recovered.
**Boundary status:** `not_delineated`
**Experimental inference readiness:** NO — target location and target coverage remain unknown.

## Executive finding

The new lead is useful: the Manirampur mouza listing identifies Sujatapur (Sujatpur) as J.L. 143, immediately after Hat Gachha J.L. 142 and before Kultia J.L. 144. The listing explicitly covers Manirampur, and the administrative village chain is separately supported by the DPHE Jessore / Manirampur / Kultia / Sujatpur code entry. This makes J.L. 143 a credible cadastral-search identifier for the intended Sujatpur, and distinguishes it from other Sujatpur/Sujatapur mouzas elsewhere. However, the listing is secondary, not an official survey record. We did not find a primary document or actual sheet that confirms this target's J.L. number. Status is therefore **provisionally corroborated, not officially verified**.

The Ministry of Land's map portal describes digitization and georeferencing of mouza sheets and exposes selectors for administrative area, mouza, sheet and plot. Publicly accessible page content did not confirm that Manirampur → Kultia → Sujatpur is currently selectable, nor return a sheet, plot layer, download, survey type or land-use record for this mouza. The official Jessore Settlement Office map index advertises village/mouza maps and includes a Manirampur selector, but its accessible page exposed no Sujatpur map file. The official ePorcha/Digital Record Room could not be inspected for Sujatpur sheet availability in this run; no claim is made that records are absent from the service. No cadastral image or PDF was downloaded, so georeferencing, control-point residuals and cadastral interpretation were not possible.

Consequently, Beel Kedaria and the distinct Pallimangal enclosure remain textually associated with Sujatpur mouza but are not geographically delineated. The south-side khal/embankment are still only incident-report descriptors; neither feature was matched to a georeferenced line or parcel. We did not create a candidate point or polygon. The Phase 4B Sentinel-1 common-valid support remains 463,292 pixels / 46.3292 km² / 18.1274% of the broad provisional raster window. **Coverage at Pallimangal is unknown**, not zero. Do not run event inference or calculate impact areas.

## Findings by question

| Question | Result | Evidence level / limitation |
|---|---|---|
| Is the lead for the intended Sujatpur? | Likely: the Manirampur listing gives Sujatapur, J.L. 143, with neighboring Hat Gachha 142 and Kultia 144; DPHE independently puts Sujatpur in Kultia, Manirampur, Jessore. | Strong secondary corroboration plus independent official administrative chain. No primary cadastral confirmation. |
| Is J.L. 143 officially verified? | **No. Provisionally corroborated only.** | The listing is not the survey authority's record. Request the J.L. number printed on the official sheet / mouza index and verify the administrative circle. |
| Was an official cadastral sheet recovered? | **No.** | No CS/SA/RS/BS/BRS sheet, map scan, plot schedule, or geospatial download was returned or locally present in the reviewed Phase 5 package. |
| Which survey edition is available? | None recovered. | CS/SA/RS/BS/BRS status unknown; no map vintage or publication date can be assigned. |
| Did georeferencing succeed? | Not attempted. | No source raster/PDF and no map control points; RMS/residual error is not applicable. |
| Was Beel Kedaria located spatially? | No. | News reporting associates it with the site context, but no georeferenced beel polygon or uniquely identifiable map annotation was recovered. |
| Was Pallimangal separated from nearby ponds? | No. | Jan 13 Sentinel-2 shows multiple pond-like parcels; no named feature, parcel, operator sketch, or reviewer point ties one to Pallimangal. |
| Were the southern khal and embankment located? | No. | Reported as adjacent to the south side in news; no site geometry to compare with map, S2 or hydrography. |
| Actual Jan S1 coverage on the enclosure? | **Unknown / not evaluated.** | No credible point or boundary. The broad-window percentage cannot be substituted for site coverage. |
| Are more satellite acquisitions required? | Cannot determine until the site is located. | After a point/polygon arrives, test actual footprint and per-pixel validity for Jan 7/19; search additional dates/orbits only if that check shows insufficient support. |
| Is experimental inference ready? | **No.** | Site position, target outline, target coverage, land-cover context and independent local reference are missing. |

## Source investigation

| Source | What was confirmed | What remains unavailable |
|---|---|---|
| [Ministry of Land digital land zoning portal](https://map.land.gov.bd/) | Official portal says mouza map sheets are being digitized/georeferenced and presents division, district, upazila, mouza, sheet and plot controls. | Static/search-indexed content did not expose a selected Manirampur/Kultia/Sujatpur record. No sheet/image/vector or plot output downloaded. This does **not** establish that the portal lacks the record. |
| [Jessore Settlement Office village map index](https://zsojessore.gov.bd/maps.html) | Official Zonal Settlement Office page exposes “Village MAPs — Mouza maps”, a Manirampur selector, and a mouza-map route. | Accessible page content had no named Sujatpur sheet or direct download. The historic index appearance/page accessibility is not proof of data absence. |
| [Digital Record Room / ePorcha](https://eporcha.gov.bd/) | Investigated as the official record-room route. | Public page could not be inspected through the available research access in this run; Sujatpur availability and survey types remain undetermined. No transaction or purchase initiated. |
| [Manirampur mouza listing, Dolil Sheba](https://dolilsheba.com/mouza/land-office/152) | Search result and page list Sujatapur / Sujatpur, J.L. 143; Hat Gachha 142 and Kultia 144 appear adjacent in the same Manirampur list. | Third-party discovery listing; it is not a cadastral sheet, survey index certified by DLRS, nor proof of current map availability. |
| [DPHE geographic code record](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf) | Jessore 41 / Manirampur 61 / Kultia 473 / Sujatpur 368. | Official administrative codes do not state a J.L. number, plot or coordinate. |
| [Manirampur official portal](https://manirampur.jessore.gov.bd/) and [Kultia Union Parishad](https://kultiaup.jessore.gov.bd/pages/leaders) | Local administrative context and Sujatpur village references. | No Pallimangal boundary or cadastral sheet found. |
| [LGED Monirampur upazila map](https://oldweb.lged.gov.bd/UploadedDocument/Map/KHULNA/jessore/monirampur/monirampur.pdf) | Regional context includes union/transport/hydrographic themes. | Scale and stated disclaimer make it contextual, not parcel-authoritative; no Sujatpur cadastral sheet or target feature was extracted. |
| [MowjaBD](https://mowjabd.vercel.app/) | Third-party interface describes public DLRMS map search and a public map-file library. | Not a government authority; no Sujatpur map file was identified or downloaded. No downloaded file is represented as original cadastral evidence. |

Searches also returned other Sujatpur/Sujatapur mouzas in Noakhali, Sunamganj and elsewhere with different J.L. numbers. Those are explicitly excluded from this case. A separate result containing “J.L. 143” for another mouza is not evidence against or for Manirampur's number: J.L. identifiers are scoped to survey jurisdiction, and name/number alone must be verified against the intended Manirampur sheet.

## GIS review package and map

The existing EPSG:32645 GeoPackage is retained. Its two geometry layers remain exactly the broad provisional search-window outline and measured Jan 7/19 common-valid footprint. A non-spatial `phase5b_cadastral_status` attribute table has been added to the GeoPackage to make the source search outcome visible in QGIS without introducing a false map location. The updated high-resolution review map adds a clear status note but no point, mouza boundary, beel outline, enclosure polygon, khal or breach marker.

No original cadastral map or georeferenced derivative exists to include. The current QGIS review package is therefore the best supportable package for requesting local identification: the existing S2 context and S1 masks can be loaded alongside the broad window, with no location claim. See `data/gherproof/review/phase5/README.md` and `data/gherproof/manifests/phase5b_cadastral_search.json`.

![Phase 5B review map — no target position asserted](../data/gherproof/review/phase5/pallimangal_phase5b_review_map.png)

## Exact document request for the local land office

Request from **Manirampur Upazila Land Office / Assistant Commissioner (Land), the relevant union land office, and Jessore Zonal Settlement Office / DLRS**:

1. Official mouza name in Bangla and English, administrative circle, and confirmed J.L. number for **Sujatpur/Sujatapur under Kultia Union, Manirampur Upazila, Jashore District**.
2. Full-sheet, legible digital copy of all available cadastral map sheets covering that mouza: CS, SA, RS and BS/BRS (or the locally applicable latest survey), with sheet numbers, adjacent-sheet index, scale, north arrow, legend, survey/settlement dates, publication/revision date and record status.
3. Georeferenced original/digital map if available; otherwise original-resolution scan (not a screenshot), scan resolution, sheet dimensions and any graticule/control-point or georeferencing metadata, stated CRS/datum and transformation details.
4. Mouza boundary and adjacent mouza labels; plot/dag boundaries and identifiers; plot index or schedule for any operator-provided plot number; map-to-khatian linkage where releasable.
5. Permission/terms for research use, redistribution, attribution, and whether the supplied raster/vector is certified or informational.
6. If the office cannot locate it, written confirmation of the correct mouza spelling, J.L. number, survey version, sheet index and custodial office to contact next.

Separately request the local fisheries committee/operator or union representative to identify the Pallimangal farm on the sheet, provide plot/dag IDs or a signed/sketched outline, and identify the reported south-side khal/embankment. Request a field GPS point or track with horizontal accuracy and collection time. A cadastral map alone may not show the commercial enclosure name or current operational boundary.

## Reproduction and validation

Rebuild the annotated map and GeoPackage status table:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5b_review_package.py
```

The build checks the source map exists, saves the Phase 5 map unchanged, verifies GeoPackage SQLite integrity and required geometry layers, adds a non-spatial status table only if absent, and verifies the output image dimensions. No network data are needed. No raster coverage calculation is performed because the target has no geometry.

## Final decision

**Conditional GO for obtaining authoritative cadastral material and local field identification. NO-GO for Pallimangal experimental inference, breach localization, water/flood mapping or area measurement at this stage.** J.L. 143 is a good request/search key, not a verified cadastral fact. When a sheet or GPS reference arrives, verify it against the official administrative chain, georeference only from documented controls, obtain independent human review, then recompute January S1 coverage against the supported candidate geometry.
