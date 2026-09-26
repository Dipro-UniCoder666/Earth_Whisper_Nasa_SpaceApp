"""Candidate data access for the Earth Whisper data API.

The service owns all file access: it loads the generated data contract once,
caches it in memory, and exposes lookup, filtering and evidence extraction.
No scientific value is recomputed, and missing values stay null.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings


class DataContractError(RuntimeError):
    """Raised when the generated data contract is missing or malformed."""


class CandidateService:
    def __init__(self, contract_path: Optional[Path] = None) -> None:
        self._path = Path(contract_path or get_settings().data_contract_path)
        self._contract: Optional[Dict[str, Any]] = None
        self._by_key: Optional[Dict[str, Dict[str, Any]]] = None

    # -- loading ---------------------------------------------------------
    def _load(self) -> Dict[str, Any]:
        if self._contract is not None:
            return self._contract

        if not self._path.exists():
            raise DataContractError(
                "Data contract not found at " + str(self._path)
                + ". Run scripts/step12_build_data_contract.py to generate it."
            )
        try:
            with open(self._path, encoding="utf-8") as fh:
                contract = json.load(fh)
        except json.JSONDecodeError as exc:
            raise DataContractError("Data contract is malformed JSON: " + exc.msg) from exc
        except OSError as exc:
            raise DataContractError("Data contract could not be read: " + str(exc)) from exc

        if not isinstance(contract, dict) or not isinstance(contract.get("candidates"), list):
            raise DataContractError("Data contract is malformed: missing candidates list.")

        candidates = contract["candidates"]
        if any(not isinstance(candidate, dict) for candidate in candidates):
            raise DataContractError("Data contract is malformed: candidates must be objects.")
        keys = [candidate.get("candidate_key") for candidate in candidates]
        if any(not isinstance(key, str) or not key for key in keys):
            raise DataContractError("Data contract is malformed: every candidate needs a candidate_key.")
        if len(set(keys)) != len(keys):
            raise DataContractError("Data contract is malformed: candidate_key values must be unique.")

        self._contract = contract
        self._by_key = {candidate["candidate_key"]: candidate for candidate in candidates}
        return contract

    def reload(self) -> Dict[str, Any]:
        self._contract = None
        self._by_key = None
        return self._load()

    # -- read API --------------------------------------------------------
    def contract_path(self) -> str:
        return str(self._path)

    def metadata(self) -> Dict[str, Any]:
        contract = self._load()
        return {
            "project": contract.get("project"),
            "aoi": contract.get("aoi"),
            "investigation_period": contract.get("investigation_period"),
            "candidate_count": contract.get("candidate_count"),
            "investigated_candidate_count": contract.get("investigated_candidate_count"),
            "comparison_populations": contract.get("comparison_populations"),
            "dashboard_summary": contract.get("dashboard_summary"),
            "identity_rule": contract.get("identity_rule"),
            "source_files": contract.get("source_files"),
        }

    def all_candidates(self) -> List[Dict[str, Any]]:
        return list(self._load()["candidates"])

    def filter_candidates(self, comparison: Optional[str] = None,
                          investigated: Optional[bool] = None) -> List[Dict[str, Any]]:
        rows = self.all_candidates()
        if comparison is not None:
            rows = [r for r in rows if r.get("comparison") == comparison]
        if investigated is not None:
            rows = [r for r in rows if bool(r.get("investigated")) is investigated]
        return rows

    def get_candidate(self, candidate_key: str) -> Optional[Dict[str, Any]]:
        self._load()
        return (self._by_key or {}).get(candidate_key)

    def evidence(self, candidate_key: str) -> Optional[Dict[str, Any]]:
        candidate = self.get_candidate(candidate_key)
        if candidate is None:
            return None
        return {
            "candidate_key": candidate["candidate_key"],
            "nisar": candidate.get("nisar", {}),
            "sentinel1": candidate.get("sentinel1", {}),
            "cross_radar": candidate.get("cross_radar", {}),
            "optical": candidate.get("optical", {}),
            "environmental": candidate.get("environmental", {}),
            "uncertainty": candidate.get("uncertainty", {}),
        }

    def is_valid_key_format(self, candidate_key: str) -> bool:
        if not candidate_key or "_" not in candidate_key:
            return False
        comparison, _, region = candidate_key.rpartition("_")
        return bool(comparison) and region.isdigit()


_service: Optional[CandidateService] = None


def get_candidate_service() -> CandidateService:
    global _service
    if _service is None:
        _service = CandidateService()
    return _service
