# GherProof Phase 8C — Fisheries Intelligence Backend

## Completion status

**Implemented as a bounded fisheries-domain backend milestone.** The existing Earth Whisper FastAPI application now includes structured fisheries incidents and assets, incident-to-asset links, evidence-backed screening, rule-based inspection review priorities, append-only persistent inspection records, concise officer summaries, and a JSON investigation report. No frontend component was added. No satellite search, raster processing campaign, model training, or model-weight change was performed.

## Audit findings

- The project has one FastAPI application mounted under `backend/app/main.py`; GherProof already has a large evidence-aware router and registry-backed screening/report services.
- Evidence registry/manifests and the previous generated evidence summary are file-backed. There was no existing SQL database, ORM, migration framework or Fisheries Officer identity/authentication layer.
- The registry remains the source of truth for sensor observations, model outputs, optical weak references, coverage, provenance and limitations.
- Existing Phase 8/8B statuses remain `exploratory_only`, `human_review_pending` and `not_approved`. The exact Pallimangal enclosure geometry remains `not_delineated`.
- The existing project PDF route serves a static Step 11 Earth Whisper case file; there is no reusable generated investigation-report PDF service. Phase 8C provides machine-readable JSON rather than adding a second PDF architecture.

The requested Phase 8, evidence-methodology, Phase 8B, weak-reference methodology/comparison, demo scenario and frontend-contract documents were reviewed before implementation. Existing API routes and typed Pydantic contracts were retained; the new router is mounted below `/api/gherproof/fisheries` in the same FastAPI app.

## Implemented domain

New code and data:

- `backend/app/schemas/gherproof_fisheries.py`: controlled incident/asset/finding/priority vocabularies, observation/source distinctions, typed API models, GeoJSON Point validation, and safeguards for verified asset geometry.
- `backend/app/services/gherproof_fisheries_service.py`: SQLite persistence, one-time seeded records, registry linkage, separate S1/S2 observation views, optical candidate translation, model comparison, geometry-aware exposure assessment, findings, prioritization, summary and report generation.
- `backend/app/api/gherproof_fisheries.py`: typed incident/asset/list/get/create, screening/findings/priorities, append-only inspection, summary and report routes.
- `backend/app/main.py`: includes the new fisheries router in the existing FastAPI application.
- `data/gherproof/fisheries/pallimangal_incident.json` and `pallimangal_asset.json`: source-attributed, machine-readable initial case and reported asset.
- `data/gherproof/fisheries/gherproof_fisheries.sqlite3`: created on first service use; ignored by Git as runtime database content. Schema is idempotently initialized and sets SQLite `user_version=1`. Tests use temporary database files.
- `.gitignore`: excludes runtime SQLite database/WAL files.

## Pallimangal demonstration record

Incident ID `incident-pallimangal-2026-01-14` is `embankment_failure`, with incident date 2026-01-14 marked `reported_inferred` and status `reported_unverified`. It references the existing event and provisional geography records and links the available S1, S2, weak-reference, prediction and disagreement evidence IDs. Its six affected-locality names are retained as source-reported information.

The reporting-source records retain URLs and reported-claim status. They preserve the Samakal 158-hectare claim and Daily Country Today's 1,500-bigha / over-500-family headline separately. These figures are not reconciled, converted, used as labels or restated as measured impact. Manirampur and the nearby Abhaynagar border context remain an administrative-location uncertainty. The incident date is an inference from reporting chronology, not an official timestamp.

Asset ID `asset-pallimangal-reported` is a `fish_enclosure` record with `geometry_status: not_delineated`, `geometry_reference: null`, and no asserted owner/operator. No coordinates, plot identity, lease boundary or fake polygon were created.

## Actual screening behavior

The fisheries screening service reuses the stored Phase 8B optical temporal-change manifest. Its current regional comparison reports 671 possible-new-water candidate cells and 1,316 possible-water-loss candidate cells, plus the recorded persistent-water, stable-nonwater, uncertain and invalid cell counts. It reports the source dates, 20 m pixel resolution and `grid_cells; not area` units. The explanation explicitly says these are automated optical candidates and are not confirmed flooding.

Six registered Sentinel-1 observations are surfaced individually, including the limited Jan 7/19 clips with their recorded limitations; two Sentinel-2 dates (Jan 10 and Jan 20) link their acquisition product IDs and registered band/QA products. Eight model/scene weak-reference comparisons remain separate. The comparison response documents pretrained model higher overall weak-reference agreement and scratch model higher weak-water positive agreement without choosing a winner or calling those local accuracy.

Pallimangal exposure returns `not_assessable`, with `candidate_pixel_overlap_count: null`. A `possible_enclosure_exposure` finding is not generated. The findings include the existing optical change candidate categories, saved model disagreement, unresolved boundary and the need for field verification. They carry evidence IDs, observation dates when applicable, method, evidence strength, validation status, limitations and verification action.

The first rule-based priority is geographic/site verification. It is not an emergency instruction, officer dispatch or diagnosis. A second review suggests collecting field evidence only after the site is located. No score, fish loss, mortality, production/financial loss, damaged area, breach point or affected-cropland area is generated.

## Persistence, source distinctions and security

SQLite stores incidents, assets and inspections with stable IDs, ISO timestamps, foreign keys and JSON data. Seed rows use `INSERT OR IGNORE`, preserving later records. Every inspection POST creates a new UUID record; there is no update route that can overwrite prior inspection history. Missing measurements stay null. Satellite evidence can be attached as a tagged reference but cannot be used as the source for fish escape or mortality reports. Non-unverified inspection statuses require a field-observation record.

Photo references are metadata only; this phase does not implement uploads. The existing app does not authenticate or authorize Fisheries Officers. All fisheries mutation routes are disabled by default and return HTTP 503. `GHERPROOF_FISHERIES_WRITES_ENABLED=true` is an unauthenticated trusted-local-development opt-in only; it must not be enabled on a public deployment. The service does not invent an inspector identity.

## Report and frontend contract

The endpoint `GET /api/gherproof/fisheries/incidents/{incident_id}/report` returns JSON titled `Exploratory Fisheries Incident Screening Report`. It includes incident sources, asset geometry status, observation dates, water-change candidates, both model streams and disagreement, exposure assessment, findings, priorities, inspection suggestions, saved inspection records, evidence references, unavailable measurements and limitations. The five-question summary is available separately at `/summary`. The new frontend can use the API contract in `docs/GHERPROOF_FISHERIES_API_CONTRACT.md` without duplicating science details in the summary panel.

## Verification

Implemented focused tests in `backend/tests/test_gherproof_fisheries.py` for:

- Seeded incident/source/asset semantics and unresolved boundary.
- Separate real Sentinel-1 and Sentinel-2 observation records.
- Actual Phase 8B candidate counts and grid-cell units.
- No unsupported enclosure exposure, evidence-linked findings and model disagreement.
- Prioritization rationale and non-emergency semantics.
- Append-only inspection persistence and null missing measurements.
- Geometry/evidence validation and field-vs-satellite claim handling.
- Report title, source evidence, null impact fields and JSON serialization.
- API route behavior, incident–asset linking, OpenAPI path/schema registration, response contracts, 404/422 mapping and create/list/report workflow.

Initial smoke check using the project Python environment succeeded: 1 seeded incident and asset loaded; six S1/two S2 observation records were returned; Pallimangal exposure was `not_assessable`; the actual manifest returned 671 possible-new-water cells; eight model comparison rows and six evidence-linked findings were available. A live ASGI smoke probe returned 200 for incident list/screening/inspection list/report, 404 for a missing incident, 422 for invalid inspection geometry, and 201 for a planned inspection. Python compilation succeeded for the new schema, service, router, app module and test module.

The final focused fisheries suite passed: **13 passed**. The broader GherProof regression suite passed: **109 passed, 5 deselected, 3 warnings**. The warnings are the existing Starlette/httpx deprecation and synthetic raster `NotGeoreferencedWarning` fixtures. See `docs/GHERPROOF_PHASE8C_VERIFICATION_REPORT.md` for live HTTP startup, API, security and persistence verification. No existing assertion was weakened.

## Limitations and readiness

The system is ready to represent reported fisheries incidents, register future assets/geometry sources, expose cautious regional evidence, persist inspection records, and produce an evidence-linked exploratory report. It is **not** ready for operational enclosure exposure or damage assessment: authoritative geometry, field labels, field inspections, verified incident records, local model validation and authenticated officer access remain outstanding. Satellite candidates are not fish escape evidence; optical weak-reference agreement is not model accuracy; absent impact values remain unavailable rather than zero.
