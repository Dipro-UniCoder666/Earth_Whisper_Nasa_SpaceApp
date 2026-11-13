from __future__ import annotations

import json
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import app
from app.api import gherproof_fisheries as routes
from app.schemas.gherproof_fisheries import AssetCreate, AssetRecord, IncidentCreate, InspectionCreate
from app.services import gherproof_fisheries_service as service


@pytest.fixture
def fisheries_db(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "DB_PATH", tmp_path / "gherproof_fisheries.sqlite3")
    service.initialize()
    return service.DB_PATH


def test_seeded_pallimangal_incident_and_asset_keep_unresolved_status(fisheries_db):
    incident = service.get_incident(service.DEMO_INCIDENT_ID)
    asset = service.get_asset(service.PALLIMANGAL_ASSET_ID)
    assert incident.incident_date.isoformat() == "2026-01-14"
    assert incident.incident_date_status == "reported_inferred"
    assert incident.incident_status == "reported_unverified"
    assert len(incident.affected_localities_reported) == 6
    assert len(incident.reporting_sources) == 3
    assert asset.geometry_status == "not_delineated"
    assert asset.geometry_reference is None
    assert asset.ownership_or_operator is None
    claims = " ".join(source.claim for source in incident.reporting_sources)
    assert "158 hectares" in claims
    assert "1,500 bighas" in claims


def test_incident_creation_is_persistent_and_source_linked(fisheries_db):
    payload = IncidentCreate.model_validate({
        "title": "Test-only fisheries incident", "incident_type": "other_reported_incident",
        "description": "Test fixture; not a project incident or observation.",
        "reporting_sources": [{"source_name": "Test fixture", "claim": "Test-only claim."}],
        "related_evidence_ids": ["reported-event-2026-01-14"],
    })
    created = service.create_incident(payload)
    assert service.get_incident(created.incident_id).related_evidence_ids == ["reported-event-2026-01-14"]
    assert created.incident_status == "reported_unverified"


def test_incident_asset_link_is_persistent_and_idempotent(fisheries_db):
    incident = service.get_incident(service.DEMO_INCIDENT_ID)
    asset = service.get_asset(service.PALLIMANGAL_ASSET_ID)
    assert asset.asset_id in incident.related_asset_ids
    updated, inserted = service.link_asset_to_incident(incident.incident_id, asset.asset_id)
    assert inserted is False
    assert updated.related_asset_ids.count(asset.asset_id) == 1
    with pytest.raises(service.FisheriesNotFound):
        service.link_asset_to_incident(incident.incident_id, "asset-missing")
    with service._connect() as con:
        legacy = con.execute("SELECT data_json FROM incidents WHERE incident_id=?", (incident.incident_id,)).fetchone()
        legacy_json = json.loads(legacy[0])
        legacy_json["related_asset_ids"] = []
        con.execute("UPDATE incidents SET data_json=? WHERE incident_id=?", (json.dumps(legacy_json), incident.incident_id))
        con.execute("DELETE FROM incident_assets WHERE incident_id=?", (incident.incident_id,))
    service.initialize()
    assert service.get_incident(incident.incident_id).related_asset_ids == [asset.asset_id]


def test_existing_evidence_becomes_separate_sensor_observations(fisheries_db):
    incident = service.get_incident(service.DEMO_INCIDENT_ID)
    observations = service.observations_for_incident(incident)
    assert sum(x.sensor == "Sentinel-1" for x in observations) == 6
    assert sum(x.sensor == "Sentinel-2" for x in observations) == 2
    assert {x.acquisition_date.isoformat() for x in observations if x.sensor == "Sentinel-2"} == {"2026-01-10", "2026-01-20"}
    assert any("local swath" in " ".join(x.limitations).lower() for x in observations if x.observation_id.endswith("partial"))


def test_screening_uses_manifest_counts_without_area_or_enclosure_claims(fisheries_db):
    incident = service.get_incident(service.DEMO_INCIDENT_ID)
    result = service.screening_for_incident(incident.incident_id)
    counts = result["optical_change_screening"]["candidate_counts_grid_cells"]
    assert counts["possible_new_water_candidate"] == 671
    assert result["optical_change_screening"]["units"] == "grid_cells; not area"
    assert result["asset_exposure"][0]["status"] == "not_assessable"
    assert result["asset_exposure"][0].get("candidate_pixel_overlap_count") is None
    assert result["model_evidence"]["model_selection"] == "none"
    assert len(result["model_evidence"]["per_acquisition_comparisons"]) == 8
    assert len(result["model_evidence"]["model_candidate_evidence_ids"]["scratch"]) == 4
    assert len(result["model_evidence"]["model_candidate_evidence_ids"]["pretrained"]) == 4
    assert result["model_evidence"]["invalid_coverage_by_acquisition"][0]["invalid_or_no_common_data_pixels"] > 0


def test_findings_keep_model_disagreement_and_do_not_create_enclosure_exposure(fisheries_db):
    findings = service.findings_for_incident(service.get_incident(service.DEMO_INCIDENT_ID))
    categories = {x.category for x in findings}
    assert "possible_new_water" in categories
    assert "boundary_unresolved" in categories
    assert "model_disagreement" in categories
    assert "requires_field_verification" in categories
    assert "possible_enclosure_exposure" not in categories
    assert all(x.evidence_ids for x in findings)


def test_priority_rationale_is_site_verification_not_emergency_action(fisheries_db):
    priorities = service.priorities_for_incident(service.DEMO_INCIDENT_ID)
    assert priorities[0].priority == "priority_1_review"
    assert "location" in priorities[0].recommended_action.lower()
    assert priorities[0].not_an_emergency_instruction is True
    assert "not an emergency" in priorities[0].rationale.lower()


def test_asset_exposure_distinguishes_candidate_geometry_and_missing_coverage():
    candidate = AssetRecord(
        asset_id="asset-test-candidate", asset_name="Test-only candidate geometry", asset_type="gher",
        geometry_status="candidate", geometry_reference=service.PROVISIONAL_AOI_ID, geometry_source="test fixture only",
        created_at="2026-11-13T00:00:00Z", updated_at="2026-11-13T00:00:00Z",
    )
    assert service.assess_asset_exposure(candidate).status == "provisional_assessment"
    verified_without_registered_geo = AssetRecord(
        asset_id="asset-test-missing-coverage", asset_name="Test-only verified asset", asset_type="gher",
        geometry_status="verified", geometry_reference="missing-geometry-evidence", geometry_source="test fixture",
        verification_date="2026-11-13", provenance=[{"source_name": "Test fixture", "claim": "Test-only source."}],
        created_at="2026-11-13T00:00:00Z", updated_at="2026-11-13T00:00:00Z",
    )
    assert service.assess_asset_exposure(verified_without_registered_geo).status == "insufficient_coverage"


def test_inspection_is_persisted_and_appended_with_missing_measurements_null(fisheries_db):
    payload = InspectionCreate.model_validate({
        "asset_id": service.PALLIMANGAL_ASSET_ID,
        "inspection_status": "completed",
        "observations": [{"source_kind": "field_observation", "value": "Test fixture observation; not a project field record."}],
        "verification_status": "unverified",
    })
    first = service.create_inspection(service.DEMO_INCIDENT_ID, payload)
    second = service.create_inspection(service.DEMO_INCIDENT_ID, payload)
    records = service.list_inspections(service.DEMO_INCIDENT_ID)
    assert first.inspection_id != second.inspection_id
    assert len(records) == 2
    assert records[0].water_level_observation is None
    assert records[0].fish_escape_report is None
    assert records[0].mortality_report is None
    assert service.get_incident(service.DEMO_INCIDENT_ID).incident_status == "reported_unverified"


def test_input_validation_rejects_bad_geometry_and_unknown_evidence(fisheries_db):
    with pytest.raises(ValidationError):
        InspectionCreate.model_validate({"inspection_status": "completed", "location_geometry": {"type": "Polygon", "coordinates": []}})
    with pytest.raises(ValidationError, match="attach satellite data as a separate observation"):
        InspectionCreate.model_validate({"inspection_status": "completed", "fish_escape_report": {"source_kind": "satellite_derived", "value": "test"}})
    with pytest.raises(ValidationError):
        AssetCreate.model_validate({"asset_name": "Candidate", "asset_type": "gher", "geometry_status": "verified", "geometry_reference": "bad", "geometry_source": "test", "verification_date": "2026-01-01", "provenance": []})
    with pytest.raises(ValueError, match="ownership/operator details require a verified"):
        service.create_asset(AssetCreate.model_validate({
            "asset_name": "Test-only reported asset", "asset_type": "gher", "ownership_or_operator": "Unverified name",
            "provenance": [{"source_name": "Unverified source", "claim": "Not verified."}],
        }))
    with pytest.raises(ValidationError, match="independently_verified reliability"):
        IncidentCreate.model_validate({
            "title": "Test incident", "incident_type": "other_reported_incident", "description": "Test-only incident.",
            "source_reliability": "independently_verified", "reporting_sources": [{"source_name": "Unverified", "claim": "Not independently verified."}],
        })
    invalid = IncidentCreate.model_validate({
        "title": "Test incident", "incident_type": "other_reported_incident", "description": "Test-only incident record.",
        "reporting_sources": [{"source_name": "Test source", "claim": "Test-only source claim."}],
        "related_evidence_ids": ["not-a-registered-evidence-id"],
    })
    with pytest.raises(ValueError, match="unknown DHARA evidence"):
        service.create_incident(invalid)


def test_report_has_five_officer_answers_and_explicit_unavailable_values(fisheries_db):
    report = service.build_investigation_report(service.DEMO_INCIDENT_ID)
    assert report["title"] == "DHARA — Pallimangal Fisheries Incident Screening Case Study"
    assert report["readiness"]["case_status"] == "exploratory_regional_investigation"
    assert report["readiness"]["pallimangal_geometry_status"] == "not_delineated"
    assert report["unavailable_measurements"]["fish_mortality"] is None
    assert report["unavailable_measurements"]["financial_loss"] is None
    assert report["evidence_sources"][0]["evidence_id"] == "reported-event-2026-01-14"
    json.dumps(report)


def test_fisheries_api_contract_and_append_only_inspection_endpoint(fisheries_db):
    incidents = routes.list_fisheries_incidents()
    assert incidents[0].incident_id == service.DEMO_INCIDENT_ID
    screening = routes.get_fisheries_screening(service.DEMO_INCIDENT_ID)
    assert screening["asset_exposure"][0]["status"] == "not_assessable"
    with pytest.raises(HTTPException) as missing:
        routes.get_fisheries_incident("absent-id")
    assert missing.value.status_code == 404
    with pytest.raises(ValidationError):
        InspectionCreate.model_validate({"inspection_status": "completed", "location_geometry": {"type": "Polygon", "coordinates": []}})
    payload = InspectionCreate.model_validate({"inspection_status": "planned", "verification_status": "unverified"})
    created = routes.create_fisheries_inspection(service.DEMO_INCIDENT_ID, payload)
    assert created.inspection_id.startswith("inspection-")
    assert created.water_level_observation is None
    assert len(routes.list_fisheries_inspections(service.DEMO_INCIDENT_ID)) == 1
    report = routes.get_fisheries_investigation_report(service.DEMO_INCIDENT_ID)
    assert report["title"] == "DHARA — Pallimangal Fisheries Incident Screening Case Study"
    schema = app.openapi()
    assert "/api/gherproof/fisheries/incidents/{incident_id}/inspections" in schema["paths"]
    assert "/api/gherproof/fisheries/incidents/{incident_id}/assets/{asset_id}" in schema["paths"]


def test_unauthenticated_write_guard_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("GHERPROOF_FISHERIES_WRITES_ENABLED", raising=False)
    with pytest.raises(HTTPException) as disabled:
        routes.require_fisheries_writes_enabled()
    assert disabled.value.status_code == 503
    monkeypatch.setenv("GHERPROOF_FISHERIES_WRITES_ENABLED", "true")
    routes.require_fisheries_writes_enabled()
