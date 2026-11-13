"""Write Phase 7B-aligned SAR/optical comparison layers without editing Phase 7 files."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np,rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
from PIL import Image,ImageDraw
INF=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json';S1=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json';OPT=ROOT/'data/gherproof/manifests/phase7_optical_processing.json'
OUT=ROOT/'data/gherproof/processed/phase7b/cross_sensor';MAN=ROOT/'data/gherproof/manifests/phase7b_cross_sensor_validation.json';NODATA=255
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(path):
 with rasterio.open(path) as d:return d.read(1,masked=True).filled(np.nan).astype(np.float32),d.profile.copy()
def warp(a,prof,dst,resamp):
 out=np.full((dst['height'],dst['width']),np.nan,np.float32)
 reproject(a,out,src_transform=prof['transform'],src_crs=prof['crs'],src_nodata=np.nan,dst_transform=dst['transform'],dst_crs=dst['crs'],dst_nodata=np.nan,resampling=resamp)
 return out
def write(path,a,profile,description,tags,valid):
 path.parent.mkdir(parents=True,exist_ok=True);p=profile.copy();p.update(driver='GTiff',count=1,dtype='uint8',nodata=NODATA,compress='deflate',predictor=2,tiled=True,blockxsize=256,blockysize=256)
 d=a.astype(np.uint8,copy=True);d[~valid]=NODATA
 with rasterio.open(path,'w',**p) as ds:ds.write(d,1);ds.set_band_description(1,description);ds.update_tags(**{str(k):str(v) for k,v in tags.items()})
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'valid_pixels':int(valid.sum()),'bytes':path.stat().st_size}
def main():
 inf=json.loads(INF.read_text());s1=json.loads(S1.read_text());opt=json.loads(OPT.read_text());optical={}
 for s in opt['scenes']:
  nd,p=load(ROOT/s['ndwi']['path']);mw,pm=load(ROOT/s['mndwi']['path']);optical[s['date']]={'ndwi':(nd,p),'mndwi':(mw,pm)}
 scenes={r['item_id']:r for r in inf['scenes']};comparisons=[];products=[];pairs=s1['pairs']
 for pair in pairs:
  pre_s2=optical['2026-01-10'];post_s2=optical['2026-01-20'];gridprof=post_s2['mndwi'][1];grid={'height':gridprof['height'],'width':gridprof['width'],'transform':gridprof['transform'],'crs':gridprof['crs']}
  for model in ('scratch','pretrained'):
   pre=next(r for r in inf['scenes'] if r['pair_id']==pair['pair_id'] and r['date']==pair['pre_date'] and r['model']==model)
   post=next(r for r in inf['scenes'] if r['pair_id']==pair['pair_id'] and r['date']==pair['post_date'] and r['model']==model)
   sar_pre,sp=load(ROOT/pre['probability']['path']);sar_post,sq=load(ROOT/post['probability']['path'])
   sarpre20=warp(sar_pre,sp,grid,Resampling.average);sarpost20=warp(sar_post,sq,grid,Resampling.average)
   sarvalid=np.isfinite(sarpre20)&np.isfinite(sarpost20);sarpremask=sarpre20>=.5;sarpostmask=sarpost20>=.5;sarchange=sarpostmask&~sarpremask
   for index in ('ndwi','mndwi'):
    opa,op=pre_s2[index];opb,oq=post_s2[index]
    if index=='ndwi':opa20=warp(opa,op,grid,Resampling.average);opb20=warp(opb,oq,grid,Resampling.average)
    else:opa20,opb20=opa,opb
    optvalid=np.isfinite(opa20)&np.isfinite(opb20);common=sarvalid&optvalid;change_delta=opb20-opa20
    for threshold in (-.05,0,.05):
     preopt=opa20>threshold;postopt=opb20>threshold;optchange=postopt&~preopt
     sarwater=sarpostmask; codes=np.zeros(gridprof['height']*gridprof['width'],np.uint8).reshape((gridprof['height'],gridprof['width']))
     codes[common&sarwater&postopt]=1;codes[common&sarwater&~postopt]=2;codes[common&~sarwater&postopt]=3
     change=np.zeros_like(codes);change[common&sarchange&optchange]=1;change[common&sarchange&~optchange]=2;change[common&~sarchange&optchange]=3
     base=OUT/pair['pair_id']/model/index/f't{threshold:+.2f}';tags={'pair_id':pair['pair_id'],'model':model,'optical_index':index,'optical_threshold':threshold,'SAR_threshold':.5,'S1_pre':pair['pre_date'],'S1_post':pair['post_date'],'S2_pre':'2026-01-10','S2_post':'2026-01-20','interpretation':'exploratory agreement coding only; not validation or fused flood truth'}
     ag=write(base/'agreement_codes_20m.tif',codes,gridprof,'0 neither; 1 both candidate; 2 SAR-only; 3 optical-only',tags,common)
     ch=write(base/'change_agreement_codes_20m.tif',change,gridprof,'0 neither; 1 both change candidates; 2 SAR-only change; 3 optical-only change',tags,common)
     def ct(mask):return int((mask&common).sum())
     counts={'valid_pixels':int(common.sum()),'SAR_post_class_candidate':ct(sarwater),'optical_post_candidate':ct(postopt),'post_positive_overlap':ct(sarwater&postopt),'post_SAR_only':ct(sarwater&~postopt),'post_optical_only':ct(~sarwater&postopt),'SAR_change_candidate':ct(sarchange),'optical_change_candidate':ct(optchange),'change_positive_overlap':ct(sarchange&optchange),'change_SAR_only':ct(sarchange&~optchange),'change_optical_only':ct(~sarchange&optchange)}
     products.extend([ag,ch]);comparisons.append({'pair_id':pair['pair_id'],'model':model,'index':index,'optical_threshold':threshold,'grid':{'crs':str(gridprof['crs']),'transform':list(gridprof['transform']),'width':gridprof['width'],'height':gridprof['height'],'resolution':list(gridprof['transform'][:2])},'time_offsets_days':{'S1_pre_minus_S2_pre':( __import__('datetime').date.fromisoformat(pair['pre_date'])-__import__('datetime').date(2026,1,10)).days,'S1_post_minus_S2_post':(__import__('datetime').date.fromisoformat(pair['post_date'])-__import__('datetime').date(2026,1,20)).days},'counts':counts,'agreement_layer':ag,'change_agreement_layer':ch})
 manifest={'status':'complete_corrected_20m_alignment','source_products_preserved':True,'phase7_ndwi_alignment_issue':'The original Phase 7 NDWI agreement output files were written with the 10m NDWI raster profile although their comparison arrays were 20m. Their prior counts were computed from 20m arrays, but those raster files are mis-georeferenced/resized in the output grid. Phase 7 outputs were not overwritten. This Phase 7B rebuild writes all NDWI and MNDWI comparisons on the exact selected-pair 20m native B11/MNDWI grid.','comparison_count':len(comparisons),'geotiff_count':len(products),'comparisons':comparisons,'outputs':products,'limitations':['Cross-sensor agreement remains corroboration only; optical indices and model predictions are not reference truth.','S1/S2 acquisition dates are non-coincident; exact offsets are listed per comparison.','No fused confirmed flood map or impact area is produced.']}
 MAN.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 # Re-open every newly written comparison and validate grids and classes.
 expected=(gridprof['crs'],gridprof['transform'],gridprof['width'],gridprof['height']);qc=[]
 for r in products:
  with rasterio.open(ROOT/r['path']) as ds:
   actual=(ds.crs,ds.transform,ds.width,ds.height)
   if actual!=expected:raise RuntimeError(f'Cross-sensor grid mismatch: {r["path"]}')
   vals=ds.read(1,masked=True).compressed()
   if not set(np.unique(vals).tolist()).issubset({0,1,2,3}):raise RuntimeError(f'Unexpected agreement code in {r["path"]}')
   qc.append({'path':r['path'],'sha256':sha(ROOT/r['path']),'grid_matches_native_20m':True,'valid_pixels':int(vals.size),'codes_present':sorted(np.unique(vals).tolist())})
 manifest['qc']={'status':'pass','rasters':qc,'grid_reference':{'crs':str(gridprof['crs']),'transform':list(gridprof['transform']),'width':gridprof['width'],'height':gridprof['height']}}
 MAN.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({'comparisons':len(comparisons),'rasters':len(products),'grid':'20m native MNDWI grid','manifest':MAN.relative_to(ROOT).as_posix()},indent=2))
if __name__=='__main__':main()
