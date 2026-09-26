"""Case-file and health schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Service status.")
    service: str = Field(description="Service identifier.")


class CaseFileResponse(BaseModel):
    project: Optional[str] = None
    aoi: Optional[str] = None
    investigation_period: Optional[str] = None
    candidate_count: Optional[int] = None
    json_path: str = Field(description="Path of the Step 11 case-file JSON that was read.")
    pdf_path: str = Field(description="Path of the Step 11 case-file PDF.")
    pdf_available: bool = Field(description="Whether the PDF file exists on disk.")
    global_limitations: Optional[list] = None
    case_file: Dict[str, Any] = Field(description="Verbatim Step 11 case-file JSON content.")
