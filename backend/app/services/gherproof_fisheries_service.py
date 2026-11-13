"""Persistent fisheries-domain layer over existing, provenance-controlled DHARA evidence."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from app.schemas.gherproof_fisheries import (
    AssetCreate, AssetRecord, ExposureAssessment, FisheriesFinding, FisheriesSummary,
    IncidentCreate, IncidentRecord, InspectionCreate, InspectionRecord,
    InspectionPriority, ModelEvidenceComparison, SatelliteObservation,
)
from app.services import gherproof_screening_service as evidence

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "gherproof" / "fisheries"
DB_PATH = Path(os.environ.get("GHERPROOF_FISHERIES_DB", DATA / "gherproof_fisheries.sqlite3")).expanduser()
INCIDENT_SEED = DATA / "pallimangal_incident.json"
ASSET_SEED = DATA / "pallimangal_asset.json"
DEMO_INCIDENT_ID = "incident-pallimangal-2026-01-14"
PALLIMANGAL_ASSET_ID = "asset-pallimangal-reported"
PROVISIONAL_AOI_ID = "geography-provisional-regional-aoi"
_MIGRATIONS = """
CREATE TABLE IF NOT EXISTS incidents (
 incident_id TEXT PRIMARY KEY, data_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets (
 asset_id TEXT PRIMARY KEY, data_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS incident_assets (
 incident_id TEXT NOT NULL REFERENCES incidents(incident_id), asset_id TEXT NOT NULL REFERENCES assets(asset_id),
 created_at TEXT NOT NULL, PRIMARY KEY(incident_id, asset_id)
);
CREATE TABLE IF NOT EXISTS inspections (
 inspection_id TEXT PRIMARY KEY, incident_id TEXT NOT NULL REFERENCES incidents(incident_id),
 asset_id TEXT REFERENCES assets(asset_id), data_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_inspections_incident_date ON inspections(incident_id, created_at);
CREATE INDEX IF NOT EXISTS idx_inspections_asset ON inspections(asset_id);
PRAGMA user_version = 1;
"""


class FisheriesNotFound(LookupError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10, isolation_level="IMMEDIATE")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.executescript(_MIGRATIONS)
    return connection


def _read_seed(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    # Seed timestamps are assigned on first database initialization; ids and source data are stable.
    return value


def initialize() -> None:
    """Create the small SQLite store and insert source-backed demo records once."""
    with _connect() as con:
        for table, key, path, model in (
            ("incidents", "incident_id", INCIDENT_SEED, IncidentRecord),
            ("assets", "asset_id", ASSET_SEED, AssetRecord),
        ):
            record = _read_seed(path)
            now = _now()
            record.setdefault("created_at", now)
            record.setdefault("updated_at", now)
            validated = model.model_validate(record).model_dump(mode="json")
            con.execute(
                f"INSERT OR IGNORE INTO {table} ({key}, data_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (validated[key], json.dumps(validated, ensure_ascii=False), validated["created_at"], validated["updated_at"]),
            )
        seed_incident = _read_seed(INCIDENT_SEED)
        incident = con.execute("SELECT data_json FROM incidents WHERE incident_id=?", (seed_incident["incident_id"],)).fetchone()
        if incident:
            stored = json.loads(incident["data_json"])
            linked = list(dict.fromkeys([*stored.get("related_asset_ids", []), *seed_incident.get("related_asset_ids", [])]))
            if linked != stored.get("related_asset_ids", []):
                stored["related_asset_ids"] = linked
                stored["updated_at"] = _now()
                con.execute("UPDATE incidents SET data_json=?, updated_at=? WHERE incident_id=?", (json.dumps(stored, ensure_ascii=False), stored["updated_at"], seed_incident["incident_id"]))
        for incident in con.execute("SELECT incident_id, data_json FROM incidents").fetchall():
            for asset_id in json.loads(incident["data_json"]).get("related_asset_ids", []):
                con.execute("INSERT OR IGNORE INTO incident_assets VALUES (?, ?, ?)", (incident["incident_id"], asset_id, _now()))


def _parse_record(row: sqlite3.Row, model: type[IncidentRecord] | type[AssetRecord] | type[InspectionRecord]) -> Any:
    return model.model_validate(json.loads(row["data_json"]))


def _known_evidence_ids() -> set[str]:
    return {r.get("evidence_id", "") for r in evidence.registry().get("records", [])}


def _require_evidence_ids(values: list[str]) -> None:
    missing = sorted(set(values) - _known_evidence_ids())
    if missing:
        raise ValueError(f"unknown DHARA evidence registry reference(s): {', '.join(missing)}")


def _require_asset_ids(values: list[str]) -> None:
    if not values:
        return
    initialize()
    with _connect() as con:
        known = {row[0] for row in con.execute("SELECT asset_id FROM assets").fetchall()}
    missing = sorted(set(values) - known)
    if missing:
        raise ValueError(f"unknown fisheries asset ID(s): {', '.join(missing)}")


def _validate_geometry_reference(asset: AssetCreate) -> None:
    if not asset.geometry_reference:
        return
    if asset.geometry_reference == PROVISIONAL_AOI_ID:
        raise ValueError("the provisional regional search extent cannot be used as a fisheries-asset boundary")
    _require_evidence_ids([asset.geometry_reference])
    try:
        record, path = evidence.geojson_path(asset.geometry_reference)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise ValueError("geometry_reference must resolve to registered GeoJSON evidence") from exc
    if record.get("evidence_category") == "provisional_geographic_reference":
        raise ValueError("provisional regional geography cannot stand in for an asset boundary")
    doc = json.loads(path.read_text(encoding="utf-8"))
    geometries = []
    if doc.get("type") == "FeatureCollection":
        geometries = [feature.get("geometry") for feature in doc.get("features", [])]
    elif doc.get("type") == "Feature":
        geometries = [doc.get("geometry")]
    elif doc.get("type") in ("Polygon", "MultiPolygon"):
        geometries = [doc]
    if not geometries or any(not g or g.get("type") not in ("Polygon", "MultiPolygon") for g in geometries):
        raise ValueError("asset boundary evidence must contain Polygon or MultiPolygon geometry")
    try:
        from shapely.geometry import shape
        if any(not shape(g).is_valid or shape(g).is_empty for g in geometries):
            raise ValueError("asset boundary geometry is empty or invalid")
    except ImportError:
        # Geometry remains provenance referenced; reject rather than claim validation without Shapely.
        raise ValueError("Shapely is required to validate fisheries-asset geometry")


def create_incident(payload: IncidentCreate) -> IncidentRecord:
    _require_evidence_ids(payload.related_evidence_ids + [s.evidence_id for s in payload.reporting_sources if s.evidence_id])
    _require_asset_ids(payload.related_asset_ids)
    incident_id = f"incident-{uuid.uuid4()}"
    now = _now()
    result = IncidentRecord(incident_id=incident_id, created_at=now, updated_at=now, **payload.model_dump())
    initialize()
    with _connect() as con:
        con.execute("INSERT INTO incidents VALUES (?, ?, ?, ?)", (incident_id, result.model_dump_json(), now, now))
        for asset_id in result.related_asset_ids:
            con.execute("INSERT INTO incident_assets VALUES (?, ?, ?)", (incident_id, asset_id, now))
    return result


def list_incidents() -> list[IncidentRecord]:
    initialize()
    with _connect() as con:
        rows = con.execute("SELECT data_json FROM incidents ORDER BY created_at, incident_id").fetchall()
    return [IncidentRecord.model_validate(json.loads(row[0])) for row in rows]


def get_incident(incident_id: str) -> IncidentRecord:
    initialize()
    with _connect() as con:
        row = con.execute("SELECT data_json FROM incidents WHERE incident_id=?", (incident_id,)).fetchone()
    if not row:
        raise FisheriesNotFound("Fisheries incident not found")
    return IncidentRecord.model_validate(json.loads(row[0]))


def create_asset(payload: AssetCreate) -> AssetRecord:
    _validate_geometry_reference(payload)
    _require_evidence_ids([s.evidence_id for s in payload.provenance if s.evidence_id])
    if payload.ownership_or_operator and not any(
        source.claim_status == "verified" and source.reliability in ("field_recorded", "independently_verified")
        for source in payload.provenance
    ):
        raise ValueError("ownership/operator details require a verified, appropriately sourced record")
    if payload.geometry_status == "verified" and not payload.verification_date:
        raise ValueError("verified asset geometry requires a verification date")
    asset_id = f"asset-{uuid.uuid4()}"
    now = _now()
    result = AssetRecord(asset_id=asset_id, created_at=now, updated_at=now, **payload.model_dump())
    initialize()
    with _connect() as con:
        con.execute("INSERT INTO assets VALUES (?, ?, ?, ?)", (asset_id, result.model_dump_json(), now, now))
    return result


def list_assets() -> list[AssetRecord]:
    initialize()
    with _connect() as con:
        rows = con.execute("SELECT data_json FROM assets ORDER BY created_at, asset_id").fetchall()
    return [AssetRecord.model_validate(json.loads(row[0])) for row in rows]


def get_asset(asset_id: str) -> AssetRecord:
    initialize()
    with _connect() as con:
        row = con.execute("SELECT data_json FROM assets WHERE asset_id=?", (asset_id,)).fetchone()
    if not row:
        raise FisheriesNotFound("Fisheries asset not found")
    return AssetRecord.model_validate(json.loads(row[0]))


def link_asset_to_incident(incident_id: str, asset_id: str) -> tuple[IncidentRecord, bool]:
    incident = get_incident(incident_id)
    get_asset(asset_id)
    if asset_id in incident.related_asset_ids:
        return incident, False
    updated_ids = [*incident.related_asset_ids, asset_id]
    now = _now()
    updated_data = incident.model_copy(update={"related_asset_ids": updated_ids, "updated_at": now})
    with _connect() as con:
        con.execute("INSERT INTO incident_assets VALUES (?, ?, ?)", (incident_id, asset_id, now))
        con.execute("UPDATE incidents SET data_json=?, updated_at=? WHERE incident_id=?", (updated_data.model_dump_json(), now, incident_id))
    return updated_data, True


def _assets_for_incident(incident: IncidentRecord) -> list[AssetRecord]:
    return [get_asset(asset_id) for asset_id in incident.related_asset_ids]


def create_inspection(incident_id: str, payload: InspectionCreate) -> InspectionRecord:
    incident = get_incident(incident_id)
    if payload.asset_id:
        get_asset(payload.asset_id)
    if payload.inspector_reference and len(payload.inspector_reference.strip()) < 2:
        raise ValueError("inspector_reference must be a real nonempty reference or omitted")
    _require_evidence_ids([x.evidence_id for x in payload.observations if x.evidence_id])
    inspection_id = f"inspection-{uuid.uuid4()}"
    now = _now()
    result = InspectionRecord(inspection_id=inspection_id, incident_id=incident.incident_id, created_at=now, updated_at=now, **payload.model_dump())
    initialize()
    with _connect() as con:
        con.execute(
            "INSERT INTO inspections VALUES (?, ?, ?, ?, ?, ?)",
            (inspection_id, incident_id, payload.asset_id, result.model_dump_json(), now, now),
        )
    return result


def list_inspections(incident_id: str) -> list[InspectionRecord]:
    get_incident(incident_id)
    with _connect() as con:
        rows = con.execute("SELECT data_json FROM inspections WHERE incident_id=? ORDER BY created_at, inspection_id", (incident_id,)).fetchall()
    return [InspectionRecord.model_validate(json.loads(row[0])) for row in rows]


def _date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None


def observations_for_incident(incident: IncidentRecord) -> list[SatelliteObservation]:
    ids = set(incident.related_evidence_ids)
    records = evidence.registry().get("records", [])
    observations: list[SatelliteObservation] = []
    # Sentinel-1 entries are actual registered RTC observations; retain each acquisition independently.
    for record in records:
        if record.get("evidence_category") != "verified_satellite_observation" or record.get("evidence_id") not in ids:
            continue
        metadata = record.get("metadata") or {}
        file_paths = [f.get("path") for f in (record.get("original_file"), record.get("derived_file")) if f and f.get("availability") == "available" and f.get("path")]
        observations.append(SatelliteObservation(
            observation_id=record["evidence_id"], sensor="Sentinel-1", acquisition_date=_date(record.get("acquisition_date")),
            product_identifier=metadata.get("product_id") or metadata.get("item_id"), relevant_bands=["VV", "VH"],
            processing_method=record.get("processing_methodology") or "Sentinel-1 RTC Gamma0 VV/VH product; see evidence record",
            spatial_coverage=record.get("spatial_coverage"), valid_data_status=record.get("confidence_or_validation_status", "unavailable"),
            evidence_registry_reference=record["evidence_id"], source_file_references=file_paths, limitations=record.get("limitations", []),
        ))
    # S2 is represented as an acquisition-level object linking its registered bands and weak-reference layers.
    s2_records = [r for r in records if r.get("acquisition_date") and r.get("evidence_id", "").startswith(("s2-", "optical-weakref-"))]
    weak_scenes = evidence.weak_reference().get("scenes", [])
    seen: set[str] = set()
    for record in s2_records:
        d = record.get("acquisition_date")
        if d in seen or not any(eid in ids for eid in (record.get("evidence_id"), f"optical-weakref-{d}-weak_reference")):
            continue
        seen.add(d)
        # Once this incident references the date's weak-reference observation, include all registered band/QA derivatives for that same acquisition.
        date_records = [r for r in s2_records if r.get("acquisition_date") == d]
        ids_for_date = [r["evidence_id"] for r in date_records]
        file_paths = [f.get("path") for r in date_records for f in (r.get("original_file"), r.get("derived_file")) if f and f.get("availability") == "available" and f.get("path")]
        scene = next((x for x in weak_scenes if x.get("date") == d), {})
        observations.append(SatelliteObservation(
            observation_id=f"sentinel2-{d}", sensor="Sentinel-2", acquisition_date=_date(d),
            product_identifier=scene.get("item_id") or next((r.get("metadata", {}).get("product_id") or r.get("metadata", {}).get("item_id") for r in date_records if r.get("metadata", {}).get("product_id") or r.get("metadata", {}).get("item_id")), None),
            relevant_bands=sorted({band for r in date_records for band in (r.get("metadata", {}).get("bands") or [])}) or ["B03", "B08", "B11", "SCL"],
            processing_method="Sentinel-2 L2A reflectance and/or Phase 8B optical weak-reference derivatives; per-record methods in registry",
            spatial_coverage=next((r.get("spatial_coverage") for r in date_records if r.get("spatial_coverage")), None),
            valid_data_status="registered optical observation and derived layers; weak-reference classes remain automated indicators",
            evidence_registry_reference=next((r["evidence_id"] for r in date_records if r["evidence_id"] in ids), ids_for_date[0]),
            source_file_references=sorted(set(file_paths)), limitations=["SCL/index products are not field labels or confirmed water."],
        ))
    return sorted(observations, key=lambda item: (item.acquisition_date or date.min, item.sensor))


def _case_temporal_change() -> dict[str, Any]:
    return evidence.weak_reference().get("temporal_change") or {}


def _has_case_optical_pair(incident: IncidentRecord) -> bool:
    ids = set(incident.related_evidence_ids)
    return {
        "optical-weakref-2026-01-10-weak_reference",
        "optical-weakref-2026-01-20-weak_reference",
    }.issubset(ids)


def model_evidence_comparison(incident: IncidentRecord) -> ModelEvidenceComparison:
    comparisons = evidence.comparisons()
    manifest_results = comparisons.get("per_model_acquisition_results", [])
    # Limit output to actual recorded rows and remove non-JSON/large block arrays.
    compact = []
    for row in manifest_results:
        compact.append({k: row.get(k) for k in (
            "model", "sentinel1_date", "sentinel1_relative_orbit", "sentinel1_direction", "sentinel2_date",
            "date_offset_hours", "common_valid_comparison_pixels", "joint_valid_observation_pixels",
            "invalid_or_no_common_data_pixels", "uncertain_reference_pixels_excluded", "weak_reference_agreement",
            "weak_reference_positive_agreement", "weak_reference_negative_agreement",
        ) if k in row})
    related = set(incident.related_evidence_ids)
    if incident.incident_id != DEMO_INCIDENT_ID:
        compact = []
    predictions = {
        model: sorted(x for x in related if x.startswith(f"prediction-{model}-"))
        for model in ("scratch", "pretrained")
    } if incident.incident_id == DEMO_INCIDENT_ID else {}
    optical_ids = sorted(x for x in related if x.startswith("optical-weakref-")) if incident.incident_id == DEMO_INCIDENT_ID else []
    disagreements = [r["evidence_id"] for r in evidence.registry().get("records", []) if r.get("evidence_id", "").startswith("phase8b-") and "all-model_disagreement_codes" in r.get("evidence_id", "")]
    return ModelEvidenceComparison(
        per_acquisition_comparisons=compact,
        model_candidate_evidence_ids=predictions,
        optical_weak_reference_evidence_ids=optical_ids,
        invalid_coverage_by_acquisition=[{k: row[k] for k in ("sentinel1_date", "sentinel1_relative_orbit", "sentinel1_direction", "joint_valid_observation_pixels", "invalid_or_no_common_data_pixels", "optical_observed_but_sar_invalid_pixels", "sar_valid_but_optical_invalid_pixels")} for row in manifest_results if "joint_valid_observation_pixels" in row] if incident.incident_id == DEMO_INCIDENT_ID else [],
        model_disagreement_evidence_ids=disagreements if incident.incident_id == DEMO_INCIDENT_ID else [],
        overall_interpretation=("Pretrained outputs have higher overall agreement with the automated optical weak reference in all four matched comparisons; scratch outputs agree with more weak-water candidates in all four. The class-dependent trade-off does not select a model." if compact else "No model comparison is linked to this incident."),
        uncertainty_reasons=["Optical references are automated SCL/NDWI/MNDWI indicators, not human labels.", "Sentinel-1 and Sentinel-2 acquisition times differ.", "The models are exploratory and have no local field validation.", "Opposite Sentinel-1 orbit geometries remain separate."],
    )


def assess_asset_exposure(asset: AssetRecord, *, temporal: dict[str, Any] | None = None) -> ExposureAssessment:
    limitations = ["No fish-loss, mortality, production-loss, or financial-loss measurement is inferred."]
    if asset.geometry_status == "not_delineated" or not asset.geometry_reference:
        return ExposureAssessment(asset_id=asset.asset_id, status="not_assessable", geometry_status=asset.geometry_status,
            explanation="Asset geometry is not delineated; enclosure-specific overlap with satellite candidates cannot be calculated.",
            limitations=limitations + ["The provisional regional search extent is not an enclosure boundary."])
    if asset.geometry_status in ("candidate", "under_review"):
        return ExposureAssessment(asset_id=asset.asset_id, status="provisional_assessment", geometry_status=asset.geometry_status,
            evidence_ids=[asset.geometry_reference], explanation="Geometry is candidate/under review, so any spatial comparison would remain provisional.",
            limitations=limitations + ["Do not interpret provisional geometry as a verified lease or parcel boundary."])
    if asset.geometry_status == "rejected":
        return ExposureAssessment(asset_id=asset.asset_id, status="not_assessable", geometry_status=asset.geometry_status,
            evidence_ids=[asset.geometry_reference], explanation="The referenced geometry has been rejected and is not used for exposure assessment.", limitations=limitations)
    try:
        _validate_geometry_reference(AssetCreate.model_validate(asset.model_dump(exclude={"asset_id", "created_at", "updated_at"})))
        import rasterio
        from rasterio.mask import mask
        from rasterio.warp import transform_geom
        record, path = evidence.geojson_path(asset.geometry_reference)
        doc = json.loads(path.read_text(encoding="utf-8"))
        features = doc.get("features", []) if doc.get("type") == "FeatureCollection" else [doc] if doc.get("type") == "Feature" else [{"geometry": doc}]
        temporal = temporal or {}
        raster_rel = temporal.get("raster", {}).get("path")
        raster_path = (ROOT / raster_rel).resolve() if raster_rel else None
        if not raster_path or not raster_path.is_file():
            raise FileNotFoundError("registered optical temporal-change raster is unavailable")
        with rasterio.open(raster_path) as ds:
            geometries = [transform_geom("EPSG:4326", ds.crs, f["geometry"]) for f in features if f.get("geometry")]
            data, _ = mask(ds, geometries, crop=True, filled=False)
            values = data[0]
            valid = ~values.mask & (values.data != 0)
            if not valid.any():
                return ExposureAssessment(asset_id=asset.asset_id, status="insufficient_coverage", geometry_status=asset.geometry_status,
                    evidence_ids=[asset.geometry_reference], explanation="No valid temporal-change pixels overlap the verified geometry.", limitations=limitations + ["No overlap is not evidence of no water change."])
            new_water_count = int(((values.data == 2) & valid).sum())
            valid_count = int(valid.sum())
        return ExposureAssessment(asset_id=asset.asset_id, status="assessed", geometry_status=asset.geometry_status,
            candidate_pixel_overlap_count=new_water_count, valid_observation_pixel_count=valid_count,
            evidence_ids=[asset.geometry_reference, "optical-weakref-2026-01-10-to-2026-01-20-temporal_change"],
            explanation="A spatial overlap count was computed from the verified geometry and existing optical temporal-change grid; it is a candidate-pixel overlap only.",
            limitations=limitations + ["Optical candidates do not confirm flooding or enclosure breach.", "No candidate pixels is not a fish-loss or impact estimate."])
    except (ValueError, KeyError, FileNotFoundError, ImportError, OSError):
        return ExposureAssessment(asset_id=asset.asset_id, status="insufficient_coverage", geometry_status=asset.geometry_status,
            evidence_ids=[asset.geometry_reference], explanation="A valid registered geometry and temporal-change raster could not be compared.",
            limitations=limitations + ["See the geometry/evidence registry status before interpreting coverage."])


def findings_for_incident(incident: IncidentRecord) -> list[FisheriesFinding]:
    if incident.incident_id != DEMO_INCIDENT_ID:
        return []
    temporal = _case_temporal_change() if _has_case_optical_pair(incident) else {}
    counts = temporal.get("counts", {})
    raster = temporal.get("raster", {})
    dates = [_date(temporal.get("pre_date")), _date(temporal.get("post_date"))]
    dates = [x for x in dates if x]
    evidence_ids = ["optical-weakref-temporal-temporal_change", "optical-weakref-2026-01-10-weak_reference", "optical-weakref-2026-01-20-weak_reference"]
    # Resolve to evidence ids that actually exist; the manifest raster is not assumed to be registered.
    existing = _known_evidence_ids()
    evidence_ids = [x for x in evidence_ids if x in existing]
    findings: list[FisheriesFinding] = []
    for key, category, label in (
        ("possible_new_water_candidate", "possible_new_water", "possible-new-water"),
        ("possible_water_loss_candidate", "possible_water_loss", "possible-water-loss"),
        ("persistent_water_candidate", "persistent_water_candidate", "persistent-water-candidate"),
    ):
        count = counts.get(key)
        if count is None:
            continue
        findings.append(FisheriesFinding(
            finding_id=f"finding-pallimangal-{label}", incident_id=incident.incident_id, category=category,
            geographic_reference=PROVISIONAL_AOI_ID, evidence_ids=evidence_ids, observation_dates=dates,
            detection_method="Sentinel-2 SCL + NDWI/MNDWI automated weak-reference temporal-change rule",
            evidence_strength="low", validation_status="exploratory_unverified",
            explanation=f"The existing optical weak-reference manifest records {int(count):,} {key.replace('_', ' ')} grid cells across the regional comparison grid.",
            limitations=["This is a regional provisional-grid candidate count, not a village or fisheries-asset finding.", "The dates do not establish incident causality.", "Counts are pixels, not hectares, bighas, or verified water."],
            recommended_verification_action="Review exact site geography and inspect water conditions in the field before attributing this regional signal.",
            candidate_pixel_count=int(count), pixel_resolution_m=float(raster.get("resolution", [None])[0]) if raster.get("resolution") else None,
        ))
    assets = _assets_for_incident(incident)
    for asset in assets:
        exposure = assess_asset_exposure(asset, temporal=temporal if _has_case_optical_pair(incident) else {})
        if exposure.status == "assessed" and (exposure.candidate_pixel_overlap_count or 0) > 0:
            findings.append(FisheriesFinding(
                finding_id=f"finding-{asset.asset_id}-possible-enclosure-exposure", incident_id=incident.incident_id,
                asset_id=asset.asset_id, category="possible_enclosure_exposure", geographic_reference=asset.geometry_reference,
                evidence_ids=exposure.evidence_ids, observation_dates=dates,
                detection_method="Verified asset polygon intersected with existing optical temporal-change candidate raster",
                evidence_strength="low", validation_status="exploratory_unverified",
                explanation=f"The documented raster overlap contains {exposure.candidate_pixel_overlap_count} possible-new-water candidate cells inside the registered verified asset geometry.",
                limitations=exposure.limitations + ["Candidate overlap does not establish flooding, breach, fish escape or damage."],
                recommended_verification_action="Field-check the asset and water conditions before treating candidate overlap as an incident impact.",
                candidate_pixel_count=exposure.candidate_pixel_overlap_count,
                pixel_resolution_m=float(raster.get("resolution", [None])[0]) if raster.get("resolution") else None,
            ))
        elif exposure.status == "insufficient_coverage":
            findings.append(FisheriesFinding(
                finding_id=f"finding-{asset.asset_id}-insufficient-coverage", incident_id=incident.incident_id,
                asset_id=asset.asset_id, category="insufficient_coverage", geographic_reference=asset.geometry_reference,
                evidence_ids=exposure.evidence_ids, observation_dates=dates,
                detection_method="Registered asset geometry and valid optical temporal-change coverage check",
                evidence_strength="not_assessed", validation_status="not_assessable",
                explanation=exposure.explanation, limitations=exposure.limitations,
                recommended_verification_action="Resolve geometry and valid-data coverage before interpreting candidate counts.",
            ))
        if asset.geometry_status == "not_delineated":
            findings.append(FisheriesFinding(
                finding_id=f"finding-{asset.asset_id}-boundary-unresolved", incident_id=incident.incident_id, asset_id=asset.asset_id,
                category="boundary_unresolved", geographic_reference=None, evidence_ids=["reported-event-2026-01-14", PROVISIONAL_AOI_ID],
                observation_dates=[], detection_method="Asset provenance and registered geography status review", evidence_strength="not_assessed",
                validation_status="not_assessable", explanation="The named enclosure has no verified coordinate or boundary; enclosure-specific exposure cannot be assessed.",
                limitations=["Regional AOI is not an enclosure boundary.", "No official parcel, fisheries ID, or field-verified polygon is available."],
                recommended_verification_action="Obtain a GPS location and locally reviewed enclosure boundary or official fisheries/cadastral geometry.",
            ))
    disagreement_ids = [r["evidence_id"] for r in evidence.registry().get("records", []) if "all-model_disagreement_codes" in r.get("evidence_id", "")]
    if disagreement_ids:
        findings.append(FisheriesFinding(
            finding_id="finding-pallimangal-model-disagreement", incident_id=incident.incident_id,
            category="model_disagreement", evidence_ids=disagreement_ids,
            observation_dates=[d for d in (date(2026, 1, 9), date(2026, 1, 12), date(2026, 1, 21), date(2026, 1, 24))],
            detection_method="Existing scratch/pretrained model disagreement rasters; four separate acquisition dates",
            evidence_strength="low", validation_status="exploratory_unverified",
            explanation="Stored model-disagreement layers show locations where the two exploratory models differ; disagreement is not an error probability or evidence of fishery exposure.",
            limitations=["Model readiness is exploratory_only.", "No human reference labels or fisheries asset polygon are available.", "Orbit geometries remain separate."],
            recommended_verification_action="Use disagreement to guide human image review only after the site is geolocated; do not treat it as an operational diagnosis.",
        ))
    findings.append(FisheriesFinding(
        finding_id="finding-pallimangal-requires-field-verification", incident_id=incident.incident_id,
        category="requires_field_verification", asset_id=PALLIMANGAL_ASSET_ID, evidence_ids=["reported-event-2026-01-14"],
        observation_dates=[], detection_method="Reported incident context and missing field verification",
        evidence_strength="not_assessed", validation_status="not_assessable",
        explanation="Source-reported embankment failure has not been independently field verified by this system.",
        limitations=["A news report is not a field observation or confirmed incident record."],
        recommended_verification_action="Record embankment condition, inside/outside water level, adjacent khal condition, photographs, and operator reports with source labels.",
    ))
    return findings


def screening_for_incident(incident_id: str) -> dict[str, Any]:
    incident = get_incident(incident_id)
    observations = observations_for_incident(incident)
    assets = _assets_for_incident(incident)
    temporal = _case_temporal_change() if incident_id == DEMO_INCIDENT_ID and _has_case_optical_pair(incident) else {}
    exposures = [assess_asset_exposure(a, temporal=temporal).model_dump(mode="json") for a in assets]
    counts = temporal.get("counts", {})
    raster = temporal.get("raster", {})
    model_comparison = model_evidence_comparison(incident)
    return {
        "incident_id": incident_id,
        "case_status": "exploratory_regional_investigation" if incident_id == DEMO_INCIDENT_ID else "incident_evidence_not_yet_linked",
        "model_readiness": "exploratory_only", "human_reference_status": "human_review_pending", "impact_quantification": "not_approved",
        "observations": [x.model_dump(mode="json") for x in observations],
        "optical_change_screening": ({
            "status": "available_automated_weak_reference", "pre_date": temporal.get("pre_date"), "post_date": temporal.get("post_date"),
            "candidate_counts_grid_cells": {k: counts.get(k) for k in ("possible_new_water_candidate", "possible_water_loss_candidate", "persistent_water_candidate", "stable_nonwater_candidate", "uncertain_change", "invalid")},
            "pixel_resolution_m": (raster.get("resolution") or [None])[0], "units": "grid_cells; not area",
            "interpretation": "Automated optical screening identified possible water-change candidates between the two dates; these candidates are not confirmed flooding.",
            "evidence_ids": [i for i in ("optical-weakref-2026-01-10-weak_reference", "optical-weakref-2026-01-20-weak_reference") if i in _known_evidence_ids()],
            "limitations": temporal.get("limitations", []),
        } if temporal else {"status": "unavailable_for_incident", "candidate_counts_grid_cells": None, "units": None}),
        "model_evidence": model_comparison.model_dump(mode="json"),
        "asset_exposure": exposures or [{"asset_id": None, "geometry_status": None, "status": "not_assessable", "candidate_pixel_overlap_count": None, "valid_observation_pixel_count": None, "evidence_ids": [], "explanation": "No fisheries asset with supported geometry is linked to this incident.", "limitations": ["No asset boundary or spatial exposure assessment is available."]}],
        "spatial_categories": {"inside_known_enclosure": "not_assessable", "outside_known_enclosure": "not_assessable", "nearby_aquaculture": "not_classified", "agricultural_land_reference": "unavailable", "permanent_water_reference": "unavailable", "unclassified_or_unavailable": "regional candidate counts remain unassigned to these land-use classes"},
        "limitations": ["The provisional AOI is not a village or asset boundary.", "No possible_enclosure_exposure finding is made without supported geometry and valid overlap.", "No fish escape, mortality, production loss, financial loss, or affected-area estimate is available."],
    }


def priorities_for_incident(incident_id: str) -> list[InspectionPriority]:
    incident = get_incident(incident_id)
    if incident_id != DEMO_INCIDENT_ID:
        return [InspectionPriority(priority="not_assessable", recommended_action="Link verified source or field evidence before prioritising this incident.", rationale="No fisheries screening evidence is linked to this incident.", missing_information=["Source evidence", "Location and asset geometry"], fisheries_officer_checks=[])]
    return [
        InspectionPriority(
            priority="priority_1_review", recommended_action="Verify the reported site location and identify the enclosure and adjacent embankment on the ground or from an authoritative fisheries/cadastral record.",
            rationale="The incident is source-reported and describes an embankment failure, but no coordinates or enclosure boundary are available. This is an information-resolution priority, not an emergency action or diagnosis.",
            supporting_evidence_ids=["reported-event-2026-01-14", PROVISIONAL_AOI_ID],
            missing_information=["Verified incident record/date", "GPS location", "Verified enclosure/embankment geometry", "Official affected-locality/jurisdiction confirmation"],
            fisheries_officer_checks=["Confirm the enclosure identity and mouza parcel/fisheries identifier.", "Record embankment condition and photographs if an inspection occurs.", "Record water levels inside and outside the enclosure with time and reference point."],
        ),
        InspectionPriority(
            priority="priority_2_review", recommended_action="If the reported site is located, collect actual field inspection records before interpreting regional candidate signals as enclosure exposure.",
            rationale="The optical change and Sentinel-1 model products are regional and exploratory; the asset cannot be spatially assessed.",
            supporting_evidence_ids=["optical-weakref-2026-01-10-weak_reference", "optical-weakref-2026-01-20-weak_reference"],
            missing_information=["Field observations", "Boundary-to-raster overlap", "Operator reports separately attributed from direct observations"],
            fisheries_officer_checks=["Check adjacent khal condition and possible external water pathways.", "Record any fish escape or mortality as a report unless independently observed.", "Photograph relevant embankment segments and note camera location/time."],
        ),
    ]


def summary_for_incident(incident_id: str) -> FisheriesSummary:
    incident = get_incident(incident_id)
    screening = screening_for_incident(incident_id)
    if incident_id != DEMO_INCIDENT_ID:
        return FisheriesSummary(incident_id=incident_id, case_status="exploratory_regional_investigation",
            what_happened=f"{incident.description} (status: {incident.incident_status}).",
            satellite_screening="No satellite findings are associated with this incident record.",
            inspection_needed="Incident location and fisheries-asset exposure have not been assessed.",
            recommended_checks=["Verify the report and site location before drawing operational conclusions."],
            unknowns=["Field verification", "Asset geometry", "Fish escape", "Mortality", "Production and financial impacts"],
            evidence_ids=incident.related_evidence_ids)
    counts = screening["optical_change_screening"].get("candidate_counts_grid_cells") or {}
    count = counts.get("possible_new_water_candidate")
    satellite_text = (f"Automated optical screening recorded {count:,} possible-new-water candidate grid cells between 2026-01-10 and 2026-01-20; these are not confirmed flooding." if isinstance(count, int) else "No optical temporal-change count is available.")
    return FisheriesSummary(
        incident_id=incident_id, case_status="exploratory_regional_investigation",
        what_happened="News accounts report a southern embankment failure associated with Pallimangal Fisheries Enclosure around January 14, 2026. The date is inferred from publication context; the event is not independently verified.",
        satellite_screening=satellite_text,
        inspection_needed="Exact enclosure-specific exposure is not assessable because the Pallimangal boundary is not delineated. Regional candidates cannot be assigned to the enclosure or named village.",
        recommended_checks=["Confirm the enclosure identity and location.", "Inspect embankment condition and adjacent khal.", "Record water levels inside and outside the enclosure with a measurement reference.", "Separate direct observations from operator reports; record fish escape or mortality only if actually observed or reported.", "Capture georeferenced photographs with timestamp."],
        unknowns=["Verified Pallimangal boundary", "Confirmed breach position", "Confirmed fish escape", "Fish mortality", "Production loss", "Financial loss", "Affected-cropland area", "Reconciled source-reported damage claims", "Local model accuracy", "Field verification"],
        evidence_ids=["reported-event-2026-01-14", PROVISIONAL_AOI_ID, "optical-weakref-2026-01-10-weak_reference", "optical-weakref-2026-01-20-weak_reference"],
    )


def build_investigation_report(incident_id: str) -> dict[str, Any]:
    incident = get_incident(incident_id)
    screening = screening_for_incident(incident_id)
    findings = findings_for_incident(incident)
    priorities = priorities_for_incident(incident_id)
    inspections = list_inspections(incident_id)
    assets = _assets_for_incident(incident)
    context_path = ROOT / "data/gherproof/manifests/fisheries_context_manifest.json"
    try:
        fisheries_context = json.loads(context_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        fisheries_context = {"status": "historical_context_manifest_unavailable", "limitations": ["No supplementary fisheries-context calculations are registered."]}
    return {
        "title": "DHARA — Pallimangal Fisheries Incident Screening Case Study", "report_type": "exploratory_regional_investigation",
        "generated_at_utc": _now(), "incident": incident.model_dump(mode="json"),
        "study_area_map": {"evidence_id": "geography-provisional-regional-aoi", "status": "provisional_regional_search_extent", "not_an_enclosure_boundary": True, "candidate_change_layer_id": "optical-weakref-temporal-temporal_change"},
        "fisheries_context": fisheries_context,
        "fisheries_assets": [a.model_dump(mode="json") for a in assets],
        "satellite_observations": screening["observations"], "water_change_screening": screening["optical_change_screening"],
        "ai_screening": screening["model_evidence"], "findings": [f.model_dump(mode="json") for f in findings],
        "asset_exposure": screening["asset_exposure"], "inspection_priorities": [p.model_dump(mode="json") for p in priorities],
        "recommended_inspection_checks": summary_for_incident(incident_id).recommended_checks,
        "evidence_sources": [source.model_dump(mode="json") for source in incident.reporting_sources],
        "field_inspection_records": [i.model_dump(mode="json") for i in inspections],
        "unavailable_measurements": {"fish_escape": None, "fish_mortality": None, "production_loss": None, "financial_loss": None, "affected_area": None, "confirmed_breach_location": None},
        "readiness": {"case_status": "exploratory_regional_investigation", "model_readiness": "exploratory_only", "human_reference_status": "human_review_pending", "impact_quantification": "not_approved", "pallimangal_geometry_status": "not_delineated"},
        "limitations": screening["limitations"] + ["No news-reported impact figure has been converted into a measurement."],
    }
