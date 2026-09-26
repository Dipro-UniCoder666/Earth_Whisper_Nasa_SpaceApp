"""Case-file data access.

Reads the existing Step 11 case-file outputs. Nothing is regenerated: the PDF
is served as produced, and the JSON is returned verbatim.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings


class CaseFileError(RuntimeError):
    """Raised when the Step 11 case file is missing or malformed."""


class CaseFileService:
    def __init__(self, json_path: Optional[Path] = None, pdf_path: Optional[Path] = None) -> None:
        settings = get_settings()
        self._json_path = Path(json_path or settings.case_file_json_path)
        self._pdf_path = Path(pdf_path or settings.case_file_pdf_path)
        self._content: Optional[Dict[str, Any]] = None

    def _load(self) -> Dict[str, Any]:
        if self._content is not None:
            return self._content
        if not self._json_path.exists():
            raise CaseFileError("Case-file JSON not found at " + str(self._json_path))
        try:
            with open(self._json_path, encoding="utf-8") as fh:
                content = json.load(fh)
        except json.JSONDecodeError as exc:
            raise CaseFileError("Case-file JSON is malformed: " + exc.msg) from exc
        except OSError as exc:
            raise CaseFileError("Case-file JSON could not be read: " + str(exc)) from exc
        if not isinstance(content, dict):
            raise CaseFileError("Case-file JSON is malformed: expected an object.")
        self._content = content
        return content

    def pdf_path(self) -> Path:
        return self._pdf_path

    def pdf_available(self) -> bool:
        return self._pdf_path.exists()

    def metadata(self) -> Dict[str, Any]:
        content = self._load()
        return {
            "project": content.get("project"),
            "aoi": content.get("aoi"),
            "investigation_period": content.get("investigation_period"),
            "candidate_count": content.get("candidate_count"),
            "json_path": str(self._json_path),
            "pdf_path": str(self._pdf_path),
            "pdf_available": self.pdf_available(),
            "global_limitations": content.get("global_limitations"),
        }

    def content(self) -> Dict[str, Any]:
        return self._load()

    def reload(self) -> Dict[str, Any]:
        self._content = None
        return self._load()


_service: Optional[CaseFileService] = None


def get_casefile_service() -> CaseFileService:
    global _service
    if _service is None:
        _service = CaseFileService()
    return _service
