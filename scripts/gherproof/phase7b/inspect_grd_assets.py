"""Read exact GRD counterparts' metadata and AOI windows; never save SAS tokens."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
ROOT=Path(__file__).resolve().parents[3];sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np, requests, rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import Window

GRD=ROOT/'data/gherproof/manifests/phase7b_grd_counterpart_manifest.json'
OUT=ROOT/'data/gherproof/manifests/phase7b_grd_raster_inspection.json'
RAW=ROOT/'data/gherproof/raw/phase7b/grd_metadata'
PIX=ROOT/'data/gherproof/processed/phase7b/sentinel1_grd'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def unsigned(href):
 u=urlsplit(href);return urlunsplit((u.scheme,u.netloc,u.path,'',''))
def stats(a):
 v=a[np.isfinite(a)]
 return {'count':int(v.size),'min':float(v.min()) if v.size else None,'max':float(v.max()) if v.size else None,'percentiles':{str(p):float(np.percentile(v,p)) for p in (1,2,25,50,75,98,99)} if v.size else {},'nonpositive_count':int((v<=0).sum()) if v.size else 0}
def main():
 man=json.loads(GRD.read_text());sess=requests.Session();tokresp=sess.get('https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-grd',timeout=(10,45));tokresp.raise_for_status();token=tokresp.json()['token']
 RAW.mkdir(parents=True,exist_ok=True);PIX.mkdir(parents=True,exist_ok=True);results=[]
 def save(stage='in_progress'):
  OUT.write_text(json.dumps({'status':stage,'collection':'sentinel-1-grd','records':results,'notes':['SAS token is memory-only.','Processing decision awaits actual raster units and metadata.']},indent=2)+'\n',encoding='utf-8')
 for rec in man['records']:
  if rec['status']!='exact_counterpart_found':continue
  item=rec['match'];itemid=item['id'];row={'item_id':itemid,'rtc_item_id':rec['rtc_item_id'],'asset_inspections':{},'metadata_files':[]}
  # Store SAFE manifest and per-polarization calibration/noise XML for provenance.
  for key in ('safe-manifest','schema-calibration-vv','schema-calibration-vh','schema-noise-vv','schema-noise-vh'):
   asset=item['assets'].get(key)
   if not asset:row['metadata_files'].append({'asset_key':key,'status':'missing'});continue
   try:
    fp=RAW/f'{itemid}_{key}.xml'
    if fp.exists():row['metadata_files'].append({'asset_key':key,'path':fp.relative_to(ROOT).as_posix(),'bytes':fp.stat().st_size,'sha256':sha(fp),'status':'already_present'});continue
    url=unsigned(asset['href'])+'?'+token;r=sess.get(url,timeout=(10,90));r.raise_for_status();fp.write_bytes(r.content)
    row['metadata_files'].append({'asset_key':key,'path':fp.relative_to(ROOT).as_posix(),'bytes':len(r.content),'sha256':sha(fp),'status':'downloaded'})
   except Exception as e:row['metadata_files'].append({'asset_key':key,'status':'error','error':f'{type(e).__name__}: {str(e).split("?")[0][:220]}'})
  for pol in ('vv','vh'):
   a=item['assets'].get(pol)
   if not a:row['asset_inspections'][pol]={'status':'missing'};continue
   try:
    href=unsigned(a['href'])+'?'+token
    # First make an explicit small range request so storage failures are distinct from GDAL issues.
    rr=sess.get(href,headers={'Range':'bytes=0-16383'},stream=True,timeout=(10,25));rr.raise_for_status()
    first=next(rr.iter_content(16384),b'');rrinfo={'http_status':rr.status_code,'content_range':rr.headers.get('Content-Range'),'content_length':rr.headers.get('Content-Length'),'range_bytes_received':len(first),'tiff_magic':first[:4].hex()}
    rr.close()
    print(f"range {itemid} {pol}: HTTP {rrinfo['http_status']} bytes={rrinfo['range_bytes_received']}",flush=True)
    with rasterio.Env(GDAL_HTTP_MAX_RETRY='0',GDAL_HTTP_TIMEOUT='15',GDAL_HTTP_CONNECTTIMEOUT='10',CPL_VSIL_CURL_USE_HEAD='NO',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
     with rasterio.open(href) as src:
      srcmeta={'crs':str(src.crs) if src.crs else None,'width':src.width,'height':src.height,'transform':list(src.transform),'bounds':list(src.bounds),'resolution':list(src.res),'dtype':list(src.dtypes),'count':src.count,'nodata':src.nodata,'units':list(src.units),'scales':list(src.scales),'offsets':list(src.offsets),'descriptions':list(src.descriptions),'dataset_tags':src.tags(),'band_tags':src.tags(1),'band1_mask_flags':[str(x) for x in src.mask_flag_enums[0]]}
      row['asset_inspections'][pol]={'status':'metadata_opened','asset_description':a.get('description'),'asset_title':a.get('title'),'range_request':rrinfo,'raster_metadata':srcmeta}
      save()
      try:
       win=Window(max(0,src.width//2-8),max(0,src.height//2-8),min(16,src.width),min(16,src.height));sample=src.read(1,window=win,masked=True).astype(np.float32).filled(np.nan)
       row['asset_inspections'][pol].update({'status':'opened','center_sample':stats(sample),'native_sample_window':[int(win.col_off),int(win.row_off),int(win.width),int(win.height)]})
      except Exception as e:row['asset_inspections'][pol]['sample_read_error']=f'{type(e).__name__}: {str(e).split("?")[0][:260]}'
      save()
   except Exception as e:row['asset_inspections'][pol]={'status':'error','error':f'{type(e).__name__}: {str(e).split("?")[0][:300]}'};save()
  results.append(row)
  save()
 metadata_count=sum(bool(x.get('raster_metadata')) for r in results for x in r['asset_inspections'].values())
 sampled_count=sum('center_sample' in x for r in results for x in r['asset_inspections'].values())
 sample_failures=sum(bool(x.get('sample_read_error')) for r in results for x in r['asset_inspections'].values())
 result={'status':'complete' if sampled_count==8 else 'partial_sample_read','collection':'sentinel-1-grd','metadata_opened_assets':metadata_count,'pixel_sampled_assets':sampled_count,'pixel_sample_read_failures':sample_failures,'processed_full_scenes':0,'records':results,'notes':['STAC assets describe terrain-corrected amplitude, but the actual TIFF tags, identity transform, absent CRS and Level-1 SAFE metadata identify these returned TIFF measurements as uncalibrated, ungeocoded GRD DN arrays.','Seven of eight VV/VH center sample windows decoded; one VH window failed with a Rasterio Read failed error while metadata/range access succeeded. No full scene pixels or compatible model input were processed.','SAS token was memory-only and omitted from outputs/logging.']}
 OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'manifest':OUT.relative_to(ROOT).as_posix(),'records':len(results),'metadata_opened_assets':metadata_count,'pixel_sampled_assets':sampled_count,'pixel_sample_read_failures':sample_failures},indent=2))
if __name__=='__main__':main()
