"""Reproducible Phase 6 regional imagery discovery and raster-coverage check.

The AOI polygons in this file are provisional search extents, not village,
cropland, enclosure, or flood boundaries. SAS tokens are memory-only.
Run: backend/.venv/Scripts/python.exe scripts/gherproof/phase6/regional_discovery.py
"""
from __future__ import annotations
import hashlib, json, math, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds, transform_geom
from rasterio.enums import Resampling
from shapely.geometry import box, mapping, shape

ROOT=Path(__file__).resolve().parents[3]
API='https://planetarycomputer.microsoft.com/api/stac/v1'
SAS='https://planetarycomputer.microsoft.com/api/sas/v1/token'
OUT=ROOT/'data/gherproof/regional'
MAN=ROOT/'data/gherproof/manifests'
# Explicit envelope based on the incident-reported Manirampur/Kultia and
# Abhaynagar/Chalishia locality context and published regional maps. Edges are
# intentionally generous search bounds; no source claims them as village edges.
AOIS={
 'manirampur_reported_cluster': box(89.24,22.94,89.39,23.10),
 'abhaynagar_reported_cluster': box(89.34,22.92,89.54,23.11),
}
REGION=box(89.24,22.92,89.54,23.11)
VILLAGES=[
 ('Sujatpur','Manirampur','Kultia','incident-reported; official DPHE geocode confirms village/union only'),
 ('Hatgachha','Manirampur','Kultia','incident-reported; official DPHE geocode confirms village/union only'),
 ('Kultia','Manirampur','Kultia','incident-reported; locality name may denote village or union'),
 ('Moshiahati','Abhaynagar as reported; jurisdiction disputed','unresolved','incident spelling; alternate sources associate Moshiahati with Manirampur'),
 ('Bedbhita','Abhaynagar','Chalishia reported by secondary sources','incident-reported; no boundary geometry found'),
 ('Bolarabad','Abhaynagar','Chalishia','incident-reported; academic literature supports union association'),
]
NODATA=-32768.0

def now(): return datetime.now(timezone.utc).isoformat()
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp')
 t.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); t.replace(p)
def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
def post_search(session,collection,start,end,bbox):
 r=session.post(API+'/search',json={'collections':[collection],'bbox':list(bbox.bounds),'datetime':f'{start}T00:00:00Z/{end}T23:59:59Z','limit':100},timeout=45)
 r.raise_for_status(); data=r.json(); feats=list(data.get('features',[]))
 while any(x.get('rel')=='next' for x in data.get('links',[])):
  link=next(x for x in data['links'] if x.get('rel')=='next')
  rr=session.request(link.get('method','GET'),link['href'],json=link.get('body'),timeout=45); rr.raise_for_status(); data=rr.json(); feats+=data.get('features',[])
 return feats
def token(session,collection):
 r=session.get(f'{SAS}/{collection}',timeout=45); r.raise_for_status(); d=r.json()
 if not d.get('token'): raise RuntimeError('Planetary Computer SAS response contained no token')
 return d['token'],d.get('msft:expiry')
def assess_asset(href,sas,grid,geom):
 signed=href+('?' if '?' not in href else '&')+sas
 with rasterio.Env(GDAL_HTTP_TIMEOUT='30',GDAL_HTTP_CONNECTTIMEOUT='10',GDAL_HTTP_MAX_RETRY='2',CPL_VSIL_CURL_USE_HEAD='NO',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
  with rasterio.open(signed) as src:
   with WarpedVRT(src,crs=grid['crs'],transform=grid['transform'],width=grid['width'],height=grid['height'],resampling=Resampling.nearest,nodata=src.nodata if src.nodata is not None else NODATA,src_nodata=src.nodata if src.nodata is not None else NODATA) as v:
    a=v.read(1,masked=True,out_dtype='float32')
    vals=np.asarray(a.data); valid=(~np.ma.getmaskarray(a)&np.isfinite(vals)&(vals!=NODATA)&grid['mask'])
   return {'status':'pixel_window_read','crs':str(src.crs),'source_resolution_m':list(src.res),'source_nodata':src.nodata,'valid_pixels':int(valid.sum()),'aoi_pixels':int(grid['mask'].sum()),'valid_fraction_of_aoi':float(valid.sum()/max(1,grid['mask'].sum()))},valid,vals
def build_grid(geom):
 b=geom.bounds; bb=transform_bounds('EPSG:4326','EPSG:32645',*b,densify_pts=21)
 l=math.floor(bb[0]/10)*10; bot=math.floor(bb[1]/10)*10; r=math.ceil(bb[2]/10)*10; top=math.ceil(bb[3]/10)*10
 w=int(round((r-l)/10)); h=int(round((top-bot)/10)); tr=from_origin(l,top,10,10)
 projected=transform_geom('EPSG:4326','EPSG:32645',mapping(geom),precision=8)
 mask=geometry_mask([projected],out_shape=(h,w),transform=tr,invert=True)
 return {'crs':'EPSG:32645','transform':tr,'width':w,'height':h,'mask':mask,'resolution_m':10}
def write_gpkg(path,geom):
 # Minimal GeoPackage 1.3: one WGS84 polygon feature and standards-compliant header.
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists(): path.unlink()
 c=sqlite3.connect(path); c.execute('PRAGMA application_id=1196444487'); c.execute('PRAGMA user_version=10300')
 c.executescript("""CREATE TABLE gpkg_spatial_ref_sys(srs_name TEXT NOT NULL,srs_id INTEGER NOT NULL PRIMARY KEY,organization TEXT NOT NULL,organization_coordsys_id INTEGER NOT NULL,definition TEXT NOT NULL,description TEXT); CREATE TABLE gpkg_contents(table_name TEXT NOT NULL PRIMARY KEY,data_type TEXT NOT NULL,identifier TEXT UNIQUE,description TEXT DEFAULT '',last_change DATETIME NOT NULL,min_x DOUBLE,min_y DOUBLE,max_x DOUBLE,max_y DOUBLE,srs_id INTEGER); CREATE TABLE gpkg_geometry_columns(table_name TEXT NOT NULL,column_name TEXT NOT NULL,geometry_type_name TEXT NOT NULL,srs_id INTEGER NOT NULL,z TINYINT NOT NULL,m TINYINT NOT NULL,PRIMARY KEY(table_name,column_name)); CREATE TABLE regional_aoi(fid INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,classification TEXT,provenance TEXT,geom BLOB);""")
 c.execute("INSERT INTO gpkg_spatial_ref_sys VALUES ('Undefined Cartesian',-1,'NONE',-1,'undefined','')")
 c.execute("INSERT INTO gpkg_spatial_ref_sys VALUES ('Undefined geographic',0,'NONE',0,'undefined','')")
 c.execute("INSERT INTO gpkg_spatial_ref_sys VALUES ('WGS 84 geodetic',4326,'EPSG',4326,'GEOGCRS[\"WGS 84\"]','longitude/latitude WGS 84')")
 b=geom.bounds; c.execute("INSERT INTO gpkg_contents VALUES ('regional_aoi','features','regional_aoi','Provisional regional search envelope; not administrative boundaries',?, ?,?,?,?,4326)",(now(),*b))
 c.execute("INSERT INTO gpkg_geometry_columns VALUES ('regional_aoi','geom','MULTIPOLYGON',4326,0,0)")
 g=geom if geom.geom_type=='MultiPolygon' else __import__('shapely').geometry.MultiPolygon([geom])
 wkb=g.wkb; header=b'GP'+bytes([0,0])+int(4326).to_bytes(4,'little',signed=True)
 blob=header+wkb
 c.execute("INSERT INTO regional_aoi(name,classification,provenance,geom) VALUES (?,?,?,?)",('six_village_regional_search_envelope','provisional_search_extent','Incident-reported locality groups and broad published regional context; NOT village, mouza, parcel or enclosure boundary',blob))
 c.commit(); c.close()
def main():
 OUT.mkdir(parents=True,exist_ok=True); sess=requests.Session(); sess.headers.update({'User-Agent':'EarthWhisper-GherProof-Phase6/1.0','Accept':'application/geo+json,application/json'})
 regional=mapping(REGION); grid=build_grid(REGION)
 aoi={'type':'FeatureCollection','name':'gherproof_phase6_provisional_regional_search_extent','crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:OGC::CRS84'}},'features':[{'type':'Feature','properties':{'name':'six_village_regional_search_envelope','classification':'provisional search extent, not admin boundary','reported_villages':[x[0] for x in VILLAGES],'source':'incident-reported locality group; approximate extents based on reported upazilas and publicly mapped context','positional_accuracy':'not quantified; village-specific edges unavailable'},'geometry':regional}]}
 (OUT/'six_village_regional_search_extent.geojson').write_text(json.dumps(aoi,indent=2)+'\n',encoding='utf-8'); write_gpkg(OUT/'six_village_regional_search_extent.gpkg',REGION)
 rows=[]
 for col,start,end in [('sentinel-1-rtc','2026-01-01','2026-01-13'),('sentinel-1-rtc','2026-01-15','2026-01-31')]:
  items=post_search(sess,col,start,end,REGION)
  rows.extend(items)
 scenes=[]
 for item in rows:
  p=item.get('properties',{}); pols=p.get('sar:polarizations',[]); geom=shape(item['geometry']); overlap=geom.intersection(REGION).area/REGION.area
  if p.get('sar:instrument_mode')!='IW' or not {'VV','VH'}.issubset(set(pols)): continue
  scenes.append({'item_id':item['id'],'collection':'sentinel-1-rtc','datetime':p.get('datetime'),'platform':p.get('platform'),'relative_orbit':p.get('sat:relative_orbit'),'orbit_direction':p.get('sat:orbit_state'),'instrument_mode':p.get('sar:instrument_mode'),'polarizations':pols,'product_type':p.get('sar:product_type'),'processing_level':p.get('s1:processing_level'),'footprint_overlap_fraction_by_degree_area':overlap,'footprint':item['geometry'],'asset_keys':list(item.get('assets',{})),'asset_access_status':'not_pixel_validated'})
 # Optional pixel windows are separated from the fast, catalogue-only default.
 do_pixels='--check-pixels' in sys.argv
 sas,expiry=token(sess,'sentinel-1-rtc') if do_pixels else (None,None)
 pre=[x for x in rows if '2026-01-01'<=x['properties']['datetime'][:10]<='2026-01-13'] if do_pixels else []
 post=[x for x in rows if '2026-01-15'<=x['properties']['datetime'][:10]<='2026-01-31'] if do_pixels else []
 pairs=[]
 byid={x['id']:x for x in rows}
 for a in pre:
  pa=a['properties']
  if pa.get('sar:instrument_mode')!='IW' or not {'VV','VH'}.issubset(set(pa.get('sar:polarizations',[]))): continue
  for b in post:
   pb=b['properties']
   if (pa.get('platform')!=pb.get('platform') or pa.get('sat:relative_orbit')!=pb.get('sat:relative_orbit') or pa.get('sat:orbit_state')!=pb.get('sat:orbit_state') or pb.get('sar:instrument_mode')!='IW' or not {'VV','VH'}.issubset(set(pb.get('sar:polarizations',[])))): continue
   if (pa.get('datetime','')[:10],pb.get('datetime','')[:10]) not in {('2026-01-07','2026-01-19'),('2026-01-12','2026-01-19'),('2026-01-09','2026-01-21'),('2026-01-12','2026-01-24')}: continue
   cov={}; common=None
   masks={}; per_asset={}
   for date,it in [('pre',a),('post',b)]:
    for pol in ('vv','vh'):
     try:
      qc,mask,values=assess_asset(it['assets'][pol]['href'],sas,grid,REGION); masks[f'{date}_{pol.upper()}']=mask; per_asset[f'{date}_{pol.upper()}']=(values,mask); cov[f'{date}_{pol.upper()}']=qc
     except Exception as e: cov[f'{date}_{pol.upper()}']={'status':'read_failed','error_type':type(e).__name__}
   common_mask=grid['mask'].copy()
   for m in masks.values(): common_mask &= m
   common=int(common_mask.sum()) if len(masks)==4 else None
   status='four_asset_intersection_validated' if len(masks)==4 else 'pixel_window_incomplete'
   pair={'pre_item_id':a['id'],'pre_datetime':pa.get('datetime'),'post_item_id':b['id'],'post_datetime':pb.get('datetime'),'platform':pa.get('platform'),'relative_orbit':pa.get('sat:relative_orbit'),'orbit_direction':pa.get('sat:orbit_state'),'mode':'IW','polarizations':['VV','VH'],'coverage_checks':cov,'common_valid_pixels':common,'common_valid_fraction_of_aoi':common/max(1,int(grid['mask'].sum())) if common is not None else None,'coverage_status':status}
   if common is not None and common>0:
    pair['products']=[]
    for key,(values,valid) in per_asset.items():
     date,pol=key.split('_'); source_scene=a if date=='pre' else b; out=OUT/'processed'/'sentinel1'/f"{a['properties']['datetime'][:10]}_{b['properties']['datetime'][:10]}_{date.lower()}_{pol.lower()}_rtc_10m_utm45n.tif"
     arr=np.where(valid,values,NODATA).astype('float32')
     with rasterio.open(out,'w',driver='GTiff',height=grid['height'],width=grid['width'],count=1,dtype='float32',crs=grid['crs'],transform=grid['transform'],nodata=NODATA,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256) as dst:
      dst.write(arr,1); dst.set_band_description(1,f'Sentinel-1 RTC {pol} gamma0 linear power'); dst.update_tags(acquisition_datetime=source_scene['properties']['datetime'],item_id=source_scene['id'],relative_orbit=str(pa.get('sat:relative_orbit')),orbit_direction=pa.get('sat:orbit_state'),processing='Planetary Computer RTC COG nearest-neighbour 10 m grid',source_href=source_scene['assets'][pol.lower()]['href'])
     h=sha256(out); pair['products'].append({'path':out.relative_to(ROOT).as_posix(),'sha256':h,'valid_pixels_in_aoi':int(valid.sum())})
   pairs.append(pair)
 compatible=[]
 for x in scenes:
  for y in scenes:
   if x['datetime']<'2026-01-14' and y['datetime']>'2026-01-14' and (x['platform'],x['relative_orbit'],x['orbit_direction'])==(y['platform'],y['relative_orbit'],y['orbit_direction']):
    compatible.append({'pre_date':x['datetime'][:10],'post_date':y['datetime'][:10],'relative_orbit':x['relative_orbit'],'orbit_direction':x['orbit_direction'],'status':'catalogue_geometry_match_only'})
 result={'created_at_utc':now(),'provider':'Microsoft Planetary Computer','stac_api':API,'aoi_geojson':'data/gherproof/regional/six_village_regional_search_extent.geojson','aoi_status':'provisional regional search envelope; not village/admin/mouza/gher boundary','aoi_bbox_wgs84':list(REGION.bounds),'aoi_area_km2_approx':round(REGION.area*111.32*111.32*math.cos(math.radians(23.015)),2),'analysis_grid':{'crs':grid['crs'],'resolution_m':10,'width':grid['width'],'height':grid['height'],'aoi_pixels':int(grid['mask'].sum())},'query_windows':[{'pre':'2026-01-01/2026-01-13'},{'post':'2026-01-15/2026-01-31'}],'catalogue_scenes':scenes,'catalogue_compatible_pairs':compatible,'same_geometry_pairs':pairs,'pixel_validation_requested':do_pixels,'sas_expiry_utc':expiry,'limitations':['Catalog search results are not raster observations.','Pixel windows are not validated in the default catalogue-only run; --check-pixels enables bounded window reads.','Regional envelope is intentionally provisional and positional accuracy is not quantified.','No event inference or affected area is produced.']}
 save(MAN/'phase6_sentinel1_regional_manifest.json',result)
 s2=[]
 for start,end in [('2026-01-01','2026-01-13'),('2026-01-15','2026-01-31')]:
  try:
   its=post_search(sess,'sentinel-2-l2a',start,end,REGION)
   for it in its:
    p=it.get('properties',{}); g=shape(it['geometry']); s2.append({'item_id':it['id'],'datetime':p.get('datetime'),'platform':p.get('platform'),'mgrs_tile':p.get('s2:mgrs_tile'),'eo_cloud_cover':p.get('eo:cloud_cover'),'footprint_overlap_fraction_by_degree_area':g.intersection(REGION).area/REGION.area,'assets':list(it.get('assets',{})),'pixel_qa_status':'not_validated'})
  except Exception as e: s2.append({'query_window':[start,end],'status':'query_failed','error_type':type(e).__name__})
 save(MAN/'phase6_sentinel2_regional_manifest.json',{'created_at_utc':now(),'provider':'Microsoft Planetary Computer','aoi_status':'same provisional regional search envelope','items':s2,'limitations':['Scene cloud percentage is not pixel-level cloud/shadow validation.','No optical corroboration claimed without SCL/cloud mask and regional asset pixels.']})
 print(json.dumps({'aoi_bbox':list(REGION.bounds),'regional_aoi_pixels':int(grid['mask'].sum()),'s1_items':len(scenes),'compatible_pairs_catalogue':len(compatible),'compatible_pairs_pixel_checked':len(pairs),'s2_items':len(s2),'pixel_validation_requested':do_pixels,'manifest':'data/gherproof/manifests/phase6_sentinel1_regional_manifest.json'},indent=2))
if __name__=='__main__': main()
