"""Health endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.casefile import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=get_settings().service_name)
