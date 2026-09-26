"""Earth Whisper backend configuration.

Environment-variable driven with local-development defaults. There is no LLM
configuration in this service - this is a read-only data API.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# backend/app/core/config.py -> repository root
REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATA_CONTRACT = REPO_ROOT / "data" / "step12_backend" / "earth_whisper_candidates.json"
DEFAULT_CASE_FILE_JSON = REPO_ROOT / "data" / "step11_event_case_file" / "earth_event_case_file.json"
DEFAULT_CASE_FILE_PDF = REPO_ROOT / "data" / "step11_event_case_file" / "earth_event_case_file.pdf"
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser().resolve() if raw else default


def _origins(name: str, default: str) -> tuple:
    raw = os.environ.get(name, default)
    return tuple(part.strip() for part in raw.split(",") if part.strip())


@dataclass(frozen=True)
class Settings:
    data_contract_path: Path
    case_file_json_path: Path
    case_file_pdf_path: Path
    host: str
    port: int
    cors_origins: tuple

    @property
    def service_name(self) -> str:
        return "earth-whisper-api"


def get_settings() -> Settings:
    return Settings(
        data_contract_path=_path("DATA_CONTRACT_PATH", DEFAULT_DATA_CONTRACT),
        case_file_json_path=_path("CASE_FILE_JSON_PATH", DEFAULT_CASE_FILE_JSON),
        case_file_pdf_path=_path("CASE_FILE_PDF_PATH", DEFAULT_CASE_FILE_PDF),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        cors_origins=_origins("CORS_ORIGINS", DEFAULT_CORS_ORIGINS),
    )
