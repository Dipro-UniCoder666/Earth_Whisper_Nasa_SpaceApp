"""Stable machine-readable schemas for evidence-aware regional screening."""
from typing import Any, Literal
from pydantic import BaseModel, Field

EvidenceCategory=Literal['verified_satellite_observation','catalogue_metadata','derived_satellite_measurement','historical_landcover_context','model_prediction','optical_reference_interpretation','optical_weak_reference','model_comparison','uncertainty_layer','news_reported_event','provisional_geographic_reference','human_verified_evidence']
# Keep the registry's explicit maturity vocabulary. Some derived comparison
# layers use the more precise derived_exploratory status so they cannot be
# mistaken for measured or validated observations.
EvidenceStatus=Literal['verified','derived','exploratory','derived_exploratory','provisional','unavailable','under_review']

class EvidenceFile(BaseModel):
    path:str|None=None
    availability:Literal['available','unavailable','invalid_path','not_downloaded']
    bytes:int|None=None
    sha256:str|None=None
    checksum_matches_manifest:bool|None=None

class EvidenceRecord(BaseModel):
    evidence_id:str
    evidence_category:EvidenceCategory
    title:str
    source_dataset:str
    acquisition_date:str|None=None
    processing_date:str|None=None
    spatial_coverage:dict[str,Any]|None=None
    crs:str|None=None
    original_file:EvidenceFile|None=None
    derived_file:EvidenceFile|None=None
    confidence_or_validation_status:EvidenceStatus
    processing_methodology:str|None=None
    limitations:list[str]=Field(default_factory=list)
    source_provenance:list[str]=Field(default_factory=list)
    metadata:dict[str,Any]=Field(default_factory=dict)

class EvidenceListResponse(BaseModel):
    total:int
    offset:int
    limit:int
    categories:list[str]
    records:list[EvidenceRecord]

class ScreeningStatusResponse(BaseModel):
    project_status:str
    product_direction:str
    data_readiness:str
    model_readiness:Literal['exploratory_only']
    geographic_readiness:str
    local_validation_status:Literal['human_review_pending']
    human_label_slots:int=0
    human_labels_completed:int=0
    impact_quantification:str
    satellite_acquisitions:dict[str,Any]
    model_outputs:dict[str,Any]
    limitations:list[str]

class SceneResponse(BaseModel):
    scenes:list[dict[str,Any]]
    pre_post_eligibility:list[dict[str,Any]]

class LayerMetadataResponse(BaseModel):
    evidence_id:str
    status:EvidenceStatus
    available:bool
    path:str|None=None
    crs:str|None=None
    bounds:list[float]|None=None
    width:int|None=None
    height:int|None=None
    resolution:list[float]|None=None
    count:int|None=None
    dtype:list[str]|None=None
    nodata:float|int|None=None
    descriptions:list[str|None]|None=None
    checksum:str|None=None
    limitations:list[str]=Field(default_factory=list)

class ReportIndexResponse(BaseModel):
    generated_at_utc:str
    reports:list[dict[str,Any]]
    evidence_summary:dict[str,Any]
