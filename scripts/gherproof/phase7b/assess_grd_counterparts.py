"""Find same-acquisition Sentinel-1 GRD items for the four Phase 7 RTC scenes.

Only public STAC metadata is queried. Asset URLs are written without query strings;
no asset is downloaded by this discovery script.
"""
from __future__ import annotations
import json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[3]
RTC=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json'
OUT=ROOT/'data/gherproof/manifests/phase7b_grd_counterpart_manifest.json'
API='https://planetarycomputer.microsoft.com/api/stac/v1'
COLLECTION='sentinel-1-grd'
AOI=ROOT/'data/gherproof/regional/six_village_regional_search_extent.geojson'

def clean_href(href):
 return href.split('?',1)[0] if href else None
def props(item):
 p=item.get('properties',{})
 return {k:p.get(k) for k in ('datetime','start_datetime','end_datetime','platform','sat:relative_orbit','sat:orbit_state','sar:instrument_mode','sar:polarizations','sar:frequency_band','s1:product_type','s1:processing_level','s1:resolution_meters','s1:mission_data_take_id','s1:instrument_configuration_id')}
def summarize(item):
 assets={}
 for key,a in item.get('assets',{}).items():
  assets[key]={'href':clean_href(a.get('href')),'type':a.get('type'),'roles':a.get('roles'),'title':a.get('title'),'description':a.get('description'),'file:size':a.get('file:size'),'raster:bands':a.get('raster:bands'),'proj:shape':a.get('proj:shape'),'proj:transform':a.get('proj:transform'),'proj:epsg':a.get('proj:epsg')}
 return {'id':item.get('id'),'collection':item.get('collection'),'bbox':item.get('bbox'),'geometry':item.get('geometry'),'properties':props(item),'assets':assets,'links':[{'rel':x.get('rel'),'href':clean_href(x.get('href'))} for x in item.get('links',[]) if x.get('rel') in ('self','collection')]}
def exact_metadata_match(rtc,item):
 a=rtc.get('properties',rtc);b=item.get('properties',{})
 return (b.get('datetime')==a.get('datetime') and b.get('platform')==a.get('platform') and b.get('sat:relative_orbit')==a.get('sat:relative_orbit') and b.get('sat:orbit_state')==a.get('sat:orbit_state') and b.get('sar:instrument_mode')==a.get('sar:instrument_mode') and b.get('sar:polarizations')==a.get('sar:polarizations'))
def main():
 rtc=json.loads(RTC.read_text(encoding='utf-8')); aoi=json.loads(AOI.read_text(encoding='utf-8'))['features'][0]['geometry']
 scenes=[x for x in rtc['scenes'] if x.get('status')=='raster_verified' and x.get('analysis_product')]
 # Exact Phase 7 model inputs only; partial Jan 7 remains out of scope.
 wanted={p[k] for p in rtc['pairs'] for k in ('pre_item_id','post_item_id')}
 scenes=[x for x in scenes if x['item_id'] in wanted]
 sess=requests.Session(); records=[]
 for scene in scenes:
  rtc_id=scene['item_id']; grd_id=re.sub(r'_rtc$','',rtc_id); meta=scene['item_metadata']; ts=datetime.fromisoformat(meta['datetime'].replace('Z','+00:00'))
  target={'rtc_item_id':rtc_id,'target_grd_item_id':grd_id,'rtc_datetime':meta.get('datetime'),'platform':meta.get('platform'),'relative_orbit':meta.get('sat:relative_orbit'),'orbit_direction':meta.get('sat:orbit_state'),'instrument_mode':meta.get('sar:instrument_mode'),'polarizations':meta.get('sar:polarizations'),'status':'not_found','match_method':None,'candidates':[]}
  item=None
  try:
   r=sess.get(f'{API}/collections/{COLLECTION}/items/{grd_id}',timeout=(10,45))
   if r.status_code==200:
    candidate=r.json(); cp=candidate.get('properties',{})
    if exact_metadata_match(meta,candidate):
     item=candidate;target['match_method']='exact product scene identifier plus platform/orbit/mode'
  except requests.RequestException as e:
   target['direct_lookup_error']=f'{type(e).__name__}: {str(e)[:220]}'
  if item is None:
   lo=(ts-timedelta(seconds=75)).isoformat().replace('+00:00','Z');hi=(ts+timedelta(seconds=75)).isoformat().replace('+00:00','Z')
   body={'collections':[COLLECTION],'intersects':aoi,'datetime':f'{lo}/{hi}','limit':100}
   try:
    r=sess.post(f'{API}/search',json=body,timeout=(10,60));r.raise_for_status()
    candidates=r.json().get('features',[])
    for c in candidates:
     pp=c.get('properties',{});dt=pp.get('datetime');delta=abs((datetime.fromisoformat(dt.replace('Z','+00:00'))-ts).total_seconds()) if dt else None
     target['candidates'].append({'id':c.get('id'),'datetime':dt,'seconds_from_rtc':delta,'platform':pp.get('platform'),'relative_orbit':pp.get('sat:relative_orbit'),'direction':pp.get('sat:orbit_state'),'mode':pp.get('sar:instrument_mode'),'polarizations':pp.get('sar:polarizations')})
    exact=[c for c in candidates if c.get('id')==grd_id and exact_metadata_match(meta,c)]
    if exact:item=exact[0];target['match_method']='STAC search exact product scene identifier'
    else:
     strict=[c for c in candidates if c.get('properties',{}).get('platform')==meta.get('platform') and c.get('properties',{}).get('sat:relative_orbit')==meta.get('sat:relative_orbit') and c.get('properties',{}).get('sat:orbit_state')==meta.get('sat:orbit_state') and c.get('properties',{}).get('sar:instrument_mode')==meta.get('sar:instrument_mode') and c.get('properties',{}).get('sar:polarizations')==meta.get('sar:polarizations') and c.get('properties',{}).get('datetime')==meta.get('datetime')]
     if len(strict)==1:item=strict[0];target['match_method']='unique exact datetime/platform/orbit/direction/mode/polarization spatial candidate'
   except requests.RequestException as e:
    target['search_error']=f'{type(e).__name__}: {str(e)[:220]}'
  if item:
   rec=summarize(item); props_grd=rec['properties']; assets=rec['assets'];
   polkeys={k.lower() for k in assets}
   hasvv='vv' in polkeys;hasvh='vh' in polkeys
   target.update({'status':'exact_counterpart_found','match':rec,'vv_asset_present':hasvv,'vh_asset_present':hasvh,'dual_pol_asset_check':'pass' if hasvv and hasvh else 'incomplete','datetime_exact':props_grd.get('datetime')==meta.get('datetime'),'relative_orbit_exact':props_grd.get('sat:relative_orbit')==meta.get('sat:relative_orbit'),'direction_exact':props_grd.get('sat:orbit_state')==meta.get('sat:orbit_state'),'mode_exact':props_grd.get('sar:instrument_mode')==meta.get('sar:instrument_mode')})
  records.append(target)
 result={'status':'complete' if len(records)==len(wanted) else 'partial','provider':'Microsoft Planetary Computer public STAC API','collection':COLLECTION,'query':'Exact RTC-derived source scene ID; fallback AOI-intersecting STAC search within ±75 seconds, then strict exact metadata match.','created_at_utc':datetime.now(timezone.utc).isoformat(),'scene_count':len(records),'records':records,'limitations':['This script searches exact sensing acquisitions only; nearby-date substitutions are never labeled exact.','A STAC item/asset record alone is not a verified local raster or model-domain comparison.','Asset href query components are stripped before persistence.']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'manifest':OUT.relative_to(ROOT).as_posix(),'records':len(records),'found':sum(r['status']=='exact_counterpart_found' for r in records),'errors':sum(bool(r.get('search_error') or r.get('direct_lookup_error')) for r in records)},indent=2))
if __name__=='__main__':main()
