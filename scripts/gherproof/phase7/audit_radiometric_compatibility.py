"""Audit Sen1Floods11-to-RTC radiometry and create linear-to-dB inputs.

No model is run here. Source Phase 6B rasters and checkpoints are read-only.
"""
from __future__ import annotations
import hashlib, json, random, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.extend([str(ROOT/'backend/.venv/Lib/site-packages'),str(ROOT/'scripts/gherproof')])
import numpy as np
import rasterio
import torch
from PIL import Image, ImageDraw, ImageFont
import train_sen1floods11 as train

S1MAN=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json'
TRAINMAN=ROOT/'data/gherproof/manifests/sen1floods11_training_results.json'
OUT=ROOT/'data/gherproof/processed/phase7/sentinel1'
PLOT=ROOT/'data/gherproof/processed/phase7/figures'
MAN=ROOT/'data/gherproof/manifests'
NODATA=-32768.0
BANDS=('VV','VH')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def pct(a,ps):
 return {str(p):float(np.percentile(a,p)) for p in ps} if a.size else {}
def savej(p,d):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); t.replace(p)
def to_summary(v):
 return {'count':int(v.size),'min':float(v.min()) if v.size else None,'max':float(v.max()) if v.size else None,'mean':float(v.mean()) if v.size else None,'std_population':float(v.std()) if v.size else None,'percentiles':pct(v,[1,2,5,25,50,75,95,98,99])}
def main():
 ckpt_paths={'scratch':ROOT/'models/gherproof/sen1floods11_attention_unet.pt','pretrained':ROOT/'models/gherproof/sen1floods11_resnet50_moco_unet.pt'}
 checkpoints={k:torch.load(p,map_location='cpu',weights_only=False) for k,p in ckpt_paths.items()}
 for k,p in ckpt_paths.items():
  expected={'scratch':'fcb244de72d51da9760d089ed5909d0cfdfda41af2e8def76aae203aadf5a040','pretrained':'084b41f06ea0f1049b53c6708fed0a78e081a38704677dce7e172e67e2b8d9f0'}[k]
  if sha(p)!=expected: raise RuntimeError(f'{k} checkpoint hash does not match Phase 2 manifest; refusing inference prep')
 results=json.loads(TRAINMAN.read_text(encoding='utf-8')); event=str(results['validation_event_id']); geom=train._event_geometries()
 all_train=train._read_split('flood_train_data.csv'); train_rows=[]; valid_chip_count=0
 rng=np.random.default_rng(260113); tr_samples=[[],[]]; tr_min=np.full(2,np.inf); tr_max=np.full(2,-np.inf); count=0; clipped_counts=np.zeros(2,dtype=np.int64)
 for row in all_train:
  ev,_=train._event_for_chip(row['s1'],geom)
  if ev==event: continue
  image,_,valid,_=train._inspect_chip(row)
  if not valid.any(): continue
  train_rows.append(row); valid_chip_count+=1; count+=int(valid.sum())
  vals=np.clip(image[:,valid],-60,20)
  tr_min=np.minimum(tr_min,vals.min(axis=1)); tr_max=np.maximum(tr_max,vals.max(axis=1))
  clipped_counts += np.array([(image[i,valid]<-60).sum()+(image[i,valid]>20).sum() for i in range(2)],dtype=np.int64)
  # Per-chip reservoir samples preserve event/chip diversity for distribution plots.
  for bi in range(2):
   v=vals[bi]
   n=min(2500,v.size); tr_samples[bi].append(rng.choice(v,n,replace=False).astype(np.float32))
 stats=train._stats(train_rows); train_mean,train_std=stats[:2]
 for k in ('scratch','pretrained'):
  if not np.allclose(train_mean,checkpoints[k]['normalization_mean'],rtol=0,atol=1e-5) and k=='scratch':
   raise RuntimeError('Recomputed train-set normalization differs from scratch checkpoint metadata')
 train_dist=[]
 for bi,band in enumerate(BANDS):
  sample=np.concatenate(tr_samples[bi]); train_dist.append({'band':band,'training_chip_count':valid_chip_count,'valid_pixels_exact':count,'checkpoint_mean_db_scratch':float(checkpoints['scratch']['normalization_mean'][bi]),'checkpoint_std_db_scratch':float(checkpoints['scratch']['normalization_std'][bi]),'checkpoint_mean_db_pretrained':float(checkpoints['pretrained']['normalization_mean'][bi]),'checkpoint_std_db_pretrained':float(checkpoints['pretrained']['normalization_std'][bi]),'exact_clipped_min':float(tr_min[bi]),'exact_clipped_max':float(tr_max[bi]),'clip_count_across_bands':int(clipped_counts[bi]),'sampled_percentiles_db':pct(sample,[1,2,5,25,50,75,95,98,99]),'sampled_values_for_plot':sample})
 s1=json.loads(S1MAN.read_text(encoding='utf-8')); scenes={x['item_id']:x for x in s1['scenes']}; all_ids=[]
 for pair in s1['pairs']:
  all_ids.extend([pair['pre_item_id'],pair['post_item_id']])
 scene_recs=[]; scene_arrays={}; sample_all=[[],[]]
 for item_id in all_ids:
  row=scenes[item_id]; srcpath=ROOT/row['analysis_product']['path']; props=row['item_metadata']; day=props['datetime'][:10]
  with rasterio.open(srcpath) as ds:
   raw=ds.read(masked=True).astype('float32'); meta={'crs':str(ds.crs),'transform':list(ds.transform),'bounds':list(ds.bounds),'resolution_m':list(ds.res),'width':ds.width,'height':ds.height,'descriptions':list(ds.descriptions),'nodata':ds.nodata,'tags':ds.tags()}
   arrays=[]; valids=[]; band_stats=[]; zero_ct=[]; neg_ct=[]; invalid_ct=[]; clipped_low=[]; clipped_high=[]; dB_arrays=[]; sample_bands=[]
   for bi,band in enumerate(BANDS):
    a=np.asarray(raw[bi].data,dtype=np.float32); mask=np.ma.getmaskarray(raw[bi]); valid=(~mask)&np.isfinite(a)&(a!=ds.nodata)
    pos=valid&(a>0); zeros=valid&(a==0); neg=valid&(a<0)
    db=np.full(a.shape,NODATA,dtype=np.float32); db[pos]=10*np.log10(a[pos]); model_db=np.clip(db[pos],-60,20)
    arrays.append(a); valids.append(pos); dB_arrays.append(db)
    vals=db[pos]; low=(vals< -60); high=(vals>20); clipped_low.append(int(low.sum())); clipped_high.append(int(high.sum()))
    band_stats.append({'band':band,'aoi_pixel_count':int(valid.sum()),'nodata_or_masked_pixels_in_array':int(mask.sum()),'finite_valid_pixels':int(valid.sum()),'positive_linear_pixels':int(pos.sum()),'zero_pixels':int(zeros.sum()),'negative_pixels':int(neg.sum()),'linear_min':float(a[pos].min()) if pos.any() else None,'linear_max':float(a[pos].max()) if pos.any() else None,'linear_percentiles':pct(a[pos],[1,2,5,25,50,75,95,98,99]),'db_unclipped':to_summary(vals),'training_clip_low_pixels':int(low.sum()),'training_clip_high_pixels':int(high.sum()),'training_clip_low_fraction':float(low.mean()) if low.size else None,'training_clip_high_fraction':float(high.mean()) if high.size else None,'db_after_training_clip':to_summary(model_db)})
    n=min(250000,vals.size); ss=rng.choice(vals,n,replace=False).astype(np.float32) if n else np.array([],np.float32); sample_bands.append(ss); sample_all[bi].append(ss)
   common=valids[0]&valids[1]; corr=float(np.corrcoef(arrays[0][common],arrays[1][common])[0,1]) if common.sum()>10 else None
   # Preserve source arrays; converted dB output is a new raster with invalid/zero/negative masked.
   out=np.stack(dB_arrays).astype(np.float32); outpath=OUT/f'{day}_{item_id}_VV_VH_gamma0_db_10m_utm45n.tif'; outpath.parent.mkdir(parents=True,exist_ok=True)
   with rasterio.open(outpath,'w',driver='GTiff',height=ds.height,width=ds.width,count=2,dtype='float32',crs=ds.crs,transform=ds.transform,nodata=NODATA,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256) as dst:
    dst.write(out)
    for ix,b in enumerate(BANDS,1): dst.set_band_description(ix,f'{b} terrain-corrected Gamma0 dB; 10*log10(linear intensity)')
    dst.update_tags(source_phase6b_raster=row['analysis_product']['path'],source_measurement='RTC gamma0 linear intensity',conversion='dB=10*log10(linear); applied once to finite positive samples only',model_clip='[-60,20] dB is applied only during model tensor normalization; these output dB arrays are unclipped',input_band_order='VV,VH',invalid='source NoData, nonfinite, zero and negative samples set to -32768')
   scene_recs.append({'item_id':item_id,'date':day,'platform':props.get('platform'),'relative_orbit':props.get('sat:relative_orbit'),'orbit_direction':props.get('sat:orbit_state'),'source_raster':row['analysis_product']['path'],'source_raster_sha256':sha(srcpath),'source_raster_metadata':meta,'common_positive_valid_pixels':int(common.sum()),'common_positive_valid_fraction_of_aoi':float(common.sum()/s1['grid']['aoi_pixels']),'vv_vh_linear_correlation':corr,'bands':band_stats,'normalized_distribution_by_model':{},'db_output':{'path':outpath.relative_to(ROOT).as_posix(),'sha256':sha(outpath),'bytes':outpath.stat().st_size,'nodata':NODATA,'bands':['VV_dB','VH_dB']}})
   scene_arrays[item_id]={'db':dB_arrays,'mask':common,'transform':ds.transform,'crs':ds.crs}
 # Normalization distributions use exact stored checkpoint parameters and training clipping.
 for rec in scene_recs:
  cp=checkpoints
  for model in ('scratch','pretrained'):
   means=np.asarray(cp[model]['normalization_mean'],np.float32)[:,None,None]; std=np.asarray(cp[model]['normalization_std'],np.float32)[:,None,None]
   db=scene_arrays[rec['item_id']]['db']; mask=scene_arrays[rec['item_id']]['mask']; row=[]
   for bi,band in enumerate(BANDS):
    vals=db[bi][mask]; clipped=np.clip(vals,-60,20); norm=(clipped-float(means[bi,0,0]))/float(std[bi,0,0])
    row.append({'band':band,'mean':float(norm.mean()),'std':float(norm.std()),'p02':float(np.percentile(norm,2)),'median':float(np.median(norm)),'p98':float(np.percentile(norm,98))})
   rec['normalized_distribution_by_model'][model]=row
 # Distribution plot: benchmark training subset versus selected RTC scenes.
 PLOT.mkdir(parents=True,exist_ok=True); W,H=1480,980; img=Image.new('RGB',(W,H),'white'); draw=ImageDraw.Draw(img); font=ImageFont.load_default()
 palette={'training':'#182b42','2026-01-09':'#2074a5','2026-01-12':'#2f925d','2026-01-21':'#dc7a22','2026-01-24':'#aa4b81'}
 def hist_draw(x0,y0,w,h,series,lo,hi,title):
  draw.text((x0,y0-20),title,fill='#1c2c3b',font=font); bins=70
  draw.rectangle((x0,y0,x0+w,y0+h),outline='#536473')
  for tick in range(5):
   xx=x0+tick*w//4; val=lo+(hi-lo)*tick/4; draw.line((xx,y0,xx,y0+h),fill='#e3e8ed'); draw.text((xx-12,y0+h+5),f'{val:.0f}',fill='#333',font=font)
  counts=[]
  for name,values in series:
   c=np.histogram(values,bins=bins,range=(lo,hi))[0].astype(float); c/=max(float(c.max()),1); counts.append((name,c))
  maxv=max((c.max() for _,c in counts),default=1)
  for name,c in counts:
   color=palette.get(name,'#888'); pts=[]
   for j,v in enumerate(c): pts.append((x0+int((j+.5)*w/bins),y0+h-int(v/maxv*(h-12))))
   for a,b in zip(pts,pts[1:]): draw.line((a,b),fill=color,width=2)
  draw.text((x0,y0+h+22),'gray=training; colored lines=each RTC scene. Densities scaled to each curve maximum.',fill='#4b5964',font=font)
  return (x0,y0,w,h)
 scenes_by_date={}
 for r in scene_recs:
  if r['date'] not in scenes_by_date:
   ix=all_ids.index(r['item_id']); scenes_by_date[r['date']]=[sample_all[0][ix],sample_all[1][ix]]
 for bi,(lo,hi) in enumerate([(-40,10),(-50,0)]):
  series=[('training',np.concatenate(tr_samples[bi]))]
  for date in sorted(scenes_by_date): series.append((date,scenes_by_date[date][bi]))
  hist_draw(70,90+bi*350,630,260,series,lo,hi,f'{BANDS[bi]} backscatter distribution after dB conversion and training clip')
 # Joint-density tiles use shared dB bins for training and pooled regional acquisitions.
 tr=np.concatenate(tr_samples[0]),np.concatenate(tr_samples[1]); rtc=np.concatenate(sample_all[0]),np.concatenate(sample_all[1])
 for i,(title,pair_samples) in enumerate([('Training subset',tr),('Four regional acquisitions',rtc)]):
  x0=800+(i%2)*330; y0=180+(i//2)*360
  draw.text((x0,y0-25),f'Joint VV/VH density — {title}',fill='#1c2c3b',font=font)
  hst,xe,ye=np.histogram2d(pair_samples[0],pair_samples[1],bins=60,range=[[-40,10],[-50,0]])
  hst=np.log1p(hst); mx=max(hst.max(),1)
  heat=np.zeros((60,60,3),np.uint8)
  for iy in range(60):
   for ix in range(60):
    v=hst[ix,iy]/mx; heat[59-iy,ix]=[int(247-150*v),int(249-80*v),int(252-20*v)]
  tile=Image.fromarray(heat).resize((300,300),Image.Resampling.NEAREST); img.paste(tile,(x0,y0)); draw.rectangle((x0,y0,x0+300,y0+300),outline='#536473')
  draw.text((x0,y0+306),'VV dB  →',fill='#333',font=font); draw.text((x0,y0+325),'VH axis increases upward; density uses log(1+count)',fill='#333',font=font)
 plotpath=PLOT/'phase7_radiometric_distributions.png'; img.save(plotpath)
 report={'created_at_utc':datetime.now(timezone.utc).isoformat(),'status':'audited_preprocessing_compatibility','training_source':{'dataset':'Sen1Floods11 v1.1 HandLabeled S1Hand','split_file':'data/gherproof/raw/sen1floods11/v1.1/splits/flood_handlabeled/flood_train_data.csv','official_train_rows':len(all_train),'event_11_validation_rows_excluded':len([r for r in all_train if train._event_for_chip(r['s1'],geom)[0]==event]),'training_rows_used_for_stats':len(train_rows),'training_valid_pixel_count_exact':count,'bands':['VV','VH'],'unit':'dB per official dataset README','source_data_metadata_example':train._inspect_chip(train_rows[0])[3],'preprocess':{'clip_range_db':[-60,20],'scratch_normalization_mean_db':checkpoints['scratch']['normalization_mean'],'scratch_normalization_std_db':checkpoints['scratch']['normalization_std'],'pretrained_normalization_mean_db':checkpoints['pretrained']['normalization_mean'],'pretrained_normalization_std_db':checkpoints['pretrained']['normalization_std'],'normalization_statistic':'population per-channel mean/std over valid pixels in actual 210-chip train subset for scratch; pretrained fixed upstream SSL4EO-S12 stats','invalid_input':'set normalized values to 0 for any invalid pixel; training label -1 becomes ignore, invalid mask applied to loss','chip_shape':[512,512],'random_train_patch':[256,256],'train_augmentation':['random 90-degree rotations','optional horizontal flip'],'validation_patch':'full 512x512 chips, no padding/cropping in evaluation','threshold':0.5,'threshold_method':'fixed 0.5; not tuned on Bolivia or local event'}},'checkpoints':{k:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'architecture':checkpoints[k].get('architecture'),'input_bands':checkpoints[k].get('input_bands'),'normalization_mean':checkpoints[k].get('normalization_mean'),'normalization_std':checkpoints[k].get('normalization_std'),'threshold':0.5} for k,p in ckpt_paths.items()},'rtc_measurement':{'provider':'Microsoft Planetary Computer Sentinel-1 RTC','metadata_interpretation':'Gamma naught linear intensity, from RTC STAC asset descriptions and per-band Scale=linear tags','conversion':'dB=10*log10(linear) once; zero, negative, nonfinite and source nodata are excluded; model input then clipped to [-60,20] dB and normalized using each checkpoint metadata','scenes':scene_recs},'selected_pairwise_dB_differences':[], 'training_distribution_sample_method':'Deterministic random sample up to 2,500 valid pixels per training chip/channel (about 525k values/channel) for quantiles/plots; training means/std/min/max and valid-pixel count computed across every exact training pixel using the project _stats routine. RTC percentiles are exact per scene.','plot':plotpath.relative_to(ROOT).as_posix(),'limitations':['S1Hand contains GRD backscatter in dB but original incidence-angle/processing details are not preserved in the local chip GeoTIFFs.','The regional RTC uses terrain-corrected gamma0; equal dB units do not remove calibration-reference, incidence, terrain correction, speckle/texture, resampling or seasonal domain differences.','This report supports exploratory input compatibility only, not quantitative accuracy.']}
 for pair in s1['pairs']:
  a=scene_arrays[pair['pre_item_id']]; b=scene_arrays[pair['post_item_id']]; mask=a['mask']&b['mask']; diff=[]
  for bi,band in enumerate(BANDS):
   d=b['db'][bi][mask]-a['db'][bi][mask]; diff.append({'band':band,'median_db_change':float(np.median(d)),'p02_db_change':float(np.percentile(d,2)),'p98_db_change':float(np.percentile(d,98)),'mean_db_change':float(d.mean())})
  report['selected_pairwise_dB_differences'].append({'pair_id':pair['pair_id'],'pre_date':pair['pre_date'],'post_date':pair['post_date'],'relative_orbit':pair['relative_orbit'],'direction':pair['orbit_direction'],'common_valid_pixels':int(mask.sum()),'by_band':diff})
 # Strip large plot sample arrays before serializing.
 for x in train_dist: x.pop('sampled_values_for_plot',None)
 report['training_source']['per_band_distribution_sampled']=train_dist
 savej(MAN/'phase7_radiometric_compatibility.json',report)
 print(json.dumps({'manifest':'data/gherproof/manifests/phase7_radiometric_compatibility.json','converted_scenes':len(scene_recs),'pairs':len(report['selected_pairwise_dB_differences']),'training_rows':len(train_rows),'training_valid_pixels':count,'plot':plotpath.relative_to(ROOT).as_posix()},indent=2))
if __name__=='__main__': main()
