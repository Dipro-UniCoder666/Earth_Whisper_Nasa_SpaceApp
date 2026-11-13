"""Quantify benchmark-dB versus RTC-dB distribution and texture differences."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.extend([str(ROOT/'backend/.venv/Lib/site-packages'),str(ROOT/'scripts/gherproof')])
import numpy as np,rasterio,csv
from scipy.stats import wasserstein_distance,ks_2samp
from PIL import Image,ImageDraw
COMP=ROOT/'data/gherproof/manifests/phase7_radiometric_compatibility.json';TRMAN=ROOT/'data/gherproof/manifests/sen1floods11_training_results.json';OUT=ROOT/'data/gherproof/manifests/phase7b_domain_shift_statistics.json'
PLOT=ROOT/'data/gherproof/processed/phase7b/figures/phase7b_radiometric_domain_shift.png'
RAW=ROOT/'data/gherproof/raw/sen1floods11/v1.1/data/flood_events/HandLabeled'
S1_DIR=RAW/'S1Hand';LABEL_DIR=RAW/'LabelHand';SPLIT_DIR=ROOT/'data/gherproof/raw/sen1floods11/v1.1/splits/flood_handlabeled'
META_FILE=ROOT/'data/gherproof/raw/sen1floods11/v1.1/Sen1Floods11_Metadata.geojson'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def quant(a):return {str(p):float(np.percentile(a,p)) for p in (1,2,5,25,50,75,95,98,99)}
def texture_add(acc,a,valid):
 for axis in (0,1):
  if axis==0:x=a[:,:-1];y=a[:,1:];m=valid[:,:-1]&valid[:,1:]
  else:x=a[:-1,:];y=a[1:,:];m=valid[:-1,:]&valid[1:,:]
  xx=x[m].astype(np.float64);yy=y[m].astype(np.float64)
  if not len(xx):continue
  z=acc[axis];z[0]+=len(xx);z[1]+=xx.sum();z[2]+=yy.sum();z[3]+=(xx*xx).sum();z[4]+=(yy*yy).sum();z[5]+=(xx*yy).sum();z[6]+=((xx-yy)**2).sum()
def texture_result(acc):
 out={}
 for axis,z in enumerate(acc):
  n,sx,sy,sxx,syy,sxy,ssq=z;cov=sxy/n-(sx/n)*(sy/n);vx=sxx/n-(sx/n)**2;vy=syy/n-(sy/n)**2
  out['horizontal' if axis==0 else 'vertical']={'neighbor_pairs':int(n),'lag1_correlation':float(cov/np.sqrt(max(vx*vy,1e-15))),'rmse_adjacent_difference_db':float(np.sqrt(ssq/n))}
 return out
def training_rows():
 with (SPLIT_DIR/'flood_train_data.csv').open(newline='',encoding='utf-8-sig') as f:
  return [{'s1':Path(r[0]).name,'label':Path(r[1]).name} for r in csv.reader(f) if len(r)>=2 and r[0].endswith('_S1Hand.tif')]
def training_event(filename,geoms):
 from shapely.geometry import box
 with rasterio.open(S1_DIR/filename) as ds:
  b=ds.bounds
  if ds.crs.to_epsg()!=4326:
   from rasterio.warp import transform_bounds
   b=transform_bounds(ds.crs,4326,*b,densify_pts=21)
  footprint=box(*b)
 ranked=sorted(((footprint.intersection(g).area/max(footprint.area,1e-12),eid) for eid,g in geoms),reverse=True)
 if not ranked or ranked[0][0]<.5 or (len(ranked)>1 and ranked[0][0]-ranked[1][0]<.1):raise RuntimeError(f'Cannot assign training chip to unique event: {filename}')
 return ranked[0][1]
def inspect_training_chip(row):
 with rasterio.open(S1_DIR/row['s1']) as ds:
  image=ds.read().astype(np.float32);nodata=ds.nodata
 with rasterio.open(LABEL_DIR/row['label']) as ds:labels=ds.read(1)
 valid=np.isfinite(image).all(axis=0)&(labels>=0)
 if nodata is not None:valid &= (image!=nodata).all(axis=0)
 return image,valid
def main():
 ck=json.load(open(TRMAN,encoding='utf-8'));event=str(ck['validation_event_id']);meta=json.load(open(META_FILE,encoding='utf-8'));from shapely.geometry import shape;geoms=[(str(f['properties']['ID']),shape(f['geometry'])) for f in meta['features']];rows=training_rows();train_rows=[];rng=np.random.default_rng(260113);tsamp=[[],[]];tacc=[[[0.0]*7 for _ in range(2)] for __ in range(2)];representative=None
 # Exact project training subset; preserve a sample for texture and histograms.
 for row in rows:
  ev=training_event(row['s1'],geoms)
  if ev==event:continue
  img,valid=inspect_training_chip(row)
  if not valid.any():continue
  train_rows.append(row);img=np.clip(img,-60,20)
  if representative is None:representative=(img.copy(),valid.copy(),row['s1'],None)
  for bi in (0,1):
   vv=img[bi][valid];nn=min(2500,len(vv));tsamp[bi].append(rng.choice(vv,nn,replace=False).astype(np.float32))
   texture_add(tacc[bi],img[bi],valid)
 # Build RTC comparison samples from the exact existing dB arrays; no source arrays modified.
 rad=json.load(open(COMP,encoding='utf-8'));rtc_samples=[[],[]];scenes=[];racc=[[[0.0]*7 for _ in range(2)] for __ in range(2)];rrng=np.random.default_rng(260113);rtc_rep=None
 for rec in rad['rtc_measurement']['scenes']:
  path=ROOT/rec['db_output']['path']
  with rasterio.open(path) as ds:
   dat=ds.read(masked=True).astype(np.float32);da=np.asarray(dat.data);m=~np.ma.getmaskarray(dat);m &= np.isfinite(da)&(da!=-32768)
   byband=[]
   for bi in (0,1):
    vals=da[bi][m[bi]];n=min(250000,len(vals));sm=rrng.choice(vals,n,replace=False) if n else np.array([],np.float32);rtc_samples[bi].append(sm.astype(np.float32));byband.append({'band':['VV','VH'][bi],'valid_pixels':int(vals.size),'median_db':float(np.median(vals)),'sample_size_for_distribution':int(n),'percentiles_db':quant(vals)})
    texture_add(racc[bi],da[bi],m[bi])
   if rtc_rep is None:rtc_rep=(da.copy(),m.copy(),rec['date'],ds.profile.copy())
   scenes.append({'date':rec['date'],'item_id':rec['item_id'],'bands':byband,'source_grid':{'crs':str(ds.crs),'resolution':list(ds.res),'shape':[ds.height,ds.width]}})
 reportbands=[]
 for bi,name in enumerate(('VV','VH')):
  trvals=np.concatenate(tsamp[bi]);rv=np.concatenate(rtc_samples[bi]);kst=ks_2samp(trvals,rv,method='asymp')
  reportbands.append({'band':name,'training':{'sample_size':int(trvals.size),'median_db':float(np.median(trvals)),'percentiles_db':quant(trvals),'lag1_texture':texture_result(tacc[bi])},'rtc_pooled_acquisitions':{'sample_size':int(rv.size),'median_db':float(np.median(rv)),'percentiles_db':quant(rv),'lag1_texture':texture_result(racc[bi])},'descriptive_shift':{'median_difference_rtc_minus_training_db':float(np.median(rv)-np.median(trvals)),'wasserstein_1_db':float(wasserstein_distance(trvals,rv)),'empirical_KS_D':float(kst.statistic),'KS_p_value_not_reported':'The observations are spatially autocorrelated and sample sizes make a conventional p-value misleading.'}})
 # Fixed-range visual samples in dB, avoiding per-image contrast normalization.
 W,H=1100,690;img=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(img);font=None
 for row,(band,titledata) in enumerate(zip(('VV','VH'),[(representative,rtc_rep)]*2)):
  left=representative[0][row];leftmask=representative[1];right=rtc_rep[0][row];rightmask=rtc_rep[1][row];
  # A fixed interior chip/window selected from the first valid training chip and first RTC scene.
  def render(a,m):
   hh,ww=a.shape;cy,cx=hh//2,ww//2;chunk=a[max(0,cy-128):cy+128,max(0,cx-128):cx+128];vm=m[max(0,cy-128):cy+128,max(0,cx-128):cx+128];scale=np.clip((chunk+30)/30,0,1);scale[~vm]=0;return Image.fromarray((scale*255).astype(np.uint8)).resize((256,256),Image.Resampling.NEAREST)
  y0=50+row*310;d.text((10,y0),f'{band} dB, fixed display range -30 to 0 dB; brighter = stronger backscatter',fill='black',font=font);img.paste(render(left,leftmask).convert('RGB'),(25,y0+22));img.paste(render(right,rightmask).convert('RGB'),(355,y0+22));d.text((25,y0+284),f"training S1Hand chip {representative[2]}",fill='black');d.text((355,y0+284),f"RTC Gamma0 {rtc_rep[2]}",fill='black')
 PLOT.parent.mkdir(parents=True,exist_ok=True);img.save(PLOT)
 out={'status':'quantified_distribution_comparison_with_measurement_domain_limits','training_subset':{'dataset':'Sen1Floods11 v1.1 local project train subset excluding full validation event','chips':len(train_rows),'bands':['VV','VH'],'units':'dataset dB values; training loader applies [-60,20] dB clip','normalization_means_std_from_checkpoint':'see Phase 7 manifest'},'rtc':{'provider':'Planetary Computer sentinel-1-rtc','representation':'linear Gamma0 converted once to dB in Phase 7, clip for metrics [-60,20]','pooled_scene_count':len(scenes),'scenes':scenes},'bands':reportbands,'figure':PLOT.relative_to(ROOT).as_posix(),'figure_training_source_sha256':sha(ROOT/'data/gherproof/raw/sen1floods11/v1.1/data/flood_events/HandLabeled/S1Hand'/representative[2]),'interpretation':['The dB numerical distributions overlap centrally; tails, especially VH low-end quantiles, differ. Distribution similarity is not measurement equivalence or proof of water classification compatibility.','RTC Gamma0 and benchmark GRD are processed with different radiometric/geometric chains; event angle, terrain flattening, resampling, filtering and spatial texture cannot be normalized away by a log conversion.','Exact Planetary Computer GRD assets are raw uint16 Level-1 DN in radar geometry without CRS; their DN is not compared with model dB. They require calibration LUT, thermal-noise/border-noise treatment, orbit and terrain geocoding before a defensible comparison.'], 'rtc_data_source_manifest':'data/gherproof/manifests/phase7_radiometric_compatibility.json','grd_metadata_manifest':'data/gherproof/manifests/phase7b_grd_metadata_summary.json'}
 OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'manifest':OUT.relative_to(ROOT).as_posix(),'training_chips':len(train_rows),'rtc_scenes':len(scenes),'plot':PLOT.relative_to(ROOT).as_posix()},indent=2))
if __name__=='__main__':main()
