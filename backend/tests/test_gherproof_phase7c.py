from __future__ import annotations
import csv, importlib.util, sqlite3, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import rasterio

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'scripts/gherproof/phase7c/merge_annotation_csv.py'
spec=importlib.util.spec_from_file_location('merge_annotation_csv',SCRIPT)
merge_module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=merge_module;spec.loader.exec_module(merge_module)
GPKG=ROOT/'data/gherproof/reference/phase7c/gherproof_optical_reference_samples_editable.gpkg'
CSV=ROOT/'data/gherproof/reference/phase7c/gherproof_optical_annotations_template.csv'

def test_original_sample_identity_and_blank_fields_are_preserved():
    rows=merge_module.rows_from_gpkg(GPKG)
    assert len(rows)==450
    assert len(set(rows))==450
    assert all(r['pre_label'] in (None,'') and r['post_label'] in (None,'') for r in rows.values())
    assert all(r['reviewed_status']=='not_reviewed' for r in rows.values())
    for key in ('sampling_stratum','spatial_block','split_group','inclusion_probability','sample_weight'):
        assert all(r[key] is not None for r in rows.values())

def test_csv_template_round_trip_to_new_geopackage():
    base=merge_module.rows_from_gpkg(GPKG)
    submitted,errors=merge_module.parse_csv(CSV,base)
    assert not errors
    assert len(submitted)==450
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'roundtrip.gpkg'
        merged=merge_module.merge(CSV,out)
        got=merge_module.rows_from_gpkg(merged)
        assert got.keys()==base.keys()
        assert all(got[s]['sample_weight']==base[s]['sample_weight'] for s in base)
        assert all(got[s]['pre_label'] in (None,'') and got[s]['post_label'] in (None,'') for s in base)

def test_invalid_or_duplicate_csv_records_are_rejected():
    base=merge_module.rows_from_gpkg(GPKG)
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'bad.csv'
        with CSV.open(newline='',encoding='utf-8-sig') as src, path.open('w',newline='',encoding='utf-8') as dst:
            rows=list(csv.DictReader(src));fields=list(rows[0])
            rows[0]['pre_label']='flood'
            w=csv.DictWriter(dst,fieldnames=fields);w.writeheader();w.writerows(rows)
        _,errors=merge_module.parse_csv(path,base)
        assert any('invalid pre_label' in e for e in errors)
        with CSV.open(newline='',encoding='utf-8-sig') as src, path.open('w',newline='',encoding='utf-8') as dst:
            rows=list(csv.DictReader(src));fields=list(rows[0]);rows[0]['pre_label']='water';rows[0]['pre_confidence']='high'
            w=csv.DictWriter(dst,fieldnames=fields);w.writeheader();w.writerows(rows)
        _,errors=merge_module.parse_csv(path,base)
        assert any('pre_reviewer required' in e for e in errors)
        with CSV.open(newline='',encoding='utf-8-sig') as src, path.open('w',newline='',encoding='utf-8') as dst:
            rows=list(csv.DictReader(src));fields=list(rows[0]);rows.append(dict(rows[0]))
            w=csv.DictWriter(dst,fieldnames=fields);w.writeheader();w.writerows(rows)
        _,errors=merge_module.parse_csv(path,base)
        assert any('duplicate sample_id' in e for e in errors)

def test_geopackage_constraints_reject_invalid_labels_and_changed_design():
    with sqlite3.connect(GPKG) as c:
        sid=c.execute('select sample_id from samples limit 1').fetchone()[0]
        try:
            c.execute('update samples set pre_label=? where sample_id=?',('flood',sid))
        except sqlite3.IntegrityError: pass
        else: raise AssertionError('invalid label category was accepted')
        try:
            c.execute('update samples set sample_weight=sample_weight+1 where sample_id=?',(sid,))
        except sqlite3.IntegrityError: pass
        else: raise AssertionError('sample design fields must be immutable')

def test_qgs_xml_layers_resolve_and_have_no_model_predictions():
    project=ROOT/'data/gherproof/reference/phase7c/gherproof_optical_annotation.qgs'
    root=ET.parse(project).getroot();sources=[x.text for x in root.findall('./projectlayers/maplayer/datasource')]
    assert len(sources)==8
    for src in sources:
        assert (project.parent/src.split('|')[0]).resolve().exists(),src
    assert not any('inference' in s.lower() or 'probability' in s.lower() or 'disagreement' in s.lower() for s in sources)

def test_optical_composite_rasters_have_consistent_grids_and_three_bands():
    for date in ('2026-01-10','2026-01-20'):
        p=ROOT/f'data/gherproof/reference/phase7c/{date}_S2_false_colour_B08_B04_B03.tif'
        with rasterio.open(p) as ds:
            assert ds.count==3 and ds.crs.to_epsg()==32645 and ds.res==(10.0,10.0)
            assert ds.descriptions[0].startswith('NIR B08')

def test_frozen_spatial_split_blocks_and_guard_distances():
    with sqlite3.connect(GPKG) as c:
        groups={s:np.asarray(c.execute('select x_utm,y_utm from samples where split_group=?',(s,)).fetchall(),dtype=float) for s in ('calibration','validation','test')}
        blocks={s:{r[0] for r in c.execute('select spatial_block from samples where split_group=?',(s,))} for s in groups}
    assert blocks['calibration'].isdisjoint(blocks['validation'])
    assert blocks['calibration'].isdisjoint(blocks['test'])
    assert blocks['validation'].isdisjoint(blocks['test'])
    for i,a in enumerate(groups):
        for b in list(groups)[i+1:]:
            distances=np.sqrt(((groups[a][:,None,:]-groups[b][None,:,:])**2).sum(axis=2))
            assert distances.min()>=1000
