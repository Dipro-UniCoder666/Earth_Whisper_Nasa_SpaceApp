"""Retrieve the exact SAFE XML metadata for the Phase 6B selected S2 pair.

Uses the saved Planetary Computer STAC item records and temporary SAS tokens.
SAS query strings are never written to disk or printed.
"""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

import requests

ROOT=Path(__file__).resolve().parents[3]
MAN=ROOT/'data/gherproof/manifests'
RAW=ROOT/'data/gherproof/raw/phase7/sentinel2_metadata'
STAC=ROOT/'data/gherproof/raw/phase6b/stac_items'
PC='https://planetarycomputer.microsoft.com/api'
COLLECTION='sentinel-2-l2a'
def noquery(url):
 p=urlsplit(url); return urlunsplit((p.scheme,p.netloc,p.path,'',''))
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def localname(tag): return tag.rsplit('}',1)[-1]
def xml_values(path):
 root=ET.parse(path).getroot(); out={}
 for e in root.iter():
  name=localname(e.tag)
  if name in {'PROCESSING_BASELINE','BOA_QUANTIFICATION_VALUE','QUANTIFICATION_VALUE','BOA_ADD_OFFSET'}:
   out.setdefault(name,[]).append({'value':e.text,'band_id':e.attrib.get('band_id')})
 return out
def safe_error(e):
 return re.sub(r'https?://[^\s?]+\?[^\s]+','[redacted signed URL]',str(e))[:300]
def main():
 s2=json.loads((MAN/'phase6b_sentinel2_pixel_validation.json').read_text(encoding='utf-8'))
 pair=s2['selected_pair']; items=[]
 for item_id in (pair['pre_item_id'],pair['post_item_id']):
  p=STAC/f'{COLLECTION}_{item_id}.json'
  if not p.is_file(): raise FileNotFoundError(f'Missing saved item metadata: {p}')
  item=json.loads(p.read_text(encoding='utf-8'))
  items.append(item)
 sess=requests.Session(); sess.headers.update({'User-Agent':'EarthWhisper-GherProof-Phase7/1.0'})
 tok=sess.get(f'{PC}/sas/v1/token/{COLLECTION}',timeout=(10,45)); tok.raise_for_status(); token=tok.json().get('token')
 if not token: raise RuntimeError('Planetary Computer SAS endpoint returned no token')
 records=[]
 for item in items:
  props=item['properties']; ident=item['id']; record={'item_id':ident,'datetime':props['datetime'],'platform':props.get('platform'),'baseline_stac':props.get('s2:processing_baseline'),'mgrs_tile':props.get('s2:mgrs_tile'),'metadata_assets':{}}
  for key in ('product-metadata','granule-metadata'):
   asset=item.get('assets',{}).get(key)
   if not asset or not asset.get('href'):
    record['metadata_assets'][key]={'status':'missing_from_stac'}; continue
   href=noquery(asset['href'])+'?'+token
   try:
    resp=sess.get(href,timeout=(10,60)); resp.raise_for_status()
    body=resp.content
    # Validate as XML before persisting; do not retain a provider HTML error response.
    ET.fromstring(body)
    name=ident+'_'+key.replace('-','_')+'.xml'; out=RAW/name; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(body)
    record['metadata_assets'][key]={'status':'downloaded','path':out.relative_to(ROOT).as_posix(),'bytes':len(body),'sha256':sha(out),'values':xml_values(out)}
   except Exception as e:
    record['metadata_assets'][key]={'status':'failed','error_type':type(e).__name__,'error':safe_error(e)}
  records.append(record)
 out={'created_at_utc':datetime.now(timezone.utc).isoformat(),'provider':'Microsoft Planetary Computer Sentinel-2 L2A SAFE metadata assets','selected_pair':{k:pair.get(k) for k in ('pre_item_id','pre_date','post_item_id','post_date','pre_platform','post_platform','pre_relative_orbit','post_relative_orbit','mgrs_tile','pre_baseline','post_baseline')},'scenes':records,'source_note':'Downloaded from each exact saved STAC item asset; any URLs in this manifest are unsigned and query-free.'}
 target=MAN/'phase7_sentinel2_radiometric_metadata.json'; tmp=target.with_suffix('.json.tmp'); tmp.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); tmp.replace(target)
 print(json.dumps({'manifest':target.relative_to(ROOT).as_posix(),'scenes':[{'item_id':r['item_id'],'assets':{k:v['status'] for k,v in r['metadata_assets'].items()}} for r in records]},indent=2))
if __name__=='__main__': main()
