"""Build Phase 6B local raster QC, coverage summaries and figures.

Run after validate_candidates.py --sensor sentinel1 and --sensor sentinel2.
This script reads only Phase 6B products and never runs inference.
"""
from __future__ import annotations
import hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'data/gherproof/regional/processed/phase6b'
MAN=ROOT/'data/gherproof/manifests'
S1=MAN/'phase6b_sentinel1_pixel_validation.json'
S2=MAN/'phase6b_sentinel2_pixel_validation.json'
def sha256(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def savej(p,d):
 t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); t.replace(p)
def pct(values, p): return float(np.percentile(values,p)) if values.size else None
def main():
 font=ImageFont.load_default()
 s1=json.loads(S1.read_text(encoding='utf-8')); s2=json.loads(S2.read_text(encoding='utf-8'))
 # Use scientifically accurate product keys and names for L2A samples; values remain the source stored samples.
 for row in s2['items']:
  if 'surface_reflectance_product' in row:
   row['l2a_stored_values_product']=row.pop('surface_reflectance_product')
  if 'surface_reflectance_20m' in row:
   row['l2a_stored_values_20m']=row.pop('surface_reflectance_20m')
  if 'surface_reflectance_probe_status' in row:
   row['l2a_band_read_status']=row.pop('surface_reflectance_probe_status')
  for prod in [row.get('l2a_stored_values_product',{})]+row.get('l2a_stored_values_20m',[]):
   if prod.get('path'):
    prod['path']=prod['path'].replace('/surface_reflectance_10m/','/l2a_stored_values_10m/').replace('/surface_reflectance_20m/','/l2a_stored_values_20m/')
 s2['candidate_counts'].pop('full_surface_reflectance_pairs',None)
 s2['candidate_counts']['full_l2a_stored_value_scenes']=sum(bool(x.get('l2a_stored_values_product')) for x in s2['items'])
 s2['value_interpretation']='Sentinel-2 L2A source integer samples retained as float32 for nodata compatibility; no reflectance scaling or index/classification applied.'
 # Correct B11 metadata on files created before the output label was corrected.
 for row in s2['items']:
  for rec in row.get('l2a_stored_values_20m',[]):
   p=ROOT/rec['path']
   if p.exists():
    with rasterio.open(p,'r+') as ds:
     ds.set_band_description(1,'Sentinel-2 L2A B11 source stored values; native 20m; no reflectance scaling applied')
     ds.update_tags(value_interpretation='source stored values; no reflectance scale applied',processing='native 20m grid warp; conservative SCL mask; no index/classification')
    rec['sha256']=sha256(p); rec['bytes']=p.stat().st_size
 savej(S2,s2)
 # Inspect all actual Phase 6B GeoTIFFs, including scene rasters, masks, and selected band outputs.
 qc=[]
 for p in sorted(OUT.rglob('*.tif')):
  with rasterio.open(p) as ds:
   bands=[]
   for i in range(1,ds.count+1):
    a=ds.read(i,masked=True)
    vals=np.asarray(a.compressed())
    raw=np.asarray(a.data)
    bands.append({'index':i,'description':ds.descriptions[i-1],'dtype':ds.dtypes[i-1],
      'valid_pixels':int(vals.size),'nodata_pixels':int(raw.size-vals.size),
      'nan_pixels':int(np.isnan(raw).sum()) if np.issubdtype(raw.dtype,np.floating) else 0,
      'infinite_pixels':int(np.isinf(raw).sum()) if np.issubdtype(raw.dtype,np.floating) else 0,
      'min':float(vals.min()) if vals.size else None,'p02':pct(vals,2),'median':pct(vals,50),'p98':pct(vals,98),'max':float(vals.max()) if vals.size else None})
   qc.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha256(p),'bytes':p.stat().st_size,
    'crs':str(ds.crs),'transform':list(ds.transform),'bounds':list(ds.bounds),'width':ds.width,'height':ds.height,
    'resolution_m':list(ds.res),'count':ds.count,'nodata':ds.nodata,'dtype':ds.dtypes[0],
    'band_descriptions':list(ds.descriptions),'bands':bands,'tags':ds.tags()})
 qc_manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'all GeoTIFFs under data/gherproof/regional/processed/phase6b','inspection':'Rasterio local open, geospatial metadata, valid/nodata/NaN/infinite counts, min/p02/median/p98/max, SHA-256','raster_count':len(qc),'rasters':qc}
 savej(MAN/'phase6b_raster_qc_manifest.json',qc_manifest)
 # Read each raster manifest summary without mutating catalogue outputs.
 aoi_pixels=s1['grid']['aoi_pixels']; scene_rows=[]
 for row in s1['scenes']:
  ras={x['asset_key']:x for x in row.get('asset_records',[])}
  scene_rows.append({'item_id':row['item_id'],'date':row.get('item_metadata',{}).get('datetime',row.get('catalogue_summary',{}).get('datetime')),'relative_orbit':row.get('item_metadata',{}).get('sat:relative_orbit',row.get('catalogue_summary',{}).get('relative_orbit')),'direction':row.get('item_metadata',{}).get('sat:orbit_state',row.get('catalogue_summary',{}).get('orbit_direction')),'status':row.get('status'),'vv_fraction':ras.get('vv',{}).get('stats',{}).get('valid_fraction_of_aoi'),'vh_fraction':ras.get('vh',{}).get('stats',{}).get('valid_fraction_of_aoi'),'vv_record':ras.get('vv'),'vh_record':ras.get('vh'),'product':row.get('analysis_product')})
 # Recover per-scene spatial cell support from the saved clips and the provisional AOI polygon.
 gj=json.loads((ROOT/'data/gherproof/regional/six_village_regional_search_extent.geojson').read_text(encoding='utf-8'))
 geoms=[f['geometry'] for f in gj.get('features',[]) if f.get('geometry')] if gj.get('type')=='FeatureCollection' else [gj.get('geometry',gj)]
 for r in scene_rows:
  if not r.get('product'): continue
  p=ROOT/r['product']['path']
  with rasterio.open(p) as ds:
   projected=[transform_geom('EPSG:4326',ds.crs,g,precision=8) for g in geoms]
   inside=geometry_mask(projected,out_shape=(ds.height,ds.width),transform=ds.transform,invert=True)
   arrays=ds.read(masked=True); valid=inside.copy()
   for bi in range(ds.count): valid &= ~np.ma.getmaskarray(arrays[bi]) & np.isfinite(arrays[bi].data)
   cells=[]
   for iy in range(4):
    for ix in range(4):
     y0,y1=iy*ds.height//4,(iy+1)*ds.height//4; x0,x1=ix*ds.width//4,(ix+1)*ds.width//4
     n=int(inside[y0:y1,x0:x1].sum()); good=int(valid[y0:y1,x0:x1].sum())
     cells.append({'row':iy,'column':ix,'aoi_pixels':n,'valid_pixels':good,'valid_fraction':good/max(n,1)})
   r['grid_cells_4x4']=cells
  src_row=next(x for x in s1['scenes'] if x['item_id']==r['item_id']); src_row['scene_raster_qc']={'status':'raster_verified','grid_cells_4x4':cells}
 savej(S1,s1)
 s2rows=[]
 for r in s2['items']:
  m=r.get('scl_asset',{}); meta=r.get('item_metadata',{})
  s2rows.append({'item_id':r['item_id'],'date':meta.get('datetime'),'platform':meta.get('platform'),'relative_orbit':meta.get('sat:relative_orbit'),'direction':meta.get('sat:orbit_state'),'baseline':meta.get('s2:processing_baseline'),'status':r['status'],'clear_pixels':m.get('clear_pixels'),'aoi_pixels':m.get('aoi_pixels'),'clear_fraction':m.get('clear_fraction_of_aoi'),'class_counts':m.get('pixel_class_counts_in_aoi'),'scl_record':m,'l2a_product':r.get('l2a_stored_values_product'),'l2a_b11':r.get('l2a_stored_values_20m')})
 # Additive references on original Phase 6 catalogue manifests.
 p=MAN/'phase6_sentinel1_regional_manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['phase6b_pixel_validation']={'manifest':'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json','raster_qc_manifest':'data/gherproof/manifests/phase6b_raster_qc_manifest.json','catalogue_candidates':len(scene_rows),'pixel_verified_complete_scenes':sum(x['status']=='raster_verified' for x in scene_rows),'partial_or_failed_scenes':sum(x['status']!='raster_verified' for x in scene_rows),'pixel_validated_pairs':len(s1['pairs'])}; savej(p,d)
 p=MAN/'phase6_sentinel2_regional_manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['phase6b_pixel_validation']={'manifest':'data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json','raster_qc_manifest':'data/gherproof/manifests/phase6b_raster_qc_manifest.json','catalogue_candidates':len(s2rows),'scl_pixel_verified_scenes':sum(x['status']=='raster_verified_scl' for x in s2rows),'same_tile_orbit_pre_post_pairs':len(s2['pairs']),'selected_pair':s2.get('selected_pair')}; savej(p,d)
 p=MAN/'phase6_regional_valid_coverage.json'; d=json.loads(p.read_text(encoding='utf-8')); d['phase6b_pixel_validation']={'sentinel1_manifest':'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json','sentinel2_manifest':'data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json','raster_qc_manifest':'data/gherproof/manifests/phase6b_raster_qc_manifest.json','aoi_status':s1.get('aoi_status'),'sentinel1_complete_scenes':sum(x['status']=='raster_verified' for x in scene_rows),'sentinel1_partial_scene_ids':[x['item_id'] for x in scene_rows if x['status']!='raster_verified'],'sentinel1_pairs':[{'pre_date':x['pre_date'],'post_date':x['post_date'],'relative_orbit':x['relative_orbit'],'direction':x['orbit_direction'],'common_valid_fraction':x['common_valid_fraction_of_aoi'],'area_km2':x['common_valid_area_km2']} for x in s1['pairs']],'sentinel2_scl_verified_scenes':len(s2rows),'sentinel2_selected_pair':s2.get('selected_pair'),'limitations':['regional AOI is provisional bbox, not official village geometry','no event inference or village-specific claim','remote product completeness does not establish water presence or cause']}; savej(p,d)
 # Temporal coverage chart + 4x4 pixel-grid coverage matrix figure.
 figdir=OUT/'figures'; figdir.mkdir(parents=True,exist_ok=True)
 # Build a local pixel-availability map from the actual joint S1 masks and S2 clear masks.
 map_specs=[]
 for pair in s1['pairs']:
  r=pair['coverage_raster']; map_specs.append((f"S1 {pair['pre_date']} / {pair['post_date']} r{pair['relative_orbit']} {pair['orbit_direction']}",ROOT/r['path'],'pair'))
 for r in scene_rows:
  if r['status']=='raster_verified' and r['date'][:10] not in [p['pre_date'] for p in s1['pairs']]+[p['post_date'] for p in s1['pairs']]:
   p=ROOT/r['product']['path']; map_specs.append((f"S1 {r['date'][:10]} r{r['relative_orbit']} ({r['status']})",p,'s1product'))
 selected=s2.get('selected_pair') or {}
 for ident,tag in [(selected.get('pre_item_id'),'pre'),(selected.get('post_item_id'),'post')]:
  row=next((x for x in s2['items'] if x['item_id']==ident),None)
  if row and row.get('scl_asset',{}).get('products'):
   rec=row['scl_asset']['products'][1]; map_specs.append((f"S2 {row['item_metadata']['datetime'][:10]} {tag} SCL clear",ROOT/rec['path'],'s2mask'))
 mw,mh=1500,930; mmap=Image.new('RGB',(mw,mh),'white'); md=ImageDraw.Draw(mmap); md.text((35,18),'Actual per-pixel data support (green = usable under stated mask; gray = invalid/unknown)',fill='#10243a',font=font)
 panelw,panelh=480,245
 for i,(label,path,kind) in enumerate(map_specs[:8]):
  c=i%3; r=i//3; x=20+c*500; y=55+r*280; md.text((x,y),label,fill='#222',font=font)
  with rasterio.open(path) as ds:
   if kind=='pair':
    a=ds.read(1); valid=(a==1); inside=(a!=255)
   elif kind=='s2mask':
    a=ds.read(1); valid=(a==1); inside=(a!=255)
   else:
    a=ds.read(1,masked=True)
    projected=[transform_geom('EPSG:4326',ds.crs,g,precision=8) for g in geoms]
    inside=geometry_mask(projected,out_shape=(ds.height,ds.width),transform=ds.transform,invert=True)
    valid=inside & ~np.ma.getmaskarray(a) & np.isfinite(a.data)
   small_v=np.asarray(Image.fromarray(valid.astype('uint8')).resize((panelw,panelh),Image.Resampling.NEAREST))>0
   small_i=np.asarray(Image.fromarray(inside.astype('uint8')).resize((panelw,panelh),Image.Resampling.NEAREST))>0
   rgb=np.full((panelh,panelw,3),255,dtype='uint8'); rgb[small_i]=[190,198,205]; rgb[small_v]=[52,154,96]
   rgbimg=Image.fromarray(rgb); mmap.paste(rgbimg,(x,y+20)); md.rectangle((x,y+20,x+panelw,y+20+panelh),outline='#35495a')
   try:
    frac=float(valid.sum()/max(inside.sum(),1)); md.text((x+4,y+panelh+22),f"{ds.crs}; {ds.res[0]:g} m; inside-grid valid {frac:.3%}",fill='#333',font=font)
   except Exception: pass
 md.text((22,900),'Provisional rectangular regional search AOI only; no village or enclosure boundaries are represented.',fill='#704b16',font=font)
 mappng=figdir/'phase6b_pixel_validity_maps.png'; mmap.save(mappng)
 W,H=1500,860; im=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(im)
 dr.text((45,20),'Phase 6B — per-acquisition valid-data coverage (no temporal interpolation)',fill='#10243a',font=font)
 # Chart area
 x0,y0,x1,y1=100,80,1430,420
 for val in (0,25,50,75,100):
  y=y1-int((y1-y0)*val/100); dr.line((x0,y,x1,y),fill='#dce3ea',width=1); dr.text((45,y-5),f'{val}%',fill='#333',font=font)
 dates=sorted(set([str(x['date'])[:10] for x in scene_rows if x['date']]+[str(x['date'])[:10] for x in s2rows if x['date']]))
 def xpos(date):
  idx=dates.index(date); return x0+int((x1-x0)*idx/max(len(dates)-1,1))
 for i,date in enumerate(dates):
  x=xpos(date); dr.line((x,y1,x,y1+4),fill='#555'); dr.text((x-18,y1+12),date[5:],fill='#333',font=font)
 colors={'S1 VV':'#005f9e','S1 VH':'#e67817','S2 clear SCL':'#248a52'}
 series=[]
 for label,key,color in [('S1 VV','vv_fraction',colors['S1 VV']),('S1 VH','vh_fraction',colors['S1 VH'])]:
  pts=[]
  for r in scene_rows:
   if r['date'] and r[key] is not None: pts.append((xpos(str(r['date'])[:10]),y1-int((y1-y0)*r[key])))
  dx=-5 if label=='S1 VV' else 5
  for x,y in pts: dr.ellipse((x+dx-5,y-5,x+dx+5,y+5),fill=color)
  series.append((label,color))
 pts=[]
 for r in s2rows:
  if r['date'] and r['clear_fraction'] is not None: pts.append((xpos(str(r['date'])[:10]),y1-int((y1-y0)*r['clear_fraction'])))
 for x,y in pts: dr.rectangle((x-4,y-4,x+4,y+4),fill=colors['S2 clear SCL'])
 # legend
 lx=100
 for label,color in series+[('S2 clear SCL',colors['S2 clear SCL'])]:
  dr.line((lx,455,lx+24,455),fill=color,width=4); dr.text((lx+31,448),label,fill='#222',font=font); lx+=200
 dr.text((100,485),'Valid fraction of provisional AOI. Points are independent acquisitions; orbit groups are not joined or pooled.',fill='#333',font=font)
 # Four by four heatmap panel per candidate group: charts show spatial support; blank means incomplete/not available.
 labels=[('S1 '+r['date'][:10]+' r'+str(r['relative_orbit']),r.get('vv_record',{}).get('stats',{}).get('grid_cells_4x4')) for r in scene_rows if r.get('date')]
 # S1 records have each band's cell summary; use VV cells first.
 labels=[]
 for r in scene_rows:
  cells=r.get('grid_cells_4x4')
  labels.append(('S1 '+str(r['date'])[:10]+' r'+str(r['relative_orbit']),cells))
 for r in s2rows:
  labels.append(('S2 '+str(r['date'])[:10],r.get('scl_record',{}).get('clear_grid_cells_4x4')))
 start_y=525; cellw=150; cellh=105; gapx=25; gapy=16
 for i,(label,cells) in enumerate(labels):
  col=i%7; row=i//7; bx=40+col*(cellw+gapx); by=start_y+row*(cellh+gapy)
  dr.text((bx,by),label,fill='#222',font=font)
  vals=[c.get('valid_fraction') for c in (cells or [])]
  for j in range(16):
   xx=bx+(j%4)*23; yy=by+18+(j//4)*18; v=vals[j] if j<len(vals) and vals[j] is not None else 0
   # White-to-green scale; red outline denotes <90%; gray denotes absent.
   if j>=len(vals): fill='#b7bec6'
   else: fill=(int(245-90*v),int(245-40*v),int(245-120*v))
   dr.rectangle((xx,yy,xx+20,yy+15),fill=fill,outline='#555' if j>=len(vals) or v<.9 else '#fff')
 covpng=figdir/'phase6b_candidate_coverage.png'; im.save(covpng)
 coverage={'created_at_utc':datetime.now(timezone.utc).isoformat(),'aoi':{'status':s1['aoi_status'],'grid_epsg':s1['grid']['crs'],'s1_resolution_m':s1['grid']['resolution_m'],'s1_width':s1['grid']['width'],'s1_height':s1['grid']['height'],'s1_aoi_pixels':aoi_pixels,'s1_area_km2':aoi_pixels*100/1e6,'s2_grid_epsg':s2['grid']['crs'],'s2_resolution_m':s2['grid']['resolution_m'],'s2_width':s2['grid']['width'],'s2_height':s2['grid']['height'],'s2_aoi_pixels':s2['grid']['aoi_pixels'],'s2_area_km2':s2['grid']['aoi_pixels']*400/1e6},'sentinel1_scenes':[{k:v for k,v in r.items() if k not in ['vv_record','vh_record','product']} for r in scene_rows],'sentinel1_pairs':[{'pair_id':r['pair_id'],'pre_date':r['pre_date'],'post_date':r['post_date'],'relative_orbit':r['relative_orbit'],'direction':r['orbit_direction'],'common_valid_pixels':r['common_valid_pixels_all_four'],'common_valid_fraction':r['common_valid_fraction_of_aoi'],'common_valid_area_km2':r['common_valid_area_km2'],'coverage_raster':r['coverage_raster']} for r in s1['pairs']],'sentinel2_scenes':[{k:v for k,v in r.items() if k not in ['scl_record','l2a_product','l2a_b11']} for r in s2rows],'sentinel2_selected_pair':s2.get('selected_pair'),'figures':[covpng.relative_to(ROOT).as_posix(),mappng.relative_to(ROOT).as_posix()]}
 savej(MAN/'phase6b_regional_coverage_assessment.json',coverage)
 print(json.dumps({'raster_qc_count':len(qc),'s1_complete':sum(x['status']=='raster_verified' for x in scene_rows),'s1_partial':sum(x['status']!='raster_verified' for x in scene_rows),'s1_pairs':len(s1['pairs']),'s2_scl_verified':sum(x['status']=='raster_verified_scl' for x in s2rows),'s2_pairs':len(s2['pairs']),'s2_selected':s2.get('selected_pair'),'coverage_figure':covpng.relative_to(ROOT).as_posix()},indent=2))
if __name__=='__main__': main()
