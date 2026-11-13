"""Compute coverage of the new provisional regional AOI by existing local rasters."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from shapely.geometry import mapping
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/gherproof/phase6'))
from regional_discovery import REGION,AOIS,build_grid,NODATA,now,save
GRID=build_grid(REGION); OUT=ROOT/'data/gherproof/regional/processed/sentinel1'; OUT.mkdir(parents=True,exist_ok=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 day_masks={}; asset_rows=[]
 for day in ('2026-01-07','2026-01-19'):
  p=ROOT/f'data/gherproof/processed/sentinel1/planetary_computer/{day}_sentinel1_rtc_vv_vh_10m_utm45n.tif'
  with rasterio.open(p) as src:
   if src.count<2 or src.crs is None: raise RuntimeError(f'Unexpected source raster structure: {p.name}')
   arrs=[]
   for b in (1,2):
    with WarpedVRT(src,crs=GRID['crs'],transform=GRID['transform'],width=GRID['width'],height=GRID['height'],resampling=Resampling.nearest,nodata=src.nodata,src_nodata=src.nodata) as vrt:
     a=vrt.read(b,masked=True,out_dtype='float32')
    vals=a.data; valid=(~np.ma.getmaskarray(a))&np.isfinite(vals)&(vals!=src.nodata)&GRID['mask']; arrs.append(valid)
    asset_rows.append({'date':day,'polarization':src.descriptions[b-1] or ('VV' if b==1 else 'VH'),'source_path':p.relative_to(ROOT).as_posix(),'source_crs':str(src.crs),'source_resolution_m':list(src.res),'source_bounds':list(src.bounds),'source_shape':[src.height,src.width],'source_nodata':src.nodata,'valid_pixels_in_provisional_region':int(valid.sum())})
   day_masks[day]=arrs[0]&arrs[1]
 common=GRID['mask']&day_masks['2026-01-07']&day_masks['2026-01-19']
 output=np.full((GRID['height'],GRID['width']),255,dtype='uint8'); output[GRID['mask']]=0; output[common]=1
 out=OUT/'existing_jan07_jan19_common_valid_coverage_10m_utm45n.tif'
 with rasterio.open(out,'w',driver='GTiff',height=GRID['height'],width=GRID['width'],count=1,dtype='uint8',crs=GRID['crs'],transform=GRID['transform'],nodata=255,compress='deflate',tiled=True,blockxsize=256,blockysize=256) as dst:
  dst.write(output,1); dst.set_band_description(1,'common valid Sentinel-1 VV/VH pixels for Jan 7 and Jan 19 (1=valid, 0=missing/invalid, 255=outside AOI)'); dst.update_tags(aoi_status='provisional regional search extent; not six village boundaries',source='existing local Sentinel-1 RTC clips only; missing pixels mean unavailable/unvalidated, not non-water')
 # Simple exported coverage visualization; colors indicate data availability only.
 small=output[::max(1,GRID['height']//600),::max(1,GRID['width']//850)]; rgb=np.zeros((*small.shape,3),dtype='uint8'); rgb[:]=[224,229,232]; rgb[small==0]=[238,241,243]; rgb[small==1]=[16,135,148]; im=Image.fromarray(rgb).resize((900,620),Image.Resampling.NEAREST)
 canvas=Image.new('RGB',(1040,760),'white'); canvas.paste(im,(90,75)); draw=ImageDraw.Draw(canvas); draw.text((90,20),'Jan 7 / Jan 19 Sentinel-1 common valid coverage',fill='#18333f'); draw.rectangle((90,75,990,695),outline='#2c414b',width=2)
 draw.rectangle((105,715,125,735),fill=(16,135,148)); draw.text((133,716),'Common VV/VH valid pixels',fill='#18333f'); draw.rectangle((410,715,430,735),fill=(238,241,243),outline='#536670'); draw.text((438,716),'No local clip or invalid data (unknown)',fill='#18333f'); draw.text((90,744),'Provisional ~650 km² envelope; no village boundaries shown. CRS: EPSG:32645.',fill='#536670')
 preview=ROOT/'data/gherproof/regional/phase6_existing_s1_coverage.png'; canvas.save(preview)
 stats={'created_at_utc':now(),'aoi_bbox_wgs84':list(REGION.bounds),'grid':{'crs':GRID['crs'],'resolution_m':10,'width':GRID['width'],'height':GRID['height'],'aoi_pixels':int(GRID['mask'].sum())},'existing_jan07_jan19':{'assets':asset_rows,'common_valid_pixels':int(common.sum()),'common_valid_area_km2':round(int(common.sum())*100/1e6,4),'fraction_of_provisional_aoi':float(common.sum()/max(1,GRID['mask'].sum())),'coverage_raster':out.relative_to(ROOT).as_posix(),'coverage_raster_sha256':sha(out),'coverage_preview':preview.relative_to(ROOT).as_posix(),'interpretation':'only locally clipped January 7/19 assets were evaluated; all pixels outside their local clips remain unvalidated'},'reporting_sectors':[],'limitations':['No official or source-verified village polygons were found for spatial per-village coverage.','West/east reporting sectors are provisional search polygons and must not be interpreted as upazila or village boundaries.','No no-data pixel is classified as dry land.']}
 # Provisional context subareas are disjoint longitude slices to report broad locality-group support only.
 from shapely.geometry import box
 for name,geom in [('western_provisional_reporting_sector',box(89.24,22.92,89.39,23.11)),('eastern_provisional_reporting_sector',box(89.39,22.92,89.54,23.11))]:
  gm=transform_geom('EPSG:4326',GRID['crs'],mapping(geom)); inside=geometry_mask([gm],out_shape=(GRID['height'],GRID['width']),transform=GRID['transform'],invert=True)&GRID['mask']; n=int((common&inside).sum()); total=int(inside.sum())
  stats['reporting_sectors'].append({'name':name,'status':'provisional search context only','aoi_pixels':total,'common_jan07_jan19_valid_pixels':n,'common_valid_area_km2':round(n*100/1e6,4),'fraction':n/max(total,1)})
 save(ROOT/'data/gherproof/manifests/phase6_regional_valid_coverage.json',stats)
 print(json.dumps({'common_valid_pixels':int(common.sum()),'aoi_pixels':int(GRID['mask'].sum()),'coverage_fraction':float(common.sum()/GRID['mask'].sum()),'coverage_km2':round(int(common.sum())*100/1e6,4),'reporting_sectors':stats['reporting_sectors'],'raster':out.as_posix()},indent=2))
if __name__=='__main__':main()
