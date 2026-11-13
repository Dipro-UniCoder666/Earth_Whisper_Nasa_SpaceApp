# GherProof Phase 5D — Free cadastral map recovery and site identification

**Review date:** 2026-11-12
**Official map status:** `official_catalogue_confirmed`; full sheet files not recovered
**Secondary-source status:** `secondary_copy_found`; preview inspected; content match `not_verified`
**Pallimangal status:** `site_unresolved`
**Boundary status:** `not_delineated`
**Experimental ML inference:** **NOT READY**

## Executive finding

The Phase 5C DLRS catalogue results remain the only verified map records for the requested J.L. 143 location: CS sheets 1 and 2 and RS sheets 1 and 2 are listed as digitized and available, but their full files are purchase-gated. Phase 5D did not repeat the catalogue discovery or buy any map.

The free/secondary-source search found one Digital Mouza Map listing for **Sujatpur, Manirampur, Jashore, J.L. 143, BS/RS sheet 1**. Its product page displayed a one-time BDT 80 price, despite the site's general free-download statements. Only the product thumbnail was publicly served and saved for review. No full-resolution sheet was recovered. The listing is not an exact edition match for the requested CS sheets or the DLRS RS catalogue record, and visual comparison against all four DLRS thumbnails did not confirm that it is the same cadastral sheet. The preview's title-block text includes the East Bengal State Acquisition and Tenancy Act and a 1958–65 period; this is not sufficient to authenticate the record or infer the edition. No checkout or paid download was attempted.

MowjaBD advertises a free DLRMS-connected interface and a public Google Drive library. Its public Drive folder URL returned HTTP 404, and its library API returned a serverless invocation error. No target sheet record or file could be inspected there. The Ministry map portal does expose administrative selectors, but its live Khulna division response listed only Bagerhat and Khulna districts; Jashore was absent. Consequently, the public Ministry query did not reach Sujatpur, render a map or expose plot geometry/downloads. A selector alone is not map access.

No full-resolution cadastral map, georeferenced sheet, road/khal/plot overlay or Pallimangal candidate geometry was produced. There are no defensible control points. The Jan 7/19 Sentinel-1 common-valid support remains measured only over the broad provisional search window (46.3292 km², 18.1274%); target-site coverage remains **unknown**, not zero. The project is not ready for experimental event inference.

## Source-by-source results

| Source | Exact target results | Full map file recovered? | Evidence / access result | Status |
|---|---|---:|---|---|
| Official DLRS catalogue (Phase 5C) | CS 1, CS 2, RS 1, RS 2 listed AVAILABLE/digitized for Sujatpur J.L. 143 | No; purchase-gated | Official record IDs and low-resolution previews retained in the Phase 5C manifest | `official_catalogue_confirmed` |
| Digital Mouza Map | One BS/RS sheet 1 listing; no exact CS 1/2 or RS 2 listing; no exact official RS match established | No | Product page and thumbnail public; page displays BDT 80 and checkout language; no payment/download attempted | `secondary_copy_found`, `preview_cross_checked`, `not_verified` |
| MowjaBD | No target result could be inspected | No | Public Drive embed HTTP 404; public `/api/drive/library` root returned `FUNCTION_INVOCATION_FAILED` | `not_verified` |
| Ministry map service | Target path unavailable in live query | No | Khulna division selector lookup returned Bagerhat (4001) and Khulna (4047), not Jashore | `not_verified` |

### Outcome for each DLRS sheet

| Official sheet | Found as a full-resolution public copy elsewhere? | Preview/content comparison |
|---|---|---|
| CS sheet 1 | No | Compared against the single third-party BS/RS sheet-1 listing preview; no match confirmed |
| CS sheet 2 | No | Compared; no match confirmed |
| RS sheet 1 | No exact RS copy. A BS/RS sheet-1 listing exists but its identity is unverified. | Compared; no match confirmed |
| RS sheet 2 | No | Compared; no match confirmed |

Here “no” means no publicly accessible full-resolution copy was recovered from the investigated sources; it does not assert that no copy exists in other archives or services. MowjaBD and Ministry outcomes remain `not_verified` where their target record could not be reached.

The source-by-source URLs, exact sheet outcomes, preview path/hash, query response summary and caveats are in [`phase5d_free_source_search.json`](../data/gherproof/manifests/phase5d_free_source_search.json). The third-party preview comparison poster is shown below.

![Phase 5D preview comparison](../data/gherproof/review/phase5/pallimangal_phase5d_preview_comparison.png)

## Preview cross-check

The 1200 × 1200 Digital Mouza Map product thumbnail was visually compared with all four 227 × 320 official DLRS thumbnails. The map arrangement and visible sheet layout do not establish a match; the secondary thumbnail does not provide independently legible J.L./sheet identity sufficient to tie it to any DLRS preview. Therefore:

- `preview_cross_checked`: **yes** (comparison performed).
- `content_match_confirmed`: **no**.
- `not_verified`: **yes** (the third-party listing's identity remains unverified).
- Full-resolution map copies recovered: **0**.

This is not a finding that the secondary map is certainly a different cadastral sheet. It is a finding that the available evidence cannot demonstrate equivalence. The preview is not georeferenced and was not traced.

## Ministry of Land portal

The [Ministry map portal](https://map.land.gov.bd/) describes a project in which mouza sheets are digitized and georeferenced and presents division, district, upazila, mouza, sheet and plot selectors. I queried its public live administrative lookup without credentials or personal data. The returned Khulna division record was code 40; its district options were Bagerhat code 4001 and Khulna code 4047. Jashore was not among the returned options. I therefore could not test Sujatpur sheet selection or observe any target rendered map, downloadable raster or plot layer.

No assertion is made about the Ministry's internal data inventory or other authenticated/project endpoints. The result here is limited to the public query path inspected on 2026-11-12.

## Georeferencing and current imagery comparison

No full-resolution sheet was recovered. The official previews are only 227 × 320 pixels and the secondary image is a listing thumbnail. None offers sufficient independently verified map controls for a defensible transformation. No georeferencing, image registration, plot digitization, road/khal matching or survey residual calculation was performed.

The existing Sentinel-2 context and historic Beel Bakar schematic remain locality context only. Neither provides a verified control point that links a cadastral sheet to the January 2026 Pallimangal facility. Historical plot boundaries, even if later acquired, would not by themselves establish present-day fish-farm lease, operator or enclosure limits.

## Candidate identification and Sentinel-1 coverage

| Question | Result |
|---|---|
| Pallimangal separated from neighboring fisheries? | No; no identity-specific evidence |
| Number of supported candidate polygons | 0 |
| Roads, canals, plot boundaries matched to current imagery? | No |
| Jan 7/19 actual enclosure coverage | Unknown because there is no supported enclosure geometry |
| Existing pair footprint in broad search window | 463,292 common-valid pixels; 46.3292 km²; 18.1274% |
| New Sentinel-1 acquisitions queried? | No; target geometry remains unresolved, so alternative scene search cannot establish coverage of the facility |

The old common-valid footprint is preserved in the Phase 5 QGIS GeoPackage. No coverage value was relabeled as enclosure coverage and no candidate was selected because of radar coverage.

## Decisions

1. **Four official sheets found elsewhere?** Not as verified content-matched copies. A secondary catalogue contains one differently labeled BS/RS sheet 1 entry; none of the exact CS 1/2 or RS 1/2 sheets was recovered. The official DLRS catalogue records remain authoritative for sheet availability.
2. **Full-resolution copies recovered?** No.
3. **Secondary copy matched to an official DLRS preview?** No match confirmed; identity remains `not_verified`.
4. **Any sheet georeferenced?** No; there is no full sheet or usable control set.
5. **Roads, khals or plots matched to imagery?** No defensible match.
6. **Pallimangal distinguished from neighboring fisheries?** No.
7. **Does Jan 7/19 cover the candidate enclosure?** Unknown because there is no supported candidate geometry.
8. **Ready for experimental ML inference?** **No.** A map preview and broad raster overlap cannot validate site identity or target coverage.
9. **Remaining access restrictions?** DLRS originals require purchase; the third-party item displays a fee/checkout despite general free claims and was not accessed beyond its public preview; MowjaBD public data endpoints were unavailable during this check; the Ministry public administrative query did not include Jashore.

## Next evidence needed

- Obtain the original DLRS CS and RS sheets through an authorized no-cost inspection/reading-room or a separately authorized purchase decision; confirm exact sheet/title-block metadata.
- Ask DLRS/Jessore Settlement Office whether supervised inspection or non-paid research scans are available (no request was submitted in this phase).
- Obtain an operator/agency document or field GPS trace that identifies Pallimangal's current enclosure separately from neighboring ponds, plus a reviewer and date.
- If a full sheet is later obtained, record its provenance and licence, compare sheet edges/title block to DLRS previews, use documented stable control points, and report independent residuals before vectorizing any plots or water features.
- Only then intersect independently reviewed candidates with the preserved Jan 7/19 validity mask; seek other compatible scenes only if actual target coverage is inadequate.

## Reproduction and files

The preview poster and non-spatial GeoPackage review table can be rebuilt with:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/build_phase5d_review_package.py
```

Outputs:

- [`docs/GHERPROOF_FREE_CADASTRAL_SOURCES.md`](GHERPROOF_FREE_CADASTRAL_SOURCES.md)
- [`docs/GHERPROOF_CADASTRAL_MAP_PROVENANCE.md`](GHERPROOF_CADASTRAL_MAP_PROVENANCE.md) (updated with Phase 5D results)
- [`data/gherproof/manifests/phase5d_free_source_search.json`](../data/gherproof/manifests/phase5d_free_source_search.json)
- `data/gherproof/reference/secondary_mouza_sources/` (public product thumbnail only; no original map)
- `data/gherproof/review/phase5/pallimangal_phase5d_preview_comparison.png`
- Existing QGIS GeoPackage with an added non-spatial Phase 5D source-review table; no geometry layers changed.

No payment, account registration, message/request submission, ML inference, frontend work or model change was performed.
