"""Schemas for request-time investigation assembly."""

from typing import Any, Dict, List, Literal

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
    source_status: Literal["LIVE", "CACHED_LIVE", "VERIFIED_STATIC"]
    scientific_result_status: Literal["VERIFIED_STATIC"]
    provenance: Dict[str, Any]
