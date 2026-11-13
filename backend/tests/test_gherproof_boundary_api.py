from pathlib import Path

from fastapi import HTTPException
from PIL import Image
import pytest

from app.api import gherproof as routes
from app.services import gherproof_service as service


def polygon(status="candidate", reviewer=None, reviewed_at=None):
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[89.2, 23.0], [89.21, 23.0], [89.21, 23.01], [89.2, 23.01], [89.2, 23.0]]]},
            "properties": {"status": status, "confidence": "low", "evidence": [{"description": "dated imagery review"}],
                           "reviewer": reviewer, "reviewed_at": reviewed_at}}


def test_boundary_api_gates_status_and_serves_context(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "ROOT", tmp_path)
    monkeypatch.setattr(service, "DATA", tmp_path / "data" / "gherproof")
    monkeypatch.setattr(service, "BOUNDARY_DIR", service.DATA / "boundaries")
    monkeypatch.setattr(service, "BOUNDARY_PATH", service.BOUNDARY_DIR / "pallimangal_enclosure.geojson")
    monkeypatch.setattr(service, "BOUNDARY_PROVENANCE_PATH", service.DATA / "manifests" / "boundary_provenance.json")
    image_path = service.DATA / "processed" / "sentinel2" / "2026-01-13_sentinel2_visual_provisional_locality.png"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (2, 2), (40, 50, 60)).save(image_path)
    assert routes.get_boundary()["status"] == "not_delineated"
    context = routes.get_sentinel2_context()
    assert Path(context.path) == image_path
    with pytest.raises(HTTPException) as error:
        routes.put_boundary(polygon("verified", "Reviewer", "2026-11-12T10:00:00Z"))
    assert error.value.status_code == 422
    assert routes.put_boundary(polygon())["status"] == "candidate"
    assert routes.put_boundary(polygon("under_review", "Reviewer", "2026-11-12T10:00:00Z"))["status"] == "under_review"
    assert routes.put_boundary(polygon("verified", "Reviewer", "2026-11-12T10:05:00Z"))["status"] == "verified"
    with pytest.raises(HTTPException) as error:
        routes.get_model_comparison()
    assert error.value.status_code == 404
