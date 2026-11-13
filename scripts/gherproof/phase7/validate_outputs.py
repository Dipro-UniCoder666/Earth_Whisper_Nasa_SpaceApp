"""Cross-sensor exploratory comparison and independent QC for Phase 7 rasters."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np, rasterio
from rasterio.warp import reproject
from rasterio.enums import Resampling
from PIL import Image,ImageDraw
S1=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json';INF=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json';OPT=ROOT/'data/gherproof/manifests/phase7_optical_processing.json'
OUT=ROOT/'data/gherproof/processed/phase7/cross_sensor';MAN=ROOT/'data/gherproof/manifests/phase7_cross_sensor_manifest.json';QC=ROOT/'data/gherproof/manifests/phase7_raster_qc_manifest.json'
NODATA=-9999.
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(path):
 with rasterio.open(path) as d:return d.read(1,masked=True).filled(np.nan),d.profile.copy(),d.transform,d.crs,d.nodata
def write(path,a,profile,desc,tags,mask):
 path.parent.mkdir(parents=True,exist_ok=True);p=profile.copy();p.update(driver='GTiff',count=1,dtype='uint8' if a.dtype==np.uint8 else 'float32',nodata=255 if a.dtype==np.uint8 else NODATA,compress='deflate',tiled=True,blockxsize=256,blockysize=256)
 data=a.copy();data[~mask]=255 if a.dtype==np.uint8 else NODATA
 with rasterio.open(path,'w',**p) as d:d.write(data,1);d.set_band_description(1,desc);d.update_tags(**tags)
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'valid_pixels':int(mask.sum()),'bytes':path.stat().st_size}
def warp(src,srcprof,grid,method):
 dst=np.full((grid['height'],grid['width']),np.nan,np.float32)
 reproject(src,dst,src_transform=srcprof['transform'],src_crs=srcprof['crs'],src_nodata=np.nan,dst_transform=grid['transform'],dst_crs=grid['crs'],dst_nodata=np.nan,resampling=method)
 return dst
def main():
 s1=json.loads(S1.read_text());inf=json.loads(INF.read_text());opt=json.loads(OPT.read_text());scenes={r['item_id']:r for r in inf['scenes']};pairs=s1['pairs']
 optics={}
 for x in opt['scenes']:
  nd,p,t,c,n=read(ROOT/x['ndwi']['path']);mw,pm,tm,cm,nm=read(ROOT/x['mndwi']['path']);optics[x['date']]={'ndwi':(nd,p,t,c),'mndwi':(mw,pm,tm,cm)}
 outputs=[];comp=[]
 for pair in pairs:
  pre=pair['pre_date'];post=pair['post_date'];opre=optics['2026-01-10'];opost=optics['2026-01-20']
  for model in ('scratch','pretrained'):
   recpre=next(r for r in inf['scenes'] if r['pair_id']==pair['pair_id'] and r['date']==pre and r['model']==model)
   recpost=next(r for r in inf['scenes'] if r['pair_id']==pair['pair_id'] and r['date']==post and r['model']==model)
   sarpre,profpre,*_=read(ROOT/recpre['probability']['path']);sarpost,profpost,*_=read(ROOT/recpost['probability']['path'])
   grid={'height':opost['mndwi'][1]['height'],'width':opost['mndwi'][1]['width'],'transform':opost['mndwi'][1]['transform'],'crs':opost['mndwi'][1]['crs']}
   # Compare probabilities on the optical native 20m grid using area averaging, and masks by nearest neighbor.
   sp=warp(sarpost,profpost,grid,Resampling.average); sm=np.isfinite(sp)&(sp>=.5)
   smpre=warp(sarpre,profpre,grid,Resampling.average); smprebin=np.isfinite(smpre)&(smpre>=.5)
   svalid=warp(np.isfinite(sarpost).astype(np.float32),profpost,grid,Resampling.nearest)>.5
   for ind in ('ndwi','mndwi'):
    prearr,preprof,_,_=opre[ind];postarr,postprof,_,_=opost[ind]
    if ind=='ndwi': post20=warp(postarr,postprof,grid,Resampling.average);pre20=warp(prearr,preprof,grid,Resampling.average)
    else: post20=postarr;pre20=prearr
    valid=np.isfinite(post20)&np.isfinite(pre20)&svalid
    delta=post20-pre20
    for threshold in (-.05,0,.05):
     om=post20>threshold;change=(post20>threshold)&~(pre20>threshold)
     both=valid&sm; counts={'valid_pixels':int(valid.sum()),'sar_predicted_water_like':int((valid&sm).sum()),'optical_candidate':int((valid&om).sum()),'agreement_positive':int((both&om).sum()),'sar_only':int((valid&sm&~om).sum()),'optical_only':int((valid&~sm&om).sum()),'neither':int((valid&~sm&~om).sum()),'optical_change_candidate':int((valid&change).sum()),'SAR_model_new_candidate':int((valid&sm&~smprebin).sum()),'overlap_of_optical_change_and_SAR_change':int((valid&change&sm&~smprebin).sum())}
     codes=np.zeros(post20.shape,np.uint8);codes[valid&sm&om]=1;codes[valid&sm&~om]=2;codes[valid&~sm&om]=3
     od=OUT/pair['pair_id']/model/ind/f't{threshold:+.2f}';tag={'pair_id':pair['pair_id'],'model':model,'index':ind,'optical_threshold':threshold,'interpretation':'cross-sensor corroboration only; neither source is local ground truth','S1_acquisition_dates':f'{pre},{post}','S2_acquisition_dates':'2026-01-10,2026-01-20'}
     out=write(od/'agreement_codes_20m.tif',codes,opost[ind][1],'0 neither; 1 both candidate; 2 SAR-only; 3 optical-only',tag,valid);outputs.append(out)
     comp.append({'pair_id':pair['pair_id'],'model':model,'index':ind,'threshold':threshold,'S1_pre_date':pre,'S1_post_date':post,'S2_pre_date':'2026-01-10','S2_post_date':'2026-01-20','S1_pre_offset_vs_S2_days':( __import__('datetime').date.fromisoformat(pre)-__import__('datetime').date(2026,1,10)).days,'S1_post_offset_vs_S2_days':(__import__('datetime').date.fromisoformat(post)-__import__('datetime').date(2026,1,20)).days,'counts':counts,'agreement_raster':out})
 result={'status':'exploratory_cross_sensor_comparison','outputs':outputs,'comparisons':comp,'limitations':['Optical index threshold candidates are exploratory and not labelled validation data.','Sentinel-1 and Sentinel-2 dates differ; offsets are reported per pair.','SCL class-6 pixels are retained in clear mask as in Phase 6B; they are not used as labels.','No fusion into a confirmed water/flood product; SAR and optical masks remain separate.']}
 MAN.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 # Independent QC of every Phase 7 GeoTIFF: reopen, checksum, finite statistics, masks, grid metadata.
 qc=[]
 for p in sorted((ROOT/'data/gherproof/processed/phase7').rglob('*.tif')):
  with rasterio.open(p) as ds:
   a=ds.read(masked=True);m=~np.ma.getmaskarray(a);v=np.asarray(a.data)[m];v=v[np.isfinite(v)];rec={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'crs':str(ds.crs),'transform':list(ds.transform),'bounds':list(ds.bounds),'width':ds.width,'height':ds.height,'res':list(ds.res),'count':ds.count,'dtype':list(ds.dtypes),'descriptions':list(ds.descriptions),'nodata':ds.nodata,'valid_values':int(v.size),'nan_count':int(np.isnan(a.data).sum()),'inf_count':int(np.isinf(a.data).sum()),'min':float(v.min()) if v.size else None,'p02':float(np.percentile(v,2)) if v.size else None,'median':float(np.median(v)) if v.size else None,'p98':float(np.percentile(v,98)) if v.size else None,'max':float(v.max()) if v.size else None,'reopened':True}
   if 'water_probability' in p.name and v.size and (v.min() < -1e-6 or v.max()>1+1e-6):raise RuntimeError(f'Probability range check failed: {p}')
   if rec['nan_count'] or rec['inf_count']:raise RuntimeError(f'NaN/Inf output: {p}')
   qc.append(rec)
 QC.write_text(json.dumps({'status':'all_phase7_geotiffs_reopened','raster_count':len(qc),'rasters':qc},indent=2)+'\n',encoding='utf-8')
 # Lightweight overview figure from real raster arrays; false color means probability/index, not classified truth.
 fig=Image.new('RGB',(1400,720),'white');draw=ImageDraw.Draw(fig)
 for j,pair in enumerate(pairs):
  for i,model in enumerate(('scratch','pretrained')):
   rec=next(r for r in inf['scenes'] if r['pair_id']==pair['pair_id'] and r['date']==pair['post_date'] and r['model']==model)
   with rasterio.open(ROOT/rec['probability']['path']) as ds:a=ds.read(1,masked=True).filled(0)
   a=np.clip(a[::8,::8]*255,0,255).astype(np.uint8);im=Image.fromarray(a).resize((630,280));fig.paste(Image.merge('RGB',(im,Image.new('L',im.size,30),Image.new('L',im.size,30))),(j*700,i*350+40));draw.text((j*700+8,i*350+10),f"{pair['pair_id']} | {model} post-event model probability (experimental)",fill='black')
 fig.save(ROOT/'data/gherproof/processed/phase7/figures/phase7_experimental_probability_overview.png')
 print(json.dumps({'cross_sensor_comparisons':len(comp),'qc_rasters':len(qc),'manifest':str(MAN),'qc_manifest':str(QC)},indent=2))
if __name__=='__main__':main()
