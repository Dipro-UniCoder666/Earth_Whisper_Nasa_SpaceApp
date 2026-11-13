# GherProof Frontend Integration Contract — Phase 8

This contract is for the next UI phase. Phases 8 and 8B changed backend/data artifacts only; the existing React app and frontend source were not changed.

## API base and readiness

Use `/api/gherproof`. Query `/screening/status` for regional Phase 8 data or `/status` when the caller also needs legacy event-case fields. Display these values without reinterpretation:

Phase 8B adds three evidence-backed read endpoints:

| Endpoint | Use |
|---|---|
| `GET /weak-reference` | Optical weak-reference scene counts, fixed threshold configuration and registered optical layers. Always label the outputs “automated optical weak references”; never call them human labels or ground truth. |
| `GET /comparisons` | Per-model/per-acquisition `weak_reference_agreement`, positive/negative agreement, temporal matches, coverage and limitations. Never rename these metrics to accuracy, precision, recall or F1. |
| `GET /scenarios/january_2026_regional_screening_demo` | Static Phase 9 demonstration metadata and eight simulated workflow stages linked to evidence IDs. The scenario is explicitly simulated even though its linked observations and derived layers are real saved artifacts. |

The central evidence route continues to filter by category. Phase 8B adds `optical_weak_reference`, `model_comparison`, and `uncertainty_layer`. Probability aggregations remain `model_prediction`. Use `/layers` and `/layers/{evidence_id}/file` for the registered rasters. Key layer products include separate optical weak-water, weak-nonwater, uncertainty and possible-new-water-candidate masks; per-model 20 m probabilities and binary predictions; SAR/optical agreement/disagreement; cross-model disagreement; and joint-coverage codes.

### Phase 8B map semantics

- Optical comparison grid is EPSG:32645 at 20 m, aligned to native Sentinel-2 B11.
- Sentinel-1 10 m probabilities are area-averaged to 20 m only when all four contributing SAR pixels are valid.
- Optical class codes distinguish weak water, weak non-water, uncertain and invalid. Keep uncertainty visible and do not render it as dry land.
- Model disagreement, SAR/optical disagreement and unavailable coverage are separate layers. Do not merge them into one confirmed flood map.
- Sentinel-1 ascending relative orbit 12 and descending relative orbit 150 remain separate scene selections. Show the nearest optical timestamp and exact temporal offset with each comparison.
- Source-reported incident context must retain attribution and the `reported/unverified` state. The regional geography is provisional, and no exact enclosure boundary or breach point is available.
- Report summaries must not include affected-area estimates, local accuracy claims, or causal breach diagnoses.

- `model_readiness`: `exploratory_only`
- `local_validation_status`: `human_review_pending`
- `geographic_readiness`: provisional; no village/enclosure boundary
- `impact_quantification`: `not_approved`

Do not use benchmark scores as Sujatpur metrics. Do not call unvalidated model outputs a flood map.

## Data loading

Initial load can request `/screening/status`, `/scenes`, `/predictions`, `/optical`, `/coverage`, and `/limitations` in parallel. `/evidence` supports category/status/date filtering and pagination (`limit` at most 500). `/layers` returns available GeoTIFF references; use each metadata URL before rendering and retain its `evidence_id`, status, date, CRS, NoData, checksum, source and limitations in layer state.

Layer downloads use `/layers/{evidence_id}/file?asset=derived|original`. For smaller map requests use `/layers/{evidence_id}/clip?bbox=west,south,east,north` with EPSG:4326 bounds. The service will reject oversized clips above 4 million pixels. GeoJSON is accessible only for registered evidence IDs through `/geography/{evidence_id}`.

## Semantic categories and badges

| API value | Display treatment |
|---|---|
| `verified_satellite_observation` + `verified` | “Verified raster / observation” with sensor/date/source; do not imply verified flood meaning. |
| `derived_satellite_measurement` + `derived` | “Derived measurement” such as dB or NDWI/MNDWI. |
| `model_prediction` + `exploratory` | “Exploratory model prediction”; always name scratch or pretrained model. |
| Disagreement record | “Model disagreement”; not error or confidence truth. |
| `catalogue_metadata` + `under_review` | “Catalogue match only”; do not render as a processed raster. |
| `provisional_geographic_reference` + `provisional` | “Provisional search extent”; never label as village boundary. |
| `optical_reference_interpretation` + `under_review` | “Human review pending”; current labels are 0/900. |
| `human_verified_evidence` + `unavailable` | Show unavailable state, not zero event impact. |
| `news_reported_event` + `provisional` | “Reported by source”; keep separate from sensor evidence. |

## Recommended map ordering

1. Provisional AOI boundary.
2. Satellite observation layers (S1 RTC or S2 optical), each with separate sensor/date selection.
3. Valid-data/SCL masks as optional QA overlays.
4. One selected model prediction at a time (scratch or pretrained).
5. Model disagreement as a distinct optional layer.
6. SAR/optical comparison code as a distinct optional layer.

Do not composite ascending and descending Sentinel-1 geometries into one unadjusted temporal series. Do not average the models. Keep indices, predictions and masks as distinct layers.

## Loading, empty and error states

- `404`: requested file/evidence/report is not available; show the evidence ID and status if returned by the registry.
- `413`: clip is too large; ask for a smaller map extent.
- `422`: invalid category, date, model, GeoJSON or bbox; show validation feedback.
- `503`: raster processing dependency is unavailable; retry only after service health changes.
- Empty results: state “No registered product for this filter,” not “no water/no event.”
- Registry record with no file: render its status/limitations card and omit raster controls.
- NoData: transparent/unknown; never style as dry/non-water.

## Reports

`GET /reports/summary` returns the generated evidence-aware JSON summary; `/reports/summary.md` returns Markdown. `/reports` lists the historic Phase 4B through Phase 7C reports and availability. The report distinguishes news-reported event context, satellite measurements, derived optical indices, exploratory model predictions, provisional geography and unavailable human evidence.

No API for affected area, village impact, breach attribution, families, fish loss or financial estimates is available or approved.

## Phase 9 frontend integration

GherProof is integrated at `/gherproof` as a child of the existing `AppLayout`. It uses Earth Whisper's shared `WhisperNav`, atmosphere, page layout and footer. The `/` landing page and the existing investigation, science and about routes remain intact. The user journey has an intro, one selectable regional screening card and a results state; query-string stages support refresh and browser navigation.

Analyze Now loads the existing screening status, evidence registry, raster layers, scene metadata, predictions, optical indicators, comparisons, coverage, scenario, provisional GeoJSON and summary report. It does not train a model or run new inference. Partial API failures are shown; catalogue metadata is not treated as a processed raster.

The result screen provides separate satellite imagery, optical comparison and AI screening views, a selectable layer, opacity control, raster metadata/limitations and an eight-line evidence summary. The underlying geometry remains a provisional regional search extent. The summary reports no local accuracy, confirmed flood extent, impact area or breach diagnosis. Saved benchmark/model outputs remain exploratory; model disagreement is not error or confidence truth.

GeoTIFF map previews use `GET /api/gherproof/layers/{evidence_id}/preview.png?bbox=west,south,east,north&width=900&band=1`. The route reads a bounded raster window and returns a transparent PNG plus `X-Preview-Bounds-WGS84`. Its display stretch is visualization only. Sentinel-2 B08 registered evidence IDs for Jan 10 and Jan 20 can request `rgb=true`; this serves the provenance-documented Phase 7C B08/B04/B03 false-colour composite with a fixed 0–0.4 display range. It is not a water classification. Other layers retain single-band rendering and separate sensor/maturity semantics.

The evidence strip previews actual saved optical composites, scratch/pretrained prediction rasters and model-disagreement products when both registry records and raster assets are available. Optical temporal-change candidate counts are shown only in the expandable methodology details, as candidate pixels at the manifest resolution and never as verified water area. The app makes the provisional boundary, weak-reference labels, model maturity and missing human reference labels explicit.
