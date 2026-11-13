"""Validate returned human labels and evaluate existing models only when ready."""
from __future__ import annotations
import json,sqlite3,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.extend([str(Path(__file__).resolve().parents[3]/'backend/.venv/Lib/site-packages'),str(Path(__file__).resolve().parents[3]/'scripts/gherproof/phase7b')])
import numpy as np,rasterio
from rasterio.windows import Window
from reference_evaluation import validate_reference_rows,weighted_metrics,choose_threshold

ROOT=Path(__file__).resolve().parents[3]
GPKG=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'data/gherproof/reference/phase7c/gherproof_optical_reference_samples_editable.gpkg'
BASE=ROOT/'data/gherproof/reference/phase7b/gherproof_optical_reference_samples.gpkg'
INF=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json'
SPLIT=ROOT/'data/gherproof/manifests/phase7c_fixed_spatial_split_manifest.json'
OUT=ROOT/'data/gherproof/manifests/phase7c_model_evaluation_manifest.json'
READY=ROOT/'data/gherproof/manifests/phase7c_model_readiness.json'
MIN_BINARY=30

def read_rows(path):
    with sqlite3.connect(path) as c:
        c.row_factory=sqlite3.Row
        return [dict(r) for r in c.execute('SELECT * FROM samples ORDER BY sample_id')]

def validate_identity(rows,baseline):
    errors=[];ids=[r.get('sample_id') for r in rows]
    if len(ids)!=len(set(ids)): errors.append('Duplicate sample_id values in annotation layer')
    bmap={r['sample_id']:r for r in baseline}
    if set(ids)!=set(bmap): errors.append('Submitted sample_id set differs from untouched baseline')
    fixed=('sampling_stratum','spatial_block','split_group','inclusion_probability','sample_weight')
    for r in rows:
        b=bmap.get(r.get('sample_id'))
        if not b: continue
        for key in fixed:
            if r.get(key)!=b.get(key): errors.append(f"{r['sample_id']} changed frozen field {key}")
        for key in ('x_utm','y_utm'):
            if abs(float(r.get(key) or 0)-float(b.get(key) or 0))>1e-7: errors.append(f"{r['sample_id']} changed coordinate {key}")
    return errors

def main():
    rows=read_rows(GPKG);base=read_rows(BASE);label_audit=validate_reference_rows(rows)
    errors=validate_identity(rows,base)+label_audit['errors']
    allowed_status={'not_reviewed','reviewed','needs_second_review'}
    for r in rows:
        if r.get('reviewed_status') not in allowed_status: errors.append(f"{r.get('sample_id')}: invalid reviewed_status")
        for side in ('pre','post'):
            if r.get(f'{side}_label') not in (None,''):
                if r.get(f'{side}_confidence') not in ('high','medium','low'): errors.append(f"{r.get('sample_id')}: {side}_confidence required for assigned label")
                for field in (f'{side}_reviewer',f'{side}_review_date',f'{side}_label_source'):
                    if not r.get(field): errors.append(f"{r.get('sample_id')}: {field} required for assigned label")
            second_label=r.get(f'{side}_second_label')
            if second_label not in (None,'','water','non_water','uncertain','invalid'): errors.append(f"{r.get('sample_id')}: invalid {side}_second_label")
            second_conf=r.get(f'{side}_second_confidence')
            if second_conf not in (None,'','high','medium','low'): errors.append(f"{r.get('sample_id')}: invalid {side}_second_confidence")
            if second_label not in (None,''):
                if second_conf not in ('high','medium','low'): errors.append(f"{r.get('sample_id')}: {side}_second_confidence required")
                if not r.get('second_reviewer') or not r.get('second_review_date'): errors.append(f"{r.get('sample_id')}: second reviewer/date required")
            disagreement=r.get(f'{side}_review_disagreement')
            if disagreement not in (None,'','agree','disagree','unresolved'): errors.append(f"{r.get('sample_id')}: invalid {side}_review_disagreement")
    review_counts={s:sum(r.get('reviewed_status')==s for r in rows) for s in sorted(allowed_status)}
    low_confidence={side:sum(r.get(f'{side}_confidence')=='low' for r in rows) for side in ('pre','post')}
    second_review_samples=[r['sample_id'] for r in rows if r.get('reviewed_status')=='needs_second_review']
    status='human_review_pending';metrics=None;thresholds=None;error_rows=[];gate={}
    if errors: status='invalid_reference_labels'
    elif label_audit['blank_slots']>0: status='human_review_pending'
    elif second_review_samples or review_counts['not_reviewed']>0: status='second_review_or_review_status_pending'
    else:
        gate_counts={}
        for split_name in ('calibration','validation','test'):
            for side in ('pre','post'):
                subset=[r for r in rows if r.get('split_group')==split_name and r.get(f'{side}_label') in ('water','non_water')]
                gate_counts[f'{split_name}_{side}']={'binary_count':len(subset),'water_count':sum(r[f'{side}_label']=='water' for r in subset),'non_water_count':sum(r[f'{side}_label']=='non_water' for r in subset)}
        gate={'minimum_binary_references_per_date_and_split':MIN_BINARY,'counts':gate_counts}
        if any(v['binary_count']<MIN_BINARY or not v['water_count'] or not v['non_water_count'] for v in gate_counts.values()):
            status='insufficient_valid_reference_labels'
        else:
            inference=json.loads(INF.read_text(encoding='utf-8'));scenes={(r['item_id'],r['model']):r for r in inference['scenes']};results=[];thresholds=[]
            for pair in inference['pairs']:
                for model in ('scratch','pretrained'):
                    observations=[]
                    for side,item_id in (('pre',pair['pre_item_id']),('post',pair['post_item_id'])):
                        rec=scenes[(item_id,model)];raster=ROOT/rec['probability']['path']
                        with rasterio.open(raster) as ds:
                            for row in rows:
                                label=row.get(f'{side}_label')
                                if label not in ('water','non_water'): continue
                                rr,cc=ds.index(float(row['x_utm']),float(row['y_utm']))
                                if rr<0 or cc<0 or rr>=ds.height or cc>=ds.width: continue
                                p=float(ds.read(1,window=Window(cc,rr,1,1))[0,0])
                                if ds.nodata is not None and p==ds.nodata: continue
                                observations.append({'sample_id':row['sample_id'],'split':row['split_group'],'side':side,'item_id':item_id,'stratum':row['sampling_stratum'],'confidence':row.get(f'{side}_confidence') or 'unspecified','label':int(label=='water'),'probability':p,'weight':float(row['sample_weight'])})
                    cal=[o for o in observations if o['split']=='calibration']
                    if not cal: continue
                    threshold=choose_threshold([o['label'] for o in cal],[o['probability'] for o in cal],[o['weight'] for o in cal])
                    thresholds.append({'pair_id':pair['pair_id'],'model':model,'calibration_count':len(cal),'selected_threshold':threshold['threshold'],'calibration_metrics':threshold})
                    for split_name in ('calibration','validation','test'):
                        for side in ('pre','post'):
                            subset=[o for o in observations if o['split']==split_name and o['side']==side]
                            if not subset: continue
                            def met(xs):
                                if not xs:return None
                                return weighted_metrics([o['label'] for o in xs],[o['probability'] for o in xs],[o['weight'] for o in xs],threshold['threshold'])
                            per_stratum={s:met([o for o in subset if o['stratum']==s]) for s in sorted({o['stratum'] for o in subset})}
                            per_confidence={s:met([o for o in subset if o['confidence']==s]) for s in sorted({o['confidence'] for o in subset})}
                            results.append({'pair_id':pair['pair_id'],'model':model,'split':split_name,'side':side,'scene_id':pair['pre_item_id'] if side=='pre' else pair['post_item_id'],'overall':met(subset),'by_stratum':per_stratum,'by_confidence':per_confidence})
                            if split_name=='test':
                                for o in subset:
                                    pred=int(o['probability']>=threshold['threshold'])
                                    if pred!=o['label']:error_rows.append({'pair_id':pair['pair_id'],'model':model,'scene_id':o['item_id'],'sample_id':o['sample_id'],'stratum':o['stratum'],'confidence':o['confidence'],'reference':'water' if o['label'] else 'non_water','prediction':'water' if pred else 'non_water','error':'false_positive' if pred else 'false_negative','probability':o['probability']})
            metrics=results;status='evaluated_spatially_heldout_human_reference'
    counts={k:int(v) for k,v in label_audit['counts'].items()}
    interrater={}
    for side in ('pre','post'):
        pairs=[r for r in rows if r.get(f'{side}_label') not in (None,'') and r.get(f'{side}_second_label') not in (None,'')]
        agreement=sum(r[f'{side}_label']==r[f'{side}_second_label'] for r in pairs)
        interrater[side]={'paired_labels':len(pairs),'exact_agreement_count':agreement,'observed_agreement':agreement/len(pairs) if pairs else None,'disagreement_count':len(pairs)-agreement,'field_disagreement_mismatches':sum(bool(r.get(f'{side}_review_disagreement')) and r[f'{side}_review_disagreement']!=('agree' if r[f'{side}_label']==r[f'{side}_second_label'] else 'disagree') for r in pairs)}
    reviewers={str(r[k]).strip() for r in rows for k in ('pre_reviewer','post_reviewer','second_reviewer') if r.get(k) not in (None,'')}
    report={'status':status,'local_validation_status':status,'readiness':'exploratory_only','phase8_impact_quantification':'NOT_APPROVED','created_at_utc':datetime.now(timezone.utc).isoformat(),'annotation_geopackage':str(GPKG.relative_to(ROOT)).replace('\\','/'),'sample_count':len(rows),'annotator_count':len(reviewers),'label_audit':label_audit,'identity_validation_errors':errors,'review_status_counts':review_counts,'low_confidence_counts':low_confidence,'needs_second_review_sample_ids':second_review_samples,'interrater_agreement':interrater,'sufficiency_gate':gate,'threshold_selection':thresholds,'metrics':metrics,'heldout_error_records':error_rows,'methodology':{'threshold':'select per model and geometry using calibration subset weighted F1; never tune on final test','final_comparison':'same held-out reference points for scratch and pretrained models; metrics reported separately by acquisition, stratum and confidence','uncertain_invalid':'excluded from binary metrics, counts and blank proportions retained','labels':'human optical interpretation only, not field-verified ground truth'}}
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    readiness={'readiness':'exploratory_only','local_validation_status':status,'phase8_impact_quantification':'NOT_APPROVED','human_labels_completed':sum(label_audit['counts'].values()),'human_label_slots':label_audit['label_slots'],'metrics_manifest':str(OUT.relative_to(ROOT)).replace('\\','/'),'reason':'No human labels supplied; model probabilities are not reference observations.' if status=='human_review_pending' else 'Evaluation output does not automatically authorize regional impact quantification; review evidence and uncertainty before changing readiness.'}
    (READY).write_text(json.dumps(readiness,indent=2)+'\n',encoding='utf-8')
    prog={'status':status,'sample_count':len(rows),'pre_label_slots':len(rows),'post_label_slots':len(rows),'completed_pre_labels':sum(r.get('pre_label') not in (None,'') for r in rows),'completed_post_labels':sum(r.get('post_label') not in (None,'') for r in rows),'reviewed_status_counts':review_counts,'updated_at_utc':datetime.now(timezone.utc).isoformat()}
    refdir=GPKG.parent;(refdir/'annotation_progress.json').write_text(json.dumps(prog,indent=2)+'\n',encoding='utf-8')
    (refdir/'annotation_progress.md').write_text('# Optical annotation progress\n\n'+''.join(f"- {k.replace('_',' ').title()}: {v}\n" for k,v in prog.items() if k!='updated_at_utc')+'\nNo labels have been added by automation.\n',encoding='utf-8')
    print(json.dumps({'status':status,'samples':len(rows),'labels':counts,'blank_slots':label_audit['blank_slots'],'identity_errors':len(errors),'metrics':len(metrics or []),'report':str(OUT.relative_to(ROOT))},indent=2))

if __name__=='__main__': main()
