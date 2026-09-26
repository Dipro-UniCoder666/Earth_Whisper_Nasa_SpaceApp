"""Step 11 case-file endpoints.

The case file is served as produced by Step 11 - it is never regenerated.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.casefile import CaseFileResponse
from app.services.casefile_service import CaseFileError, get_casefile_service

router = APIRouter(prefix="/case-file", tags=["case-file"])


def _service():
    try:
        return get_casefile_service()
    except CaseFileError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("", response_model=CaseFileResponse)
def get_case_file() -> CaseFileResponse:
    service = _service()
    try:
        meta = service.metadata()
        content = service.content()
    except CaseFileError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return CaseFileResponse(case_file=content, **meta)


@router.get("/pdf")
def get_case_file_pdf() -> FileResponse:
    service = _service()
    if not service.pdf_available():
        raise HTTPException(status_code=404, detail="Case-file PDF is not available on disk.")
    return FileResponse(
        path=str(service.pdf_path()),
        media_type="application/pdf",
        filename="earth_event_case_file.pdf",
    )
