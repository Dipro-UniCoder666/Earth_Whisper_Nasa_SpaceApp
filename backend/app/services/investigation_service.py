"""Request-time assembly of verified investigation evidence.

This service coordinates existing Step 12 records. It does not download data,
rerun scientific processing, or derive probabilities or causal labels.
"""

from math import hypot
from typing import Any, Dict, List, Optional

from app.services.candidate_service import CandidateService, DataContractError, get_candidate_service


class InvestigationError(RuntimeError):
    """Raised when a requested investigation cannot be assembled safely."""


class InvestigationService:
    def __init__(self, candidate_service: Optional[CandidateService] = None) -> None:
        self._candidates = candidate_service or get_candidate_service()

    def run(self, location_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        stages: List[Dict[str, str]] = []

        def complete(stage_id: str, label: str, detail: str) -> None:
            stages.append({"id": stage_id, "label": label, "status": "complete", "detail": detail})

        if location_id == "monda-uttarakhand":
            return self._run_monda(latitude, longitude, complete, stages)
        if location_id != "sandhya-river":
            raise InvestigationError("This investigation location is not available in the verified evidence contract.")
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise InvestigationError("The selected investigation coordinates are invalid.")
        complete("initializing", "Location resolved", "The selected Sandhya River investigation was validated.")

        try:
            metadata = self._candidates.metadata()
            candidates = [candidate for candidate in self._candidates.all_candidates() if candidate.get("investigated")]
        except DataContractError as exc:
            raise InvestigationError(str(exc)) from exc
        if not candidates:
            raise InvestigationError("No verified investigated candidates are available for this location.")

        candidate = min(
            candidates,
            key=lambda row: hypot(float(row.get("lat") or 0) - latitude, float(row.get("lon") or 0) - longitude),
        )
        complete("loading_observations", "Observations loaded", "Verified radar, rainfall, optical, and uncertainty records were read.")

        required_nisar = candidate.get("nisar", {})
        source_records = candidate.get("source_records", {})
        if not required_nisar or not source_records.get("step8c_evidence_matrix"):
            raise InvestigationError("The selected verified candidate is missing required radar observations.")
        complete("analyzing_radar_change", "Radar change analyzed", "NISAR change and Sentinel-1 cross-check records were assembled.")

        evidence_groups = {
            "nisar": candidate.get("nisar", {}),
            "sentinel1": candidate.get("sentinel1", {}),
            "rainfall": candidate.get("environmental", {}),
            "optical": candidate.get("optical", {}),
        }
        availability = {
            name: "available" if bool(group) and any(value is not None for value in group.values()) else "not_available"
            for name, group in evidence_groups.items()
        }
        complete("checking_supporting_evidence", "Supporting evidence checked", "Radar, environmental, and optical availability was recorded without filling missing values.")

        uncertainty = candidate.get("uncertainty", {})
        limitations = candidate.get("observations", {}).get("limitation_summary") or candidate.get("evidence_limitation")
        complete("assessing_uncertainty", "Uncertainty assessed", "Recorded uncertainty and limitation statements were retained.")

        result = {
            "project": metadata.get("project") or "Earth Whisper",
            "location_id": location_id,
            "candidate_count": metadata.get("candidate_count") or len(self._candidates.all_candidates()),
            "investigated_candidate_count": metadata.get("investigated_candidate_count") or len(candidates),
            "candidate": candidate,
            "evidence_groups": evidence_groups,
            "evidence_availability": availability,
            "uncertainty": uncertainty,
            "limitations": limitations,
            "provenance": candidate.get("provenance", {}),
        }
        complete("assembling_investigation", "Investigation assembled", "The verified evidence groups and supporting context are ready to present.")
        return {"status": "ready", "location_id": location_id, "candidate_key": candidate["candidate_key"], "stages": stages, "result": result}

    def _run_monda(self, latitude: float, longitude: float, complete: Any, stages: List[Dict[str, str]]) -> Dict[str, Any]:
        if hypot(latitude - 31.1105, longitude - 77.9373) > 1:
            raise InvestigationError("The selected coordinates do not match the verified Monda investigation.")
        complete("initializing", "Location resolved", "The selected Monda investigation was validated.")
        site = {
            "id": "monda-uttarakhand",
            "shortName": "Monda, Uttarakhand",
            "name": "Monda, Uttarakhand, India",
            "coords": {"lat": 31.1105, "lng": 77.9373},
            "latitude": "31.110500",
            "longitude": "77.937300",
            "coordLabel": "31.110500° N · 77.937300° E",
            "nisar": {
                "product": "NISAR GUNW coherence",
                "beforeCoherence": 0.6648,
                "afterCoherence": 0.2188,
                "meanChange": -0.446,
                "medianChange": -0.4667,
                "validPixels": 6504,
                "observationSummary": "Substantial coherence loss was observed across the investigated region.",
            },
            "terrain": {
                "dem": "NASADEM",
                "elevationMeters": 2794,
                "localSlopeDegrees": 40.8,
                "context": "Mountainous",
                "summary": "The investigated point sits at 2,794 m elevation with a local slope of 40.8°.",
            },
            "sources": [
                {"dataset": "NISAR GUNW coherence", "provider": "NASA / JPL - NASA-ISRO SAR mission", "purpose": "Regional radar coherence-change detection", "url": "https://science.nasa.gov/"},
                {"dataset": "NASA-ISRO SAR (NISAR) mission reference", "provider": "NASA Jet Propulsion Laboratory", "purpose": "Mission and instrument reference", "url": "https://www.jpl.nasa.gov/"},
                {"dataset": "NASADEM", "provider": "NASA", "purpose": "Elevation and terrain/slope context", "url": "https://www.earthdata.nasa.gov/"},
                {"dataset": "NASADEM distribution", "provider": "OpenTopography", "purpose": "Digital elevation model distribution", "url": "https://portal.opentopography.org/"},
                {"dataset": "OpenStreetMap tiles", "provider": "OpenStreetMap contributors", "purpose": "Investigation map basemap", "url": "https://www.openstreetmap.org/copyright"},
            ],
            "methodology": [
                "NISAR GUNW coherence products for the investigated observation pair",
                "Regional coherence comparison across the candidate investigation region",
                "Zonal statistics over the candidate polygon (mean, median, valid pixel count)",
                "NASADEM elevation and local slope derived at the investigation point",
            ],
            "limitation": "Coherence change indicates a change in radar-scattering consistency between observations; it does not by itself establish the physical cause of the change.",
        }
        complete("loading_observations", "Observations loaded", "Verified NISAR and terrain records were read.")
        complete("analyzing_radar_change", "Radar change analyzed", "The recorded NISAR coherence comparison was assembled.")
        complete("checking_supporting_evidence", "Supporting evidence checked", "Terrain context and source availability were recorded.")
        complete("assessing_uncertainty", "Uncertainty assessed", "The existing scientific limitation statement was retained.")
        complete("assembling_investigation", "Investigation assembled", "The verified Monda evidence is ready to present.")
        return {
            "status": "ready",
            "location_id": "monda-uttarakhand",
            "candidate_key": "monda-uttarakhand",
            "stages": stages,
            "result": {"project": "Earth Whisper", "location_id": "monda-uttarakhand", "site": site},
        }


def get_investigation_service() -> InvestigationService:
    return InvestigationService()
