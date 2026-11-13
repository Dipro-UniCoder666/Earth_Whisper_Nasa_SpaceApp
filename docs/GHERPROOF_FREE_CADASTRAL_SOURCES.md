# GherProof Phase 5D — Free cadastral source investigation

**Checked:** 2026-11-12
**Target:** Sujatpur/Sujatapur, Manirampur, Jashore; J.L. 143; CS and RS sheets 1 and 2.

## Result summary

| Source | What the source says | What the live check established | Use in this project |
|---|---|---|---|
| [Digital Mouza Map](https://mouza.bd/en/mouza-maps) | Its explorer describes free map downloads and says it is a private repository of reference copies assembled from public/private sources, not a government office. | Search returned one matching Manirampur/J.L.143 record, listed as BS/RS sheet 1. The product page displayed BDT 80 and one-time payment/checkout language. Only the public listing thumbnail was saved; no full file was obtained. | Secondary listing only. The preview was compared against four DLRS previews; no content match was confirmed. Not georeferenced or used to draw geometry. |
| [Digital Mouza Map About](https://mouza.bd/en/about) / [Terms](https://mouza.bd/terms-of-conditions) | The site describes reference copies, not certified copies; it says it is not affiliated with government. General pages describe downloads as free. | The specific Sujatpur product page showed a charge, conflicting with broad free-access claims. Item-specific reuse licence was not found. | No checkout, payment, registration or full-resolution download. Retained only its publicly served preview for internal review and provenance. |
| [MowjaBD](https://mowjabd.vercel.app/) | Landing page advertises a free, no-login DLRMS-connected interface and a public Google Drive library. | Public Drive folder returned HTTP 404; the site's public library API returned `FUNCTION_INVOCATION_FAILED`. No target catalogue result or image could be inspected. | Not evidence that target maps are absent; access could not be completed. |
| [Ministry land zoning map](https://map.land.gov.bd/) | Portal describes digitizing/georeferencing mouza sheets and shows division/district/upazila/mouza/sheet/plot selectors. | Live public Khulna division lookup returned only Bagerhat (4001) and Khulna (4047). Jashore was absent; the target record could not be reached and no map was rendered/downloaded. | Selector presence is documented, but no Sujatpur map service or plot geometry is claimed. |
| [Official DLRS purchase portal](https://map.settlement.gov.bd/) | DLRS describes official map search, payment and delivery. | Phase 5C catalogue lookup already established four digitized/available records for CS 1/2 and RS 1/2, with originals purchase-gated. Phase 5D did not repeat catalogue discovery or purchase. | Official catalogue metadata and previews remain the verified sheet availability evidence. Full copies remain pending. |

## Digital Mouza Map listing and preview

The one matching listing is [Sujatpur Mouza Map — Monirampur, Jashore (BS/RS survey, J.L. 143, Sheet 1)](https://mouza.bd/en/products/default-bsrs-143-sujatpur-1resultresult-aa51c8e490fc). This is **not an exact survey-edition match** for the official CS 1/2 or RS 1/2 records. Its listing page says metadata is read automatically from the folder/name and tells users to cross-check the printed sheet. The displayed BDT 80 charge and one-time checkout language meant we did not enter the download/checkout flow. The general site's free-download description conflicts with that specific product page, so access and item licence remain unresolved.

The public image file was saved as:

`data/gherproof/reference/secondary_mouza_sources/mouza_bd_Sujatpur_JL143_BSRS_sheet1_listing_thumbnail.webp`

SHA-256: `bcba83d458e63d3fb4587531b510f834d61846a76e0488b31456b48e107df5bc`
Dimensions: 1200 × 1200 px, WEBP. It is a product/listing preview, not the original file. A crop of the visible title block is also saved for internal inspection. The map text appears to reference an East Bengal State Acquisition and Tenancy Act notice and a 1958–65 period; this alone does not establish the survey edition, J.L. or sheet number.

The thumbnail was visually checked against the four official DLRS previews preserved from Phase 5C. **The comparison did not establish identity.** We record `preview_cross_checked` because the comparison was performed, but `content_match_confirmed` is false and the secondary record remains `not_verified`. We do not conclude that the image is definitively a different sheet; the evidence is insufficient to show it is one of the exact DLRS sheets.

## Ministry portal query detail

The public HTML includes selectors, but this phase also queried the live administrative endpoint used by the public portal. In the Khulna division response (division code 40), only Bagerhat (4001) and Khulna (4047) were returned. Jashore was not in the response. As a result, no Sujatpur selection, sheet rendering, plot geometry inspection or geospatial download could be performed. The result describes the public lookup path checked on 2026-11-12, not the Ministry's entire internal inventory.

## Reuse and legal status

The third-party source calls its maps reference copies and disclaims government affiliation/certification. No explicit item-level open licence was identified during this review. The saved file is only a publicly exposed listing thumbnail used for internal visual provenance comparison; it is not offered as an official document, legal map, full map copy or georeferenceable source. For legal use, consult DLRS/Jessore Settlement Office and certified records.

The full query provenance and exact result status for each requested sheet are in [`phase5d_free_source_search.json`](../data/gherproof/manifests/phase5d_free_source_search.json). See [Phase 5D report](GHERPROOF_PHASE5D_REPORT.md) for site identification and coverage conclusions.
