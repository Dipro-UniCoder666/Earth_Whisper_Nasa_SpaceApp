"""Create editable Phase 7C review artifacts without assigning labels."""
from __future__ import annotations
import csv, hashlib, json, shutil, sqlite3
from datetime import datetime, timezone
from pathlib import Path
import rasterio
from rasterio.enums import ColorInterp
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / 'data/gherproof/reference/phase7c'
SRC = ROOT / 'data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg'
GPKG = REF / 'gherproof_optical_reference_samples_editable.gpkg'
DESIGN = ROOT / 'data/gherproof/reference/phase7b/sampling_design_manifest.json'
OUT_MANIFEST = ROOT / 'data/gherproof/manifests/phase7c_annotation_workflow_manifest.json'
S2 = ROOT / 'data/gherproof/processed/phase7/sentinel2'

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def create_composite(date: str) -> Path:
    """Create fixed-source false-colour stack: R=B08, G=B04, B=B03."""
    out=REF/f'{date}_S2_false_colour_B08_B04_B03.tif'
    paths=[S2/f'{date}_B{b}_reflectance_10m.tif' for b in ('08','04','03')]
    with rasterio.open(paths[0]) as base:
        profile=base.profile.copy(); profile.update(count=3,dtype='float32',nodata=-9999.0,compress='deflate',predictor=3)
        arrays=[]
        for p in paths:
            with rasterio.open(p) as ds:
                if ds.crs!=base.crs or ds.transform!=base.transform or ds.shape!=base.shape:
                    raise ValueError(f'Optical source grids differ for {date}: {p.name}')
                a=ds.read(1).astype(np.float32)
                if ds.nodata is not None: a[a==ds.nodata]=-9999.0
                arrays.append(a)
        with rasterio.open(out,'w',**profile) as dst:
            for i,(a,desc) in enumerate(zip(arrays,('NIR B08 (red display channel)','Red B04 (green display channel)','Green B03 (blue display channel)')),1):
                dst.write(a,i);dst.set_band_description(i,desc)
            dst.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue)
            dst.update_tags(AREA_OR_POINT='Area',SOURCE_DATE=date,COMPOSITE='R=B08,G=B04,B=B03',DISPLAY_STRETCH='fixed reflectance 0.0-0.4')
    return out

def main():
    REF.mkdir(parents=True,exist_ok=True)
    if not SRC.exists(): raise FileNotFoundError(SRC)
    shutil.copy2(SRC,GPKG)
    con=sqlite3.connect(GPKG)
    cols={r[1] for r in con.execute('pragma table_info(samples)')}
    additions={
        'pre_notes':'TEXT','post_notes':'TEXT','reviewed_status':"TEXT NOT NULL DEFAULT 'not_reviewed'",
        'pre_reviewer':'TEXT','post_reviewer':'TEXT','pre_review_date':'TEXT','post_review_date':'TEXT',
        'pre_label_source':'TEXT','post_label_source':'TEXT','needs_second_review_reason':'TEXT',
        'pre_second_label':'TEXT','pre_second_confidence':'TEXT','pre_second_notes':'TEXT',
        'post_second_label':'TEXT','post_second_confidence':'TEXT','post_second_notes':'TEXT',
        'second_reviewer':'TEXT','second_review_date':'TEXT',
        'pre_review_disagreement':'TEXT','post_review_disagreement':'TEXT'}
    for name,typ in additions.items():
        if name not in cols: con.execute(f'ALTER TABLE samples ADD COLUMN {name} {typ}')
    # Enforce the controlled vocabulary for future edits; do not set any labels.
    for side in ('pre','post'):
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_label_insert BEFORE INSERT ON samples WHEN NEW.{side}_label IS NOT NULL AND NEW.{side}_label NOT IN ('water','non_water','uncertain','invalid') BEGIN SELECT RAISE(ABORT,'invalid {side}_label'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_label_update BEFORE UPDATE OF {side}_label ON samples WHEN NEW.{side}_label IS NOT NULL AND NEW.{side}_label NOT IN ('water','non_water','uncertain','invalid') BEGIN SELECT RAISE(ABORT,'invalid {side}_label'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_confidence_insert BEFORE INSERT ON samples WHEN NEW.{side}_confidence IS NOT NULL AND NEW.{side}_confidence NOT IN ('high','medium','low') BEGIN SELECT RAISE(ABORT,'invalid {side}_confidence'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_confidence_update BEFORE UPDATE OF {side}_confidence ON samples WHEN NEW.{side}_confidence IS NOT NULL AND NEW.{side}_confidence NOT IN ('high','medium','low') BEGIN SELECT RAISE(ABORT,'invalid {side}_confidence'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_second_label_insert BEFORE INSERT ON samples WHEN NEW.{side}_second_label IS NOT NULL AND NEW.{side}_second_label NOT IN ('water','non_water','uncertain','invalid') BEGIN SELECT RAISE(ABORT,'invalid {side}_second_label'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_second_label_update BEFORE UPDATE OF {side}_second_label ON samples WHEN NEW.{side}_second_label IS NOT NULL AND NEW.{side}_second_label NOT IN ('water','non_water','uncertain','invalid') BEGIN SELECT RAISE(ABORT,'invalid {side}_second_label'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_second_confidence_insert BEFORE INSERT ON samples WHEN NEW.{side}_second_confidence IS NOT NULL AND NEW.{side}_second_confidence NOT IN ('high','medium','low') BEGIN SELECT RAISE(ABORT,'invalid {side}_second_confidence'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{side}_second_confidence_update BEFORE UPDATE OF {side}_second_confidence ON samples WHEN NEW.{side}_second_confidence IS NOT NULL AND NEW.{side}_second_confidence NOT IN ('high','medium','low') BEGIN SELECT RAISE(ABORT,'invalid {side}_second_confidence'); END")
    con.execute("CREATE TRIGGER IF NOT EXISTS valid_review_status_insert BEFORE INSERT ON samples WHEN NEW.reviewed_status NOT IN ('not_reviewed','reviewed','needs_second_review') BEGIN SELECT RAISE(ABORT,'invalid reviewed_status'); END")
    con.execute("CREATE TRIGGER IF NOT EXISTS valid_review_status_update BEFORE UPDATE OF reviewed_status ON samples WHEN NEW.reviewed_status NOT IN ('not_reviewed','reviewed','needs_second_review') BEGIN SELECT RAISE(ABORT,'invalid reviewed_status'); END")
    for field in ('pre_review_disagreement','post_review_disagreement'):
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{field}_insert BEFORE INSERT ON samples WHEN NEW.{field} IS NOT NULL AND NEW.{field} NOT IN ('agree','disagree','unresolved') BEGIN SELECT RAISE(ABORT,'invalid {field}'); END")
        con.execute(f"CREATE TRIGGER IF NOT EXISTS valid_{field}_update BEFORE UPDATE OF {field} ON samples WHEN NEW.{field} IS NOT NULL AND NEW.{field} NOT IN ('agree','disagree','unresolved') BEGIN SELECT RAISE(ABORT,'invalid {field}'); END")
    immutable=('sample_id','sampling_stratum','spatial_block','split_group','x_utm','y_utm','inclusion_probability','sample_weight','pre_date','post_date','context_image','geom')
    unchanged=' OR '.join(f'NEW.{name} IS NOT OLD.{name}' for name in immutable)
    con.execute(f"CREATE TRIGGER IF NOT EXISTS preserve_sample_design BEFORE UPDATE ON samples WHEN {unchanged} BEGIN SELECT RAISE(ABORT,'sample identity/design/geometry fields are immutable'); END")
    con.execute('CREATE TABLE IF NOT EXISTS gpkg_data_columns (table_name TEXT NOT NULL, column_name TEXT NOT NULL, name TEXT, title TEXT, description TEXT, mime_type TEXT, constraint_name TEXT, CONSTRAINT pk_gpkg_data_columns PRIMARY KEY (table_name,column_name))')
    descriptions={
      'pre_label':'Human optical interpretation for Sentinel-2 2026-01-10: water/non_water/uncertain/invalid.',
      'post_label':'Human optical interpretation for Sentinel-2 2026-01-20: water/non_water/uncertain/invalid.',
      'pre_confidence':'Reviewer confidence: high/medium/low.','post_confidence':'Reviewer confidence: high/medium/low.',
      'pre_notes':'Pre-date interpretation notes; do not infer from model output.','post_notes':'Post-date interpretation notes; do not infer from model output.',
      'reviewed_status':'not_reviewed, reviewed, or needs_second_review; applies to the point pair.',
      'pre_second_label':'Optional independent second-review label for Jan 10.','post_second_label':'Optional independent second-review label for Jan 20.',
      'pre_second_confidence':'Second-reviewer confidence for Jan 10.','post_second_confidence':'Second-reviewer confidence for Jan 20.',
      'second_reviewer':'Independent second reviewer identifier when used.','second_review_date':'Second review date when used.',
      'pre_review_disagreement':'Independent reviewers: agree/disagree/unresolved for Jan 10.','post_review_disagreement':'Independent reviewers: agree/disagree/unresolved for Jan 20.',
      'sampling_stratum':'Blind-coded design stratum; do not reveal mapping during primary review.',
      'split_group':'Fixed spatial assignment: calibration, validation, or test.'}
    for field,desc in descriptions.items():
        con.execute('INSERT OR REPLACE INTO gpkg_data_columns(table_name,column_name,name,title,description) VALUES(?,?,?,?,?)',('samples',field,field.replace('_',' ').title(),field.replace('_',' ').title(),desc))
    con.commit()
    con.row_factory=sqlite3.Row
    rows=[dict(r) for r in con.execute('SELECT * FROM samples ORDER BY sample_id')]
    con.close()
    if len(rows)!=450 or len({r['sample_id'] for r in rows})!=450: raise ValueError('Sample IDs/count differ from expected original baseline')
    if any(r['pre_label'] not in (None,'') or r['post_label'] not in (None,'') for r in rows): raise ValueError('Source baseline unexpectedly contains labels')
    if any(r['reviewed_status']!='not_reviewed' for r in rows): raise ValueError('New copy must start not_reviewed')
    # A tabular template references immutable sample ids and assignment fields; leave all labels blank.
    fields=['sample_id','sampling_stratum','spatial_block','split_group','x_utm','y_utm','inclusion_probability','sample_weight','pre_date','post_date','pre_label','pre_confidence','pre_notes','post_label','post_confidence','post_notes','reviewed_status','pre_reviewer','post_reviewer','pre_review_date','post_review_date','pre_label_source','post_label_source','needs_second_review_reason','pre_second_label','pre_second_confidence','pre_second_notes','post_second_label','post_second_confidence','post_second_notes','second_reviewer','second_review_date','pre_review_disagreement','post_review_disagreement']
    csv_path=REF/'gherproof_optical_annotations_template.csv'
    with csv_path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:
            w.writerow({k:(r.get(k) if k in ('sample_id','sampling_stratum','spatial_block','split_group','x_utm','y_utm','inclusion_probability','sample_weight','pre_date','post_date') else '') for k in fields})
    # Freeze original spatial assignment; keep three existing groups intact.
    split={r['sample_id']:r['split_group'] for r in rows}
    split_path=ROOT/'data/gherproof/manifests/phase7c_fixed_spatial_split_manifest.json'
    split_doc={'status':'fixed_before_human_annotation','seed':20261113,'source':'Phase 7B sample package; assignments preserved, not regenerated','geometry_crs':'EPSG:32645','block_size_m':5000,'guard_band_m':1000,'roles':{'calibration':'calibration','validation':'validation','final_independent_evaluation':'test'},'sample_count':len(rows),'split_counts':{s:sum(v==s for v in split.values()) for s in ('calibration','validation','test')},'sample_assignments':split,'assignment_sha256':hashlib.sha256(json.dumps(split,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'no_split_changes_after_review':True,'limitations':'Spatial blocks and guards reduce local leakage; long-range spatial autocorrelation remains possible.'}
    split_path.write_text(json.dumps(split_doc,indent=2)+'\n',encoding='utf-8')
    composites=[create_composite(d) for d in ('2026-01-10','2026-01-20')]
    by_status={s:sum(r['reviewed_status']==s for r in rows) for s in ('not_reviewed','reviewed','needs_second_review')}
    progress={'status':'human_review_pending','sample_count':len(rows),'pre_label_slots':450,'post_label_slots':450,'completed_pre_labels':sum(r['pre_label'] not in (None,'') for r in rows),'completed_post_labels':sum(r['post_label'] not in (None,'') for r in rows),'reviewed_status_counts':by_status,'updated_at_utc':datetime.now(timezone.utc).isoformat()}
    (REF/'annotation_progress.json').write_text(json.dumps(progress,indent=2)+'\n',encoding='utf-8')
    (REF/'annotation_progress.md').write_text('# Optical annotation progress\n\n- Samples: 450\n- Pre-date slots: 0 / 450 complete\n- Post-date slots: 0 / 450 complete\n- Reviewed samples: 0 / 450\n- Needs second review: 0\n- Status: human review pending\n\nThis summary is generated from the editable GeoPackage. No labels have been assigned by automation.\n',encoding='utf-8')
    manifest={'status':'annotation_workflow_prepared_human_review_pending','source_baseline':str(SRC.relative_to(ROOT)).replace('\\','/'),'source_baseline_sha256':sha(SRC),'editable_geopackage':str(GPKG.relative_to(ROOT)).replace('\\','/'),'editable_geopackage_sha256':sha(GPKG),'sample_count':len(rows),'blank_pre_label_slots':450,'blank_post_label_slots':450,'split_manifest':str(split_path.relative_to(ROOT)).replace('\\','/'),'split_counts':split_doc['split_counts'],'csv_template':str(csv_path.relative_to(ROOT)).replace('\\','/'),'composites':[{'path':str(x.relative_to(ROOT)).replace('\\','/'),'sha256':sha(x)} for x in composites],'qgis_available':False,'qgis_project':'data/gherproof/reference/phase7c/gherproof_optical_annotation.qgs','qgis_open_test':'blocked_qgis_not_installed','progress':progress}
    OUT_MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'gpkg':str(GPKG.relative_to(ROOT)),'samples':len(rows),'blank_slots':900,'csv':str(csv_path.relative_to(ROOT)),'composites':[str(x.relative_to(ROOT)) for x in composites],'split_counts':split_doc['split_counts']},indent=2))

if __name__=='__main__': main()
