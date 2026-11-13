import json

import pytest

from app.services import gherproof_service as service


def feature(status="candidate", evidence=None, reviewer=None, reviewed_at=None):
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[89.2, 23.0], [89.21, 23.0], [89.21, 23.01], [89.2, 23.01], [89.2, 23.0]]]},
            "properties": {"status": status, "evidence": evidence if evidence is not None else [{"description": "reviewed imagery reference"}],
                           "reviewer": reviewer, "reviewed_at": reviewed_at, "confidence": "medium"}}


@pytest.fixture
def boundary_store(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "ROOT", tmp_path)
    monkeypatch.setattr(service, "DATA", tmp_path / "data")
    monkeypatch.setattr(service, "BOUNDARY_DIR", tmp_path / "data" / "boundaries")
    monkeypatch.setattr(service, "BOUNDARY_PATH", tmp_path / "data" / "boundaries" / "pallimangal_enclosure.geojson")
    monkeypatch.setattr(service, "BOUNDARY_PROVENANCE_PATH", tmp_path / "data" / "manifests" / "boundary_provenance.json")
    return tmp_path


def test_boundary_requires_valid_polygon_and_evidence(boundary_store):
    with pytest.raises(ValueError, match="supporting evidence"):
        service.save_boundary(feature(evidence=[]))
    invalid = feature()
    invalid["geometry"]["coordinates"] = [[[89.2, 23.0], [89.21, 23.01], [89.21, 23.0], [89.2, 23.01], [89.2, 23.0]]]
    with pytest.raises(ValueError, match="valid non-empty polygon"):
        service.save_boundary(invalid)


def test_candidate_review_verified_transition_and_version_history(boundary_store):
    assert service.boundary_record()["status"] == "not_delineated"
    candidate = service.save_boundary(feature())
    assert candidate["status"] == "candidate"
    with pytest.raises(ValueError, match="Invalid boundary status transition"):
        service.save_boundary(feature("verified", reviewer="Reviewer", reviewed_at="2026-11-12T10:00:00Z"))
    reviewed = service.save_boundary(feature("under_review", reviewer="Reviewer", reviewed_at="2026-11-12T10:00:00Z"))
    assert reviewed["status"] == "under_review"
    verified = service.save_boundary(feature("verified", reviewer="Reviewer", reviewed_at="2026-11-12T10:05:00Z"))
    assert verified["status"] == "verified"
    manifest = json.loads(service.BOUNDARY_PROVENANCE_PATH.read_text())
    assert [x["status"] for x in manifest["versions"]] == ["candidate", "under_review", "verified"]
    assert all((boundary_store / x["geojson_path"]).is_file() for x in manifest["versions"])


def test_review_states_require_reviewer_and_valid_timestamp(boundary_store):
    service.save_boundary(feature())
    with pytest.raises(ValueError, match="reviewer and reviewed_at"):
        service.save_boundary(feature("under_review"))
    with pytest.raises(ValueError, match="ISO-8601"):
        service.save_boundary(feature("under_review", reviewer="R", reviewed_at="tomorrow"))


def test_verified_geometry_cannot_be_changed_without_review(boundary_store):
    service.save_boundary(feature())
    service.save_boundary(feature("under_review", reviewer="R", reviewed_at="2026-11-12T10:00:00Z"))
    service.save_boundary(feature("verified", reviewer="R", reviewed_at="2026-11-12T10:01:00Z"))
    changed = feature("under_review", reviewer="R", reviewed_at="2026-11-12T10:02:00Z")
    changed["geometry"]["coordinates"][0][1] = [89.22, 23.0]
    returned = service.save_boundary(changed)
    assert returned["status"] == "under_review"
