from __future__ import annotations
import json
from pathlib import Path
from fastapi.testclient import TestClient
import rasterio
from rasterio.warp import transform_bounds
from app.main import app
from app.services import gherproof_screening_service as screening
from app.services.gherproof_report_service import build_report

ROOT=Path(__file__).resolve().parents[2]
client=TestClient(app)

def test_registry_categories_integrity_and_provenance():
    data=json.loads((ROOT/'data/gherproof/manifests/evidence_registry.json').read_text())
    assert data['record_count']==len(data['records'])
    assert len({r['evidence_id'] for r in data['records']})==len(data['records'])
    expected={'verified_satellite_observation','catalogue_metadata','derived_satellite_measurement','model_prediction','optical_reference_interpretation','optical_weak_reference','model_comparison','uncertainty_layer','news_reported_event','provisional_geographic_reference','human_verified_evidence'}
    assert set(data['category_counts'])==expected
    for r in data['records']:
        assert r['confidence_or_validation_status'] in {'verified','derived','exploratory','provisional','unavailable','under_review'}
        for f in (r.get('original_file'),r.get('derived_file')):
            if f and f['availability']=='available':
                assert (ROOT/f['path']).is_file()
                assert f['checksum_matches_manifest'] is not False
    assert not any(r['evidence_category']=='human_verified_evidence' and r['confidence_or_validation_status']=='verified' for r in data['records'])

def test_status_keeps_unvalidated_readiness_explicit_and_legacy_fields():
    response=client.get('/api/gherproof/status')
    assert response.status_code==200
    body=response.json()
    assert body['model_readiness']=='exploratory_only'
    assert body['local_validation_status']=='human_review_pending'
    assert body['impact_quantification']=='not_approved'
    assert body['event_status']=='reported_by_news_sources_not_independently_verified'
    assert body['sentinel1_processed_event_observations']==0 if 'sentinel1_processed_event_observations' in body else body['processed_event_observations']==0

def test_evidence_filters_categories_and_invalid_filter():
    r=client.get('/api/gherproof/evidence',params={'category':'model_prediction','limit':500})
    assert r.status_code==200
    body=r.json();assert body['total']>=30
    assert all(x['evidence_category']=='model_prediction' for x in body['records'])
    assert client.get('/api/gherproof/evidence',params={'category':'made_up'}).status_code==422
    assert client.get('/api/gherproof/evidence',params={'acquisition_date':'not-a-date'}).status_code==422

def test_scene_prediction_and_optical_endpoints_do_not_merge_models():
    scenes=client.get('/api/gherproof/scenes').json()
    s1=[s for s in scenes['scenes'] if s['sensor']=='Sentinel-1']
    assert len(s1)==6
    partial=[s for s in s1 if s['acquisition_date'] in {'2026-01-07','2026-01-19'}]
    assert len(partial)==2
    assert all('local swath' in ' '.join(s['limitations']).lower() for s in partial)
    pairs=scenes['pre_post_eligibility']
    assert len(pairs)==3
    assert any(p.get('pair_id')=='2026-01-07_2026-01-19_rel114_ascending' for p in pairs)
    predictions=client.get('/api/gherproof/predictions').json()
    assert len(predictions['prediction_layers'])==24
    assert len(predictions['disagreement_layers'])==8
    assert predictions['model_selection']=='none'
    assert client.get('/api/gherproof/predictions',params={'model':'scratch'}).json()['models']==['scratch']
    optical=client.get('/api/gherproof/optical').json()
    assert optical['label_semantics'].startswith('optical reference indicators')
    assert 'not a human reference label' in ' '.join(optical['limitations'])

def test_raster_metadata_file_and_crs_nodata_preserved():
    evidence_id='prediction-scratch-2026-01-12-probability'
    meta=client.get(f'/api/gherproof/layers/{evidence_id}')
    assert meta.status_code==200
    body=meta.json();assert body['crs']=='EPSG:32645' and body['nodata']==-9999.0 and body['width']==3111
    file=client.get(f'/api/gherproof/layers/{evidence_id}/file')
    assert file.status_code==200 and file.headers['content-type'].startswith('image/tiff')
    assert file.headers['x-evidence-status']=='exploratory'

def test_missing_and_invalid_raster_paths_are_safe():
    assert client.get('/api/gherproof/layers/no-such-layer').status_code==404
    assert client.get('/api/gherproof/layers/prediction-scratch-2026-01-12-probability',params={'asset':'bad'}).status_code==422

def test_geographic_clip_is_bounded_and_preserves_crs():
    evidence_id='prediction-scratch-2026-01-12-probability';layer=screening.records('model_prediction')
    p=next(x for x in layer if x['evidence_id']==evidence_id)['derived_file']['path']
    with rasterio.open(ROOT/p) as ds:
        b=transform_bounds(ds.crs,'EPSG:4326',*ds.bounds,densify_pts=21)
    west,south,east,north=b;cx=(west+east)/2;cy=(south+north)/2
    bbox=f'{cx-0.005},{cy-0.005},{cx+0.005},{cy+0.005}'
    response=client.get(f'/api/gherproof/layers/{evidence_id}/clip',params={'bbox':bbox})
    assert response.status_code==200
    from rasterio.io import MemoryFile
    with MemoryFile(response.content) as mem:
        with mem.open() as ds:
            assert ds.crs.to_epsg()==32645 and ds.width<3111 and ds.height<2156 and ds.nodata==-9999.0
    assert client.get(f'/api/gherproof/layers/{evidence_id}/clip',params={'bbox':'0,0,100,100'}).status_code in (200,422)
    assert client.get(f'/api/gherproof/layers/{evidence_id}/clip',params={'bbox':'0,0,181,95'}).status_code==422

def test_provisional_geojson_validates_and_exposes_uncertainty():
    assert client.get('/api/gherproof/coverage').json()['status']=='provisional'
    response=client.get('/api/gherproof/geography/geography-provisional-regional-aoi')
    assert response.status_code==200 and response.json()['type']=='FeatureCollection'

def test_unavailable_annotation_and_no_impact_estimation_route():
    body=client.get('/api/gherproof/limitations').json()
    assert body['local_validation_status']=='human_review_pending'
    assert client.get('/api/gherproof/impact-estimate').status_code==404
    assert client.get('/api/gherproof/area').status_code==404

def test_report_generation_is_evidence_aware_and_non_attributive():
    report=build_report()
    assert report['model_readiness']=='exploratory_only'
    assert report['impact_quantification']=='not_approved'
    assert report['optical_reference']['completed_labels']==0
    assert report['study_area']['authoritative_village_or_enclosure_boundary'] is False
    assert all(x.startswith('prediction-') for x in report['model_predictions']['evidence_ids'])
    response=client.get('/api/gherproof/reports/summary.md')
    assert response.status_code==200
    assert 'presented as measured flood area' in response.text

def test_report_index_and_registry_counts():
    idx=client.get('/api/gherproof/reports')
    assert idx.status_code==200
    assert idx.json()['evidence_summary']['model_prediction']==50
    assert client.get('/api/gherproof/reports/files/../../README.md').status_code==404
