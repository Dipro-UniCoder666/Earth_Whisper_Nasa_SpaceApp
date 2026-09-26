"""Read-only candidate endpoints.

Routers contain no file access: all data work happens in the service layer.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.candidate import (
    CandidateDetail,
    CandidateListResponse,
    CandidateSummary,
    EvidenceResponse,
)
from app.services.candidate_service import DataContractError, get_candidate_service

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _service():
    try:
        return get_candidate_service()
    except DataContractError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("", response_model=CandidateListResponse)
def list_candidates(
    comparison: Optional[str] = Query(
        None, description="Filter by comparison type, for example HH_023_to_029 or VV_025_to_026."
    ),
    investigated: Optional[bool] = Query(
        None, description="Filter by the Step 10 investigated flag. The Step 10 output is authoritative."
    ),
) -> CandidateListResponse:
    service = _service()
    try:
        meta = service.metadata()
        rows = service.filter_candidates(comparison=comparison, investigated=investigated)
    except DataContractError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return CandidateListResponse(
        project=meta.get("project") or "Earth Whisper",
        aoi=meta.get("aoi") or {"name": "unknown", "wkt": ""},
        candidate_count=meta.get("candidate_count") or len(rows),
        investigated_candidate_count=meta.get("investigated_candidate_count") or 0,
        dashboard_summary=meta.get("dashboard_summary") or {},
        candidates=[CandidateSummary(**row) for row in rows],
    )


@router.get("/{candidate_key}", response_model=CandidateDetail)
def get_candidate(candidate_key: str) -> CandidateDetail:
    service = _service()
    if not service.is_valid_key_format(candidate_key):
        raise HTTPException(
            status_code=400,
            detail="Invalid candidate key. Expected comparison + '_' + region_id, for example HH_023_to_029_265.",
        )
    try:
        candidate = service.get_candidate(candidate_key)
    except DataContractError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found: " + candidate_key)
    return CandidateDetail(**candidate)


@router.get("/{candidate_key}/evidence", response_model=EvidenceResponse)
def get_candidate_evidence(candidate_key: str) -> EvidenceResponse:
    service = _service()
    if not service.is_valid_key_format(candidate_key):
        raise HTTPException(
            status_code=400,
            detail="Invalid candidate key. Expected comparison + '_' + region_id, for example HH_023_to_029_265.",
        )
    try:
        evidence = service.evidence(candidate_key)
    except DataContractError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if evidence is None:
        raise HTTPException(status_code=404, detail="Candidate not found: " + candidate_key)
    return EvidenceResponse(**evidence)
