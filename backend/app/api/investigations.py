"""Request-time investigation assembly endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.investigation import InvestigationRequest, InvestigationResponse
from app.services.investigation_service import InvestigationError, get_investigation_service

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.post("", response_model=InvestigationResponse)
def run_investigation(request: InvestigationRequest) -> InvestigationResponse:
    try:
        return InvestigationResponse(**get_investigation_service().run(**request.model_dump()))
    except InvestigationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
