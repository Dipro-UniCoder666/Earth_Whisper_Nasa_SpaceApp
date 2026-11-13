"""Read-only, provenance-first access to the regional DHARA evidence set."""
from __future__ import annotations
import json,sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'data/gherproof'
REGISTRY=DATA/'manifests/evidence_registry.json'
INFERENCE=DATA/'manifests/phase7_inference_manifest.json'
ANNOTATION=DATA/'manifests/phase7c_model_evaluation_manifest.json'
READINESS=DATA/'manifests/phase7c_model_readiness.json'
LIMITATIONS=[
 'Model outputs are exploratory predictions, not measured water observations or validated flood extent.',
 'No human optical reference labels are complete; local validation is pending.',
 'The regional search area is provisional and is not an authoritative village or enclosure boundary.',
 'Sentinel-1 RTC Gamma0 and Sen1Floods11 benchmark GRD inputs have unresolved processing-domain differences.',
 'Exact GRD catalogue counterparts have not been processed into compatible calibrated and geocoded rasters.',
 'Sentinel-2 indices and cross-sensor candidate layers are not ground truth.',
 'No operational breach diagnosis, village-specific impact, or impact-area estimate is approved.',
]

def _json(path:Path,default:Any):
    if not path.is_file():return default
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):return default

@lru_cache(maxsize=1)
def registry()->dict:
    data=_json(REGISTRY,{})
    return data if isinstance(data,dict) and isinstance(data.get('records'),list) else {'records':[],'category_counts':{},'record_count':0}

def clear_registry_cache():registry.cache_clear()

def records(category:str|None=None,status:str|None=None,acquisition_date:str|None=None)->list[dict]:
    values=registry().get('records',[])
    return [r for r in values if (not category or r.get('evidence_category')==category) and (not status or r.get('confidence_or_validation_status')==status) and (not acquisition_date or r.get('acquisition_date')==acquisition_date)]

def evidence_list(category:str|None=None,status:str|None=None,acquisition_date:str|None=None,offset:int=0,limit:int=100)->dict:
    all_records=records(category,status,acquisition_date);return {'total':len(all_records),'offset':offset,'limit':limit,'categories':sorted(registry().get('category_counts',{})),'records':all_records[offset:offset+limit]}

def screening_status()->dict:
    rs=registry().get('records',[]);verified_s1=[r for r in rs if r.get('evidence_category')=='verified_satellite_observation' and r.get('title','').startswith('Sentinel-1')]
    s1dates={r.get('acquisition_date') for r in verified_s1 if r.get('acquisition_date')}
    nisar_dates=sorted({r.get('acquisition_date') for r in rs if r.get('title','').startswith('NISAR L-band validated') and r.get('acquisition_date')})
    s2dates={r.get('acquisition_date') for r in rs if r.get('evidence_category')=='derived_satellite_measurement' and r.get('title','').startswith('Sentinel-2') and r.get('acquisition_date')}
    s2reflectance_dates={r.get('acquisition_date') for r in rs if r.get('evidence_category')=='derived_satellite_measurement' and r.get('title','').startswith('Sentinel-2') and any(b in r.get('title','') for b in (' B03 ',' B04 ',' B08 ',' NDWI ',' MNDWI ')) and r.get('acquisition_date')}
    s2scl_dates={r.get('acquisition_date') for r in rs if r.get('evidence_category')=='derived_satellite_measurement' and r.get('title','').startswith('Sentinel-2') and ('SCL' in r.get('title','') or 'clear-pixel' in r.get('title','')) and r.get('acquisition_date')}
    preds=[r for r in rs if r.get('evidence_category')=='model_prediction' and r.get('evidence_id','').startswith('prediction-')]
    disag=[r for r in rs if r.get('evidence_id','').startswith('disagreement-')]
    ann=_json(ANNOTATION,{});readiness=_json(READINESS,{})
    return {'project_status':'regional_evidence_screening_ready','product_direction':'Evidence-Aware Regional Flood Screening and Investigation Platform','data_readiness':'partial_real_satellite_and_derived_products_available','model_readiness':readiness.get('readiness','exploratory_only'),'geographic_readiness':'provisional_regional_search_extent; site_and_village_boundaries_unverified','local_validation_status':ann.get('local_validation_status','human_review_pending'),'human_label_slots':ann.get('label_audit',{}).get('label_slots',900),'human_labels_completed':ann.get('label_audit',{}).get('labeled_reference_slots',0),'impact_quantification':'not_approved','satellite_acquisitions':{'sentinel1_rtc_validated_observations':len(s1dates),'sentinel1_dates':sorted(s1dates),'sentinel1_grd_processed_scenes':0,'nisar_validated_regional_observations':len(nisar_dates),'nisar_validated_dates':nisar_dates,'nisar_january_2026_event_pair_available':False,'sentinel2_dates_with_scl_products':sorted(s2scl_dates),'sentinel2_dates_with_reflectance_or_indices':sorted(s2reflectance_dates),'sentinel2_any_product_dates':sorted(s2dates)},'model_outputs':{'probability_mask_uncertainty_layers':len(preds),'disagreement_layers':len(disag),'models':['scratch','pretrained'],'model_selection':'none; separate exploratory outputs'},'limitations':LIMITATIONS}

def scenes()->dict:
    allr=registry().get('records',[]);out=[]
    for r in allr:
        if r.get('evidence_category')=='verified_satellite_observation' and r.get('title','').startswith('Sentinel-1'):
            out.append({'sensor':'Sentinel-1','product':'RTC Gamma0 VV/VH','acquisition_date':r.get('acquisition_date'),'status':r.get('confidence_or_validation_status'),'evidence_id':r['evidence_id'],'source_dataset':r.get('source_dataset'),'crs':r.get('crs'),'coverage':r.get('spatial_coverage'),'original_file':r.get('original_file'),'derived_file':r.get('derived_file'),'metadata':r.get('metadata'),'limitations':r.get('limitations')})
        elif r.get('evidence_category')=='verified_satellite_observation' and r.get('title','').startswith('NISAR L-band'):
            out.append({'sensor':'NISAR','product':'L-band GCOV HH/HV diagonal covariance power','acquisition_date':r.get('acquisition_date'),'status':r.get('confidence_or_validation_status'),'evidence_id':r['evidence_id'],'source_dataset':r.get('source_dataset'),'crs':r.get('crs'),'coverage':r.get('spatial_coverage'),'original_file':r.get('original_file'),'derived_file':r.get('derived_file'),'metadata':r.get('metadata'),'limitations':r.get('limitations')})
        elif r.get('evidence_id')=='nisar-gcov-change-2026-10-23-to-2026-11-04-track170':
            out.append({'sensor':'NISAR','product':'Exploratory validated-maturity temporal gamma0 ratio, HH/HV','acquisition_date':None,'status':r.get('confidence_or_validation_status'),'evidence_id':r['evidence_id'],'source_dataset':r.get('source_dataset'),'crs':r.get('crs'),'coverage':r.get('spatial_coverage'),'derived_file':r.get('derived_file'),'metadata':r.get('metadata'),'limitations':r.get('limitations')})
    s2=sorted({r.get('acquisition_date') for r in allr if r.get('evidence_category')=='derived_satellite_measurement' and r.get('title','').startswith('Sentinel-2') and r.get('acquisition_date')})
    for d in s2:
        layers=[r for r in allr if r.get('acquisition_date')==d and r.get('title','').startswith('Sentinel-2')]
        products=sorted({'SCL or clear mask' if ('SCL' in r.get('title','') or 'clear-pixel' in r.get('title','')) else 'reflectance/index' for r in layers})
        out.append({'sensor':'Sentinel-2','product_types':products,'acquisition_date':d,'status':'derived','evidence_ids':[r['evidence_id'] for r in layers],'layer_count':len(layers),'limitations':['Optical products are contextual indicators and are not human labels.']})
    inf=_json(INFERENCE,{});pair_records=[]
    for p in inf.get('pairs',[]):
        pair_records.append({**p,'assessment_status':'experimental_same_geometry_pair','evidence_source':'Phase 7 pixel-validated RTC products','limitations':['The paired acquisitions use the same relative orbit but remain model-analysis candidates, not event confirmation.']})
    event_manifest=_json(DATA/'manifests/planetary_computer_event_imagery.json',{})
    assessment=event_manifest.get('pair_assessment',{})
    if assessment:
        pair_records.append({'pair_id':'2026-01-07_2026-01-19_rel114_ascending','pre_date':'2026-01-07','post_date':'2026-01-19','relative_orbit':114,'orbit_direction':'ascending','assessment_status':'conditionally_suitable_for_backscatter_comparison','evidence_source':'Phase 4B bounded COG window reads and local clipped rasters','common_valid_pixels':assessment.get('common_valid_pixels_all_dates_polarizations'),'valid_fraction_reported_by_phase4b':assessment.get('common_valid_fraction_of_provisional_aoi'),'evidence_ids':['s1-rtc-2026-01-07-orbit114-partial','s1-rtc-2026-01-19-orbit114-partial','s1-rtc-2026-01-07-2026-01-19-validity-mask'],'limitations':['Local swath coverage is limited and does not establish full regional coverage or enclosure coverage.','Phase 6B recorded a separate Jan 7 VV read failure in its broader regional candidate retrieval.','Backscatter comparison does not establish water, flood or breach.']})
    return {'scenes':sorted(out,key=lambda x:(x.get('acquisition_date') or '',x['sensor'])),'pre_post_eligibility':pair_records}

def predictions(model:str|None=None)->dict:
    if model not in (None,'scratch','pretrained'):raise ValueError('model must be scratch or pretrained')
    rs=records('model_prediction');filtered=[r for r in rs if not model or r.get('metadata',{}).get('model')==model or model in r.get('evidence_id','')]
    phase8b=[r for r in filtered if r.get('evidence_id','').startswith('phase8b-') and ('probability_20m_mean' in r.get('evidence_id','') or 'model_water_prediction_20m' in r.get('evidence_id',''))]
    return {'status':'exploratory','model_selection':'none','models':sorted({r.get('metadata',{}).get('model') for r in filtered if r.get('metadata',{}).get('model') in ('scratch','pretrained')}),'checkpoint_metadata':[r for r in filtered if r.get('evidence_id','').startswith('model-checkpoint-')],'prediction_layers':[r for r in filtered if r.get('evidence_id','').startswith('prediction-')],'comparison_grid_prediction_layers':phase8b,'disagreement_layers':[r for r in filtered if r.get('evidence_id','').startswith('disagreement-')],'limitations':['Predictions are not observations or locally validated labels.','Do not interpret pixel totals as measured flood or affected area.']}

def optical()->dict:
    rs=[r for r in registry().get('records',[]) if r.get('evidence_category') in ('derived_satellite_measurement','optical_reference_interpretation') and (r.get('title','').startswith('Sentinel-2') or r.get('evidence_category')=='optical_reference_interpretation')]
    comparisons=[r for r in registry().get('records',[]) if r.get('title','').startswith('Cross-sensor')]
    return {'status':'available_with_interpretation_limits','label_semantics':'optical reference indicators; human labels pending; not ground truth','acquisition_dates':sorted({r.get('acquisition_date') for r in rs if r.get('acquisition_date')}),'records':rs,'sar_optical_comparisons':comparisons,'limitations':['NDWI/MNDWI and SCL values are indicators/context, not independent truth.','SCL water class is not a human reference label.','Human annotation package has 0/900 labels complete.','SAR/optical agreement layers are comparisons, not validation or ground truth.']}

def weak_reference()->dict:
    rs=[r for r in registry().get('records',[]) if r.get('evidence_category') in ('optical_weak_reference','uncertainty_layer') and r.get('evidence_id','').startswith('optical-weakref-')]
    manifest=_json(DATA/'manifests/phase8b_weak_reference_manifest.json',{})
    return {'status':manifest.get('status','unavailable'),'label_semantics':'automated optical weak reference; not human truth or field validation','thresholds':manifest.get('methodology',{}).get('thresholds_fixed_before_model_comparison'), 'scenes':manifest.get('scenes',[]),'temporal_change':manifest.get('temporal_change'),'records':rs,'limitations':manifest.get('limitations',[])}

def comparisons()->dict:
    rs=[r for r in registry().get('records',[]) if r.get('evidence_category') in ('model_comparison','uncertainty_layer') and r.get('evidence_id','').startswith('phase8b-')]
    manifest=_json(DATA/'manifests/phase8b_weak_reference_comparison.json',{})
    return {'status':manifest.get('status','unavailable'),'metric_semantics':'weak_reference_agreement; not local accuracy','temporal_matches':manifest.get('temporal_matches',[]),'per_model_acquisition_results':manifest.get('per_model_acquisition_results',[]),'records':rs,'model_readiness':'exploratory_only','human_reference_status':'human_review_pending','impact_quantification':'not_approved','limitations':manifest.get('limitations',[])}

def scenario(scenario_id:str)->dict:
    if scenario_id!='january_2026_regional_screening_demo':raise KeyError('Scenario not found')
    return _json(DATA/'scenarios'/f'{scenario_id}.json',{})

def coverage()->dict:
    rec=next((r for r in registry().get('records',[]) if r.get('evidence_id')=='geography-provisional-regional-aoi'),None)
    obs=[r for r in registry().get('records',[]) if r.get('evidence_category')=='verified_satellite_observation']
    return {'status':'provisional','aoi':rec,'datasets':[{'evidence_id':r['evidence_id'],'acquisition_date':r.get('acquisition_date'),'crs':r.get('crs'),'coverage':r.get('spatial_coverage'),'status':r.get('confidence_or_validation_status')} for r in obs],'spatially_validated_boundary_available':False,'village_boundaries_available':False,'exact_pallimangal_boundary_available':False,'limitations':['The provisional search extent is not a village/admin/mouza/gher boundary.','Coverage summaries belong to distinct raster scopes and should not be compared as if their AOIs were identical.','No village-level coverage statistic is available.']}

def limitations()->dict:return {'items':LIMITATIONS,'local_validation_status':'human_review_pending','model_readiness':'exploratory_only','impact_quantification':'not_approved'}

def raster_path(evidence_id:str,asset:str='derived')->tuple[dict,Path]:
    r=next((x for x in registry().get('records',[]) if x.get('evidence_id')==evidence_id),None)
    if not r:raise KeyError('Evidence layer not found')
    key='derived_file' if asset=='derived' else 'original_file' if asset=='original' else None
    if key is None:raise ValueError('asset must be derived or original')
    f=r.get(key)
    if not f or f.get('availability')!='available':raise FileNotFoundError('Requested evidence file is unavailable')
    path=(ROOT/f['path']).resolve()
    try:path.relative_to(ROOT.resolve())
    except ValueError as exc:raise ValueError('Evidence path is outside the repository root') from exc
    if not path.is_file():raise FileNotFoundError('Requested evidence file is unavailable')
    return r,path

def raster_metadata(evidence_id:str,asset:str='derived')->dict:
    r,path=raster_path(evidence_id,asset)
    env=ROOT/'backend/.venv/Lib/site-packages'
    if env.exists() and str(env) not in sys.path:sys.path.append(str(env))
    try:import rasterio
    except ImportError as exc:raise RuntimeError('Rasterio is unavailable in the API environment') from exc
    with rasterio.open(path) as ds:
        return {'evidence_id':evidence_id,'status':r.get('confidence_or_validation_status'),'available':True,'path':str(path.relative_to(ROOT)).replace('\\','/'),'crs':ds.crs.to_string() if ds.crs else None,'bounds':[ds.bounds.left,ds.bounds.bottom,ds.bounds.right,ds.bounds.top],'width':ds.width,'height':ds.height,'resolution':list(ds.res),'count':ds.count,'dtype':list(ds.dtypes),'nodata':ds.nodata,'descriptions':list(ds.descriptions),'checksum':(r.get('derived_file') if asset=='derived' else r.get('original_file') or {}).get('sha256'),'limitations':r.get('limitations',[])}

def geojson_path(evidence_id:str)->tuple[dict,Path]:
    r=next((x for x in registry().get('records',[]) if x.get('evidence_id')==evidence_id),None)
    if not r:raise KeyError('Evidence layer not found')
    f=r.get('original_file') or r.get('derived_file')
    if not f or f.get('availability')!='available' or not f.get('path','').lower().endswith(('.geojson','.json')):raise FileNotFoundError('GeoJSON evidence is unavailable')
    path=(ROOT/f['path']).resolve()
    try:path.relative_to(ROOT.resolve())
    except ValueError as exc:raise ValueError('Evidence path is outside the repository root') from exc
    return r,path
