"""Read-only DHARA event-data manifest services."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import shape
from shapely.validation import explain_validity

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "gherproof"
BOUNDARY_DIR = DATA / "boundaries"
BOUNDARY_PATH = BOUNDARY_DIR / "pallimangal_enclosure.geojson"
BOUNDARY_PROVENANCE_PATH = DATA / "manifests" / "boundary_provenance.json"


def _read(name: str, default):
    path = DATA / "manifests" / name
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def status() -> dict:
    catalogue = _read("event_satellite_catalogue.json", {})
    items = catalogue.get("items", [])
    s1 = [item for item in items if item.get("collection") == "sentinel-1-grd"]
    s2 = [item for item in items if item.get("collection") == "sentinel-2-l2a"]
    event_manifest = _read("event_imagery_manifest.json", {})
    validation = _read("event_imagery_validation.json", {})
    assets = event_manifest.get("records", [])
    recovered = sum(bool(record.get("path")) and (ROOT / record["path"]).is_file() for record in assets)
    verified = sum(record.get("verification_status", record.get("status")) == "verified" for record in assets)
    scene_polarizations: dict[str, set[str]] = {}
    for record in assets:
        if record.get("verification_status", record.get("status")) == "verified":
            scene_polarizations.setdefault(record.get("scene_id", ""), set()).add(record.get("polarization", ""))
    verified_scenes = sum({"VV", "VH"}.issubset(pols) for pols in scene_polarizations.values())
    boundary_status = _read("boundary_provenance.json", {}).get("status") or _read("enclosure_boundary_provenance.json", {}).get("boundary_status", "not_delineated")
    pair_ready = validation.get("pre_post_assessment", {}).get("suitable_for_change_inference") is True
    workflow = "imagery_unavailable" if recovered < 4 else "imagery_downloaded"
    if recovered == 4 and verified == 4 and pair_ready:
        workflow = "imagery_validated"
    if workflow == "imagery_validated" and boundary_status in {"candidate", "under_review"}:
        workflow = "boundary_under_review"
    if workflow == "imagery_validated" and boundary_status == "verified":
        workflow = "boundary_verified"
    if (DATA / "processed" / "event" / "inference_manifest.json").is_file():
        workflow = "inference_complete"
    if (DATA / "processed" / "event" / "area_manifest.json").is_file():
        workflow = "area_analysis_complete"
    return {
        "case_id": "GHERPROOF-SUJATPUR-2026-01",
        "reported_incident_date": "2026-01-14",
        "event_status": "reported_by_news_sources_not_independently_verified",
        "study_geometry_status": catalogue.get("bbox_status", "not_available"),
        "catalogue_search": "complete_for_provisional_bbox_only" if catalogue else "not_run",
        "sentinel1_catalogue_matches": len(s1),
        "sentinel2_catalogue_matches": len(s2),
        "processed_event_observations": verified_scenes,
        "local_flood_inference": "not_available",
        "model_training": "benchmark_completed_not_local_event",
        "event_workflow_state": workflow,
        "recovered_event_assets": recovered,
        "verified_event_assets": verified,
        "boundary_status": boundary_status,
        "pre_post_suitable": pair_ready,
        "model_comparison_available": (DATA / "manifests" / "pretrained_model_comparison.json").is_file(),
        "last_manifest_query_utc": catalogue.get("queried_at_utc"),
    }


def catalogue() -> dict:
    return _read("event_satellite_catalogue.json", {
        "items": [], "bbox_status": "not available", "query_status": "not_run"
    })


def evidence_report() -> dict:
    current = status()
    event_manifest = _read("event_imagery_manifest.json", {})
    validation = _read("event_imagery_validation.json", {})
    return {
        "case_id": "GHERPROOF-SUJATPUR-2026-01",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "location": "Sujatpur Pallimangal Fisheries Enclosure, Monirampur, Jashore, Bangladesh",
        "reported_event": {
            "date": "2026-01-14",
            "status": "reported, not independently verified by this system",
            "sources": [
                "https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore"
            ],
        },
        "satellite_catalogue_status": current,
        "event_imagery_assets": event_manifest.get("records", []),
        "event_imagery_validation": validation.get("pre_post_assessment"),
        "boundary": boundary_record(),
        "processed_observations": [],
        "predicted_spillover_mask": None,
        "affected_area_estimate": None,
        "model_evaluation": None,
        "limitations": [
            "The catalogue query uses a provisional broad locality bounding box, not an authoritative enclosure boundary.",
            "Catalogue matches are not downloaded or processed observations.",
            "No flood mask, local area estimate, model metric, fish-loss estimate, or compensation determination is available.",
            "Satellite imagery alone cannot establish a physical breach point or its cause.",
        ],
    }


def boundary_record() -> dict:
    provenance = _read("boundary_provenance.json", {"status": "not_delineated", "versions": []})
    feature = None
    if BOUNDARY_PATH.is_file():
        feature = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
    return {"status": provenance.get("status", "not_delineated"), "feature": feature,
            "provenance": provenance, "context_image": "/api/gherproof/context/sentinel2",
            "context_bounds_wgs84": _context_bounds()}


def _context_bounds() -> list[list[float]] | None:
    manifest = _read("pre_event_sentinel2_manifest.json", {})
    qc = manifest.get("raster_qc", {})
    bounds = qc.get("crop_bounds")
    if not bounds:
        return None
    try:
        import sys
        raster_env = ROOT / "backend/.venv/Lib/site-packages"
        if raster_env.exists():
            sys.path.append(str(raster_env))
        from rasterio.warp import transform_bounds
        west, south, east, north = transform_bounds(qc["crs"], "EPSG:4326", *bounds, densify_pts=21)
        return [[south, west], [north, east]]
    except Exception:
        return None


def save_boundary(feature: dict) -> dict:
    if not isinstance(feature, dict) or feature.get("type") != "Feature":
        raise ValueError("Boundary must be a GeoJSON Feature")
    geometry_json = feature.get("geometry")
    if not isinstance(geometry_json, dict):
        raise ValueError("Feature geometry is required")
    try:
        geom = shape(geometry_json)
    except Exception as exc:
        raise ValueError("Boundary geometry is not valid GeoJSON") from exc
    if geom.geom_type not in {"Polygon", "MultiPolygon"} or geom.is_empty or not geom.is_valid or geom.area <= 0:
        raise ValueError(f"Boundary geometry must be a valid non-empty polygon: {explain_validity(geom)}")
    minx, miny, maxx, maxy = geom.bounds
    if minx < -180 or maxx > 180 or miny < -90 or maxy > 90:
        raise ValueError("Boundary coordinates must be longitude/latitude in EPSG:4326")
    props = feature.get("properties") or {}
    status = props.get("status")
    allowed = {"candidate", "under_review", "verified"}
    if status not in allowed:
        raise ValueError("status must be candidate, under_review, or verified")
    evidence = props.get("evidence")
    def valid_evidence(item):
        if isinstance(item, str):
            return bool(item.strip())
        return isinstance(item, dict) and isinstance(item.get("description"), str) and bool(item["description"].strip())

    if not isinstance(evidence, list) or not evidence or not all(valid_evidence(x) for x in evidence):
        raise ValueError("At least one supporting evidence item is required")
    reviewer = props.get("reviewer")
    reviewed_at = props.get("reviewed_at")
    confidence = props.get("confidence")
    if status in {"under_review", "verified"}:
        if not isinstance(reviewer, str) or not reviewer.strip() or not reviewed_at:
            raise ValueError("Review states require reviewer and reviewed_at metadata")
        try:
            datetime.fromisoformat(str(reviewed_at).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("reviewed_at must be an ISO-8601 timestamp") from exc
    if confidence not in {"low", "medium", "high"}:
        raise ValueError("confidence must be low, medium, or high")
    old = boundary_record()
    old_status = old.get("status", "not_delineated")
    transitions = {"not_delineated": {"candidate"}, "candidate": {"candidate", "under_review"},
                   "under_review": {"under_review", "verified"}, "verified": {"under_review", "verified"}}
    if status not in transitions.get(old_status, set()):
        raise ValueError(f"Invalid boundary status transition: {old_status} -> {status}")
    if old_status == "verified" and status == "verified" and old.get("feature", {}).get("geometry") != geometry_json:
        raise ValueError("Changing a verified geometry requires moving it back to under_review")
    normalized = {"type": "Feature", "geometry": geometry_json,
                  "properties": {"name": "Pallimangal Fisheries Enclosure boundary trace",
                                 "status": status, "evidence": evidence, "reviewer": reviewer,
                                 "reviewed_at": reviewed_at, "confidence": confidence}}
    BOUNDARY_DIR.mkdir(parents=True, exist_ok=True)
    BOUNDARY_PROVENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    previous = _read("boundary_provenance.json", {"versions": []})
    version = len(previous.get("versions", [])) + 1
    version_dir = BOUNDARY_DIR / "versions"
    version_dir.mkdir(parents=True, exist_ok=True)
    version_file = version_dir / f"pallimangal_boundary_v{version:03d}.geojson"
    record = {"version": version, "status": status, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "reviewer": reviewer, "reviewed_at": reviewed_at, "confidence": confidence,
              "evidence": evidence, "geometry_type": geom.geom_type,
              "geometry_area_degrees_squared": float(geom.area), "source": "human-delineated on contextual/reference map; not authoritative GIS unless supporting evidence explicitly establishes that",
              "geojson_path": str(version_file.relative_to(ROOT)).replace("\\", "/"),
              "verification_rule": "verified requires valid polygon, evidence, reviewer, review timestamp, confidence, and transition from under_review"}
    previous.update(status=status, active_version=version)
    previous.setdefault("versions", []).append(record)
    for path, payload in ((version_file, normalized), (BOUNDARY_PATH, normalized), (BOUNDARY_PROVENANCE_PATH, previous)):
        fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                json.dump(payload, out, indent=2)
                out.write("\n")
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
    return boundary_record()
