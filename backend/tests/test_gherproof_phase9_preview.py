from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.api.gherproof import get_evidence, get_layers
from app.main import app
from app.schemas.gherproof_evidence import EvidenceListResponse

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)


def _regional_bbox() -> str:
    geo = json.loads((ROOT / "data/gherproof/regional/six_village_regional_search_extent.geojson").read_text())
    points: list[list[float]] = []

    def walk(value):
        if isinstance(value, list) and len(value) >= 2 and isinstance(value[0], (int, float)):
            points.append(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for feature in geo.get("features", []):
        walk(feature["geometry"]["coordinates"])
    assert points, "registered provisional AOI has coordinates"
    return ",".join(str(value) for value in (min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)))


def test_registered_sentinel1_preview_returns_georeferenced_png():
    response = client.get("/api/gherproof/layers/s1-rtc-2026-01-12/preview.png", params={"bbox": _regional_bbox(), "width": 600})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert response.headers["x-evidence-id"] == "s1-rtc-2026-01-12"
    assert len(response.headers["x-preview-bounds-wgs84"].split(",")) == 4


def test_categorical_weak_reference_preview_handles_integer_nodata():
    response = client.get("/api/gherproof/layers/optical-weakref-2026-01-10-weak_reference/preview.png", params={"bbox": _regional_bbox(), "width": 400})
    assert response.status_code == 200
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_temporal_change_preview_uses_distinct_candidate_and_uncertainty_colours():
    response = client.get(
        "/api/gherproof/layers/optical-weakref-temporal-temporal_change/preview.png",
        params={"bbox": _regional_bbox(), "width": 700},
    )
    assert response.status_code == 200
    colors = set(Image.open(BytesIO(response.content)).convert("RGBA").getdata())
    assert (56, 199, 229, 225) in colors  # possible increase in water indicators
    assert (232, 76, 176, 225) in colors  # possible decrease in water indicators
    assert (151, 158, 165, 195) in colors  # uncertain change


def test_registered_sentinel2_false_colour_rgb_preview():
    response = client.get(
        "/api/gherproof/layers/s2-2026-01-10-B08/preview.png",
        params={"bbox": _regional_bbox(), "width": 500, "rgb": "true"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert "S2 false-color B08/B04/B03" in response.headers["x-preview-display"]


def test_registered_sentinel2_true_colour_preview_uses_b04_b03_b02():
    response = client.get(
        "/api/gherproof/layers/s2-true-colour-2026-01-10/preview.png",
        params={"bbox": _regional_bbox(), "width": 500, "rgb": "true"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert "S2 true-colour RGB B04/B03/B02" in response.headers["x-preview-display"]
    colors = set(Image.open(BytesIO(response.content)).convert("RGBA").getdata())
    assert any(r > 40 and g > 30 and b > 20 and a > 0 for r, g, b, a in colors)


def test_preview_validates_raster_band_and_bounds():
    bad_band = client.get("/api/gherproof/layers/s1-rtc-2026-01-12/preview.png", params={"bbox": _regional_bbox(), "band": 99})
    bad_bbox = client.get("/api/gherproof/layers/s1-rtc-2026-01-12/preview.png", params={"bbox": "89,23,89,24"})
    assert bad_band.status_code == 422
    assert bad_bbox.status_code == 422


def test_screening_status_accepts_actual_model_metadata_schema():
    response = client.get("/api/gherproof/screening/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["model_outputs"]["models"] == ["scratch", "pretrained"]
    assert payload["human_labels_completed"] == 0


def test_fisheries_context_records_and_registered_map_previews_are_available():
    evidence = client.get("/api/gherproof/evidence", params={"limit": 500})
    assert evidence.status_code == 200
    records = {record["evidence_id"]: record for record in evidence.json()["records"]}
    clark = records["clark-2022-aquaculture-context"]
    worldcover = records["worldcover-2021-landcover-context"]
    assert clark["metadata"]["class_legend"]["3"] == "Pond aquaculture"
    assert clark["metadata"]["pond_aquaculture_area_km2_in_covered_footprint"] == 2.317275
    assert worldcover["metadata"]["class_counts"]["40"]["class_name"] == "Cropland"
    assert worldcover["metadata"]["attribution"].startswith("© ESA WorldCover project 2021")

    layers = client.get("/api/gherproof/layers").json()["layers"]
    layer_ids = {layer["evidence_id"] for layer in layers}
    assert {"clark-2022-aquaculture-context", "worldcover-2021-landcover-context"} <= layer_ids
    for evidence_id in ("clark-2022-aquaculture-context", "worldcover-2021-landcover-context"):
        response = client.get(f"/api/gherproof/layers/{evidence_id}/preview.png", params={"bbox": _regional_bbox(), "width": 240})
        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")

    report = client.get("/api/gherproof/fisheries/incidents/incident-pallimangal-2026-01-14/report")
    assert report.status_code == 200
    assert report.json()["fisheries_context"]["department_of_fisheries"]["geographic_level"] == "Bangladesh national aggregate"
    assert report.json()["study_area_map"]["not_an_enclosure_boundary"] is True


def test_evidence_catalogue_accepts_registered_nisar_maturity_and_exposes_all_six_layers():
    evidence = get_evidence(category=None, status=None, acquisition_date=None, offset=0, limit=500)
    response = EvidenceListResponse.model_validate(evidence)
    records = {record.evidence_id: record for record in response.records}
    assert records["nisar-gcov-change-2026-10-23-to-2026-11-04-track170"].confidence_or_validation_status == "derived_exploratory"
    assert records["nisar-gcov-change-2026-10-23-to-2026-11-04-track170-frequencyB"].confidence_or_validation_status == "derived_exploratory"

    layers_response = get_layers()
    layer_ids = {layer["evidence_id"] for layer in layers_response["layers"]}
    nisar_layers = {evidence_id for evidence_id in layer_ids if evidence_id.startswith("nisar-gcov")}
    assert nisar_layers == {
        "nisar-gcov-2026-10-23-track170-ascending-validated",
        "nisar-gcov-2026-11-04-track170-ascending-validated",
        "nisar-gcov-2026-10-23-track170-ascending-validated-frequencyB",
        "nisar-gcov-2026-11-04-track170-ascending-validated-frequencyB",
        "nisar-gcov-change-2026-10-23-to-2026-11-04-track170",
        "nisar-gcov-change-2026-10-23-to-2026-11-04-track170-frequencyB",
    }

    january_card_sources = {
        "s2-true-colour-2026-01-10",
        "s2-true-colour-2026-01-20",
        "prediction-scratch-2026-01-12-probability",
        "prediction-pretrained-2026-01-12-probability",
        "optical-weakref-temporal-temporal_change",
        "disagreement-disagreement_2026-01-12_2026-01-24_rel12_ascending-xor",
    }
    assert january_card_sources <= layer_ids
    context = json.loads((ROOT / "data/gherproof/manifests/fisheries_context_manifest.json").read_text())
    assert context["clark_2022"]["class_legend"]["3"] == "Pond aquaculture"
    assert context["clark_2022"]["pond_aquaculture_class_3_area_km2_in_covered_footprint"] == 2.317275
    assert context["clark_2022"]["valid_covered_aoi_area_km2"] == 102.23415
