"""Candidate and evidence schemas.

Every field maps directly onto a verified source value. Numeric fields are
Optional and default to None so that unavailable data stays null instead of
being replaced with zero.

Note on comparison_aware_anomaly_percentile: this is a statistical isolation
percentile within the relevant comparison population. It is NOT a probability
of any physical event, and no probability or confidence field exists here.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AoiInfo(BaseModel):
    name: str = Field(description="Area of interest name.")
    wkt: str = Field(description="Area of interest geometry as WKT.")


class NisarEvidence(BaseModel):
    nisar_change: Optional[float] = Field(None, description="Comparison-specific NISAR change statistic.")
    nisar_change_strength: Optional[float] = Field(None, description="Magnitude of the change statistic.")
    nisar_signal_percentile: Optional[float] = Field(None, description="Percentile of the change statistic within its comparison population.")
    nisar_signal_band: Optional[str] = Field(None, description="Band label for the change statistic (for example upper_quartile).")


class Sentinel1Evidence(BaseModel):
    s1_mean_db: Optional[float] = Field(None, description="Sentinel-1 backscatter mean (dB).")
    s1_median_db: Optional[float] = Field(None, description="Sentinel-1 backscatter median (dB).")
    s1_min_db: Optional[float] = Field(None, description="Sentinel-1 backscatter minimum (dB).")
    s1_max_db: Optional[float] = Field(None, description="Sentinel-1 backscatter maximum (dB).")
    s1_pct_le_minus3db: Optional[float] = Field(None, description="Percentage of pixels at or below -3 dB.")
    s1_anomaly_percentile: Optional[float] = Field(None, description="Statistical isolation percentile within the relevant comparison population.")
    s1_anomaly_stability: Optional[str] = Field(None, description="Stability of the anomaly position across neighbourhood sizes.")
    comparison_aware_anomaly_percentile: Optional[float] = Field(
        None,
        description="Statistical isolation percentile within the relevant comparison population (k = 3, 5, 8). Not a probability.",
    )
    comparison_aware_k_score_std: Optional[float] = Field(None, description="Spread of the anomaly score across neighbourhood sizes.")


class CrossRadarEvidence(BaseModel):
    cross_radar_status: Optional[str] = Field(None, description="Recorded cross-radar consistency status; no new score is derived.")
    nisar_signal_band: Optional[str] = Field(None, description="NISAR signal band used by the cross-radar comparison.")
    s1_anomaly_band: Optional[str] = Field(None, description="Sentinel-1 anomaly band used by the cross-radar comparison.")


class OpticalEvidence(BaseModel):
    optical_status: Optional[str] = Field(
        None,
        description="Verified optical status, for example not_tested or tested_but_inconclusive_no_valid_pixels. "
        "not_tested is never treated as evidence of absence.",
    )
    optical_tested: Optional[str] = Field(None, description="Whether optical verification was performed for this candidate.")
    optical_observation_count: Optional[int] = Field(None, description="Number of optical observations associated with the candidate.")
    optical_valid_observation_count: Optional[int] = Field(None, description="Number of optical observations with valid pixels.")
    optical_max_valid_pixels: Optional[int] = Field(None, description="Maximum valid pixel count across the associated optical observations.")
    optical_max_high_aerosol_fraction: Optional[float] = Field(None, description="Maximum high-aerosol fraction across the associated optical observations.")


class EnvironmentalEvidence(BaseModel):
    rainfall_context_status: Optional[str] = Field(None, description="Availability status of the rainfall context window.")
    rainfall_role: Optional[str] = Field(None, description="Always environmental context; rainfall is AOI-level and never a spatial event score.")
    gunw_023_rainfall_14day_mm: Optional[float] = Field(None, description="14-day rainfall context for GUNW_023 (unavailable in this dataset remains null).")
    gunw_025_rainfall_14day_mm: Optional[float] = Field(None, description="14-day rainfall context for GUNW_025.")
    gunw_026_rainfall_14day_mm: Optional[float] = Field(None, description="14-day rainfall context for GUNW_026.")
    gunw_029_rainfall_14day_mm: Optional[float] = Field(None, description="14-day rainfall context for GUNW_029.")


class UncertaintyEvidence(BaseModel):
    comparison_population_size: Optional[int] = Field(None, description="Size of the candidate pool for the same comparison type.")
    anomaly_stability_band: Optional[str] = Field(None, description="Sensitivity of the anomaly position to neighbourhood size.")
    evidence_limitation: Optional[str] = Field(None, description="Recorded evidence limitation for this candidate.")


class Step10Summaries(BaseModel):
    observation_summary: Optional[str] = Field(None, description="Step 10 observation summary (investigated candidates only).")
    inference_summary: Optional[str] = Field(None, description="Step 10 conservative inference (investigated candidates only).")
    limitation_summary: Optional[str] = Field(None, description="Step 10 limitation statement (investigated candidates only).")


class SourceRecords(BaseModel):
    """Raw verified CSV fields retained for auditability and future consumers."""

    step8c_evidence_matrix: Dict[str, Optional[str]]
    step8e_uncertainty_annotations: Dict[str, Optional[str]]
    step8f_cross_radar_consistency: Dict[str, Optional[str]]
    step10_candidate_investigations: Optional[Dict[str, Optional[str]]] = None


class CandidateSummary(BaseModel):
    candidate_key: str = Field(description="Unique identity: comparison + '_' + region_id.")
    comparison: str = Field(description="Comparison type, for example HH_023_to_029 or VV_025_to_026. Never combined.")
    region_id: int = Field(description="Region id. Not unique on its own.")
    lon: Optional[float] = Field(None, description="Longitude of the candidate region.")
    lat: Optional[float] = Field(None, description="Latitude of the candidate region.")
    area_m2: Optional[float] = Field(None, description="Candidate area in square metres.")
    investigated: bool = Field(description="True only for the 32 candidates present in the Step 10 investigation subset.")


class CandidateDetail(CandidateSummary):
    nisar_change: Optional[float] = None
    nisar_change_strength: Optional[float] = None
    nisar_signal_percentile: Optional[float] = None
    nisar_signal_band: Optional[str] = None
    s1_mean_db: Optional[float] = None
    s1_median_db: Optional[float] = None
    s1_min_db: Optional[float] = None
    s1_max_db: Optional[float] = None
    s1_pct_le_minus3db: Optional[float] = None
    s1_anomaly_percentile: Optional[float] = None
    s1_anomaly_stability: Optional[str] = None
    cross_radar_status: Optional[str] = None
    optical_status: Optional[str] = None
    rainfall_context_status: Optional[str] = None
    comparison_population_size: Optional[int] = None
    anomaly_stability_band: Optional[str] = None
    evidence_limitation: Optional[str] = None
    observation_summary: Optional[str] = None
    inference_summary: Optional[str] = None
    limitation_summary: Optional[str] = None
    nisar: NisarEvidence
    sentinel1: Sentinel1Evidence
    cross_radar: CrossRadarEvidence
    optical: OpticalEvidence
    environmental: EnvironmentalEvidence
    uncertainty: UncertaintyEvidence
    observations: Step10Summaries
    provenance: Dict[str, Optional[str]]
    source_records: SourceRecords


class NisarComparisonSummary(BaseModel):
    comparison: str
    observation_pairs: List[str]
    polarization: str
    mean_change: float
    median_change: float


class DashboardSummary(BaseModel):
    exact_aoi_valid_pixels: int
    nisar_comparisons: List[NisarComparisonSummary]
    sentinel1_threshold_counts: Dict[str, int]
    dual_radar_stable_patterns: int
    stability_bands: Dict[str, int]
    optical_tested_regions: int
    optical_inconclusive_regions: int
    optical_not_tested_regions: int
    rainfall_context: Dict[str, Optional[float]]


class CandidateListResponse(BaseModel):
    project: str
    aoi: AoiInfo
    candidate_count: int = Field(description="Total candidates in the contract.")
    investigated_candidate_count: int = Field(description="Candidates flagged as investigated by the Step 10 output.")
    dashboard_summary: DashboardSummary
    candidates: List[CandidateSummary]


class EvidenceResponse(BaseModel):
    candidate_key: str
    nisar: NisarEvidence
    sentinel1: Sentinel1Evidence
    cross_radar: CrossRadarEvidence
    optical: OpticalEvidence
    environmental: EnvironmentalEvidence
    uncertainty: UncertaintyEvidence
