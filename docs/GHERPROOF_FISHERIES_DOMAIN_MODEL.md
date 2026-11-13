# GherProof Fisheries Domain Model — Phase 8C

## Purpose and boundaries

This domain layer adds fisheries incidents, fisheries assets, an incident-to-asset relationship, screening findings, inspections and officer-oriented decision support inside the existing FastAPI application. It reads the Phase 8/8B evidence registry and manifests; it does not copy satellite rasters into fisheries records, retrain models, or change evidence readiness.

## Entities

| Entity | Identity and persistence | Important semantics |
|---|---|---|
| Fisheries incident | Stable `incident_id`; source-backed seed JSON is inserted into SQLite once; new incidents are persisted in the same table. | Controlled incident type/status; reported date, inferred incident date, source claims and reliability remain distinct. Creating an incident cannot promote it beyond `under_review`. |
| Fisheries asset | Stable `asset_id`; source-backed seed JSON plus API-created assets in SQLite. | Asset type and geometry status are controlled. `not_delineated` cannot carry geometry. Candidate/reviewed/verified geometry must reference registered polygon evidence. The regional search extent is expressly rejected as an asset boundary. Verified geometry requires provenance and verification date. Ownership/operator details require explicitly verified, appropriately sourced provenance. |
| Satellite observation | Derived on read from existing registry entries and manifests; not duplicated in SQLite. | Sentinel-1 dates are individual RTC products; Jan 7/19 limited clips retain their existing coverage caveats. Sentinel-2 Jan 10/20 observations link existing optical evidence and per-date band/QA files. Sensor streams remain separate. |
| Screening finding | Derived from the existing optical weak-reference manifest and registered disagreement evidence; not treated as field data. | Findings carry evidence IDs, dates, algorithm, evidence strength, validation status, explanation, limitations and next verification action. Pixel counts remain grid-cell counts. |
| Inspection record | Append-only SQLite record with generated `inspection_id`, incident foreign key, optional asset foreign key and timestamps. | Direct observations, operator reports and satellite-derived references are tagged separately. Missing water-level, fish-escape, mortality, production and financial measurements remain `null`. There is no update/delete route that silently overwrites inspection history. |

## Persistence and integrity

`data/gherproof/fisheries/gherproof_fisheries.sqlite3` uses Python's built-in SQLite support. Tables are created idempotently and set SQLite `user_version=1`; foreign keys and a busy timeout are enabled. `GHERPROOF_FISHERIES_DB` can select a different database path for tests or deployment. The runtime database and SQLite WAL files are ignored by Git; the two JSON seed records are the reproducible source fixtures.

Evidence IDs accepted on incident, asset provenance and inspection satellite references must exist in the existing evidence registry. Asset geometry references must resolve to registered GeoJSON containing valid Polygon/MultiPolygon geometry. The provisional six-locality extent cannot be used as an asset geometry. Inspection GPS geometry, when present, must be a finite WGS84 GeoJSON Point.

## Pallimangal source-backed records

- Incident ID: `incident-pallimangal-2026-01-14`.
- Asset ID: `asset-pallimangal-reported`.
- Incident type: `embankment_failure` as described by the secondary reports.
- Date: January 14, 2026, explicitly `reported_inferred` from reports published January 15–17 that describe a Wednesday event; no official incident timestamp was found in project evidence.
- Place names and six localities are retained as reported. The jurisdiction note preserves the Manirampur/Abhaynagar border context instead of asserting an unresolved enclosure jurisdiction.
- Reported damage claims remain attached to their individual source. Samakal's 158-hectare report and Daily Country Today's 1,500-bigha/500-family headline are not reconciled, converted or presented as measured impact.
- Geometry status remains `not_delineated`; geometry reference, owner/operator, verified breach location, fish escape, mortality and financial/production losses are unavailable (`null` or explicit not-assessable status).

Source records are in `data/gherproof/fisheries/pallimangal_incident.json` and `data/gherproof/fisheries/pallimangal_asset.json`. They are seeded only when their stable IDs are absent, so new inspection records and user-created records are not overwritten at service startup.

## Fisheries screening rules

1. The January 10→20 possible-new-water count (671) and possible-water-loss count (1,316) are optical weak-reference **grid cells on a 20 m grid**, sourced from the Phase 8B manifest. They are not hectares, confirmed water, flood extent, or fishery exposure.
2. Persistent-water candidates (144,170), stable-nonwater candidates (900,758), uncertain changes (570,341), and invalid/unavailable cells (61,668) retain the manifest's own categories and units.
3. A no-geometry asset returns `not_assessable` with `candidate_pixel_overlap_count: null`. The code does not treat no geometry as zero exposure.
4. Candidate/review geometry yields `provisional_assessment`; only a provenance-backed verified polygon can enter a raster overlap calculation. A successful calculation reports valid candidate grid-cell overlap, not fishery damage or loss.
5. Scratch and pretrained comparison results remain separate. Existing overall and class-specific weak-reference agreement metrics are named as consistency measures, not accuracy. The service selects neither model.
6. A regional observation and candidate count do not receive village, agriculture, pond or permanent-water labels when those geometries are unavailable.

## Inspection workflow

An inspection is created with `POST /api/gherproof/fisheries/incidents/{incident_id}/inspections`. It can represent `planned`, `in_progress` or `completed`, but creating one does not itself assert verification. Its source-tagged observations distinguish `field_observation`, `operator_report` and `satellite_derived`. Fish escape and mortality report fields reject satellite-derived sources. Missing values stay null. Every request creates a new record; the API exposes listing but no silent update endpoint.

`photograph_references` are provenance references only. This phase does not upload or store image files. `inspector_reference` is an optional external reference; it is not an authenticated user identity.

## Decision-support priority

Priority categories are rule-based and have no numeric score. For Pallimangal, the first review action is geographic/site verification because the report is source-reported and no enclosure location is available. A second action collects actual field records if the site is found. Neither category is an emergency instruction, dispatch, evacuation or harvest recommendation. Asset-specific exposure stays `not_assessable`.

## Security and deployment note

The existing app has no Fisheries Officer authentication/authorization middleware. Fisheries mutation routes are disabled by default and reject requests with HTTP 503. `GHERPROOF_FISHERIES_WRITES_ENABLED=true` enables unauthenticated writes only for trusted local development; do not use it on a public deployment. Add an authenticated, authorized service boundary before operational use. The API does not fabricate an identity field.
