"""Schemas for request-time investigation assembly."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    location_id: str = Field(description="Existing investigation location id selected by the frontend.")
    latitude: float
    longitude: float


class InvestigationStage(BaseModel):
    id: str
    label: str
    status: str
    detail: str


class InvestigationResponse(BaseModel):
    status: str
    location_id: str
    candidate_key: str
    stages: List[InvestigationStage]
    result: Dict[str, Any]
