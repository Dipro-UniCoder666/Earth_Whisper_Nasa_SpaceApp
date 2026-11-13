# GherProof Phase 5C — Cadastral map provenance register (includes Phase 5B history)

**Case:** `GHERPROOF-SUJATPUR-2026-01`
**Assessment date:** 2026-11-12
**Requested mouza:** Sujatpur / Sujatapur, Kultia Union, Manirampur, Jashore
**J.L. catalogue reference:** 143 — confirmed in the official DLRS catalogue; printed title block not inspected
**Recovered cadastral original:** none; four low-resolution catalogue thumbnails inspected
**Georeferencing:** not performed; no source map or control points
**Boundary status:** `not_delineated`

> **Phase 5C supersedes the Phase 5B availability and J.L. verification statements below.** The official DLRS catalogue now confirms J.L. 143 and lists two CS and two RS sheets as available/digitized; originals are purchase-gated and were not downloaded.

> **Phase 5D update:** A free-source search found one third-party listing for a BS/RS J.L. 143 sheet 1. Only its public product thumbnail was retained; the product page displayed a fee. Its content was compared with the four DLRS previews, but no match was confirmed. No full map copy, georeference, candidate geometry or target coverage result was produced. See `docs/GHERPROOF_PHASE5D_REPORT.md` and `data/gherproof/manifests/phase5d_free_source_search.json`.

## Provenance table

| Record | Source / owner | Observed information | Evidentiary classification | File handling / result |
|---|---|---|---|---|
| Manirampur mouza list | [Dolil Sheba](https://dolilsheba.com/mouza/land-office/152), third-party land information | Sujatapur/Sujatpur J.L. 143, between Hat Gachha 142 and Kultia 144 in the Manirampur list | Secondary discovery lead only; internally consistent with locality context but not authoritative map proof | No source map file. Captured as URL and description in `phase5b_cadastral_search.json`. |
| Administrative village code | [Bangladesh DPHE](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf), p.72 | Jessore 41 / Manirampur 61 / Kultia 473 / Sujatpur 368 | Official administrative corroboration; does not establish survey J.L., parcel or geometry | Existing source is referenced in site evidence; no new copy made. |
| Digital land zoning / map portal | [Ministry of Land](https://map.land.gov.bd/) | Portal describes mouza sheets being digitized/georeferenced and provides administrative/mouza/sheet/plot controls | Official source describing service and workflow; this run could not confirm target mouza availability | No selected record, map, download URL or output file exposed in the accessible public page content. This is an access/verification limitation, not proof of non-availability. |
| Jessore settlement map index | [Zonal Settlement Office, Jessore](https://zsojessore.gov.bd/maps.html) | Official page includes a Manirampur selector and “Village MAPs / Mouza maps” section | Official map index; page is relevant but no named Sujatpur sheet was accessible | No original file or map record recovered. |
| Digital Record Room | [ePorcha](https://eporcha.gov.bd/) | Official record-room route investigated | Availability not determined | The service page could not be inspected through this run's web access; no Sujatpur survey sheet availability is asserted. No purchase or transaction. |
| Regional context map | [LGED Monirampur map](https://oldweb.lged.gov.bd/UploadedDocument/Map/KHULNA/jessore/monirampur/monirampur.pdf) | Upazila-scale administrative, transport and water-feature context | Context only; disclaimer and scale do not support cadastral boundaries | Previously reviewed PDF, not treated as a Sujatpur sheet and not georeferenced. |

## Search result

No official cadastral sheet, cadastral index entry, survey edition, map scale, plot/dag schedule, georeferenced raster/vector, CRS, datum, map control point or map publication date was recovered in Phase 5B. No cadastral file has been added under `data/gherproof/reference/` or `data/gherproof/raw/`; no empty placeholder is presented as a map. No survey type (CS, SA, RS, BS/BRS) is confirmed available. The answer to “was the official sheet recovered?” is **no**. The reason is that the available official portal pages were informational/index pages, not an accessible target-sheet response during this review; ePorcha could not be inspected. Do not infer nonexistence of a sheet or service record from this unsuccessful retrieval.

## J.L. number determination

The secondary list's ordering and explicit jurisdiction make J.L. 143 a useful and plausible identifier. DPHE independently confirms the administrative village chain, while the land list independently associates the Manirampur mouza spelling with 143. Neither is a primary land-survey document. Thus:

- Use **“candidate J.L. 143”** when requesting the sheet.
- Do not use **“verified J.L. 143”** in project metadata, a map label or legal/parcel interpretation.
- Verify against the J.L. printed on the official sheet or DLRS index and have the local land office confirm the administrative circle and spelling.
- Do not transfer J.L. values from other Sujatpur names or other survey jurisdictions.

## Georeferencing decision

No georeferencing was attempted because there was no map image/PDF. Accordingly, no control points, transformation, residuals or RMS error exist. The local imagery, broad raster crop, news descriptions, and search-window coordinates are not substitutes for cadastral control. A future georeference should preserve the source scan, document each control point and its source, use a locally compatible datum/CRS (EPSG:32645 may be used only after confirming datum/control compatibility), report independent check-point residuals and transformation/RMS, and label image-derived alignment as approximate if authoritative survey controls are absent.

## Request and chain of custody

The exact source request and required map metadata are in `docs/GHERPROOF_PHASE5B_REPORT.md`, “Exact document request for the local land office.” No map was purchased, no account was created, and no land transaction was initiated. On receipt, preserve the supplied file byte-for-byte under a dated raw/source directory, record filename, source office/contact, receipt time, license/permission, byte size and SHA-256, then create only derived copies in the processed/reference area. Keep official and third-party maps as separate sources; never overwrite the original scan.

Machine-readable search log: `data/gherproof/manifests/phase5b_cadastral_search.json`.

## Phase 5C official DLRS catalogue update (2026-11-12)

The Phase 5B statement that no authoritative catalogue record had been confirmed is superseded by a read-only query of the official DLRS Integrated Online Map Purchase System. With Division **খুলনা**, District **যশোর**, Upazila **মনিরামপুর**, Mouza **সুজাতপুর**, the location API returned J.L. **১৪৩**. The survey-type endpoint for this exact mouza returned only **আর.এস (RS)** and **সি.এস (CS)**. Catalogue search returned two digitized, `AVAILABLE` records per edition: sheets 1 and 2 for CS, and sheets 1 and 2 for RS. No SA, BRS or BDS record was returned for this mouza. These are exact current catalogue outcomes; they do not establish that no other paper record exists outside this portal.

The DLRS catalogue thus confirms the Sujatpur/J.L. 143 association at the official catalogue level, strengthening and superseding the former secondary-only lead. The requested original-sheet title-block inspection is still incomplete: each result's full map requires purchase. The public thumbnails were downloaded to `data/gherproof/reference/dlrs_portal_previews/` and visually reviewed. They show two cadastral sheet layouts per survey edition but are low-resolution previews; their plotted text, scale, survey date, legend and plot numbers are not reliably legible. Do not use them for parcel delineation or georeferencing.

The DLRS portal labels each sheet `AVAILABLE` and `isDigitized=true`; each record lists Tk 500 map price, Tk 70 delivery fee and Tk 20 court fee. The exact per-order/per-sheet application of delivery and court charges is not stated in the public response, so no total is calculated. The portal advertises account registration and payment for instant digital download or printed courier delivery, plus a scan-request route when a map is not digitized. Since these sheets are digitized and available, a scan request appears unnecessary. No account, cart, order or payment was initiated. The user would need to authorize purchase before a full map can be obtained.

**Georeferencing remains not attempted.** The full sheets are not local, the previews are insufficient resolution, and no usable map control data were returned. No CRS, scale, map date, control points, transformation, residual or RMS is claimed. No candidate parcel, Beel Kedaria boundary, Pallimangal boundary, southern khal, embankment, or breach location was generated.

### Historical locality map provenance

The source `data/gherproof/reference/historical/Beel_Bakar_Study_2014_source.pdf` is *Beel Bakar Study*, published March 2014 by Ulashi Sreejony Sangha (USS) with Oxfam. Figure 2 (printed page 3) was cropped to `beel_bakar_map_figure2_context.png`; original PDF SHA-256 is `04311a58e51671a4b933a53e8875ab94f521749789c0d07299bcc766651de2ae`. Figure 2 labels the broad Beel Bakar area, Mukteswari River, Sujatpur, Moshihati, Bhaba Daha, roads, bridges, sluice symbols, and Kultia Union. The accompanying text places Beel Bakar mostly north of Moshihati Bazar and south of the Manirampur–Abhaynagar road, with the river dividing Manirampur and Abhaynagar sides.

This is a useful historical *schematic* for broad locality orientation. It has no coordinate grid, CRS, scale, cadastral authority, surveyed polygon, or exact Pallimangal marker. It depicts Beel Bakar, whereas recent incident reports describe the farm context as Beel Kedaria/Bhavadah. The sources may refer to nearby/overlapping wetland landscapes, but the naming relationship is unresolved; do not equate Beel Bakar with Beel Kedaria or assign the entire blue shape to the target. It cannot support georeferencing or a candidate enclosure polygon.

Full catalogue responses and preview-file hashes are in `data/gherproof/manifests/phase5c_official_map_search.json`.
