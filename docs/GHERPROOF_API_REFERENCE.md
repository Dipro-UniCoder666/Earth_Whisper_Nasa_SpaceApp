# GherProof Regional Screening API Reference

Base path: `/api/gherproof`. This API is read-only for evidence products. The existing `/boundary` review routes remain available for their prior human geometry workflow. No impact-estimate route is registered.

Every response is JSON unless noted. Layer files are GeoTIFF downloads; clips are in-memory GeoTIFFs. Registry and report JSON are generated from the manifests under `data/gherproof/manifests/`.

## Endpoints

| Method / route | Purpose | Key query parameters |
|---|---|---|
| `GET /status` | Backward-compatible event status plus regional readiness fields. | none |
| `GET /screening/status` | Regional evidence readiness only. | none |
| `GET /evidence` | Paginated registry. | `category`, `status`, `acquisition_date`, `offset` (≥0), `limit` (1–500) |
| `GET /scenes` | Processed S1/S2 acquisition metadata and separate pair eligibility groups. | none |
| `GET /predictions` | Separate checkpoint metadata, model prediction layers, and disagreement. | `model=scratch|pretrained` optional |
| `GET /optical` | S2 reflectance/index/SCL/reference layers and SAR/optical comparisons. | none |
| `GET /coverage` | Provisional geography and per-observation raster-scope metadata. | none |
| `GET /limitations` | Readiness and explicit restrictions. | none |
| `GET /layers` | List available GeoTIFF assets with metadata/download links. | none |
| `GET /layers/{evidence_id}` | Raster metadata: CRS, bounds, transform-derived resolution, dimensions, bands, NoData and checksum. | `asset=derived|original` (default derived) |
| `GET /layers/{evidence_id}/file` | Download registered original or derived GeoTIFF. | `asset=derived|original` |
| `GET /layers/{evidence_id}/clip` | Rectangular spatial crop, preserving source CRS and NoData/mask. | required `bbox=west,south,east,north` in EPSG:4326; max 4 million pixels; optional `asset` |
| `GET /geography/{evidence_id}` | Validated registered GeoJSON. | registry evidence ID only |
| `GET /reports` | Existing report index and evidence summary. | none |
| `GET /reports/files/{name}` | Download allowlisted Phase 4B–7C and method reports. | fixed allowlist only |
| `GET /reports/summary` | Generated machine-readable screening report. | none |
| `GET /reports/summary.md` | Generated Markdown screening report. | none |

The model state is always `exploratory_only` and local labels are `human_review_pending` in the current data. `GET /status` retains the legacy event fields used by the existing page and adds the regional contract; callers needing only Phase 8 fields can use `/screening/status`.

## Evidence record schema

Each `/evidence` record follows this structure:

```json
{
  "evidence_id": "prediction-scratch-2026-01-12-probability",
  "evidence_category": "model_prediction",
  "title": "scratch water probability 2026-01-12",
  "source_dataset": "S1A_IW_GRDH_..._rtc",
  "acquisition_date": "2026-01-12",
  "processing_date": "2026-11-13",
  "spatial_coverage": {"crs": "EPSG:32645", "resolution_m": 10},
  "crs": "EPSG:32645",
  "original_file": null,
  "derived_file": {"path": "data/gherproof/processed/...tif", "availability": "available", "sha256": "..."},
  "confidence_or_validation_status": "exploratory",
  "processing_methodology": "...",
  "limitations": ["Prediction is not a measured water observation."],
  "source_provenance": ["data/gherproof/manifests/phase7_inference_manifest.json"],
  "metadata": {"model": "scratch", "threshold": 0.5}
}
```

Evidence categories are `verified_satellite_observation`, `catalogue_metadata`, `derived_satellite_measurement`, `model_prediction`, `optical_reference_interpretation`, `news_reported_event`, `provisional_geographic_reference`, and `human_verified_evidence`. Status is one of `verified`, `derived`, `exploratory`, `provisional`, `unavailable`, or `under_review`. A `verified` raster does not establish flood interpretation.

## Example calls and responses

```http
GET /api/gherproof/screening/status
```

```json
{
  "project_status": "regional_evidence_screening_ready",
  "model_readiness": "exploratory_only",
  "geographic_readiness": "provisional_regional_search_extent; site_and_village_boundaries_unverified",
  "local_validation_status": "human_review_pending",
  "impact_quantification": "not_approved",
  "satellite_acquisitions": {
    "sentinel1_rtc_validated_observations": 6,
    "sentinel1_grd_processed_scenes": 0
  }
}
```

```http
GET /api/gherproof/evidence?category=model_prediction&limit=2
GET /api/gherproof/layers/prediction-scratch-2026-01-12-probability
GET /api/gherproof/layers/prediction-scratch-2026-01-12-probability/clip?bbox=89.25,22.95,89.27,22.97
```

The clip bbox is validated in EPSG:4326, transformed to the raster CRS, intersected with the raster, and constrained to 4 million pixels. It returns 404 for unregistered/missing products, 413 when over the pixel limit, and 422 for invalid or nonintersecting bounds. Raster assets with no CRS cannot be clipped geographically. Existing GRD records are catalogue metadata and are not registered as downloadable processed rasters.

## Status and layer ordering for maps

Suggested frontend layer order:

1. Provisional regional AOI outline (status `provisional`).
2. Sentinel-1 RTC VV/VH or Sentinel-2 reflectance/index layers (status `verified` or `derived`, according to record).
3. SCL/validity masks (data-quality overlays, not labels).
4. Model probability layers, selected individually (status `exploratory`).
5. Model disagreement layers (status `exploratory`, separate overlay).
6. SAR/optical comparison codes (status `exploratory`).

Do not display a selected model as “the correct model”; do not merge model outputs. Preserve NoData transparency and show status badge + evidence ID + source/date for each layer. The AOI layer does not provide village outlines.

## Error contract

Errors are JSON with a `detail` string. Common status codes: `404` evidence/file/report missing; `413` clip too large; `422` invalid query, category, path, GeoJSON or clip bounds; `503` raster library unavailable. No stack traces or provider credentials are returned. `GET /layers` excludes unavailable products; `/evidence` retains records with availability metadata so missing data remains explicit.

## OpenAPI

FastAPI OpenAPI is available from the existing application at `/openapi.json` and `/docs`. The Pydantic contracts live in `backend/app/schemas/gherproof_evidence.py`.
