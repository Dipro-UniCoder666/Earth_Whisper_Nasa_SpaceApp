# GherProof — Remote geolocation evidence, Phase 5C

**Finding:** Regional locality is better constrained; Pallimangal remains unlocated. No coordinates or candidate boundary are asserted.

## Evidence register

| Evidence | What it supports | What it does not support |
|---|---|---|
| Official DPHE geographic code table | Jessore 41 / Manirampur 61 / Kultia 473 / Sujatpur 368 administrative chain | Mouza J.L. number, parcel, point or enclosure geometry |
| Official DLRS public catalogue | Sujatpur in Manirampur is catalogued as J.L. 143; two CS and two RS sheets (1/2) are digitized and available | Printed full-sheet title-block inspection, commercial farm identity, plot-owner/lease attribution, location of Pallimangal inside the mouza |
| 2014 USS/Oxfam *Beel Bakar Study*, Figure 2, p.3 | Broad diagrammatic relationship of Beel Bakar, Mukteswari River, Sujatpur, Moshihati, Bhaba Daha, Kultia Union, roads, bridge and sluice symbols | CRS, scale, positional accuracy, exact Beel Bakar boundary, Beel Kedaria equivalence, Pallimangal parcel/boundary, 2026 infrastructure state |
| January 13, 2026 Sentinel-2 visual context | Broad surface appearance within the existing provisional raster window; many pond/field-like parcels | Unique farm name/parcel, land-cover class, water persistence, or site coordinate without a known reference point |
| January 7/19 Sentinel-1 common mask | Actual shared VV/VH data support in the broad search window | Whether Pallimangal intersects it, water extent or impact area |
| January 2026 incident reporting | Named Sujatpur / Beel Kedaria / Bhavadah context and reported south-side khal/embankment relation | Geodetic point, cadastral plot, mapped khal, farm outline or proven breach point |

## Reading the historical diagram cautiously

The USS/Oxfam map depicts Sujatpur near the south/east edge of a broad blue Beel Bakar schematic, close to labels for Moshihati and Bhaba Daha. It is useful for recognizing a landscape cluster and planning manual review of the official sheets. It is not georeferenced. Its pale-blue fill is a thematic sketch, not a digitized beel polygon. The Mukteswari, road, bridge and sluice symbols have no coordinates or positional accuracy. No lines were digitized from it.

Incident reports call the farm's setting Beel Kedaria/Bhavadah. Available evidence does not resolve whether that usage overlaps, adjoins or differs from the 2014 Beel Bakar map area. We do not equate the names. The diagram's Sujatpur label cannot distinguish which of its nearby pond systems is Pallimangal.

## Candidate search-area decision

The evidence supports a **textual locality search context**, not a defensible geospatial candidate area:

- Administrative context: Kultia Union, Manirampur, Jashore; Sujatpur village/mouza.
- Cadastral request key: J.L. 143; official DLRS catalogue lists CS and RS sheets 1 and 2.
- Hydrographic/local context: a 2014 schematic around Beel Bakar/Mukteswari with Sujatpur, Moshihati and Bhaba Daha labels; incident reports separately mention Beel Kedaria and a south-side khal.
- Exact target coordinate, selected parcel, enclosure outline, southern khal, embankment and breach point: unresolved.

No map pin or polygon was created. Do not spatially search scene alternatives against the Beel Bakar blue fill, choose a pond based on visual resemblance, or treat the historic schematic as a current boundary. First obtain the full official sheet(s) and an independent link between Pallimangal and plot/landmark; then record a reviewed candidate if evidence supports it.

## Supporting files

- Official DLRS query and record manifest: `data/gherproof/manifests/phase5c_official_map_search.json`.
- Public DLRS preview thumbnails: `data/gherproof/reference/dlrs_portal_previews/`.
- Preserved historical source PDF: `data/gherproof/reference/historical/Beel_Bakar_Study_2014_source.pdf`.
- Cropped but unmodified-in-content Figure 2 context image: `data/gherproof/reference/historical/beel_bakar_map_figure2_context.png`.
- Current raster context and common support: `data/gherproof/review/phase5/pallimangal_phase5c_review_map.png`.
- Search/status report: `docs/GHERPROOF_PHASE5C_REPORT.md`.
