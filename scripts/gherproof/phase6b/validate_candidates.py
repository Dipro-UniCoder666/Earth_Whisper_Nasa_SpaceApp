"""Phase 6B pixel validation of saved Planetary Computer candidate IDs.

Does not rerun STAC discovery, persist SAS credentials, infer water, or modify
existing rasters/checkpoints. COG assets are read by AOI window with Rasterio.

Run either track:
  backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel1
  backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel2
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import numpy as np
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds, transform_geom
from shapely.geometry import box, mapping, shape

ROOT=Path(__file__).resolve().parents[3]
API='https://planetarycomputer.microsoft.com/api/stac/v1'
SAS='https://planetarycomputer.microsoft.com/api/sas/v1/token'
AOI_PATH=ROOT/'data/gherproof/regional/six_village_regional_search_extent.geojson'
S1_CATALOG=ROOT/'data/gherproof/manifests/phase6_sentinel1_regional_manifest.json'
S2_CATALOG=ROOT/'data/gherproof/manifests/phase6_sentinel2_regional_manifest.json'
RAW=ROOT/'data/gherproof/raw/phase6b/stac_items'
OUT=ROOT/'data/gherproof/regional/processed/phase6b'
MAN=ROOT/'data/gherproof/manifests'
NODATA=-32768.0
SCL_CLEAR={2,4,5,6}  # conservative clear land/water/dark-area classes
SCL_EXCLUDE={0,1,3,7,8,9,10,11}
EVENT=datetime(2026,1,14,tzinfo=timezone.utc)

def utcnow(): return datetime.now(timezone.utc).isoformat()
def log(msg): print(f'[{datetime.now().astimezone().isoformat(timespec="seconds")}] {msg}',flush=True)
def safe_error(e):
 s=re.sub(r'https?://[^\s?]+\?[^\s]+','[redacted signed URL]',str(e))
 return s[:300]
def save_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); tmp.replace(path)
def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
def unsigned(href):
 u=urlsplit(href); return urlunsplit((u.scheme,u.netloc,u.path,'',''))
def get_item(session,collection,item_id):
 r=session.get(f'{API}/collections/{collection}/items/{item_id}',timeout=(10,45)); r.raise_for_status(); item=r.json()
 clean=json.loads(json.dumps(item))
 for a in clean.get('assets',{}).values():
  if a.get('href'): a['href']=unsigned(a['href'])
 RAW.mkdir(parents=True,exist_ok=True); save_json(RAW/f'{collection}_{item_id}.json',clean)
 return item
def get_token(session,collection):
 r=session.get(f'{SAS}/{collection}',timeout=(10,45)); r.raise_for_status(); d=r.json()
 if not d.get('token'): raise RuntimeError('SAS endpoint did not return a token')
 return d['token'],d.get('msft:expiry')
def signed_href(href,token): return unsigned(href)+'?'+token
def range_check(session,href,token):
 url=signed_href(href,token)
 with session.get(url,headers={'Range':'bytes=0-16383'},stream=True,timeout=(10,30),allow_redirects=True) as r:
  if r.status_code!=206: raise RuntimeError(f'HTTP {r.status_code} on bounded COG range request')
  sig=next(r.iter_content(16384),b'')
  if len(sig)<8 or sig[:4] not in (b'II*\x00',b'MM\x00*'): raise RuntimeError('range response did not contain a GeoTIFF header')
  cr=r.headers.get('Content-Range','')
  total=int(cr.rsplit('/',1)[1]) if '/' in cr and cr.rsplit('/',1)[1].isdigit() else None
  return url,{'http_status':r.status_code,'content_range_total_bytes':total}
def grid_for(geom,res):
 b=transform_bounds('EPSG:4326','EPSG:32645',*geom.bounds,densify_pts=21)
 l=math.floor(b[0]/res)*res; bottom=math.floor(b[1]/res)*res; right=math.ceil(b[2]/res)*res; top=math.ceil(b[3]/res)*res
 w=int(round((right-l)/res)); h=int(round((top-bottom)/res)); tr=from_origin(l,top,res,res)
 pg=transform_geom('EPSG:4326','EPSG:32645',mapping(geom),precision=8)
 mask=geometry_mask([pg],out_shape=(h,w),transform=tr,invert=True)
 return {'crs':'EPSG:32645','resolution_m':res,'width':w,'height':h,'transform':tr,'mask':mask}
def open_remote(url):
 return rasterio.open(url)
def read_to_grid(url,grid,band=1,resampling=Resampling.nearest):
 with rasterio.Env(GDAL_HTTP_TIMEOUT='30',GDAL_HTTP_CONNECTTIMEOUT='10',GDAL_HTTP_MAX_RETRY='1',GDAL_HTTP_RETRY_DELAY='1',CPL_VSIL_CURL_USE_HEAD='NO',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
  with open_remote(url) as src:
   src_meta={'crs':str(src.crs),'width':src.width,'height':src.height,'transform':list(src.transform),'bounds':list(src.bounds),'resolution_m':list(src.res),'dtype':src.dtypes[band-1],'count':src.count,'nodata':src.nodata,'scale':src.scales[band-1],'offset':src.offsets[band-1],'description':src.descriptions[band-1],'tags':src.tags(),'band_tags':src.tags(band)}
   nd=src.nodata
   with WarpedVRT(src,crs=grid['crs'],transform=grid['transform'],width=grid['width'],height=grid['height'],resampling=resampling,nodata=nd if nd is not None else NODATA,src_nodata=nd if nd is not None else NODATA) as vrt:
    a=vrt.read(band,masked=True,out_dtype='float32' if np.issubdtype(np.dtype(src.dtypes[band-1]),np.floating) else src.dtypes[band-1])
   values=np.asarray(a.data)
   valid=(~np.ma.getmaskarray(a))&np.isfinite(values)&grid['mask']
   if nd is not None: valid &= values!=nd
   return values,valid,src_meta
def grid_cells(mask,valid,n=4):
 h,w=mask.shape; out=[]
 for iy in range(n):
  y0=iy*h//n; y1=(iy+1)*h//n
  for ix in range(n):
   x0=ix*w//n; x1=(ix+1)*w//n; region=mask[y0:y1,x0:x1]; count=int(region.sum()); good=int((valid[y0:y1,x0:x1]&region).sum())
   out.append({'row':iy,'column':ix,'aoi_pixels':count,'valid_pixels':good,'valid_fraction':good/max(count,1)})
 return out
def write_single(path,array,grid,dtype,nodata,description,tags=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 with rasterio.open(path,'w',driver='GTiff',height=grid['height'],width=grid['width'],count=1,dtype=dtype,crs=grid['crs'],transform=grid['transform'],nodata=nodata,compress='deflate',predictor=2 if np.issubdtype(np.dtype(dtype),np.integer) else 3,tiled=True,blockxsize=256,blockysize=256) as dst:
  dst.write(array.astype(dtype,copy=False),1); dst.set_band_description(1,description)
  if tags: dst.update_tags(**{str(k):str(v) for k,v in tags.items()})
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha256(path),'bytes':path.stat().st_size}
def asset_provenance(item,asset_key,asset):
 p=item.get('properties',{})
 return {'item_id':item.get('id'),'collection':item.get('collection'),'asset_key':asset_key,'unsigned_href':unsigned(asset.get('href','')),'datetime':p.get('datetime'),'platform':p.get('platform'),'relative_orbit':p.get('sat:relative_orbit'),'orbit_direction':p.get('sat:orbit_state'),'instrument_mode':p.get('sar:instrument_mode'),'polarizations':p.get('sar:polarizations'),'processing_level':p.get('s1:processing_level'),'product_type':p.get('sar:product_type'),'processing_datetime':p.get('s1:processing_datetime'),'processing_baseline':p.get('s2:processing_baseline'),'mgrs_tile':p.get('s2:mgrs_tile'),'eo_cloud_cover_percent':p.get('eo:cloud_cover'),'asset_type':asset.get('type'),'asset_roles':asset.get('roles'),'raster_bands':asset.get('raster:bands')}
def scene_common_valid_from_arrays(item,session,token,grid):
 assets=item.get('assets',{}); arrays={}; masks={}; records=[]; pol_meta={}
 for pol in ('vv','vh'):
  if pol not in assets: records.append({'asset_key':pol,'status':'missing'}); continue
  try:
   log(f"S1 pixel read start {item['id']} {pol.upper()}")
   url,rq=range_check(session,assets[pol]['href'],token)
   vals,valid,meta=read_to_grid(url,grid)
   arr=np.asarray(vals,dtype=np.float32); valid &= np.isfinite(arr)
   if meta['nodata'] is not None: valid &= arr!=meta['nodata']
   arrays[pol]=arr; masks[pol]=valid; pol_meta[pol]=meta
   v=arr[valid]
   stats={'valid_pixels':int(valid.sum()),'valid_fraction_of_aoi':float(valid.sum()/max(1,int(grid['mask'].sum()))),'min':float(v.min()) if v.size else None,'p02':float(np.percentile(v,2)) if v.size else None,'median':float(np.median(v)) if v.size else None,'p98':float(np.percentile(v,98)) if v.size else None,'max':float(v.max()) if v.size else None,'nan_count_in_aoi':int((np.isnan(arr)&grid['mask']).sum()),'infinite_count_in_aoi':int((np.isinf(arr)&grid['mask']).sum())}
   records.append({'asset_key':pol,'status':'pixel_readable','range_check':rq,'raster':meta,'stats':stats,'provenance':asset_provenance(item,pol,assets[pol])})
   log(f"S1 pixel read done {item['properties'].get('datetime')} {pol.upper()} valid={stats['valid_pixels']} ({stats['valid_fraction_of_aoi']:.4f})")
  except Exception as e:
   records.append({'asset_key':pol,'status':'failed','error_type':type(e).__name__,'error':safe_error(e)})
 return arrays,masks,pol_meta,records
def validate_s1(session,geom,grid10,only_item=None,resume=False):
 cat=json.loads(S1_CATALOG.read_text(encoding='utf-8')); all_meta=cat['catalogue_scenes']; result_path=MAN/'phase6b_sentinel1_pixel_validation.json'
 prior=json.loads(result_path.read_text(encoding='utf-8')) if resume and result_path.exists() else {}
 prior_scenes=prior.get('scenes',[]); prior_by_id={x['item_id']:x for x in prior_scenes}; scenes=list(prior_scenes); scene_masks={}; pairs=[]
 token,expiry=get_token(session,'sentinel-1-rtc')
 for r in prior_scenes:
  if r.get('status')!='raster_verified': continue
  pp=ROOT/r.get('analysis_product',{}).get('path','')
  if not pp.exists(): continue
  try:
   with rasterio.open(pp) as src:
    aa=src.read(1,masked=True); bb=src.read(2,masked=True)
    va=(~np.ma.getmaskarray(aa))&np.isfinite(aa.data)&(aa.data!=src.nodata)&grid10['mask']; vb=(~np.ma.getmaskarray(bb))&np.isfinite(bb.data)&(bb.data!=src.nodata)&grid10['mask']; scene_masks[r['item_id']]=va&vb
  except Exception as e: log(f"resume local mask read failed {r['item_id']}: {type(e).__name__}")
 items_meta=[x for x in all_meta if (not only_item or x['item_id']==only_item) and (not resume or x['item_id'] not in scene_masks)]
 if only_item and not any(x['item_id']==only_item for x in all_meta): raise ValueError(f'Unknown Phase 6 candidate ID: {only_item}')
 outdir=OUT/'sentinel1'; outdir.mkdir(parents=True,exist_ok=True)
 for ix,summary in enumerate(items_meta,1):
  item_id=summary['item_id']; log(f'S1 candidate {ix}/{len(items_meta)} metadata {item_id}')
  row={'item_id':item_id,'catalogue_status':'catalogue_match','catalogue_summary':summary,'asset_records':[]}
  try: item=get_item(session,'sentinel-1-rtc',item_id)
  except Exception as e:
   row.update({'metadata_status':'failed','error_type':type(e).__name__,'error':safe_error(e)}); scenes.append(row); save_json(MAN/'phase6b_sentinel1_pixel_validation.json',{'updated_at_utc':utcnow(),'provider':'Microsoft Planetary Computer','sas_expiry_utc':expiry,'aoi_status':cat['aoi_status'],'grid':{'crs':grid10['crs'],'resolution_m':10,'width':grid10['width'],'height':grid10['height'],'aoi_pixels':int(grid10['mask'].sum())},'scenes':scenes,'pairs':pairs}); continue
  row['metadata_status']='retrieved'; row['item_metadata']={k:v for k,v in item.get('properties',{}).items() if k in {'datetime','platform','sat:relative_orbit','sat:orbit_state','sar:instrument_mode','sar:polarizations','sar:product_type','s1:processing_level','s1:product_timeliness','s1:processing_datetime','s1:orbit_source','sat:absolute_orbit','s1:datatake_id','s1:processing_baseline'}}
  arrays,masks,metas,recs=scene_common_valid_from_arrays(item,session,token,grid10); row['asset_records']=recs
  if set(masks)=={'vv','vh'}:
   common=masks['vv']&masks['vh']&grid10['mask']; scene_masks[item_id]=common
   out=outdir/f"{item['properties']['datetime'][:10]}_{item_id}_rtc_vv_vh_10m_utm45n.tif"
   write_profile={'driver':'GTiff','height':grid10['height'],'width':grid10['width'],'count':2,'dtype':'float32','crs':grid10['crs'],'transform':grid10['transform'],'nodata':NODATA,'compress':'deflate','predictor':3,'tiled':True,'blockxsize':256,'blockysize':256}
   out.parent.mkdir(parents=True,exist_ok=True)
   with rasterio.open(out,'w',**write_profile) as dst:
    for b,pol in enumerate(('vv','vh'),1):
     a=np.where(masks[pol],arrays[pol],NODATA).astype('float32'); dst.write(a,b); dst.set_band_description(b,pol.upper())
    props=item['properties']; dst.update_tags(item_id=item_id,collection='sentinel-1-rtc',datetime=props.get('datetime',''),platform=props.get('platform',''),relative_orbit=props.get('sat:relative_orbit',''),orbit_direction=props.get('sat:orbit_state',''),instrument_mode=props.get('sar:instrument_mode',''),polarizations='VV,VH',processing='MPC Sentinel-1 RTC; nearest-neighbor warp to EPSG:32645 10m; float32 native RTC values; nodata preserved',aoi_status=cat['aoi_status'])
   qcpair={'status':'raster_verified','valid_vv_vh_pixels':int(common.sum()),'valid_fraction_of_aoi':float(common.sum()/max(1,int(grid10['mask'].sum()))),'grid_cells_4x4':grid_cells(grid10['mask'],common)}
   row['scene_raster_qc']=qcpair
   row['analysis_product']={'path':out.relative_to(ROOT).as_posix(),'sha256':sha256(out),'bytes':out.stat().st_size,'crs':grid10['crs'],'resolution_m':10,'height':grid10['height'],'width':grid10['width'],'bands':['VV','VH'],'nodata':NODATA,'valid_pixels_both_pols':int(common.sum())}
   row['status']='raster_verified'; log(f"S1 scene complete {item['properties']['datetime']} common={int(common.sum())}")
  else:
   row['status']='partial_or_failed'; row['scene_raster_qc']={'status':'not_verified','reason':'both VV and VH pixel masks were not successfully read'}
   failed=[x for x in recs if x.get('status')!='pixel_readable']; log(f"S1 incomplete {item_id}: "+('; '.join(f"{x['asset_key']} {x.get('error_type','')}: {x.get('error','')}" for x in failed)[:500]))
  if item_id in prior_by_id: scenes=[row if x['item_id']==item_id else x for x in scenes]
  else: scenes.append(row)
  save_json(MAN/'phase6b_sentinel1_pixel_validation.json',{'updated_at_utc':utcnow(),'provider':'Microsoft Planetary Computer','sas_expiry_utc':expiry,'aoi_status':cat['aoi_status'],'grid':{'crs':grid10['crs'],'resolution_m':10,'width':grid10['width'],'height':grid10['height'],'aoi_pixels':int(grid10['mask'].sum())},'scenes':scenes,'pairs':pairs})
 # Pair masks use same platform, relative orbit, pass, mode, and VV/VH requirements.
 byid={x['item_id']:x for x in scenes}
 for pre in scenes:
  p=pre.get('item_metadata',{}); date=(p.get('datetime') or '')[:10]
  if not date or date>'2026-01-13' or pre['item_id'] not in scene_masks: continue
  for post in scenes:
   q=post.get('item_metadata',{}); d2=(q.get('datetime') or '')[:10]
   if not d2 or d2<'2026-01-15' or post['item_id'] not in scene_masks: continue
   if (p.get('platform'),p.get('sat:relative_orbit'),p.get('sat:orbit_state'),p.get('sar:instrument_mode'),tuple(sorted(p.get('sar:polarizations',[])))) != (q.get('platform'),q.get('sat:relative_orbit'),q.get('sat:orbit_state'),q.get('sar:instrument_mode'),tuple(sorted(q.get('sar:polarizations',[])))): continue
   common=scene_masks[pre['item_id']]&scene_masks[post['item_id']]&grid10['mask']; count=int(common.sum())
   pair_id=f'{date}_{d2}_rel{p.get("sat:relative_orbit")}_{p.get("sat:orbit_state")}'
   maskarr=np.full(common.shape,255,dtype='uint8'); maskarr[grid10['mask']]=0; maskarr[common]=1
   prod=write_single(OUT/'sentinel1'/'pair_masks'/f'{pair_id}_common_valid_10m.tif',maskarr,grid10,'uint8',255,'1=common valid VV/VH pixels on both dates; 0=not common valid; 255=outside AOI',{'pair_id':pair_id,'pre_date':date,'post_date':d2,'relative_orbit':p.get('sat:relative_orbit'),'orbit_direction':p.get('sat:orbit_state')})
   pairs.append({'pair_id':pair_id,'pre_item_id':pre['item_id'],'pre_date':date,'post_item_id':post['item_id'],'post_date':d2,'platform':p.get('platform'),'relative_orbit':p.get('sat:relative_orbit'),'orbit_direction':p.get('sat:orbit_state'),'mode':p.get('sar:instrument_mode'),'polarizations':p.get('sar:polarizations'),'compatible_processing':'same Planetary Computer sentinel-1-rtc collection and common grid','temporal_offsets_days':{'pre_before_event':(EVENT-datetime.fromisoformat(date).replace(tzinfo=timezone.utc)).days,'post_after_event':(datetime.fromisoformat(d2).replace(tzinfo=timezone.utc)-EVENT).days},'common_valid_pixels_all_four':count,'common_valid_area_km2':count*100/1e6,'common_valid_fraction_of_aoi':count/max(int(grid10['mask'].sum()),1),'grid_cells_4x4':grid_cells(grid10['mask'],common),'coverage_raster':prod,'status':'pixel_validated'})
  # Persist once after all pair masks are available.
 save_json(result_path,{'updated_at_utc':utcnow(),'provider':'Microsoft Planetary Computer','sas_expiry_utc':expiry,'aoi_status':cat['aoi_status'],'grid':{'crs':grid10['crs'],'resolution_m':10,'width':grid10['width'],'height':grid10['height'],'aoi_pixels':int(grid10['mask'].sum())},'scenes':scenes,'pairs':pairs,'candidate_counts':{'catalogue':len(all_meta),'pixel_verified':sum(x.get('status')=='raster_verified' for x in scenes)}})
 return {'scenes':scenes,'pairs':pairs,'sas_expiry_utc':expiry}
def s2_clear_grid(session,item,token,grid20):
 a=item.get('assets',{}).get('SCL')
 if not a: raise RuntimeError('SCL asset missing')
 log(f"S2 SCL pixel read start {item['id']}")
 url,rq=range_check(session,a['href'],token); values,valid,meta=read_to_grid(url,grid20)
 scl=np.asarray(values,dtype='uint8'); valid &= np.isin(scl,list(SCL_CLEAR)); valid &= grid20['mask']
 hist={str(int(k)):int(v) for k,v in zip(*np.unique(scl[grid20['mask']],return_counts=True))}
 log(f"S2 SCL pixel read done {item['properties'].get('datetime')} clear={int(valid.sum())}/{int(grid20['mask'].sum())}")
 return scl,valid,meta,rq,hist
def validate_s2(session,geom,grid10,grid20):
 cat=json.loads(S2_CATALOG.read_text(encoding='utf-8')); summaries=cat['items']; token,expiry=get_token(session,'sentinel-2-l2a'); items=[]; masks={}; item_objs={}
 outdir=OUT/'sentinel2'; outdir.mkdir(parents=True,exist_ok=True)
 for ix,summary in enumerate(summaries,1):
  item_id=summary['item_id']; log(f'S2 candidate {ix}/{len(summaries)} metadata {item_id}')
  row={'item_id':item_id,'catalogue_status':'catalogue_match','catalogue_summary':summary}
  try:
   item=get_item(session,'sentinel-2-l2a',item_id); item_objs[item_id]=item
   props=item.get('properties',{}); row['metadata_status']='retrieved'; row['item_metadata']={k:props.get(k) for k in ['datetime','platform','s2:processing_baseline','s2:product_type','s2:mgrs_tile','sat:relative_orbit','sat:orbit_state','eo:cloud_cover','proj:epsg']}
   scl,clear,meta,rq,hist=s2_clear_grid(session,item,token,grid20); masks[item_id]=clear
   sclout=np.where(grid20['mask'],scl,255).astype('uint8'); prod=write_single(outdir/'scl'/f"{props['datetime'][:10]}_{item_id}_SCL_20m.tif",sclout,grid20,'uint8',255,'Sentinel-2 L2A Scene Classification Layer (SCL)',{'item_id':item_id,'datetime':props.get('datetime'),'classification_clear_codes':','.join(map(str,sorted(SCL_CLEAR))),'clear_class_policy':'2,4,5,6; excluded 0,1,3,7,8,9,10,11'})
   maskarr=np.full(clear.shape,255,dtype='uint8'); maskarr[grid20['mask']]=0; maskarr[clear]=1
   maskprod=write_single(outdir/'clear_masks'/f"{props['datetime'][:10]}_{item_id}_clear_20m.tif",maskarr,grid20,'uint8',255,'1=clear SCL class 2/4/5/6; 0=cloud/shadow/invalid/other class; 255=outside AOI',{'item_id':item_id,'datetime':props.get('datetime')})
   row['scl_asset']={'status':'pixel_readable','range_check':rq,'raster':meta,'pixel_class_counts_in_aoi':hist,'clear_codes':sorted(SCL_CLEAR),'clear_pixels':int(clear.sum()),'aoi_pixels':int(grid20['mask'].sum()),'clear_fraction_of_aoi':float(clear.sum()/max(1,int(grid20['mask'].sum()))),'clear_grid_cells_4x4':grid_cells(grid20['mask'],clear),'provenance':asset_provenance(item,'SCL',item['assets']['SCL']),'products':[prod,maskprod]}
   row['status']='raster_verified_scl'; row['l2a_band_read_status']='not_yet_read'
  except Exception as e:
   row['status']='partial_or_failed'; row['error_type']=type(e).__name__; row['error']=safe_error(e)
   log(f'S2 candidate failed {item_id}: {type(e).__name__}')
  items.append(row)
  save_json(MAN/'phase6b_sentinel2_pixel_validation.json',{'updated_at_utc':utcnow(),'provider':'Microsoft Planetary Computer','sas_expiry_utc':expiry,'aoi_status':cat['aoi_status'],'grid':{'crs':grid20['crs'],'resolution_m':20,'width':grid20['width'],'height':grid20['height'],'aoi_pixels':int(grid20['mask'].sum())},'scl_clear_policy':{'clear_codes':sorted(SCL_CLEAR),'excluded_codes':sorted(SCL_EXCLUDE),'description':'conservative; clear only codes 2 dark area, 4 vegetation, 5 bare soil, 6 water'},'items':items,'pairs':[]})
 # Evaluate same-tile pre/post clear masks and S2 relative orbit from item ID.
 pairs=[]
 pre=[r for r in items if r.get('item_id') in masks and r.get('item_metadata',{}).get('datetime','')[:10]<='2026-01-13']
 post=[r for r in items if r.get('item_id') in masks and r.get('item_metadata',{}).get('datetime','')[:10]>='2026-01-15']
 for a in pre:
  ia=item_objs[a['item_id']]; pa=ia['properties']; ma=re.search(r'_R(\d{3})_',a['item_id']); orbit_a=ma.group(1) if ma else None
  for b in post:
   ib=item_objs[b['item_id']]; pb=ib['properties']; mb=re.search(r'_R(\d{3})_',b['item_id']); orbit_b=mb.group(1) if mb else None
   if (pa.get('s2:mgrs_tile'),orbit_a)!=(pb.get('s2:mgrs_tile'),orbit_b): continue
   common=masks[a['item_id']]&masks[b['item_id']]&grid20['mask']; n=int(common.sum()); da=pa['datetime'][:10]; db=pb['datetime'][:10]
   pairs.append({'pre_item_id':a['item_id'],'pre_date':da,'pre_platform':pa.get('platform'),'pre_relative_orbit':orbit_a,'post_item_id':b['item_id'],'post_date':db,'post_platform':pb.get('platform'),'post_relative_orbit':orbit_b,'mgrs_tile':pa.get('s2:mgrs_tile'),'same_platform':pa.get('platform')==pb.get('platform'),'pre_baseline':pa.get('s2:processing_baseline'),'post_baseline':pb.get('s2:processing_baseline'),'common_clear_pixels_20m':n,'common_clear_area_km2':n*400/1e6,'common_clear_fraction_of_aoi':n/max(int(grid20['mask'].sum()),1),'grid_cells_4x4':grid_cells(grid20['mask'],common),'status':'SCL_pixel_validated'})
 # Select geometry/platform-compatible, near-event pair; clear coverage is evaluated as a gate/quality metric.
 same=[p for p in pairs if p['same_platform']]
 selected=max(same or pairs,key=lambda p:(-abs((datetime.fromisoformat(p['pre_date']).replace(tzinfo=timezone.utc)-EVENT).days)-abs((datetime.fromisoformat(p['post_date']).replace(tzinfo=timezone.utc)-EVENT).days),p['common_clear_fraction_of_aoi'])) if pairs else None
 if selected:
  s2grid10=grid10
  for item_id,date_key in [(selected['pre_item_id'],'pre'),(selected['post_item_id'],'post')]:
   item=item_objs[item_id]; props=item['properties']; bands={}; band_meta={}
   for band in ('B03','B04','B08'):
    log(f"S2 SR full AOI read {props['datetime'][:10]} {band}")
    if band not in item['assets']: continue
    try:
     url,rq=range_check(session,item['assets'][band]['href'],token); vals,valid,meta=read_to_grid(url,grid=s2grid10,resampling=Resampling.bilinear)
     # Reproject the 20 m clear SCL mask to 10 m by nearest neighbour for the three 10 m bands.
     clear10=np.zeros((grid10['height'],grid10['width']),dtype='uint8')
     from rasterio.warp import reproject
     reproject(masks[item_id].astype('uint8'),clear10,src_transform=grid20['transform'],src_crs=grid20['crs'],dst_transform=grid10['transform'],dst_crs=grid10['crs'],resampling=Resampling.nearest,src_nodata=0,dst_nodata=0)
     valid &= clear10.astype(bool)
     bands[band]=np.where(valid,vals.astype('float32'),np.float32(-32768)).astype('float32'); band_meta[band]={'range_check':rq,'raster':meta,'pixel_value_interpretation':'source L2A stored values; no reflectance scale/offset applied','valid_pixels_after_scl_mask':int(valid.sum()),'provenance':asset_provenance(item,band,item['assets'][band])}
    except Exception as e:
     band_meta[band]={'status':'failed','error_type':type(e).__name__,'error':str(e)[:300]}; log(f"S2 SR band failed {props['datetime'][:10]} {band}: {type(e).__name__}")
   if bands:
    path=outdir/'l2a_stored_values_10m'/f"{props['datetime'][:10]}_{item_id}_B03_B04_B08_10m_utm45n.tif"; path.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(path,'w',driver='GTiff',height=grid10['height'],width=grid10['width'],count=len(bands),dtype='float32',crs=grid10['crs'],transform=grid10['transform'],nodata=-32768,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256) as dst:
     for i,(band,arr) in enumerate(bands.items(),1): dst.write(arr,i); dst.set_band_description(i,band)
     dst.update_tags(item_id=item_id,datetime=props.get('datetime'),platform=props.get('platform'),mgrs_tile=props.get('s2:mgrs_tile'),relative_orbit=selected['pre_relative_orbit'],processing='Sentinel-2 L2A source stored values; B03/B04/B08 bilinear warp to 10m EPSG:32645; masked with 20m SCL nearest-upsample; no reflectance scale applied; no index/classification produced',scl_mask_resampling='nearest 20m to 10m')
    rec={'path':path.relative_to(ROOT).as_posix(),'sha256':sha256(path),'bytes':path.stat().st_size,'bands':list(bands),'crs':grid10['crs'],'resolution_m':10,'valid_pixels_per_band':{k:int(np.count_nonzero(v!=-32768)) for k,v in bands.items()},'asset_metadata':band_meta,'value_interpretation':'source stored values; no reflectance scale/offset applied'}
    # Add selected L2A source-value product to that item's record.
    target=next(x for x in items if x['item_id']==item_id); target['l2a_stored_values_product']=rec; target['l2a_band_read_status']='full_AOI_bands_read'
   # B11 is native 20m; retain the 20m grid and mask without upsampling.
   if 'B11' in item['assets']:
    log(f"S2 SR full AOI read {props['datetime'][:10]} B11")
    url,rq=range_check(session,item['assets']['B11']['href'],token); vals,valid,meta=read_to_grid(url,grid20,resampling=Resampling.bilinear); valid &= masks[item_id]
    arr=np.where(valid,vals.astype('float32'),np.float32(-32768)).astype('float32'); b11path=outdir/'l2a_stored_values_20m'/f"{props['datetime'][:10]}_{item_id}_B11_20m_utm45n.tif"
    prod=write_single(b11path,arr,grid20,'float32',-32768,'Sentinel-2 L2A B11 source stored values; native 20m grid; SCL masked; no reflectance scaling applied',{'item_id':item_id,'datetime':props.get('datetime'),'value_interpretation':'source stored values; no reflectance scale applied','resampling':'bilinear reprojection on native 20m grid','asset_href':unsigned(item['assets']['B11']['href'])})
    target=next(x for x in items if x['item_id']==item_id); target.setdefault('l2a_stored_values_20m',[]).append({**prod,'band':'B11','valid_pixels_after_scl_mask':int(valid.sum()),'raster':meta,'provenance':asset_provenance(item,'B11',item['assets']['B11'])})
 # persist completed pair list and selected pair
 save_json(MAN/'phase6b_sentinel2_pixel_validation.json',{'updated_at_utc':utcnow(),'provider':'Microsoft Planetary Computer','sas_expiry_utc':expiry,'aoi_status':cat['aoi_status'],'grid':{'crs':grid20['crs'],'resolution_m':20,'width':grid20['width'],'height':grid20['height'],'aoi_pixels':int(grid20['mask'].sum())},'scl_clear_policy':{'clear_codes':sorted(SCL_CLEAR),'excluded_codes':sorted(SCL_EXCLUDE),'description':'conservative; clear only codes 2 dark area, 4 vegetation, 5 bare soil, 6 water'},'items':items,'pairs':pairs,'selected_pair':selected,'candidate_counts':{'catalogue':len(summaries),'scl_pixel_verified':sum(x.get('status')=='raster_verified_scl' for x in items),'full_l2a_stored_value_scenes':sum(bool(x.get('l2a_stored_values_product')) for x in items)}})
 return {'items':items,'pairs':pairs,'selected_pair':selected,'sas_expiry_utc':expiry}
def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--sensor',choices=['sentinel1','sentinel2'],required=True); parser.add_argument('--only-item',help='Process one exact candidate item ID'); parser.add_argument('--resume',action='store_true',help='Keep successful local results and retry incomplete S1 scenes'); args=parser.parse_args()
 session=requests.Session(); session.headers.update({'User-Agent':'EarthWhisper-GherProof-Phase6B/1.0','Accept':'application/geo+json,application/json'})
 fc=json.loads(AOI_PATH.read_text(encoding='utf-8')); geom=shape(fc['features'][0]['geometry']); grid10=grid_for(geom,10); grid20=grid_for(geom,20)
 if args.sensor=='sentinel1': result=validate_s1(session,geom,grid10,only_item=args.only_item,resume=args.resume)
 else: result=validate_s2(session,geom,grid10,grid20)
 print(json.dumps({'sensor':args.sensor,'result_manifest':f'data/gherproof/manifests/phase6b_{args.sensor}_pixel_validation.json','candidate_scenes':len(result.get('scenes',result.get('items',[]))),'pixel_validated_pairs':len(result.get('pairs',[])),'sas_expiry_utc':result.get('sas_expiry_utc')},indent=2))
if __name__=='__main__': main()
