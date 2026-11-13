"""Fisheries incident/asset/inspection routes mounted within DHARA's legacy API prefix."""
import os

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.gherproof_fisheries import (
    AssetCreate, AssetRecord, FisheriesReportResponse, FisheriesScreeningResponse, FisheriesSummary,
    IncidentCreate, IncidentFindingsResponse, IncidentPrioritiesResponse, IncidentRecord,
    InspectionCreate, InspectionRecord,
)
from app.services import gherproof_fisheries_service as fisheries

router = APIRouter(prefix="/fisheries", tags=["DHARA Fisheries"])


def require_fisheries_writes_enabled() -> None:
    """Keep unauthenticated mutation routes off unless explicitly enabled for trusted development."""
    if os.environ.get("GHERPROOF_FISHERIES_WRITES_ENABLED", "false").strip().lower() not in {"1", "true", "yes"}:
        raise HTTPException(status_code=503, detail="Fisheries write operations are disabled until an authenticated deployment boundary is configured")


def _not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=404, detail=str(error))


@router.get("/incidents", response_model=list[IncidentRecord])
def list_fisheries_incidents():
    return fisheries.list_incidents()


@router.post("/incidents", response_model=IncidentRecord, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_fisheries_writes_enabled)])
def create_fisheries_incident(payload: IncidentCreate):
    try:
        return fisheries.create_incident(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/incidents/{incident_id}", response_model=IncidentRecord)
def get_fisheries_incident(incident_id: str):
    try:
        return fisheries.get_incident(incident_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/incidents/{incident_id}/assets/{asset_id}", response_model=IncidentRecord, dependencies=[Depends(require_fisheries_writes_enabled)])
def link_fisheries_asset(incident_id: str, asset_id: str):
    try:
        record, _created = fisheries.link_asset_to_incident(incident_id, asset_id)
        return record
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/summary", response_model=FisheriesSummary)
def get_fisheries_incident_summary(incident_id: str):
    try:
        return fisheries.summary_for_incident(incident_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/screening", response_model=FisheriesScreeningResponse)
def get_fisheries_screening(incident_id: str):
    try:
        return fisheries.screening_for_incident(incident_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/findings", response_model=IncidentFindingsResponse)
def get_fisheries_findings(incident_id: str):
    try:
        incident = fisheries.get_incident(incident_id)
        return {"incident_id": incident_id, "findings": fisheries.findings_for_incident(incident)}
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/priorities", response_model=IncidentPrioritiesResponse)
def get_fisheries_priorities(incident_id: str):
    try:
        return {"incident_id": incident_id, "priorities": fisheries.priorities_for_incident(incident_id)}
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/inspections", response_model=list[InspectionRecord])
def list_fisheries_inspections(incident_id: str):
    try:
        return fisheries.list_inspections(incident_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/incidents/{incident_id}/inspections", response_model=InspectionRecord, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_fisheries_writes_enabled)])
def create_fisheries_inspection(incident_id: str, payload: InspectionCreate):
    try:
        return fisheries.create_inspection(incident_id, payload)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/assets", response_model=list[AssetRecord])
def list_fisheries_assets():
    return fisheries.list_assets()


@router.post("/assets", response_model=AssetRecord, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_fisheries_writes_enabled)])
def create_fisheries_asset(payload: AssetCreate):
    try:
        return fisheries.create_asset(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/assets/{asset_id}", response_model=AssetRecord)
def get_fisheries_asset(asset_id: str):
    try:
        return fisheries.get_asset(asset_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/incidents/{incident_id}/report", response_model=FisheriesReportResponse)
def get_fisheries_investigation_report(incident_id: str):
    try:
        return fisheries.build_investigation_report(incident_id)
    except fisheries.FisheriesNotFound as exc:
        raise _not_found(exc) from exc
