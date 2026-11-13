from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
import rasterio
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/gherproof/phase8b'))
from weak_reference import classify_change, classify_weak_reference, comparison_metrics, normalized_difference, reflectance_from_dn, spatial_block_summaries
from app.main import app
from app.api.gherproof import get_evidence
from app.services import gherproof_screening_service as screening

client=TestClient(app)

def test_reflectance_metadata_formula_and_offset():
    a,valid=reflectance_from_dn(np.array([0,1000,3000],dtype=np.uint16),-1000,10000)
    assert valid.tolist()==[False,True,True]
    assert np.isnan(a[0]) and a[1]==0 and np.isclose(a[2],0.2)

def test_dn_zero_and_nonfinite_are_nodata():
    a,valid=reflectance_from_dn(np.array([0,np.nan,4000]),-1000,10000)
    assert valid.tolist()==[False,False,True] and np.isfinite(a[2])

def test_scene_offsets_are_recorded_per_scene():
    m=json.loads((ROOT/'data/gherproof/manifests/phase8b_weak_reference_manifest.json').read_text())
    assert set(m['methodology']['BOA_add_offset_by_band_each_scene'])=={'2026-01-10','2026-01-20'}
    assert all(set(v.values())=={-1000} for v in m['methodology']['BOA_add_offset_by_band_each_scene'].values())

def test_ndwi_formula_and_bounds_on_positive_reflectance():
    out,valid=normalized_difference(np.array([0.3]),np.array([0.1]))
    assert valid[0] and np.isclose(out[0],0.5)

def test_mndwi_formula_uses_green_and_swir1():
    green=np.array([0.25]);swir=np.array([0.05])
    out,valid=normalized_difference(green,swir)
    assert valid[0] and np.isclose(out[0],2/3)

def test_low_denominator_is_excluded():
    out,valid=normalized_difference(np.array([0.001]),np.array([0.002]))
    assert not valid[0] and np.isnan(out[0])

def test_threshold_provenance_was_frozen_before_sar_comparison():
    c=json.loads((ROOT/'data/gherproof/manifests/phase8b_optical_threshold_config.json').read_text())
    assert c['frozen_before_sar_comparison'] is True
    assert c['model_prediction_used'] is False and c['thresholds']=={'ndwi':0.0,'mndwi':0.0}

def test_scl_six_requires_both_positive_indices_for_weak_water():
    labels=classify_weak_reference([6,6],[0.1,-0.1],[0.2,0.2],[True,True])
    assert labels.tolist()==[1,3]

def test_scl_four_five_require_both_negative_indices_for_weak_nonwater():
    labels=classify_weak_reference([4,5],[-0.1,-0.1],[-0.2,0.2],[True,True])
    assert labels.tolist()==[2,3]

def test_scl_two_and_seven_remain_uncertain():
    labels=classify_weak_reference([2,7],[0.2,0.2],[0.2,0.2],[True,True])
    assert labels.tolist()==[3,3]

def test_cloud_shadow_and_defective_scl_are_not_binary():
    labels=classify_weak_reference([0,1,3,8,9,10,11],[0.2]*7,[0.2]*7,[True]*7)
    assert labels.tolist()==[0]*7

def test_no_spectral_validity_is_invalid_or_uncertain_only_by_scl_context():
    labels=classify_weak_reference([6,7],[np.nan,np.nan],[np.nan,np.nan],[False,False])
    assert labels.tolist()==[0,0]

def test_temporal_change_categories_cover_all_transitions():
    out=classify_change([1,2,1,2,3,0],[1,1,2,2,1,1],[1,1,1,1,1,0],[1,1,1,1,1,1])
    assert out.tolist()==[1,2,3,4,5,0]

def test_temporal_change_rejects_grid_mismatch():
    import pytest
    with pytest.raises(ValueError): classify_change([1],[1,2])

def test_all_weak_reference_products_share_native_20m_grid():
    for date in ('2026-01-10','2026-01-20'):
        with rasterio.open(ROOT/f'data/gherproof/processed/phase8b/optical/{date}/weak_reference.tif') as ds:
            assert ds.crs.to_string()=='EPSG:32645' and ds.res==(20.0,20.0)
            assert (ds.width,ds.height)==(1556,1079) and ds.nodata==255

def test_probability_aggregation_is_on_the_20m_common_grid():
    p=ROOT/'data/gherproof/processed/phase8b/comparison/sar_optical/2026-01-12_scratch/probability_20m_mean.tif'
    with rasterio.open(p) as ds:
        assert ds.crs.to_string()=='EPSG:32645' and ds.res==(20.0,20.0)
        a=ds.read(1,masked=True).compressed();assert a.size and np.nanmin(a)>=0 and np.nanmax(a)<=1

def test_joint_validity_layer_keeps_availability_classes_separate():
    p=ROOT/'data/gherproof/processed/phase8b/comparison/sar_optical/2026-01-12_scratch/joint_coverage_codes.tif'
    with rasterio.open(p) as ds:
        vals=set(np.unique(ds.read(1,masked=True).compressed()).tolist())
    assert vals <= {0,1,2,3}

def test_weak_reference_agreement_confusion_counts():
    m=comparison_metrics(np.array([1,1,2,2,3]),np.array([1,0,0,1,1]),np.array([1,1,1,1,1]))
    assert m['confusion_matrix']=={'weak_water_predicted_water':1,'weak_water_predicted_nonwater':1,'weak_nonwater_predicted_nonwater':1,'weak_nonwater_predicted_water':1}
    assert m['weak_reference_agreement']==0.5 and m['weak_reference_positive_agreement']==0.5 and m['weak_reference_negative_agreement']==0.5
    assert m['uncertain_reference_pixels_excluded']==1

def test_spatial_blocks_are_descriptive_not_naive_confidence_intervals():
    summary,blocks=spatial_block_summaries(np.array([[1,2],[1,2]]),np.array([[1,0],[0,1]]),np.ones((2,2),bool),0,0,1)
    assert summary['block_count_with_valid_labels']==4 and len(blocks)==4
    assert 'not a pixel-independent confidence interval' in summary['uncertainty_note']

def test_model_labels_never_feed_weak_reference_thresholds():
    m=json.loads((ROOT/'data/gherproof/manifests/phase8b_weak_reference_manifest.json').read_text())
    assert m['methodology']['model_prediction_used_in_label_creation'] is False
    c=json.loads((ROOT/'data/gherproof/manifests/phase8b_optical_threshold_config.json').read_text())
    assert c['model_prediction_used'] is False

def test_registry_preserves_existing_and_adds_phase8b_categories():
    r=json.loads((ROOT/'data/gherproof/manifests/evidence_registry.json').read_text())
    assert r['record_count']==len(r['records']) and len({x['evidence_id'] for x in r['records']})==r['record_count']
    assert {'optical_weak_reference','model_comparison','uncertainty_layer'} <= set(r['category_counts'])
    assert 'reported-event-2026-01-14' in {x['evidence_id'] for x in r['records']}

def test_new_evidence_categories_are_accepted_by_registry_api_handler():
    body=get_evidence(category='optical_weak_reference',status=None,acquisition_date=None,offset=0,limit=100)
    assert body['total']==8 and all(x['evidence_category']=='optical_weak_reference' for x in body['records'])

def test_scenario_json_is_evidence_linked_and_explicitly_simulated():
    s=json.loads((ROOT/'data/gherproof/scenarios/january_2026_regional_screening_demo.json').read_text())
    ids={r['evidence_id'] for r in json.loads((ROOT/'data/gherproof/manifests/evidence_registry.json').read_text())['records']}
    assert s['is_simulated'] and s['demonstration_mode'].startswith('simulated_')
    assert len(s['demonstration_steps'])==8 and s['incident_context']['coordinates'] is None
    assert all(x['evidence_id'] in ids for x in [s['source_event_registry_record']])
    assert s['readiness_statuses']['impact_quantification']=='not_approved'

def test_api_returns_consistent_weak_reference_metrics_and_demo():
    w=client.get('/api/gherproof/weak-reference').json();c=client.get('/api/gherproof/comparisons').json()
    s=client.get('/api/gherproof/scenarios/january_2026_regional_screening_demo').json()
    p=client.get('/api/gherproof/predictions').json()
    weak_records=screening.records('optical_weak_reference')
    assert w['status']=='generated_independent_optical_weak_reference'
    assert len(c['per_model_acquisition_results'])==8 and c['metric_semantics']=='weak_reference_agreement; not local accuracy'
    assert len(p['comparison_grid_prediction_layers'])==16
    assert len(weak_records)==8 and all(x['evidence_category']=='optical_weak_reference' for x in weak_records)
    assert s['is_simulated'] is True
    assert client.get('/api/gherproof/scenarios/not-allowed').status_code==404

def test_original_annotation_package_and_fixed_split_remain_unchanged():
    m=json.loads((ROOT/'data/gherproof/manifests/phase7c_annotation_workflow_manifest.json').read_text())
    baseline=ROOT/m['source_baseline'];editable=ROOT/m['editable_geopackage']
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()==m['source_baseline_sha256']
    assert hashlib.sha256(editable.read_bytes()).hexdigest()==m['editable_geopackage_sha256']
    assert m['sample_count']==450 and m['progress']['completed_pre_labels']==0 and m['progress']['completed_post_labels']==0

def test_every_generated_geotiff_reopens_and_matches_qc_checksums():
    qc=json.loads((ROOT/'data/gherproof/manifests/phase8b_raster_qc_manifest.json').read_text())
    assert qc['status']=='all_phase8b_geotiffs_reopened' and qc['raster_count']>=40
    for x in qc['rasters']:
        p=ROOT/x['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
        with rasterio.open(p) as ds:
            assert ds.crs and ds.width==x['width'] and ds.height==x['height'] and ds.nodata==x['nodata']
            a=ds.read(1,masked=True).compressed()
            if np.issubdtype(a.dtype,np.floating): assert np.isfinite(a).all()
