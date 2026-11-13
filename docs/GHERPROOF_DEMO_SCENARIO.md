# GherProof Phase 9 Demonstration Scenario

## Scenario identity

**January 2026 — Regional Flood Screening Investigation** is a simulated demonstration workflow for a hypothetical regional disaster-monitoring officer reviewing a reported embankment incident in the Manirampur/Abhaynagar region. The user, actions, and operational use are fictional. The linked imagery, derived layers, model predictions, comparison outputs, and published reports are real saved project artifacts; their scientific qualifications remain in force.

Scenario JSON: `data/gherproof/scenarios/january_2026_regional_screening_demo.json`.

## Source-reported context shown in the application

The case record associates the report with **January 14, 2026**, but the date is reported/inferred from news accounts and is not independently verified. The linked reporting names Sujatpur Pallimangal Fisheries Enclosure and describes a southern embankment incident. Secondary reports place the operation in the Sujatpur mouza / Beel Kedaria / Bhavadah textual context and name Sujatpur, Hatgachha, Kultia, Moshiahati, Bedbhita, and Balarabad among reportedly affected locations. Daily Country Today’s headline reports “1,500 bighas” and “over 500 families”; show those only as source-attributed claims, never as measured satellite values. The reports provide no site coordinate or validated enclosure polygon. The regional search geography remains provisional.

The scenario links these reports:

- [Daily Country Today](https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore)
- [Dhaka Post](https://www.dhakapost.com/country/424238)
- [Samakal](https://samakal.com/whole-country/article/334020)

All descriptions stay marked `source_reported_unverified`. No article claim becomes a satellite label.

## Eight-stage user journey

1. **Open investigation.** The user opens the January 2026 demonstration card. A persistent banner identifies the workflow as simulated, the event as reported, and the search geography as provisional.
2. **Review incident context.** Source attribution, reported date basis, place-name descriptions, and report links appear in a context panel. The user can distinguish report text from sensor observations.
3. **Review radar scenes.** The user selects among Sentinel-1 scenes dated Jan 9, 12, 21, and 24. Orbit 150 descending and orbit 12 ascending remain distinct. Each view shows the acquisition date, provenance, coverage, and data limitations.
4. **Compare optical indicators.** The user toggles Jan 10/20 weak-reference, NDWI, MNDWI, SCL, and uncertainty layers. The UI exposes the fixed 0.0 dual-index threshold and 20 m grid. It distinguishes weak water/nonwater, uncertain, and invalid pixels.
5. **Inspect AI screening.** Scratch and pretrained outputs are independently switchable. They are labeled exploratory model predictions, not confirmed water. The interface does not select a winner.
6. **Review uncertainty and disagreement.** Separate controls show optical uncertainty, SAR/optical agreement, SAR/optical disagreement, scratch/pretrained disagreement, and joint-valid-data coverage. The nearest optical time offset is displayed with every comparison.
7. **Assess evidence.** Filters separate verified observations, derived measurements, optical weak references, model predictions/comparisons, uncertainty, news reports, and provisional geography. Each layer shows source, processing method, checksum, status, and limitations.
8. **Generate a screening summary.** The user can produce a qualified evidence summary with per-scene weak-reference consistency, date offsets, and next evidence needs. The report states that human review, field observations, an authoritative enclosure boundary, and official incident records are missing. No impact estimate or breach diagnosis is generated.

All clicks or toggles in the demonstration are simulated user actions. The underlying raster values and manifests are actual saved artifacts. The demo should show this distinction in both the header and exported report.

## Phase 9 API contract

Use the existing `/api/gherproof` API and the additions made in Phase 8B:

| Endpoint | Purpose |
|---|---|
| `GET /scenarios/january_2026_regional_screening_demo` | Scenario metadata, source claims, evidence IDs, workflow stages and status flags. |
| `GET /weak-reference` | Optical label counts, fixed threshold and registered layers. |
| `GET /comparisons` | Per-model/per-acquisition weak-reference consistency and limitations. |
| `GET /evidence?category=...` | Central evidence records and provenance. |
| `GET /scenes` | Sensor acquisition inventory and temporal pair notes. |
| `GET /predictions?model=scratch` or `?model=pretrained` | Existing model outputs, with the models kept separate. |
| `GET /layers` and `GET /layers/{evidence_id}/file` | Registered raster layers and GeoTIFFs. |
| `GET /reports/summary` or `/reports/summary.md` | Evidence-aware report summary. |

The backend does not offer impact-estimation, confirmed flood-mask, or breach-diagnosis endpoints. Keep all Phase 8 readiness and limitations in the UI; never rename weak-reference metrics as local accuracy.

## Expected demonstration output

The generated comparison manifest currently includes eight per-model/per-Sentinel-1-acquisition results. Overall weak-reference agreement is higher for the pretrained outputs in the four comparisons, but weak-water positive agreement is higher for the scratch outputs. Show both class-specific measures and explain that this trade-off does not validate or select a model. Scene geometry, date separation, threshold sensitivity, and uncertain optical labels remain visible.

The optical Jan 10→Jan 20 product has 671 `possible_new_water_candidate` pixels and 1,316 `possible_water_loss_candidate` pixels on the 20 m comparison grid. These are explicitly optical change candidates over a provisional region, not flood extents or affected-area figures. Do not calculate hectares or bighas from them.

## Prohibited interface claims

- No live/real-time alert, actual officer dispatch, or named real user.
- No verified village boundary, enclosure boundary, breach coordinate, or village-level statistic.
- No confirmed flood, embankment failure, or incident causality.
- No local accuracy or field-validation claim from optical weak-reference agreement.
- No affected cropland/family, fish mortality, or financial-loss estimate.
- No conversion of candidate pixel counts into affected area.

## Phase 9 readiness

**Ready for frontend workflow prototyping** with explicit evidence badges, separate layers, uncertainty handling, temporal offsets, and source attribution. Scientific readiness remains model `exploratory_only`, human labels `human_review_pending`, impact quantification `not_approved`, and Pallimangal location `unresolved`.
