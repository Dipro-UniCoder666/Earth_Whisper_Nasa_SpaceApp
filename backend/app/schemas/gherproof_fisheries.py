"""Typed fisheries incident, asset, finding, inspection and decision-support contracts."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

IncidentType = Literal[
    "embankment_failure", "fisheries_enclosure_breach", "possible_water_intrusion",
    "aquaculture_flooding", "other_reported_incident",
]
IncidentStatus = Literal["reported_unverified", "under_review", "field_verified", "closed"]
AssetType = Literal["fish_enclosure", "gher", "aquaculture_pond", "fisheries_cluster", "embankment", "drainage_canal"]
GeometryStatus = Literal["not_delineated", "candidate", "under_review", "verified", "rejected"]
FindingCategory = Literal[
    "possible_new_water", "possible_water_loss", "persistent_water_candidate",
    "possible_enclosure_exposure", "possible_adjacent_land_exposure",
    "model_disagreement", "insufficient_coverage", "boundary_unresolved",
    "requires_field_verification",
]
Priority = Literal["priority_1_review", "priority_2_review", "priority_3_review", "not_assessable"]


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_name: str = Field(min_length=2, max_length=200)
    source_type: Literal["news", "government", "operator", "field", "satellite", "other"] = "other"
    url: str | None = Field(default=None, max_length=2000)
    published_date: date | None = None
    claim: str = Field(min_length=2, max_length=2000)
    claim_status: Literal["reported_unverified", "corroborated", "verified", "disputed"] = "reported_unverified"
    reliability: Literal["unknown", "secondary_reporting", "official_unverified", "field_recorded", "independently_verified"] = "unknown"
    evidence_id: str | None = Field(default=None, max_length=160)


class IncidentBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=3, max_length=300)
    incident_type: IncidentType
    incident_date: date | None = None
    incident_date_status: Literal["reported", "reported_inferred", "verified", "unknown"] = "unknown"
    reported_date: date | None = None
    reported_date_note: str | None = Field(default=None, max_length=1000)
    administrative_location: dict[str, str | None] = Field(default_factory=dict)
    mouza: str | None = Field(default=None, max_length=200)
    affected_localities_reported: list[str] = Field(default_factory=list, max_length=30)
    description: str = Field(min_length=5, max_length=5000)
    reporting_sources: list[SourceReference] = Field(min_length=1, max_length=30)
    source_reliability: Literal["unknown", "secondary_reporting", "official_unverified", "field_recorded", "independently_verified"] = "unknown"
    incident_status: IncidentStatus = "reported_unverified"
    related_evidence_ids: list[str] = Field(default_factory=list, max_length=100)
    related_asset_ids: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("affected_localities_reported")
    @classmethod
    def normalize_localities(cls, values: list[str]) -> list[str]:
        clean = [v.strip() for v in values if v and v.strip()]
        return list(dict.fromkeys(clean))

    @field_validator("related_evidence_ids")
    @classmethod
    def valid_evidence_ids(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value or len(value) > 160 or any(ch.isspace() for ch in value):
                raise ValueError("evidence IDs must be nonempty registry-style identifiers")
        return list(dict.fromkeys(values))

    @field_validator("related_asset_ids")
    @classmethod
    def valid_asset_ids(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value or len(value) > 160 or any(ch.isspace() for ch in value):
                raise ValueError("asset IDs must be nonempty stable identifiers")
        return list(dict.fromkeys(values))

    @model_validator(mode="after")
    def sourced_reliability(self) -> "IncidentBase":
        if self.source_reliability == "independently_verified" and not any(
            source.claim_status == "verified" and source.reliability == "independently_verified"
            for source in self.reporting_sources
        ):
            raise ValueError("independently_verified reliability requires an explicitly verified source record")
        return self


class IncidentCreate(IncidentBase):
    incident_status: Literal["reported_unverified", "under_review"] = "reported_unverified"


class IncidentRecord(IncidentBase):
    incident_id: str
    created_at: datetime
    updated_at: datetime


class AssetBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_name: str = Field(min_length=2, max_length=300)
    asset_type: AssetType
    administrative_location: dict[str, str | None] = Field(default_factory=dict)
    mouza: str | None = Field(default=None, max_length=200)
    geometry_reference: str | None = Field(default=None, max_length=160)
    geometry_status: GeometryStatus = "not_delineated"
    geometry_source: str | None = Field(default=None, max_length=1000)
    ownership_or_operator: str | None = Field(default=None, max_length=300)
    verification_date: date | None = None
    verification_notes: str | None = Field(default=None, max_length=3000)
    provenance: list[SourceReference] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def geometry_reference_matches_status(self) -> "AssetBase":
        if self.geometry_status == "not_delineated" and self.geometry_reference is not None:
            raise ValueError("not_delineated assets cannot reference geometry")
        if self.geometry_status in ("candidate", "under_review", "verified") and not self.geometry_reference:
            raise ValueError("candidate/reviewed/verified geometry requires a registered geometry reference")
        if self.geometry_status == "verified" and not self.geometry_source:
            raise ValueError("verified geometry requires a source")
        if self.geometry_status == "verified" and not self.provenance:
            raise ValueError("verified geometry requires provenance records")
        if self.geometry_status in ("candidate", "under_review") and not (self.geometry_source or self.provenance):
            raise ValueError("candidate/reviewed geometry requires provenance")
        return self


class AssetCreate(AssetBase):
    pass


class AssetRecord(AssetBase):
    asset_id: str
    created_at: datetime
    updated_at: datetime


class SatelliteObservation(BaseModel):
    observation_id: str
    sensor: Literal["Sentinel-1", "Sentinel-2"]
    acquisition_date: date | None
    product_identifier: str | None = None
    relevant_bands: list[str] = Field(default_factory=list)
    processing_method: str | None = None
    spatial_coverage: dict[str, Any] | None = None
    valid_data_status: str
    evidence_registry_reference: str
    source_file_references: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class FisheriesFinding(BaseModel):
    finding_id: str
    incident_id: str
    category: FindingCategory
    asset_id: str | None = None
    geographic_reference: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    observation_dates: list[date] = Field(default_factory=list)
    detection_method: str
    evidence_strength: Literal["low", "moderate", "strong", "not_assessed"]
    validation_status: Literal["exploratory_unverified", "not_assessable", "under_review", "field_verified"]
    explanation: str
    limitations: list[str] = Field(default_factory=list)
    recommended_verification_action: str
    candidate_pixel_count: int | None = Field(default=None, ge=0)
    pixel_resolution_m: float | None = Field(default=None, gt=0)


class ExposureAssessment(BaseModel):
    asset_id: str | None = None
    status: Literal["not_assessable", "provisional_assessment", "assessed", "insufficient_coverage"]
    geometry_status: GeometryStatus | None = None
    candidate_pixel_overlap_count: int | None = Field(default=None, ge=0)
    valid_observation_pixel_count: int | None = Field(default=None, ge=0)
    evidence_ids: list[str] = Field(default_factory=list)
    explanation: str
    limitations: list[str] = Field(default_factory=list)


class ModelEvidenceComparison(BaseModel):
    status: Literal["exploratory_only"] = "exploratory_only"
    metric_semantics: Literal["weak_reference_agreement_not_accuracy"] = "weak_reference_agreement_not_accuracy"
    model_selection: Literal["none"] = "none"
    per_acquisition_comparisons: list[dict[str, Any]] = Field(default_factory=list)
    model_candidate_evidence_ids: dict[str, list[str]] = Field(default_factory=dict)
    optical_weak_reference_evidence_ids: list[str] = Field(default_factory=list)
    invalid_coverage_by_acquisition: list[dict[str, Any]] = Field(default_factory=list)
    model_disagreement_evidence_ids: list[str] = Field(default_factory=list)
    overall_interpretation: str
    uncertainty_reasons: list[str] = Field(default_factory=list)


class InspectionPriority(BaseModel):
    priority: Priority
    recommended_action: str
    rationale: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    fisheries_officer_checks: list[str] = Field(default_factory=list)
    not_an_emergency_instruction: bool = True


class TaggedObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_kind: Literal["field_observation", "operator_report", "satellite_derived"]
    value: str = Field(min_length=1, max_length=2000)
    observed_at: datetime | None = None
    source_reference: str | None = Field(default=None, max_length=500)
    evidence_id: str | None = Field(default=None, max_length=160)


class TaggedMeasurement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_kind: Literal["field_observation", "operator_report"]
    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1, max_length=40)
    reference_level: str | None = Field(default=None, max_length=200)
    observed_at: datetime | None = None
    source_reference: str | None = Field(default=None, max_length=500)


class InspectionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str | None = None
    inspection_status: Literal["planned", "in_progress", "completed"]
    inspection_date: datetime | None = None
    inspector_reference: str | None = Field(default=None, max_length=160)
    location_reference: str | None = Field(default=None, max_length=500)
    location_geometry: dict[str, Any] | None = None
    observations: list[TaggedObservation] = Field(default_factory=list, max_length=100)
    water_level_observation: TaggedMeasurement | None = None
    embankment_condition: TaggedObservation | None = None
    visible_damage: TaggedObservation | None = None
    fish_escape_report: TaggedObservation | None = None
    mortality_report: TaggedObservation | None = None
    photograph_references: list[str] = Field(default_factory=list, max_length=100)
    verification_status: Literal["unverified", "field_observed", "corroborated", "independently_verified"] = "unverified"
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("location_geometry")
    @classmethod
    def valid_point_geometry(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        if value.get("type") != "Point" or not isinstance(value.get("coordinates"), list) or len(value["coordinates"]) < 2:
            raise ValueError("inspection location geometry must be a GeoJSON Point")
        coords = value["coordinates"]
        if not all(isinstance(x, (int, float)) and abs(x) < float("inf") for x in coords[:2]):
            raise ValueError("inspection point coordinates must be finite numbers")
        if not (-180 <= coords[0] <= 180 and -90 <= coords[1] <= 90):
            raise ValueError("inspection point must use WGS84 longitude/latitude")
        return value

    @model_validator(mode="after")
    def keep_fisheries_claims_out_of_satellite_inference(self) -> "InspectionCreate":
        for field_name in ("embankment_condition", "visible_damage", "fish_escape_report", "mortality_report"):
            observation = getattr(self, field_name)
            if observation and observation.source_kind == "satellite_derived":
                raise ValueError(f"{field_name} must be a field observation or operator report; attach satellite data as a separate observation instead")
        if self.verification_status in ("field_observed", "corroborated", "independently_verified"):
            sources = [*self.observations, self.embankment_condition, self.visible_damage, self.fish_escape_report, self.mortality_report]
            if not any(item and item.source_kind == "field_observation" for item in sources):
                raise ValueError("a field-based verification status requires a recorded field observation")
        if self.verification_status == "independently_verified" and not self.inspector_reference:
            raise ValueError("independently_verified inspection status requires a verifiable inspector reference")
        return self


class InspectionRecord(InspectionCreate):
    inspection_id: str
    incident_id: str
    created_at: datetime
    updated_at: datetime


class FisheriesScreeningResponse(BaseModel):
    incident_id: str
    case_status: str
    model_readiness: Literal["exploratory_only"]
    human_reference_status: Literal["human_review_pending"]
    impact_quantification: Literal["not_approved"]
    observations: list[SatelliteObservation]
    optical_change_screening: dict[str, Any]
    model_evidence: ModelEvidenceComparison
    asset_exposure: list[ExposureAssessment]
    spatial_categories: dict[str, str]
    limitations: list[str]


class IncidentFindingsResponse(BaseModel):
    incident_id: str
    findings: list[FisheriesFinding]


class IncidentPrioritiesResponse(BaseModel):
    incident_id: str
    priorities: list[InspectionPriority]


class FisheriesReportResponse(BaseModel):
    title: Literal["DHARA — Pallimangal Fisheries Incident Screening Case Study"]
    report_type: Literal["exploratory_regional_investigation"]
    generated_at_utc: datetime
    incident: IncidentRecord
    study_area_map: dict[str, Any]
    fisheries_context: dict[str, Any]
    fisheries_assets: list[AssetRecord]
    satellite_observations: list[SatelliteObservation]
    water_change_screening: dict[str, Any]
    ai_screening: ModelEvidenceComparison
    findings: list[FisheriesFinding]
    asset_exposure: list[ExposureAssessment]
    inspection_priorities: list[InspectionPriority]
    recommended_inspection_checks: list[str]
    evidence_sources: list[SourceReference]
    field_inspection_records: list[InspectionRecord]
    unavailable_measurements: dict[str, Any]
    readiness: dict[str, str]
    limitations: list[str]


class FisheriesSummary(BaseModel):
    incident_id: str
    case_status: Literal["exploratory_regional_investigation"]
    what_happened: str
    satellite_screening: str
    inspection_needed: str
    recommended_checks: list[str]
    unknowns: list[str]
    evidence_ids: list[str]
