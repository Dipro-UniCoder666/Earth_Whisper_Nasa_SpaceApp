# GherProof Phase 8 — Evidence-Aware Regional Screening and Backend Finalisation

**Status:** Complete for evidence registry, read-only regional screening APIs, and backend verification. This phase does not approve operational waterlogging diagnoses, local model claims, or impact quantification.

## 1. Scope and preservation

Phase 8 adds a manifest-backed evidence registry and regional screening API for existing GherProof products. It preserves the prior event routes and boundary-review workflow. No frontend source, model weights, Sandhya or Monda project files, DELTAQ archive, or training outputs were intentionally changed as part of this phase. Existing repository modifications from earlier phases remain in the working tree.

The Phase 4B–7C reports and associated availability, raster-QC, inference, radiometric-compatibility, optical, and human-annotation manifests were reviewed as inputs to the registry. Registry presence means an artifact is inventoried; it does not imply scientific suitability or independent validation.

## 2. Evidence inventory

Generated files:

- `data/gherproof/manifests/evidence_registry.json`
- `data/gherproof/manifests/phase8_data_availability.json`

The current registry contains **135 records**:

| Evidence category | Records | Interpretation |
|---|---:|---|
| Verified satellite observation | 6 | Sentinel-1 RTC observation products listed in the current registry, including limited local January 7/19 clips. |
| Derived satellite measurement | 87 | Processed radar/optical measurements and derived layers; not water labels. |
| Model prediction | 34 | Checkpoints and generated probability, mask, uncertainty, and model-disagreement layers. |
| Catalogue metadata | 4 | Sentinel-1 GRD catalogue/counterpart metadata; no GRD scenes are locally processed. |
| Optical reference interpretation | 1 | Human annotation package, still under review. |
| Provisional geographic reference | 1 | Regional search geography; not an authoritative village or enclosure boundary. |
| News-reported event | 1 | Reported incident metadata, not a remotely verified impact boundary. |
| Human-verified evidence | 1 | Explicitly unavailable pending completion of reference labeling. |

The generated file inventory found **133 available file references**, **0 unavailable references**, **0 invalid paths**, and **0 checksum mismatches**. Two evidence records are contextual/unavailable-as-file records rather than missing file references (event report and human-label evidence). This is an inventory/checksum result, not a scientific quality score.

## 3. Satellite and derived evidence currently represented

### Sentinel-1

The regional RTC inventory has six acquisition dates: **2026-01-07, 2026-01-09, 2026-01-12, 2026-01-19, 2026-01-21, and 2026-01-24**. Four scenes are the Phase 7 regional inference pair inputs (January 9, 12, 21, and 24). January 7/19 records refer to limited local Phase 4B clips. They must not be treated as equivalent full regional coverage: Phase 6B separately reported a January 7 VV read failure for its broader-region extraction. The dataset contains **zero fully processed Sentinel-1 GRD scenes**.

RTC and GRD processing products are distinct measurement/processing streams. The registry keeps them separate, and the Phase 7 model predictions are not retroactively treated as GRD-trained model validation for local conditions.

### Sentinel-2

The availability manifest lists **13 SCL dates** from January 3 through January 30, 2026. The current reflectance/index stack has **two dates: January 10 and January 20**. SCL availability does not mean a complete optical reflectance product exists for each listed date. Optical indices and classification masks are supporting evidence with their own quality constraints, not ground truth.

### Model outputs and local labels

The inventory includes **two checkpoints**, **24 probability/mask/uncertainty layers**, and **8 model-disagreement layers**. The local model readiness is **`exploratory_only`**. Human review remains **`human_review_pending`**: the annotation workflow has 450 sampled locations and 900 pre/post label slots, with **0 completed labels**. Benchmark results in earlier reports remain benchmark-only; Phase 8 adds no local accuracy, calibration, or event-performance result.

## 4. Geography, event interpretation, and limitations

The current geography is provisional. There are no authoritative village boundaries and no verified Pallimangal enclosure boundary in this Phase 8 inventory. A regional raster footprint or approximate geolocation cannot substitute for cadastral or field-verified geometry. The January incident is represented as a reported event, not as confirmed satellite-delineated inundation.

The evidence does not support an affected-area estimate, fish-loss estimate, embankment-failure diagnosis, or operational drainage-failure finding. No such endpoint is provided. Do not interpret raw backscatter, model probability, disagreement, optical indices, or catalogue presence as confirmed water extent. The January 7/19 clip coverage and January 7 regional VV issue must remain visible in downstream evidence displays.

## 5. Backend implementation

Added schemas and services:

- `backend/app/schemas/gherproof_evidence.py`
- `backend/app/services/gherproof_screening_service.py`
- `backend/app/services/gherproof_report_service.py`

Extended `backend/app/api/gherproof.py` while retaining legacy event and boundary routes. The regional endpoints provide:

| Route | Function |
|---|---|
| `GET /api/gherproof/screening/status` | Data and scientific-readiness summary. |
| `GET /api/gherproof/evidence` | Filtered, paginated registry records. |
| `GET /api/gherproof/scenes` | Acquisition-level sensor inventory and scope notes. |
| `GET /api/gherproof/predictions` | Separate scratch/pretrained model outputs. |
| `GET /api/gherproof/optical` | Optical layers and separate SAR/optical comparison records. |
| `GET /api/gherproof/coverage` | Coverage/readiness summaries by evidence stream. |
| `GET /api/gherproof/limitations` | Explicit scientific and spatial limitations. |
| `GET /api/gherproof/layers` | Registered raster layer catalog. |
| `GET /api/gherproof/layers/{evidence_id}` | Registered layer metadata. |
| `GET /api/gherproof/layers/{evidence_id}/file` | Registered GeoTIFF access. |
| `GET /api/gherproof/layers/{evidence_id}/clip` | Bounded EPSG:4326 bbox clipping to GeoTIFF, with CRS/nodata/mask preserved. |
| `GET /api/gherproof/geography/{evidence_id}` | Registered and geometry-validated GeoJSON. |
| `GET /api/gherproof/reports` and `/reports/files/{name}` | Allowlisted report index and file access. |
| `GET /api/gherproof/reports/summary` and `/summary.md` | Generated evidence-aware summary. |

The legacy `/status`, `/catalogue`, `/evidence-report`, `/boundary`, and Sentinel-2 context routes remain available. There is no impact-area or drainage-failure endpoint. The API reference and frontend contract are documented separately in `docs/GHERPROOF_API_REFERENCE.md` and `docs/GHERPROOF_FRONTEND_INTEGRATION_CONTRACT.md`; evidence class meanings are in `docs/GHERPROOF_EVIDENCE_METHODOLOGY.md`.

## 6. Verification

The Phase 8 test run exercised the new registry/API behavior alongside the related Phase 7C, 7B, 7 input, legacy GherProof, boundary, CDSE-auth, event-imagery, and Planetary Computer tests:

**66 passed, 3 warnings.** The warnings were deprecation notices from Starlette/httpx and `NotGeoreferencedWarning` from synthetic test fixtures; no test failed. Tests cover registry completeness and file integrity, backward-compatible status fields, evidence filtering, scene/model/optical separation, raster metadata and checksums, invalid or unavailable layers, bounded clipping, GeoJSON validation, report allowlisting, and the absence of an impact endpoint.

Reproduce from the repository root in PowerShell:

```powershell
Push-Location backend
.venv/Scripts/python.exe -m pytest --basetemp ../tmp/gherproof_pytest_phase8 tests/test_gherproof_phase8.py tests/test_gherproof_phase7c.py tests/test_gherproof_phase7b.py tests/test_gherproof_phase7_inputs.py tests/test_gherproof.py tests/test_gherproof_boundary.py tests/test_gherproof_boundary_api.py tests/test_gherproof_cdse_auth.py tests/test_gherproof_event_imagery.py tests/test_gherproof_planetary_computer.py -q
Pop-Location
```

Regenerate the registry and availability snapshot with:

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase8/build_evidence_registry.py
```

The evidence registry is derived from existing manifests and files. Regeneration updates its timestamp and should be followed by a diff/checksum review before committing.

## 7. Readiness decision

**CONDITIONAL GO** for evidence-aware regional screening and human-reference collection. The API is ready to expose clearly separated observations, derived layers, model outputs, provisional geography, and limitations. Model validation, waterlogging labels, authoritative boundaries, and impact quantification are not ready. Complete human labeling and independent review, confirm reference geometry, and resolve the limited January 7/19 coverage caveats before drawing event-specific conclusions.
