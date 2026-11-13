import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/gherproof/phase7b'))
from reference_evaluation import validate_reference_rows,weighted_metrics,choose_threshold
from assess_grd_counterparts import exact_metadata_match

def test_weighted_metrics_and_threshold_selection_are_correct():
    result=weighted_metrics([1,1,0],[.9,.2,.8],[2,1,3],.5)
    assert result['weighted_confusion_rows_true_0_1_cols_pred_0_1']==[[0.0,3.0],[1.0,2.0]]
    assert result['weighted_precision']==pytest.approx(2/5)
    assert result['weighted_recall']==pytest.approx(2/3)
    assert result['weighted_iou']==pytest.approx(2/6)
    assert 0 <= result['weighted_pr_auc_average_precision'] <= 1
    threshold=choose_threshold([0,0,1,1],[.1,.3,.7,.9],[1,1,2,2])
    assert threshold['weighted_f1']==pytest.approx(1)
    assert threshold['threshold']==pytest.approx(.5)

def test_metrics_reject_nonbinary_or_invalid_probability_and_weight():
    with pytest.raises(ValueError): weighted_metrics([0,2],[.1,.9],[1,1])
    with pytest.raises(ValueError): weighted_metrics([0,1],[.1,float('nan')],[1,1])
    with pytest.raises(ValueError): weighted_metrics([0,1],[.1,.9],[1,0])

def test_reference_validation_tracks_uncertain_invalid_and_bad_labels():
    rows=[{'sample_id':'a','pre_label':'water','pre_confidence':'high'},
          {'sample_id':'b','post_label':'uncertain','post_confidence':'low'},
          {'sample_id':'c','pre_label':'invalid','pre_confidence':'medium'},
          {'sample_id':'d','post_label':'maybe','post_confidence':'certain'}]
    result=validate_reference_rows(rows)
    assert result['counts']=={'water':1,'non_water':0,'uncertain':1,'invalid':1}
    assert result['binary_reference_count']==1
    assert len(result['errors'])==2

def test_annotation_geopackage_is_blind_valid_and_spatially_blocked():
    package=ROOT/'data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg'
    design=json.loads((package.parent/'sampling_design_manifest.json').read_text())
    con=sqlite3.connect(package);con.row_factory=sqlite3.Row
    rows=[dict(r) for r in con.execute('SELECT * FROM samples')]
    srs=con.execute('SELECT srs_id FROM gpkg_geometry_columns WHERE table_name="samples"').fetchone()[0]
    cols={r['name'] for r in con.execute('PRAGMA table_info(samples)')}
    con.close()
    assert srs==32645
    assert len(rows)==design['sample_count']==450
    assert {'pre_label','post_label','pre_confidence','post_confidence','pre_scl_clear','post_scl_clear','sample_weight','inclusion_probability','context_image'}<=cols
    assert not any('model' in c.lower() or 'prediction' in c.lower() for c in cols)
    assert all(r['pre_label'] is None and r['post_label'] is None for r in rows)
    assert len({r['sample_id'] for r in rows})==len(rows)
    split_by_block={}
    for r in rows:
        split_by_block.setdefault(r['spatial_block'],set()).add(r['split_group'])
        assert len(r['sampling_stratum'])==3
        assert r['inclusion_probability']>0 and r['sample_weight']==pytest.approx(1/r['inclusion_probability'])
        assert (package.parent/r['context_image']).exists()
    assert all(len(v)==1 for v in split_by_block.values())
    assert design['model_predictions_embedded_in_annotation_package'] is False

def test_evaluator_reports_pending_without_human_labels():
    p=ROOT/'data/gherproof/manifests/phase7b_model_evaluation_manifest.json'
    if p.exists():
        d=json.loads(p.read_text())
        assert d['local_validation_status']=='human_review_pending'
        assert d['metrics'] is None
        assert d['label_audit']['counts']['water']==0

def test_grd_counterparts_are_exact_time_geometry_and_polarization_matches():
    p=json.loads((ROOT/'data/gherproof/manifests/phase7b_grd_counterpart_manifest.json').read_text())
    rtc=json.loads((ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json').read_text())
    assert len(p['records'])==4
    assert all(r['status']=='exact_counterpart_found' for r in p['records'])
    for r in p['records']:
        source=next(x for x in rtc['scenes'] if x['item_id']==r['rtc_item_id'])
        assert exact_metadata_match(source['item_metadata'],r['match'])
        assert r['vv_asset_present'] and r['vh_asset_present']

def test_grd_inspection_does_not_claim_georeferenced_or_processed_grd():
    p=json.loads((ROOT/'data/gherproof/manifests/phase7b_grd_raster_inspection.json').read_text())
    assert len(p['records'])==4
    assets=[v for x in p['records'] for v in x['asset_inspections'].values()]
    metadata=[x for x in assets if x.get('raster_metadata')]
    assert len(metadata)==8
    assert all(x['raster_metadata']['crs'] in (None,'None') for x in metadata)
    assert all(x['raster_metadata']['dtype']==['uint16'] for x in metadata)
    assert p['processed_full_scenes']==0
    assert p['pixel_sampled_assets']==7 and p['pixel_sample_read_failures']==1

def test_model_output_audit_and_cross_sensor_alignment():
    audit=json.loads((ROOT/'data/gherproof/manifests/phase7b_model_output_audit.json').read_text())
    assert audit['status']=='pass' and audit['scene_count']==8
    assert all(s['hash_matches_manifest'] and s['valid_count_matches_manifest'] for s in audit['scenes'])
    assert all(s['valid_pixels']==6_475_371 and s['invalid_pixels']==231_945 for s in audit['scenes'])
    cross=json.loads((ROOT/'data/gherproof/manifests/phase7b_cross_sensor_validation.json').read_text())
    opt=json.loads((ROOT/'data/gherproof/manifests/phase7_optical_processing.json').read_text())
    assert len(cross['comparisons'])==24 and len(cross['outputs'])==48
    assert cross['source_products_preserved'] is True
    assert cross['qc']['status']=='pass'
    import sys
    sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
    import rasterio
    refpath=ROOT/opt['scenes'][0]['mndwi']['path']
    with rasterio.open(refpath) as ref:grid=(ref.crs,ref.transform,ref.width,ref.height)
    for item in cross['outputs']:
        with rasterio.open(ROOT/item['path']) as ds:
            assert (ds.crs,ds.transform,ds.width,ds.height)==grid
