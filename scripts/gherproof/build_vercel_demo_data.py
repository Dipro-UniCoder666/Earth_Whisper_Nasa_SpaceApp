"""Build the lightweight, static DHARA data package used by the Vercel demo.

Run from the repository root with backend/.venv/Scripts/python.exe. The script
reads registered local outputs only; it does not run satellite processing or ML.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("GHERPROOF_FISHERIES_DB", str(Path(os.environ.get("TEMP", "/tmp")) / "dhara-vercel-demo.sqlite3"))

from app.api.gherproof import get_layer_preview  # noqa: E402
from app.services import gherproof_fisheries_service as fisheries  # noqa: E402
from app.services import gherproof_screening_service as screening  # noqa: E402
from app.services import gherproof_service as service  # noqa: E402
import rasterio  # noqa: E402
from rasterio.warp import transform_bounds  # noqa: E402

OUT_DATA = ROOT / "app/public/data/dhara-demo.json"
OUT_EVIDENCE = ROOT / "app/public/data/dhara-evidence-report.json"
OUT_PREVIEWS = ROOT / "app/public/images/dhara-demo"
INCIDENT_ID = fisheries.DEMO_INCIDENT_ID


def jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def layer_list() -> list[dict[str, Any]]:
    output = []
    card_ids = {
        "s2-true-colour-2026-01-10", "s2-true-colour-2026-01-20",
        "s2-2026-01-10-B08", "s2-2026-01-20-B08",
        "prediction-scratch-2026-01-12-probability", "prediction-pretrained-2026-01-12-probability",
        "optical-weakref-temporal-temporal_change",
        "disagreement-disagreement_2026-01-12_2026-01-24_rel12_ascending-xor",
        "clark-2022-aquaculture-context", "worldcover-2021-landcover-context",
        "nisar-gcov-2026-10-23-track170-ascending-validated",
        "nisar-gcov-2026-11-04-track170-ascending-validated",
        "nisar-gcov-change-2026-10-23-to-2026-11-04-track170",
    }
    for record in screening.registry().get("records", []):
        asset = record.get("derived_file") or {}
        path = asset.get("path", "")
        if asset.get("availability") != "available" or not path.lower().endswith((".tif", ".tiff")):
            continue
        evidence_id = record.get("evidence_id", "")
        category = record.get("evidence_category", "")
        in_map_selector = (
            category == "verified_satellite_observation"
            or evidence_id in card_ids
            or evidence_id.startswith("nisar-gcov-change-")
            or (category in {"model_prediction", "model_comparison", "uncertainty_layer", "optical_weak_reference"}
                and any(token in evidence_id for token in ("2026-01-12", "temporal_change", "disagreement-")))
        )
        if not in_map_selector:
            continue
        output.append({
            "evidence_id": evidence_id,
            "asset": "derived",
            "title": record.get("title", record["evidence_id"]),
            "status": record.get("confidence_or_validation_status", "unknown"),
            "evidence_category": category or "unknown",
            "url": "",
            "metadata_url": "",
            "crs": record.get("crs"),
            "acquisition_date": record.get("acquisition_date"),
            "sha256": asset.get("sha256"),
        })
    return output


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


async def stream_response(response: Any) -> bytes:
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    return b"".join(chunks)


async def create_preview(layer: dict[str, Any], band: int = 1) -> tuple[str, dict[str, Any]]:
    record, path = screening.raster_path(layer["evidence_id"], "derived")
    with rasterio.open(path) as dataset:
        if not dataset.crs:
            raise ValueError(f"Missing CRS for {layer['evidence_id']}")
        bounds = transform_bounds(dataset.crs, "EPSG:4326", *dataset.bounds, densify_pts=21)
    bbox = ",".join(f"{value:.9f}" for value in bounds)
    rgb = layer["evidence_id"].startswith("s2-true-colour-") or layer["evidence_id"] in {"s2-2026-01-10-B08", "s2-2026-01-20-B08"}
    response = get_layer_preview(layer["evidence_id"], bbox, band, 720, "derived", rgb)
    body = await stream_response(response)
    name = f"{safe_name(layer['evidence_id'])}--b{band}.png"
    output = OUT_PREVIEWS / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(body)
    return f"/images/dhara-demo/{name}", {
        "path": f"/images/dhara-demo/{name}",
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "source_raster": str(path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": (record.get("derived_file") or {}).get("sha256"),
        "display_bounds_wgs84": response.headers.get("X-Preview-Bounds-WGS84"),
        "band": band,
        "rgb": rgb,
        "display_only": True,
    }


async def main() -> None:
    fisheries.initialize()
    records = screening.evidence_list(limit=500)
    layers = layer_list()
    metadata: dict[str, dict[str, Any]] = {}
    previews: dict[str, str] = {}
    preview_bounds: dict[str, str] = {}
    preview_manifest: dict[str, Any] = {}
    for layer in layers:
        try:
            metadata[layer["evidence_id"]] = screening.raster_metadata(layer["evidence_id"], "derived")
            url, manifest = await create_preview(layer, 1)
            previews[f"{layer['evidence_id']}|1"] = url
            preview_bounds[f"{layer['evidence_id']}|1"] = manifest["display_bounds_wgs84"]
            preview_manifest[f"{layer['evidence_id']}|1"] = manifest
            # NISAR GCOV rasters store HHHH and HVHV in bands 1 and 2.
            if layer["evidence_id"].startswith("nisar-gcov-") and "-change-" not in layer["evidence_id"]:
                url2, manifest2 = await create_preview(layer, 2)
                previews[f"{layer['evidence_id']}|2"] = url2
                preview_bounds[f"{layer['evidence_id']}|2"] = manifest2["display_bounds_wgs84"]
                preview_manifest[f"{layer['evidence_id']}|2"] = manifest2
        except Exception as error:  # Keep the row; the client presents it as unavailable.
            preview_manifest[f"{layer['evidence_id']}|1"] = {"error": str(error)}

    aoi_path = ROOT / "data/gherproof/regional/six_village_regional_search_extent.geojson"
    geography = json.loads(aoi_path.read_text(encoding="utf-8")) if aoi_path.is_file() else None
    incident = fisheries.get_incident(INCIDENT_ID)
    screening_result = fisheries.screening_for_incident(INCIDENT_ID)
    report = fisheries.build_investigation_report(INCIDENT_ID)
    demo = {
        "mode": "prepared_static_demo",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Existing local DHARA evidence registry and registered processed outputs; no new processing or inference was run.",
        "limitations": [
            "Static prepared snapshot; it does not connect to or imply availability of a hosted FastAPI service.",
            "No Pallimangal enclosure boundary is established; the mapped search area is provisional.",
            "Optical candidate counts are grid cells, not area or confirmed flood observations.",
            "Model outputs remain exploratory, separately displayed, and not locally validated.",
            "NISAR observations are later 2026 regional data, not evidence for the January incident.",
        ],
        "previews": previews,
        "preview_bounds": preview_bounds,
        "layer_metadata": metadata,
        "evidence_report_url": "/data/dhara-evidence-report.json",
    }
    payload = {
        "status": {**service.status(), **screening.screening_status()},
        "evidence": records,
        "layers": {"count": len(layers), "layers": layers},
        "scenes": screening.scenes(),
        "predictions": screening.predictions(),
        "weakReference": screening.weak_reference(),
        "comparisons": screening.comparisons(),
        "coverage": screening.coverage(),
        "geography": geography,
        "fisheriesScreening": screening_result,
        "fisheriesSummary": jsonable(fisheries.summary_for_incident(INCIDENT_ID)),
        "fisheriesFindings": {"incident_id": INCIDENT_ID, "findings": jsonable(fisheries.findings_for_incident(incident))},
        "fisheriesPriorities": {"incident_id": INCIDENT_ID, "priorities": jsonable(fisheries.priorities_for_incident(INCIDENT_ID))},
        "report": jsonable(report),
        "demo": demo,
    }
    OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
    OUT_DATA.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    OUT_EVIDENCE.write_text(json.dumps(service.evidence_report(), ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "generated_at_utc": demo["generated_at_utc"],
        "data_json": {"path": str(OUT_DATA.relative_to(ROOT)).replace("\\", "/"), "bytes": OUT_DATA.stat().st_size, "sha256": hashlib.sha256(OUT_DATA.read_bytes()).hexdigest()},
        "evidence_report": {"path": str(OUT_EVIDENCE.relative_to(ROOT)).replace("\\", "/"), "bytes": OUT_EVIDENCE.stat().st_size, "sha256": hashlib.sha256(OUT_EVIDENCE.read_bytes()).hexdigest()},
        "preview_count": len(previews),
        "preview_manifest": preview_manifest,
        "source_evidence_record_count": len(records["records"]),
        "source_layer_count": len(layers),
        "incident_id": INCIDENT_ID,
        "boundary_status": "not_delineated",
        "no_processing_or_model_inference_run": True,
    }
    manifest_path = ROOT / "app/public/data/dhara-demo-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    referenced = {OUT_PREVIEWS / Path(url).name for url in previews.values()}
    for existing in OUT_PREVIEWS.glob("*.png"):
        if existing not in referenced:
            existing.unlink()
    print(json.dumps({"data_bytes": OUT_DATA.stat().st_size, "evidence_report_bytes": OUT_EVIDENCE.stat().st_size, "layers": len(layers), "previews": len(previews), "preview_errors": sum("error" in item for item in preview_manifest.values()), "manifest": str(manifest_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
