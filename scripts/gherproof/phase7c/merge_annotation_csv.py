"""Validate an edited CSV against the frozen design and merge to a new GPKG."""
from __future__ import annotations
import argparse,csv,shutil,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DEFAULT=ROOT/'data/gherproof/reference/phase7c/gherproof_optical_reference_samples_editable.gpkg'
LABELS={'water','non_water','uncertain','invalid'};CONF={'high','medium','low'};REVIEW={'not_reviewed','reviewed','needs_second_review'};DISAGREE={'agree','disagree','unresolved'}
IMMUTABLE=('sampling_stratum','spatial_block','split_group','x_utm','y_utm','inclusion_probability','sample_weight','pre_date','post_date')

def rows_from_gpkg(path):
    c=sqlite3.connect(path)
    try:
        c.row_factory=sqlite3.Row
        return {r['sample_id']:dict(r) for r in c.execute('SELECT * FROM samples')}
    finally: c.close()

def parse_csv(path,base):
    errors=[];out={}
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        for n,row in enumerate(csv.DictReader(f),start=2):
            sid=(row.get('sample_id') or '').strip()
            if not sid: errors.append(f'row {n}: missing sample_id');continue
            if sid in out: errors.append(f'row {n}: duplicate sample_id {sid}');continue
            if sid not in base: errors.append(f'row {n}: unknown sample_id {sid}');continue
            for key in IMMUTABLE:
                raw=row.get(key,'')
                try:
                    same=(abs(float(raw)-float(base[sid][key]))<=1e-7) if key in ('x_utm','y_utm','inclusion_probability','sample_weight') else raw==str(base[sid][key])
                except (ValueError,TypeError): same=False
                if not same: errors.append(f'row {n}: frozen field changed: {key}')
            for side in ('pre','post'):
                label=(row.get(f'{side}_label') or '').strip()
                confidence=(row.get(f'{side}_confidence') or '').strip()
                if label and label not in LABELS: errors.append(f'row {n}: invalid {side}_label {label}')
                if confidence and confidence not in CONF: errors.append(f'row {n}: invalid {side}_confidence {confidence}')
                if label and not confidence: errors.append(f'row {n}: {side}_confidence required for assigned label')
                if label:
                    for field in (f'{side}_reviewer',f'{side}_review_date',f'{side}_label_source'):
                        if not (row.get(field) or '').strip(): errors.append(f'row {n}: {field} required when {side}_label is assigned')
                second_label=(row.get(f'{side}_second_label') or '').strip()
                second_confidence=(row.get(f'{side}_second_confidence') or '').strip()
                if second_label and second_label not in LABELS: errors.append(f'row {n}: invalid {side}_second_label {second_label}')
                if second_confidence and second_confidence not in CONF: errors.append(f'row {n}: invalid {side}_second_confidence {second_confidence}')
                if second_label and not second_confidence: errors.append(f'row {n}: {side}_second_confidence required for second label')
                disagreement=(row.get(f'{side}_review_disagreement') or '').strip()
                if disagreement and disagreement not in DISAGREE: errors.append(f'row {n}: invalid {side}_review_disagreement {disagreement}')
            status=(row.get('reviewed_status') or 'not_reviewed').strip()
            if status not in REVIEW: errors.append(f'row {n}: invalid reviewed_status {status}')
            if status=='reviewed' and (not (row.get('pre_label') or '').strip() or not (row.get('post_label') or '').strip()): errors.append(f'row {n}: reviewed requires both date labels')
            out[sid]={k:(row.get(k) or '').strip() or None for k in ('pre_label','pre_confidence','pre_notes','post_label','post_confidence','post_notes','reviewed_status','pre_reviewer','post_reviewer','pre_review_date','post_review_date','pre_label_source','post_label_source','needs_second_review_reason','pre_second_label','pre_second_confidence','pre_second_notes','post_second_label','post_second_confidence','post_second_notes','second_reviewer','second_review_date','pre_review_disagreement','post_review_disagreement')}
            out[sid]['reviewed_status']=status
    missing=set(base)-set(out)
    if missing: errors.append(f'CSV missing {len(missing)} sample IDs')
    if len(out)!=len(base): errors.append(f'CSV row count {len(out)} differs from frozen sample count {len(base)}')
    return out,errors

def merge(csv_path,output_path,source=DEFAULT):
    base=rows_from_gpkg(source);values,errors=parse_csv(csv_path,base)
    if errors: raise ValueError('\n'.join(errors))
    output=Path(output_path).resolve()
    if output==Path(source).resolve(): raise ValueError('Output must be a new file; source annotation package cannot be overwritten')
    if output.exists(): raise FileExistsError(f'Refusing to overwrite existing output: {output}')
    output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,output)
    fields=('pre_label','pre_confidence','pre_notes','post_label','post_confidence','post_notes','reviewed_status','pre_reviewer','post_reviewer','pre_review_date','post_review_date','pre_label_source','post_label_source','needs_second_review_reason','pre_second_label','pre_second_confidence','pre_second_notes','post_second_label','post_second_confidence','post_second_notes','second_reviewer','second_review_date','pre_review_disagreement','post_review_disagreement')
    sql='UPDATE samples SET '+','.join(f'{x}=?' for x in fields)+' WHERE sample_id=?'
    c=sqlite3.connect(output)
    try:
        for sid,v in values.items(): c.execute(sql,tuple(v[k] for k in fields)+(sid,))
        c.commit()
    except Exception:
        c.close()
        output.unlink(missing_ok=True);raise
    finally:
        if c: c.close()
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--output',required=True);p.add_argument('--source',default=str(DEFAULT));a=p.parse_args()
    out=merge(a.csv,a.output,Path(a.source));print(f'Validated {len(rows_from_gpkg(out))} sample rows. Wrote new annotation GeoPackage: {out}')
