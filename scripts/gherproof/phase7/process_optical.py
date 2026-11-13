"""Scale the selected S2 L2A pair using product offsets and derive indices."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

MAN=ROOT/'data/gherproof/manifests/phase7_sentinel2_radiometric_metadata.json'
PIX=ROOT/'data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json'
OUT=ROOT/'data/gherproof/processed/phase7/sentinel2'
NODATA=-9999.0

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def write(path,a,ref,desc,tags):
 path.parent.mkdir(parents=True,exist_ok=True)
 prof=ref.profile.copy(); prof.update(driver='GTiff',count=1,dtype='float32',nodata=NODATA,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256)
 with rasterio.open(path,'w',**prof) as ds:
  ds.write(a.astype('float32'),1); ds.set_band_description(1,desc); ds.update_tags(**tags)
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,'valid_pixels':int((np.isfinite(a)&(a!=NODATA)).sum())}
def index_summary(a,mask):
 v=a[mask & np.isfinite(a)]
 return {'valid_pixels':int(v.size),'min':float(v.min()),'max':float(v.max()),'percentiles':{str(p):float(np.percentile(v,p)) for p in (1,2,25,50,75,98,99)},'exploratory_candidate_pixels':{str(t):int((v>t).sum()) for t in (-.05,0,.05)}}
def main():
 meta=json.loads(MAN.read_text()); pix=json.loads(PIX.read_text()); recs=meta['scenes']
 # Validate each of the required products explicitly before reading any samples.
 products=[]
 for item in (pix['selected_pair']['pre_item_id'],pix['selected_pair']['post_item_id']):
  candidates=[v for v in recs if v.get('item_id')==item]
  if not candidates: raise RuntimeError(f'No product metadata record found for {item}')
  rec=candidates[0]
  vals=json.dumps(rec.get('metadata_assets',{}))
  for required in ('05.11','10000','-1000'):
   if required not in vals: raise RuntimeError(f'Metadata record for {item} missing expected {required}')
  products.append((item,rec))
 results=[]
 for pair_item,(date,scene_id) in zip(products,[(pix['selected_pair']['pre_date'],pix['selected_pair']['pre_item_id']),(pix['selected_pair']['post_date'],pix['selected_pair']['post_item_id'])]):
  item,rec=pair_item
  if item!=scene_id: raise RuntimeError('Pair metadata order mismatch')
  paths=list((ROOT/'data/gherproof/regional/processed/phase6b/sentinel2/l2a_stored_values_10m').glob(f'{date}_*_B03_B04_B08_10m_utm45n.tif'))
  p20=list((ROOT/'data/gherproof/regional/processed/phase6b/sentinel2/l2a_stored_values_20m').glob(f'{date}_*_B11_20m_utm45n.tif'))
  if len(paths)!=1 or len(p20)!=1: raise RuntimeError(f'Expected exactly one selected stored-value stack for {date}; got {len(paths)}/{len(p20)}')
  with rasterio.open(paths[0]) as ds10:
   a=ds10.read(masked=True).astype('float32'); ref10=ds10
   dn=a.filled(np.nan); valid10=(~np.ma.getmaskarray(a))&(dn!=0)&np.isfinite(dn)
   # Product metadata confirms baseline 05.11, quantification 10000, offset -1000 for B03/B04/B08.
   refl=np.full(dn.shape,np.nan,np.float32); refl[:,valid10[0]]= (dn[:,valid10[0]]-1000.0)/10000.0
   bands={n:refl[i] for i,n in enumerate(('B03','B04','B08'))}
   clear10=np.zeros(valid10.shape[1:],bool)
   sclpath=next((ROOT/'data/gherproof/regional/processed/phase6b/sentinel2/clear_masks').glob(f'*{item}_clear_20m.tif'))
   with rasterio.open(sclpath) as sclds:
    scl=sclds.read(1); clear20=(scl==1) if sclds.nodata is None else (scl==1)&(scl!=sclds.nodata)
    clear10_u8=np.zeros(clear10.shape,np.uint8)
    reproject(clear20.astype('uint8'),clear10_u8,src_transform=sclds.transform,src_crs=sclds.crs,dst_transform=ds10.transform,dst_crs=ds10.crs,resampling=Resampling.nearest)
    clear10=clear10_u8.astype(bool)
   common10=clear10 & np.all(valid10,axis=0)
   outscene={'date':date,'item_id':item,'baseline':'05.11','quantification_value':10000,'offsets':{'B03':-1000,'B04':-1000,'B08':-1000,'B11':-1000},'bands':{},'source_10m':paths[0].relative_to(ROOT).as_posix(),'source_20m':p20[0].relative_to(ROOT).as_posix()}
   for name,arr in bands.items():
    raw=np.where(valid10[0]&clear10,arr,NODATA)
    outscene['bands'][name]=write(OUT/f'{date}_{name}_reflectance_10m.tif',raw,ds10,f'{name} BOA reflectance',{'formula':'(DN + BOA_ADD_OFFSET)/BOA_QUANTIFICATION_VALUE','dn_zero':'NoData','offset':-1000,'quantification_value':10000,'baseline':'05.11','SCL_clear_codes':'2,4,5,6','purpose':'exploratory reflectance; masked to clear SCL and valid source'})
   green,nir=bands['B03'],bands['B08']; den=green+nir; valid=common10&np.isfinite(den)&(np.abs(den)>1e-8)
   ndwi=np.full(den.shape,NODATA,np.float32); ndwi[valid]=(green[valid]-nir[valid])/den[valid]
   outscene['ndwi']=write(OUT/f'{date}_NDWI_10m.tif',ndwi,ds10,'NDWI (Green,NIR)',{'formula':'(B03-B08)/(B03+B08)','reflectance':'BOA reflectance with metadata offsets','mask':'SCL clear and both bands valid','interpretation':'continuous index; not a water label'})
   outscene['ndwi_summary']=index_summary(ndwi,valid)
   outscene['grid10']={'crs':str(ds10.crs),'transform':list(ds10.transform),'width':ds10.width,'height':ds10.height}
  with rasterio.open(p20[0]) as ds20:
   b11=ds20.read(1,masked=True).astype('float32'); d11=b11.filled(np.nan); v11=(~np.ma.getmaskarray(b11))&(d11!=0)&np.isfinite(d11)
   refl11=np.full(d11.shape,np.nan,np.float32); refl11[v11]=(d11[v11]-1000)/10000
   # Green reflectance is averaged from native 10 m to the native B11 20 m grid.
   b03source=OUT/f'{date}_B03_reflectance_10m.tif'
   with rasterio.open(b03source) as gds:
    green20=np.full((ds20.height,ds20.width),np.nan,np.float32)
    reproject(gds.read(1),green20,src_transform=gds.transform,src_crs=gds.crs,src_nodata=NODATA,dst_transform=ds20.transform,dst_crs=ds20.crs,dst_nodata=np.nan,resampling=Resampling.average)
   sclpath=next((ROOT/'data/gherproof/regional/processed/phase6b/sentinel2/clear_masks').glob(f'*{item}_clear_20m.tif'))
   with rasterio.open(sclpath) as sds: clear20=(sds.read(1)==1)
   valid20=clear20&v11&np.isfinite(green20)&(np.abs(green20+refl11)>1e-8)
   mndwi=np.full(refl11.shape,NODATA,np.float32); mndwi[valid20]=(green20[valid20]-refl11[valid20])/(green20[valid20]+refl11[valid20])
   outscene['B11']=write(OUT/f'{date}_B11_reflectance_20m.tif',np.where(valid20,refl11,NODATA),ds20,'B11 BOA reflectance',{'formula':'(DN-1000)/10000','native_resolution':'20 m'})
   outscene['mndwi']=write(OUT/f'{date}_MNDWI_20m.tif',mndwi,ds20,'MNDWI (Green averaged to 20m, B11)',{'formula':'(B03_10m averaged to 20m - B11)/(B03_10m averaged to 20m + B11)','resampling':'average from 10 m to native B11 20 m grid','mask':'SCL clear and valid B03/B11','interpretation':'continuous index; not a water label'})
   outscene['mndwi_summary']=index_summary(mndwi,valid20)
   outscene['grid20']={'crs':str(ds20.crs),'transform':list(ds20.transform),'width':ds20.width,'height':ds20.height}
  results.append(outscene)
 result={'status':'processed','formula':'(DN + BOA_ADD_OFFSET)/BOA_QUANTIFICATION_VALUE','dn_zero_nodata':True,'scenes':results,'threshold_sensitivity':{'candidate_thresholds':[-0.05,0,0.05],'meaning':'exploratory index threshold counts only; not validated water masks'},'optical_limitations':['SCL class 6 is included among clear SCL pixels but denotes water class in SCL; it is a quality/land-cover classification, not an independent label.','Optical index thresholds are exploratory and sensitive to turbidity, vegetation, wet soil, shadow, ponds and mixed pixels.','No optical/SAR fusion is a confirmed flood map.']}
 outpath=ROOT/'data/gherproof/manifests/phase7_optical_processing.json'; outpath.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'scenes':len(results),'output_manifest':str(outpath)},indent=2))
if __name__=='__main__': main()
