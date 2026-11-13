# GherProof Fisheries API Contract — Phase 8C

Base path: `/api/gherproof/fisheries`. The routes live in the existing Earth Whisper FastAPI app. Satellite evidence remains available through the existing `/api/gherproof` registry, raster, geography and report services.

## Routes

| Method and path | Purpose |
|---|---|
| `GET /incidents` | List source-backed and persisted fisheries incidents. |
| `POST /incidents` | Create a reported/unreviewed incident with attributed source records and existing evidence references. |
| `GET /incidents/{incident_id}` | Retrieve a typed incident record. |
| `POST /incidents/{incident_id}/assets/{asset_id}` | Idempotently link an existing asset to an incident. |
| `GET /incidents/{incident_id}/summary` | Concise incident, screening, inspection need, checks and unknowns. |
| `GET /incidents/{incident_id}/screening` | Existing observations, optical candidate counts, model comparison, asset exposure and spatial-category availability. |
| `GET /incidents/{incident_id}/findings` | Evidence-linked fisheries-relevant findings. |
| `GET /incidents/{incident_id}/priorities` | Rule-based review priorities with rationale and missing information. |
| `GET /incidents/{incident_id}/inspections` | Append-only inspection history. |
| `POST /incidents/{incident_id}/inspections` | Persist an inspection or planned-inspection record. |
| `GET /incidents/{incident_id}/report` | Machine-readable `Exploratory Fisheries Incident Screening Report`. |
| `GET /assets` | List known fisheries assets. |
| `POST /assets` | Create a sourced asset record; supplied geometry must reference registered polygon evidence. |
| `GET /assets/{asset_id}` | Retrieve an asset and geometry status. |

Typed Pydantic response models are used for stable records. Unknown IDs return 404; malformed geometry/status and unknown evidence IDs return 422. Inspection records have no update/delete route; each POST appends a new record.

## Actual Pallimangal incident response excerpt

Request:

```http
GET /api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14
```

```json
{
  "incident_id": "incident-pallimangal-2026-01-14",
  "title": "Reported southern embankment failure near Pallimangal Fisheries Enclosure",
  "incident_type": "embankment_failure",
  "incident_date": "2026-01-14",
  "incident_date_status": "reported_inferred",
  "reported_date": null,
  "mouza": "Sujatpur",
  "affected_localities_reported": ["Sujatpur", "Hatgachha", "Kultia", "Moshiahati", "Bedbhita", "Balarabad"],
  "source_reliability": "secondary_reporting",
  "incident_status": "reported_unverified",
  "related_evidence_ids": ["reported-event-2026-01-14", "geography-provisional-regional-aoi"]
}
```

The full response contains all source records and 23 linked evidence IDs. January 14 is inferred from news chronology, not an official incident timestamp. Samakal's reported 158 hectares and Daily Country Today's 1,500 bighas / over-500-family headline remain separate source-attributed claims; neither is a measured impact, and they are not reconciled or converted. The location record retains Manirampur/Abhaynagar border uncertainty.

## Actual concise officer-summary response

Request:

```http
GET /api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/summary
```

```json
{
  "incident_id": "incident-pallimangal-2026-01-14",
  "case_status": "exploratory_regional_investigation",
  "what_happened": "News accounts report a southern embankment failure associated with Pallimangal Fisheries Enclosure around January 14, 2026. The date is inferred from publication context; the event is not independently verified.",
  "satellite_screening": "Automated optical screening recorded 671 possible-new-water candidate grid cells between 2026-01-10 and 2026-01-20; these are not confirmed flooding.",
  "inspection_needed": "Exact enclosure-specific exposure is not assessable because the Pallimangal boundary is not delineated. Regional candidates cannot be assigned to the enclosure or named village.",
  "recommended_checks": [
    "Confirm the enclosure identity and location.",
    "Inspect embankment condition and adjacent khal.",
    "Record water levels inside and outside the enclosure with a measurement reference.",
    "Separate direct observations from operator reports; record fish escape or mortality only if actually observed or reported.",
    "Capture georeferenced photographs with timestamp."
  ],
  "unknowns": ["Verified Pallimangal boundary", "Confirmed breach position", "Confirmed fish escape", "Fish mortality", "Production loss", "Financial loss", "Affected-cropland area", "Reconciled source-reported damage claims", "Local model accuracy", "Field verification"],
  "evidence_ids": ["reported-event-2026-01-14", "geography-provisional-regional-aoi", "optical-weakref-2026-01-10-weak_reference", "optical-weakref-2026-01-20-weak_reference"]
}
```

The `671` is a Phase 8B weak-reference count of candidate grid cells on a 20 m grid, not area or confirmed flooding.

## Screening semantics

The full screening response returns six individual Sentinel-1 RTC dates and Sentinel-2 observations from Jan 10 and Jan 20, along with the linked product/evidence files and per-record limitations. It includes the original optical candidate pixel counts and units (`grid_cells; not area`), eight separate scratch/pretrained comparisons, model candidate evidence IDs, optical weak-reference IDs, disagreement layers and per-acquisition invalid/uncertain coverage counts.

Metrics retain the names `weak_reference_agreement`, `weak_reference_positive_agreement` and `weak_reference_negative_agreement`; they are not local accuracy. The model-selection value remains `none`. Pallimangal asset exposure returns `not_assessable` with `candidate_pixel_overlap_count: null`; it does not return a zero exposure measurement. Spatial categories for enclosure, outside-enclosure, nearby aquaculture, agriculture and permanent water remain separately marked unavailable/unclassified as supported by actual geometries.

Readiness values remain `exploratory_only`, `human_review_pending`, and `not_approved`; the asset remains `not_delineated`. Fish escape, mortality, production/financial loss, affected area and breach position are null/unavailable.

## Asset response

```http
GET /api/gherproof/fisheries/assets/asset-pallimangal-reported
```

The returned asset is a reported-name `fish_enclosure` with `geometry_status: "not_delineated"`, `geometry_reference: null`, `ownership_or_operator: null`, and source provenance. No coordinates, parcel identity, lease boundary or polygon is invented. The provisional regional search extent is rejected as an asset boundary.

## Planned inspection request example

This request creates a **planned** record only; it does not state that a field visit occurred. A future completed inspection must contain only actual information and retain the evidence source type.

```http
POST /api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/inspections
Content-Type: application/json
```

```json
{
  "inspection_status": "planned",
  "verification_status": "unverified",
  "observations": [],
  "water_level_observation": null,
  "embankment_condition": null,
  "fish_escape_report": null,
  "mortality_report": null
}
```

A successful response includes a generated `inspection_id`, incident/optional asset links, timestamps and the submitted values. Missing measurements remain null. `inspector_reference` is an external reference, not an authenticated identity. Photo references do not upload files.

## Report

```http
GET /api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/report
```

Returns JSON titled `Exploratory Fisheries Incident Screening Report`, including incident/source facts, asset geometry status, observations, optical candidates, both model streams, disagreement, exposure, findings, priorities, inspection checks, saved inspection records, evidence citations, unavailable measurements and limitations. The existing PDF route serves a static Step 11 case-file artifact; no generated fisheries-report PDF service existed, so this phase provides JSON without creating a second PDF architecture.

## Security limitation

The current application has no Fisheries Officer authentication or authorization. All fisheries mutation routes are disabled by default and return HTTP 503. `GHERPROOF_FISHERIES_WRITES_ENABLED=true` is a trusted-local-development opt-in only; it does not authenticate or authorize users and must not be enabled on a public deployment. No fake user identity is created.
