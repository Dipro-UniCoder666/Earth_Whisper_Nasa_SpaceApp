"""Build a manifest-backed inventory of existing GherProof evidence artifacts."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];DATA=ROOT/'data/gherproof';MAN=DATA/'manifests';OUT=MAN/'evidence_registry.json'

def read(name,default=None):
 p=MAN/name
 if not p.exists():return default if default is not None else {}
 return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def record(eid,category,title,source,*,acq=None,status='derived',original=None,derived=None,crs=None,coverage=None,method=None,limitations=None,provenance=None,metadata=None,checksum=None):
 def fileinfo(raw,expected=None):
  if not raw:return None
  p=(ROOT/raw).resolve()
  try:p.relative_to(ROOT.resolve())
  except ValueError:return {'path':raw,'availability':'invalid_path'}
  if not p.is_file():return {'path':raw,'availability':'unavailable'}
  actual=sha(p)
  return {'path':raw.replace('\\','/'),'availability':'available','bytes':p.stat().st_size,'sha256':actual,'checksum_matches_manifest':None if not expected else actual==expected}
 return {'evidence_id':eid,'evidence_category':category,'title':title,'source_dataset':source,'acquisition_date':acq,'processing_date':datetime.now(timezone.utc).date().isoformat(),'spatial_coverage':coverage,'crs':crs,'original_file':fileinfo(original,checksum),'derived_file':fileinfo(derived,None if original else checksum),'confidence_or_validation_status':status,'processing_methodology':method,'limitations':limitations or [],'source_provenance':provenance or [],'metadata':metadata or {}}

def main():
 out=[];inf=read('phase7_inference_manifest.json');rad=read('phase7_radiometric_compatibility.json');qc=read('phase7_raster_qc_manifest.json');opt=read('phase7_optical_processing.json');cross=read('phase7b_cross_sensor_validation.json');audit=read('phase7b_model_output_audit.json');evaluation=read('phase7c_model_evaluation_manifest.json');readiness=read('phase7c_model_readiness.json');
 # Satellite observation records are based on processed source rasters and raster-QC manifests, not STAC catalogue counts.
 qc_by_path={x.get('path'):x for x in qc.get('rasters',qc.get('records',[])) if isinstance(x,dict)}
 for s in rad.get('rtc_measurement',{}).get('scenes',[]):
  src=s.get('source_raster');m=s.get('source_raster_metadata',{});d=s.get('db_output',{});date=s.get('date');iid=s.get('item_id');
  out.append(record(f's1-rtc-{date}','verified_satellite_observation',f'Sentinel-1 RTC VV/VH observation {date}','Planetary Computer sentinel-1-rtc',acq=date,status='verified',original=src,checksum=s.get('source_raster_sha256'),derived=d.get('path'),crs=m.get('crs'),coverage={'crs':m.get('crs'),'bounds':m.get('bounds'),'resolution_m':m.get('resolution_m'),'width':m.get('width'),'height':m.get('height'),'aoi_status':'provisional regional search envelope'},method=m.get('tags',{}).get('processing'),limitations=['Coverage is a provisional regional search envelope, not a verified village or enclosure boundary.','RTC Gamma0 measurement is not directly interchangeable with Sentinel-1 GRD benchmark inputs.'],provenance=['data/gherproof/manifests/phase6_sentinel1_regional_manifest.json','data/gherproof/manifests/phase6b_raster_qc_manifest.json','data/gherproof/manifests/phase7_radiometric_compatibility.json'],metadata={'item_id':iid,'platform':s.get('platform'),'relative_orbit':s.get('relative_orbit'),'orbit_direction':s.get('orbit_direction'),'polarizations':['VV','VH'],'nodata':m.get('nodata'),'db_derived_checksum':d.get('sha256')}))
 # Earlier orbit-114 clips are valid only on their smaller measured swath support.
 event=read('planetary_computer_event_imagery.json',{})
 for scene in event.get('selected_scenes',[]):
  date=scene.get('date');output=next((x for x in event.get('outputs',[]) if x.get('date')==date and x.get('path')),None)
  if not output:continue
  out.append(record(f"s1-rtc-{date}-orbit114-partial","verified_satellite_observation",f"Sentinel-1 RTC VV/VH locally clipped support {date}",'Planetary Computer sentinel-1-rtc',acq=date,status='verified',derived=output.get('path'),crs=output.get('crs'),coverage={'crs':output.get('crs'),'resolution_m':output.get('resolution'),'width':output.get('width'),'height':output.get('height'),'bounds_from_transform':output.get('transform'),'common_valid_pixels':output.get('common_valid_pixels'),'valid_fraction_reported_by_phase4b':output.get('valid_fraction_of_aoi'),'coverage_scope':'Phase 4B local clip footprint; do not generalize to full regional AOI'},method='Planetary Computer RTC linear intensity VV/VH, bounded COG reads and local clip; nodata/masks retained.',limitations=['Only eastern local swath support is represented; full regional coverage is not established.','The Phase 6B broader regional extraction independently reported a Jan 7 VV access failure; this record refers to the earlier Phase 4B locally clipped artifact.','Not evidence of water or incident causality.'],provenance=['data/gherproof/manifests/planetary_computer_event_imagery.json','data/gherproof/manifests/planetary_computer_scene_validation.json','data/gherproof/manifests/phase6b_regional_coverage_assessment.json',scene.get('metadata_path')],metadata={'item_id':scene.get('item_id'),'relative_orbit':scene.get('relative_orbit'),'orbit_direction':scene.get('orbit_direction'),'platform':scene.get('platform'),'polarizations':scene.get('polarizations'),'common_valid_pixels':output.get('common_valid_pixels'),'pair_assessment':event.get('pair_assessment',{}).get('classification'),'nodata':output.get('nodata')},checksum=output.get('sha256')))
 validity=next((x for x in event.get('outputs',[]) if x.get('kind')=='validity-mask-stack'),None)
 if validity:
  out.append(record('s1-rtc-2026-01-07-2026-01-19-validity-mask','derived_satellite_measurement','Sentinel-1 Jan 7/19 validity masks','Phase 4B paired RTC clip masks',status='verified',derived=validity.get('path'),crs=validity.get('crs'),coverage={'width':validity.get('width'),'height':validity.get('height'),'crs':validity.get('crs'),'common_valid_pixels':validity.get('common_valid_pixels')},method='Per-date VV/VH validity, common validity and provisional AOI mask stack.',limitations=['Validity code only; not a water mask.','Limited to Phase 4B local clip grid.'],provenance=['data/gherproof/manifests/planetary_computer_event_imagery.json'],metadata={'band_descriptions':validity.get('band_descriptions'),'nodata':validity.get('nodata')},checksum=validity.get('sha256')))
 # Model artifacts and predictions remain separate from observations.
 for model,c in inf.get('checkpoints',{}).items():
  out.append(record(f'model-checkpoint-{model}','model_prediction',f'{model} model checkpoint metadata','Sen1Floods11 v1.1',status='exploratory',original=c.get('path'),checksum=c.get('sha256'),method='Existing benchmark-trained checkpoint; no local labels used for selection.',limitations=['Benchmark results do not establish local GherProof accuracy.'],provenance=['data/gherproof/manifests/phase7_inference_manifest.json','data/gherproof/manifests/phase7c_model_readiness.json'],metadata={'model':model,'architecture':c.get('architecture'),'sha256_expected':c.get('sha256'),'threshold':c.get('threshold'),'benchmark_only':c.get('benchmark_only')}))
 for s in inf.get('scenes',[]):
  date=s.get('date');model=s.get('model');iid=s.get('item_id');pair=s.get('pair_id')
  for kind,title in [('probability','water probability'),('mask','binary mask'),('uncertainty','binary entropy uncertainty')]:
   obj=s.get(kind) or {}
   if obj.get('path'):
    out.append(record(f'prediction-{model}-{date}-{kind}','model_prediction',f'{model} {title} {date}',iid,acq=date,status='exploratory',derived=obj.get('path'),coverage={'crs':'EPSG:32645','resolution_m':10,'valid_pixels':s.get('valid_pixels'),'provisional_aoi':True},method='Phase 7 RTC Gamma0 to dB; clipped [-60,20]; checkpoint-specific z-score; 256 px patches, 64 px overlap; threshold 0.5 for mask.',limitations=['Prediction is not a measured water observation or validated flood map.','Local human optical labels are pending.','Do not interpret counts as affected area.'],provenance=['data/gherproof/manifests/phase7_inference_manifest.json','data/gherproof/manifests/phase7b_model_output_audit.json'],metadata={'model':model,'pair_id':pair,'item_id':iid,'threshold':inf.get('configuration',{}).get('threshold'),'valid_pixels':s.get('valid_pixels'),'probability_quantiles':next((x.get('statistics') for x in audit.get('scenes',[]) if x.get('path')==obj.get('path')),None)} ,checksum=obj.get('sha256')))
 for key,item in inf.get('model_disagreement',{}).items():
  for kind,title in [('xor','model binary XOR disagreement'),('probability_difference','absolute probability difference')]:
   obj=item.get(kind) or {}
   if obj.get('path'):
    out.append(record(f'disagreement-{key}-{kind}','model_prediction',f'{title}: {key}','Phase 7 scratch vs pretrained outputs',status='exploratory',derived=obj['path'],coverage={'crs':'EPSG:32645','resolution_m':10,'valid_pixels':obj.get('valid_pixels')},method='Pixelwise comparison of separate model outputs; not an accuracy metric.',limitations=['Disagreement measures model inconsistency, not error or water truth.'],provenance=['data/gherproof/manifests/phase7_inference_manifest.json'],metadata={'comparison_key':key,'xor_fraction':item.get('binary_xor_fraction'),'xor_pixels':item.get('binary_xor_pixels')},checksum=obj.get('sha256')))
 # Sentinel-2 reflectance and index products.
 for scene in opt.get('scenes',[]):
  date=scene.get('date');
  for band,b in scene.get('bands',{}).items():
   out.append(record(f's2-{date}-{band}','derived_satellite_measurement',f'Sentinel-2 {band} surface reflectance {date}',scene.get('item_id','Sentinel-2 L2A'),acq=date,status='verified',derived=b.get('path'),crs='EPSG:32645',coverage=scene.get('grid10'),method='Sentinel-2 L2A stored value converted using BOA_ADD_OFFSET and quantification value; see optical-processing manifest.',limitations=['Optical reflectance is observation context; not a human reference label.'],provenance=['data/gherproof/manifests/phase7_optical_processing.json','data/gherproof/manifests/phase7_sentinel2_radiometric_metadata.json'],metadata={'band':band,'valid_pixels':b.get('valid_pixels')},checksum=b.get('sha256')))
  for kind,key in [('NDWI','ndwi'),('MNDWI','mndwi')]:
   x=scene.get(key) or {}
   if x.get('path'):
    grid=scene.get('grid10' if kind=='NDWI' else 'grid20')
    out.append(record(f's2-{date}-{kind.lower()}','derived_satellite_measurement',f'Sentinel-2 {kind} {date}',scene.get('item_id','Sentinel-2 L2A'),acq=date,status='derived',derived=x.get('path'),crs='EPSG:32645',coverage=grid,method=f'{kind} index computed from reflectance; thresholds are exploratory candidates only.',limitations=['Index values are not ground-truth water labels.','Sensitive to turbidity, wet soil, vegetation, shadow, ponds and mixed pixels.'],provenance=['data/gherproof/manifests/phase7_optical_processing.json'],metadata={'valid_pixels':x.get('valid_pixels'),'summary':scene.get(f'{key}_summary')},checksum=x.get('sha256')))
 # SCL and clear masks are ancillary optical QC layers (actual date-level files).
 regional=DATA/'regional/processed/phase6b/sentinel2';
 for p in sorted((regional/'scl').glob('*_SCL_20m.tif')):
  date=p.name[:10];out.append(record(f's2-scl-{p.stem}','derived_satellite_measurement',f'Sentinel-2 Scene Classification Layer {date}',p.stem,acq=date,status='verified',derived=p.relative_to(ROOT).as_posix(),crs='EPSG:32645',method='SCL context layer; quality/classification categories retained.',limitations=['SCL water class is not independent ground truth.'],provenance=['data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json']))
 for p in sorted((regional/'clear_masks').glob('*_clear_20m.tif')):
  date=p.name[:10];out.append(record(f's2-clear-{p.stem}','derived_satellite_measurement',f'Sentinel-2 clear-pixel mask {date}',p.stem,acq=date,status='verified',derived=p.relative_to(ROOT).as_posix(),crs='EPSG:32645',method='Mask derived from SCL codes; see raster QC manifest.',limitations=['Mask indicates pixel screening status, not water status.'],provenance=['data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json']))
 # Corrected cross-sensor rasters remain exploratory comparisons.
 for i,c in enumerate(cross.get('comparisons',[])):
  for key in ('agreement_layer','change_agreement_layer'):
   a=c.get(key) or {}
   if a.get('path'):
    out.append(record(f'cross-sensor-{i}-{key}','derived_satellite_measurement',f"Cross-sensor {c.get('index')} {key}: {c.get('pair_id')} {c.get('model')}",'Sentinel-1 RTC + Sentinel-2 optical indices',status='exploratory',derived=a['path'],crs=c.get('grid',{}).get('crs'),coverage=c.get('grid'),method='Corrected Phase 7B 20m grid comparison; codes show candidate agreement only.',limitations=['Not a confirmed flood map or independent ground truth.','Sentinel-1 model input domain and optical acquisition dates differ.'],provenance=['data/gherproof/manifests/phase7b_cross_sensor_validation.json'],metadata={'pair_id':c.get('pair_id'),'model':c.get('model'),'index':c.get('index'),'threshold':c.get('optical_threshold')},checksum=a.get('sha256')))
 # Provisional geography and reported incident are explicit non-satellite evidence.
 aoi='data/gherproof/regional/six_village_regional_search_extent.geojson'
 out.append(record('geography-provisional-regional-aoi','provisional_geographic_reference','Provisional six-village search extent','Approximate regional locality context',status='provisional',original=aoi,method='Approximate search envelope documented in source GeoJSON.',limitations=['Not an authoritative village, cadastral, gher or administrative boundary.'],provenance=[aoi]))
 event_cat=read('event_satellite_catalogue.json',{});news=event_cat.get('source',{}).get('url') or 'https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore'
 out.append(record('reported-event-2026-01-14','news_reported_event','Reported Sujatpur incident (not independently verified)','News report',acq='2026-01-14',status='provisional',provenance=[news],limitations=['Reported incident is not independently verified by this platform.','Reported figures are not satellite measurements or model labels.']))
 # Annotation status and unsupported GRD matching are audit records, not field verification.
 pkg=read('phase7c_annotation_workflow_manifest.json',{});out.append(record('optical-reference-labeling-status','optical_reference_interpretation','Sentinel-2 optical annotation package status','Phase 7C human review package',status='under_review',original=pkg.get('editable_geopackage'),method='450 samples prepared for human pre/post interpretation; label slots remain blank.',limitations=['0 of 900 labels completed.','Optical interpretation is not field-verified truth.'],provenance=['data/gherproof/manifests/phase7c_model_evaluation_manifest.json'],metadata={'sample_count':pkg.get('sample_count'),'blank_pre':pkg.get('blank_pre_label_slots'),'blank_post':pkg.get('blank_post_label_slots')}))
 grds=read('phase7b_grd_counterpart_manifest.json',{});
 for g in grds.get('records',[]):out.append(record(f"grd-catalogue-{g.get('target_grd_item_id')}",'catalogue_metadata',f"Sentinel-1 GRD catalogue counterpart {g.get('rtc_datetime')}",'Planetary Computer sentinel-1-grd',acq=(g.get('rtc_datetime') or '')[:10],status='under_review',provenance=['data/gherproof/manifests/phase7b_grd_counterpart_manifest.json','data/gherproof/manifests/phase7b_grd_raster_inspection.json'],limitations=['Catalogue match is not a processed or validated raster observation.','Processing representation conflict remains unresolved.'],metadata={'item_id':g.get('target_grd_item_id'),'relative_orbit':g.get('relative_orbit'),'direction':g.get('orbit_direction'),'polarizations':g.get('polarizations')}))
 # Inventory missing annotated outputs explicitly.
 out.append(record('human-verified-reference-availability','human_verified_evidence','Human-verified reference labels','Phase 7C annotation package',status='unavailable',limitations=['No human labels supplied; do not describe local model results as validated.'],provenance=['data/gherproof/manifests/phase7c_model_evaluation_manifest.json'],metadata={'label_slots':900,'completed_labels':0}))
 # Ensure identifiers unique and files are hashed from actual disk state.
 ids=[r['evidence_id'] for r in out]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate evidence IDs')
 payload={'schema_version':'1.0.0','generated_at_utc':datetime.now(timezone.utc).isoformat(),'repository':'Earth Whisper / GherProof','readiness':{'model':'exploratory_only','local_validation':'human_review_pending','geography':'provisional','impact_quantification':'not_approved'},'record_count':len(out),'category_counts':{k:sum(r['evidence_category']==k for r in out) for k in sorted({r['evidence_category'] for r in out})},'records':out,'registry_limitations':['Registry records expose products and their evidence status; registry inclusion does not imply scientific validation.','Model prediction artifacts are kept separate from observation artifacts.','Unavailable human labels and unresolved GRD data are represented explicitly.']}
 OUT.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
 file_refs=[f for r in out for f in (r.get('original_file'),r.get('derived_file')) if f]
 availability={'schema_version':'1.0.0','generated_at_utc':payload['generated_at_utc'],'status':'available_with_scientific_limitations','evidence_registry':'data/gherproof/manifests/evidence_registry.json','registry_record_count':len(out),'category_counts':payload['category_counts'],'file_inventory':{'available':sum(f.get('availability')=='available' for f in file_refs),'unavailable':sum(f.get('availability')=='unavailable' for f in file_refs),'invalid_path':sum(f.get('availability')=='invalid_path' for f in file_refs),'checksum_mismatches':sum(f.get('checksum_matches_manifest') is False for f in file_refs)},'observations':{'sentinel1_rtc_dates':sorted({r['acquisition_date'] for r in out if r['evidence_category']=='verified_satellite_observation' and r.get('acquisition_date')}),'sentinel1_grd_fully_processed_scenes':0,'sentinel2_reflectance_index_dates':['2026-01-10','2026-01-20'],'sentinel2_scl_dates':sorted({r.get('acquisition_date') for r in out if r.get('title','').startswith('Sentinel-2 Scene Classification') and r.get('acquisition_date')})},'model_outputs':{'model_checkpoints':2,'probability_mask_uncertainty_layers':sum(r['evidence_id'].startswith('prediction-') for r in out),'disagreement_layers':sum(r['evidence_id'].startswith('disagreement-') for r in out),'local_validation_status':'human_review_pending','model_readiness':'exploratory_only'},'annotation':{'samples':450,'pre_post_label_slots':900,'completed_labels':0},'geography':{'regional_extent':'provisional','authoritative_village_boundaries':False,'exact_pallimangal_boundary':False},'reports':['docs/GHERPROOF_PHASE4B_REPORT.md','docs/GHERPROOF_PHASE5_REPORT.md','docs/GHERPROOF_PHASE6_REPORT.md','docs/GHERPROOF_PHASE6B_REPORT.md','docs/GHERPROOF_PHASE7_REPORT.md','docs/GHERPROOF_PHASE7B_REPORT.md','docs/GHERPROOF_PHASE7C_REPORT.md'],'limitations':['Evidence inventory availability is not equivalent to scientific suitability.','Phase 4B Jan 7/19 clips cover a limited local swath and Phase 6B has a separate Jan 7 VV read failure.','No local model accuracy or impact-area result is available.']}
 (MAN/'phase8_data_availability.json').write_text(json.dumps(availability,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'registry':str(OUT.relative_to(ROOT)),'records':len(out),'categories':payload['category_counts'],'availability':availability['file_inventory']},indent=2))
if __name__=='__main__':main()
