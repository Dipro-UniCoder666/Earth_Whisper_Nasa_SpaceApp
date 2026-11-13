"""Create a blinded, spatially blocked optical-review sampling package.

No reference labels or model performance are generated. The GeoPackage labels
are blank; optical contexts contain no model overlays or model probabilities.
"""
from __future__ import annotations
import hashlib, html, json, math, random, sqlite3, struct
from datetime import datetime, timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import xy
from rasterio.warp import reproject
from rasterio.windows import Window
from PIL import Image, ImageDraw
from shapely.geometry import Point
from shapely import wkb

OPT=ROOT/'data/gherproof/manifests/phase7_optical_processing.json'
INF=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json'
S1=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json'
OUT=ROOT/'data/gherproof/reference/phase7b'
GPKG=OUT/'gherproof_optical_reference_samples.gpkg'
SEED=20261113; TARGET_PER_GROUP_STRATUM=15; BLOCK_M=5000.0; GUARD_M=1000.0
LABELS=('water','non_water','uncertain','invalid')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def arr(path):
 with rasterio.open(path) as ds:return ds.read(1,masked=True).filled(np.nan).astype(np.float32),ds.profile.copy()
def warp(a,srcprof,dstprof,resampling=Resampling.average):
 out=np.full((dstprof['height'],dstprof['width']),np.nan,np.float32)
 reproject(a,out,src_transform=srcprof['transform'],src_crs=srcprof['crs'],src_nodata=np.nan,dst_transform=dstprof['transform'],dst_crs=dstprof['crs'],dst_nodata=np.nan,resampling=resampling)
 return out
def gpkg_header(point,srs=32645):
 x,y=point.x,point.y; env=struct.pack('<4d',x,x,y,y); return b'GP'+bytes((0,3))+struct.pack('<i',srs)+env+wkb.dumps(point,big_endian=False)
def init_gpkg(path,wkt):
 if path.exists():path.unlink()
 con=sqlite3.connect(path);con.execute('PRAGMA application_id=1196444487');con.execute('PRAGMA user_version=10300')
 con.executescript('''CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT NOT NULL,srs_id INTEGER NOT NULL PRIMARY KEY,organization TEXT NOT NULL,organization_coordsys_id INTEGER NOT NULL,definition TEXT NOT NULL,description TEXT);
 CREATE TABLE gpkg_contents (table_name TEXT NOT NULL PRIMARY KEY,data_type TEXT NOT NULL,identifier TEXT UNIQUE,description TEXT DEFAULT '',last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),min_x DOUBLE,min_y DOUBLE,max_x DOUBLE,max_y DOUBLE,srs_id INTEGER);
 CREATE TABLE gpkg_geometry_columns (table_name TEXT NOT NULL,column_name TEXT NOT NULL,geometry_type_name TEXT NOT NULL,srs_id INTEGER NOT NULL,z TINYINT NOT NULL,m TINYINT NOT NULL,PRIMARY KEY (table_name,column_name));''')
 con.executemany('INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)', [('Undefined Cartesian SRS',-1,'NONE',-1,'undefined','undefined'),('Undefined geographic SRS',0,'NONE',0,'undefined','undefined'),('WGS 84 geodetic',4326,'EPSG',4326,'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]','EPSG reference'),('WGS 84 / UTM zone 45N',32645,'EPSG',32645,wkt,'EPSG reference')])
 cols=['fid INTEGER PRIMARY KEY AUTOINCREMENT','geom POINT NOT NULL','sample_id TEXT UNIQUE NOT NULL','sampling_stratum TEXT NOT NULL','spatial_block TEXT NOT NULL','split_group TEXT NOT NULL','x_utm REAL NOT NULL','y_utm REAL NOT NULL','inclusion_probability REAL NOT NULL','sample_weight REAL NOT NULL','pre_date TEXT NOT NULL','post_date TEXT NOT NULL','pre_scl INTEGER','post_scl INTEGER','pre_scl_clear INTEGER NOT NULL','post_scl_clear INTEGER NOT NULL','ndwi_pre REAL','ndwi_post REAL','mndwi_pre REAL','mndwi_post REAL','context_image TEXT NOT NULL','pre_label TEXT CHECK(pre_label IS NULL OR pre_label IN (\'water\',\'non_water\',\'uncertain\',\'invalid\'))','post_label TEXT CHECK(post_label IS NULL OR post_label IN (\'water\',\'non_water\',\'uncertain\',\'invalid\'))','pre_confidence TEXT CHECK(pre_confidence IS NULL OR pre_confidence IN (\'high\',\'medium\',\'low\'))','post_confidence TEXT CHECK(post_confidence IS NULL OR post_confidence IN (\'high\',\'medium\',\'low\'))','annotator TEXT','review_date TEXT','notes TEXT','label_source TEXT']
 con.execute('CREATE TABLE samples ('+','.join(cols)+')')
 con.execute("INSERT INTO gpkg_contents(table_name,data_type,identifier,description,srs_id) VALUES('samples','features','optical_reference_samples','Blinded optical reference annotation points; labels intentionally blank',32645)")
 con.execute("INSERT INTO gpkg_geometry_columns VALUES('samples','geom','POINT',32645,0,0)")
 return con
def load_inputs():
 opt=json.loads(OPT.read_text()); inf=json.loads(INF.read_text()); s1=json.loads(S1.read_text())
 bydate={x['date']:x for x in opt['scenes']}
 ndpre,pnd=arr(ROOT/bydate['2026-01-10']['ndwi']['path']); ndpost,_=arr(ROOT/bydate['2026-01-20']['ndwi']['path'])
 mpre,pm=arr(ROOT/bydate['2026-01-10']['mndwi']['path']); mpost,_=arr(ROOT/bydate['2026-01-20']['mndwi']['path'])
 ndpre20=warp(ndpre,pnd,pm);ndpost20=warp(ndpost,pnd,pm)
 # NDVI is derived from metadata-scaled 10 m reflectance, averaged to the same 20 m grid.
 bpre={};bpost={}
 for d,key in [('2026-01-10','pre'),('2026-01-20','post')]:
  scene=bydate[d];
  for b in ('B04','B08'):
   aa,pp=arr(ROOT/scene['bands'][b]['path']);
   if key=='pre':bpre[b],bp=aa,pp
   else:bpost[b]=aa
 ndvi_pre=(bpre['B08']-bpre['B04'])/(bpre['B08']+bpre['B04']+1e-8);ndvi_post=(bpost['B08']-bpost['B04'])/(bpost['B08']+bpost['B04']+1e-8)
 ndvi_pre20=warp(ndvi_pre,bp,pm);ndvi_post20=warp(ndvi_post,bp,pm)
 # exact SCL acquisition rasters, same B2 product items.
 itemids=[json.loads((ROOT/'data/gherproof/raw/phase6b/stac_items'/f"sentinel-2-l2a_{bydate[d]['item_id']}.json").read_text()) for d in ('2026-01-10','2026-01-20')]
 scl=[]
 for item in itemids:
  ident=item['id'];p=next((ROOT/'data/gherproof/regional/processed/phase6b/sentinel2/scl').glob(f'*{ident}*SCL_20m.tif'))
  with rasterio.open(p) as ds:scl.append((ds.read(1).astype(np.int16),ds.profile.copy()))
 # AOI common-valid raster from both same-geometry Phase 6B pairs; reproject to optical 20 m.
 pair=s1['pairs'][0]; cmask=s1['scenes'][0] if False else pair['coverage_raster']['path']
 with rasterio.open(ROOT/cmask) as ds: aoi=ds.read(1).astype(np.float32);ap=ds.profile.copy()
 valid=warp(aoi,ap,pm,Resampling.nearest)>0.5
 # mask out any optical invalids.
 valid &= np.isfinite(mpre)&np.isfinite(mpost)&np.isfinite(ndpre20)&np.isfinite(ndpost20)&np.isfinite(ndvi_pre20)&np.isfinite(ndvi_post20)
 model={}
 for k in ('scratch','pretrained'):
  records=[r for r in inf['scenes'] if r['model']==k]
  for d in ('2026-01-12','2026-01-24','2026-01-09','2026-01-21'):
   rec=next(x for x in records if x['date']==d);pp=ROOT/rec['probability']['path'];x,pr=arr(pp);model[(k,d)]=warp(x,pr,pm)
 # The union flags reflect separate same-acquisition model comparisons only; they do not
 # composite observations across viewing geometries into a single prediction.
 disagreement=np.zeros_like(valid)
 bothwater=np.zeros_like(disagreement)
 for date in ('2026-01-09','2026-01-12','2026-01-21','2026-01-24'):
  aa=model[('scratch',date)]>=.5;bb=model[('pretrained',date)]>=.5
  disagreement|=(aa!=bb);bothwater|=(aa&bb)
 scls=[s[0] for s in scl]
 mnd_delta=mpost-mpre;nd_delta=ndpost20-ndpre20;ndvi=(ndvi_pre20+ndvi_post20)/2;mw=(mpre+mpost)/2
 # Exclusive, coded strata. Model-derived strata are recorded only in the separate design manifest.
 conds=[disagreement,bothwater,(np.abs(mnd_delta)>.20)|(np.abs(nd_delta)>.20),((mpre>.30)&(mpost>.30)&(scls[0]==6)&(scls[1]==6)),(mw>.25), (ndvi>.4)&(mw>-.05),(ndvi>.45)&(mw<=-.05), (mw>=-.05)&(mw<=.20)&(ndvi<.30), (mw<-.20)&(ndvi<.25)]
 names=['model_disagreement','consensus_water_like','optical_temporal_change','clear_scl_water_candidate','pond_or_open_water_spectral_candidate','vegetated_water_spectral_candidate','vegetation_spectral_candidate','wet_soil_ambiguous_proxy','dry_exposed_land_proxy']
 codes={f'S{i:02d}':n for i,n in enumerate(names,1)}
 strata=np.zeros(valid.shape,np.uint8)
 for idx,c in enumerate(conds,1):strata[valid&(strata==0)&c]=idx
 strata[valid&(strata==0)]=len(names)+1;codes['S10']='mixed_or_other_valid_context'
 return {'opt':opt,'inf':inf,'profile':pm,'valid':valid,'strata':strata,'codes':codes,'indices':{'ndwi_pre':ndpre20,'ndwi_post':ndpost20,'mndwi_pre':mpre,'mndwi_post':mpost},'scl':scls,'bandpaths':{d:{b:ROOT/bydate[d]['bands'][b]['path'] for b in ('B03','B04','B08')} for d in ('2026-01-10','2026-01-20')},'disagreement':disagreement,'aoi':aoi,'aoi_profile':ap}
def main():
 d=load_inputs();p=d['profile'];h,w=p['height'],p['width'];tr=p['transform'];xmin=tr.c;xmax=tr.c+w*tr.a
 # Assign complete 5 km block columns into west/calibration, middle/validation, east/test groups.
 blockcols=sorted(set(np.floor((xmin+np.arange(w)*tr.a)/BLOCK_M).astype(int).tolist()));n=len(blockcols)
 ncal=max(1,int(round(n*.5)));nval=max(1,int(round(n*.25)));nval=min(nval,n-ncal-1)
 groupcols={'calibration':set(blockcols[:ncal]),'validation':set(blockcols[ncal:ncal+nval]),'test':set(blockcols[ncal+nval:])}
 blockgroup={bc:g for g,cols in groupcols.items() for bc in cols}
 xcoord=xmin+(np.arange(w)+.5)*tr.a; bcol=np.floor(xcoord/BLOCK_M).astype(int)
 groups=np.empty((h,w),object)
 for bc,g in blockgroup.items():groups[:,bcol==bc]=g
 # Guard cells around group boundaries: 1 km in UTM on each side of the distinct spatial strips.
 # right edge of west and middle ranges from block-column grid
 west_right=(max(groupcols['calibration'])+1)*BLOCK_M; mid_right=(max(groupcols['validation'])+1)*BLOCK_M
 guard=np.ones((h,w),bool)
 if groupcols['validation']:guard[:,(xcoord>=west_right-GUARD_M)&(xcoord<west_right+GUARD_M)]=False
 if groupcols['test']:guard[:,(xcoord>=mid_right-GUARD_M)&(xcoord<mid_right+GUARD_M)]=False
 groupnames=np.array(['calibration','validation','test'],dtype=object)
 rng=np.random.default_rng(SEED);selected=[];count_manifest={}
 for code,name in d['codes'].items():
  sid=int(code[1:]); cm=d['valid']&(d['strata']==sid)&guard
  for group in ('calibration','validation','test'):
   rows,cols=np.where(cm&(groups==group));total=len(rows);nsel=min(TARGET_PER_GROUP_STRATUM,total)
   if nsel==0:count_manifest[f'{code}:{group}']={'candidate_pixels':total,'selected':0,'inclusion_probability':None};continue
   indices=rng.choice(total,nsel,replace=False);prob=nsel/total
   count_manifest[f'{code}:{group}']={'candidate_pixels':total,'selected':nsel,'inclusion_probability':prob}
   for ix in indices:
    y,x=int(rows[ix]),int(cols[ix]);cx,cy=xy(tr,y,x,offset='center')
    selected.append({'row':y,'col':x,'x':cx,'y':cy,'stratum':code,'split':group,'block':f'{math.floor(cx/BLOCK_M)}_{math.floor(cy/BLOCK_M)}','inclusion_probability':prob,'weight':1/prob})
 # Build imagery-only false-color context chips. Same fixed reflectance stretch for both dates.
 chips=OUT/'context_chips';chips.mkdir(parents=True,exist_ok=True)
 bandds={date:{b:rasterio.open(path) for b,path in bands.items()} for date,bands in d['bandpaths'].items()}
 gallery=[]
 for i,s in enumerate(selected,1):
  s['sample_id']=f'GW7B-{i:05d}';center_x,center_y=s['x'],s['y'];panels=[]
  for date in ('2026-01-10','2026-01-20'):
   # Context imagery is 10 m false-color NIR/red/green. No SAR/model layers are opened here.
   ds=bandds[date];r,c=ds['B08'].index(center_x,center_y);win=Window(c-64,r-64,128,128)
   bands=[ds[b].read(1,window=win,boundless=True,fill_value=-9999) for b in ('B08','B04','B03')]
   rgb=np.stack([np.clip((np.where(x==-9999,0,x))/0.4,0,1) for x in bands],axis=-1)
   img=Image.fromarray((rgb*255).astype(np.uint8),'RGB');ImageDraw.Draw(img).ellipse((61,61,67,67),outline='yellow',width=2);panels.append(img)
  canvas=Image.new('RGB',(256,148),'white');canvas.paste(panels[0],(0,20));canvas.paste(panels[1],(128,20));dr=ImageDraw.Draw(canvas);dr.text((2,3),'2026-01-10',fill='black');dr.text((130,3),'2026-01-20',fill='black')
  cp=chips/f"{s['sample_id']}_optical_pre_post.png";canvas.save(cp,optimize=True);rel=cp.relative_to(OUT).as_posix();s['context_image']=rel
  y,x=s['row'],s['col'];s.update({k:(float(a[y,x]) if np.isfinite(a[y,x]) else None) for k,a in d['indices'].items()});s['pre_scl']=int(d['scl'][0][y,x]);s['post_scl']=int(d['scl'][1][y,x]);s['pre_scl_clear']=int(s['pre_scl'] in (2,4,5,6));s['post_scl_clear']=int(s['post_scl'] in (2,4,5,6));gallery.append({'sample_id':s['sample_id'],'context':rel,'stratum':s['stratum']})
 for x in bandds.values():
  for ds in x.values():ds.close()
 crs=rasterio.crs.CRS.from_wkt(p['crs'].to_wkt() if hasattr(p['crs'],'to_wkt') else str(p['crs']))
 with rasterio.open(ROOT/d['opt']['scenes'][0]['ndwi']['path']) as ref: wkt=ref.crs.to_wkt()
 con=init_gpkg(GPKG,wkt)
 bnds=[]
 for s in selected:
  geom=gpkg_header(Point(s['x'],s['y']));bnds.append((s['x'],s['y']))
  columns='geom,sample_id,sampling_stratum,spatial_block,split_group,x_utm,y_utm,inclusion_probability,sample_weight,pre_date,post_date,pre_scl,post_scl,pre_scl_clear,post_scl_clear,ndwi_pre,ndwi_post,mndwi_pre,mndwi_post,context_image,pre_label,post_label,pre_confidence,post_confidence,annotator,review_date,notes,label_source'
  values=','.join(['?']*20+['NULL']*8)
  con.execute(f'INSERT INTO samples ({columns}) VALUES ({values})',(geom,s['sample_id'],s['stratum'],s['block'],s['split'],s['x'],s['y'],s['inclusion_probability'],s['weight'],'2026-01-10','2026-01-20',s['pre_scl'],s['post_scl'],s['pre_scl_clear'],s['post_scl_clear'],s['ndwi_pre'],s['ndwi_post'],s['mndwi_pre'],s['mndwi_post'],s['context_image']))
 if bnds:
  con.execute("UPDATE gpkg_contents SET min_x=?,min_y=?,max_x=?,max_y=? WHERE table_name='samples'",(min(x for x,y in bnds),min(y for x,y in bnds),max(x for x,y in bnds),max(y for x,y in bnds)))
 con.commit();con.close()
 manifest={'status':'annotation_package_prepared_human_labels_pending','seed':SEED,'target_per_stratum_per_split':TARGET_PER_GROUP_STRATUM,'spatial_design':{'crs':str(p['crs']),'block_size_m':BLOCK_M,'grouping':'contiguous west calibration / center validation / east final-test bands of complete 5 km block columns','guard_band_m':GUARD_M,'all_samples_from_a_block_column_assigned_to_one_group':True,'unique_blocks_per_split':{g:len({s['block'] for s in selected if s['split']==g}) for g in ('calibration','validation','test')},'note':'Separated strips and guard margins reduce near-pixel leakage; spatial autocorrelation beyond this guard remains possible.'},'source_dates':['2026-01-10','2026-01-20'],'sampling_strata':d['codes'],'stratum_counts_and_inclusion_probabilities':count_manifest,'sample_count':len(selected),'split_counts':{g:sum(s['split']==g for s in selected) for g in ('calibration','validation','test')},'labels_completed':0,'label_fields':['pre_label','post_label'],'permitted_labels':list(LABELS),'model_predictions_embedded_in_annotation_package':False,'context_chips':'10m false-color NIR/red/green optical context panels with fixed 0-0.4 reflectance display stretch; no model predictions','geopackage':{'path':GPKG.relative_to(ROOT).as_posix(),'sha256':sha(GPKG),'feature_count':len(selected),'layer':'samples','crs':str(p['crs'])},'context_gallery_html':'data/gherproof/reference/phase7b/annotation_review_gallery.html','limitations':['These optical samples support human interpretation; they are not absolute ground truth.','Strata are sampling proxies, not ground labels.','Model-derived strata are coded in the reviewer GeoPackage and no model identifier or prediction score is included.','A single reviewer is expected; no inter-annotator agreement is available until a second independent reviewer labels the same samples.','Labels must be supplied by a human before evaluation; no predictions or labels were added to the annotation table.']}
 (ROOT/'data/gherproof/manifests/phase7b_sampling_design_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 public_manifest={k:v for k,v in manifest.items() if k!='sampling_strata'}
 public_manifest['sampling_stratum_key']='Held separately from the blinded annotation package; do not use codes to assign labels.'
 (OUT/'sampling_design_manifest.json').write_text(json.dumps(public_manifest,indent=2)+'\n',encoding='utf-8')
 # A blind gallery linked from the GeoPackage's context_image column.
 cards='\n'.join(f'<article><h3>{html.escape(g["sample_id"])} · {html.escape(g["stratum"])}</h3><img src="{html.escape(g["context"])}" alt="Jan 10 and Jan 20 optical false-color context"><p>Label pre and post in the GeoPackage. Do not infer labels from the coded stratum alone.</p></article>' for g in gallery)
 page='<!doctype html><meta charset="utf-8"><title>GherProof optical annotation review</title><style>body{font:14px Arial;margin:1rem;background:#f3f5f7}article{display:inline-block;vertical-align:top;background:white;margin:8px;padding:8px;width:272px}img{width:256px;height:148px;image-rendering:auto}h3{font-size:13px}</style><h1>Optical annotation gallery — blind review</h1><p>Jan 10 and Jan 20 2026 false-color NIR/red/green context. Yellow circle marks the sample center. No model predictions are displayed. Use the GeoPackage to record separate pre/post labels, confidence and notes.</p>'+cards
 (OUT/'annotation_review_gallery.html').write_text(page,encoding='utf-8')
 print(json.dumps({'geopackage':str(GPKG.relative_to(ROOT)),'samples':len(selected),'splits':manifest['split_counts'],'status':manifest['status']},indent=2))
if __name__=='__main__':main()
