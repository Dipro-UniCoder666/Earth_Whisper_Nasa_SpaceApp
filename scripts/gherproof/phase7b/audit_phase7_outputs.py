"""Independent audit of Phase 7 model rasters, masks, hashes and disagreement."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.append(str(ROOT/'backend/.venv/Lib/site-packages'))
import numpy as np,rasterio
from PIL import Image,ImageDraw
INF=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json';S1=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json'
OUT=ROOT/'data/gherproof/manifests/phase7b_model_output_audit.json';FIG=ROOT/'data/gherproof/processed/phase7/figures/phase7b_model_disagreement_audit.png'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def stats(a):
 v=a[np.isfinite(a)];return {'valid_count':int(v.size),'min':float(v.min()) if v.size else None,'max':float(v.max()) if v.size else None,'mean':float(v.mean()) if v.size else None,'std':float(v.std()) if v.size else None,'percentiles':{str(p):float(np.percentile(v,p)) for p in (1,5,10,25,50,75,90,95,99)} if v.size else {}}
def raster(path,check_hash=None):
 with rasterio.open(path) as ds:
  a=ds.read(1,masked=True);mask=~np.ma.getmaskarray(a);v=np.asarray(a.data,dtype=np.float32);good=mask&np.isfinite(v)
  return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'hash_matches_manifest':sha(path)==check_hash if check_hash else None,'bytes':path.stat().st_size,'crs':str(ds.crs),'transform':list(ds.transform),'bounds':list(ds.bounds),'shape':[ds.height,ds.width],'resolution':list(ds.res),'dtype':ds.dtypes[0],'nodata':ds.nodata,'valid_pixels':int(good.sum()),'invalid_pixels':int(v.size-good.sum()),'statistics':stats(v[good]),'array':v,'valid':good}
def main():
 inf=json.loads(INF.read_text());s1=json.loads(S1.read_text());scene_r={};audit=[]
 for rec in inf['scenes']:
  p=ROOT/rec['probability']['path'];q=raster(p,rec['probability']['sha256']);valid=q.pop('valid');v=q.pop('array');q['model']=rec['model'];q['item_id']=rec['item_id'];q['date']=rec['date'];q['threshold']=.5;q['predicted_class_pixels_at_threshold']=int(((v>=.5)&valid).sum());q['coverage_fraction_of_rectangular_grid']=float(valid.sum()/(q['shape'][0]*q['shape'][1]));q['source_valid_pixels_recorded']=rec['valid_pixels'];q['valid_count_matches_manifest']=q['valid_pixels']==rec['valid_pixels'];audit.append(q);scene_r[(rec['item_id'],rec['model'])]=(v,valid,p)
 pairs=[];heat=[]
 for pair in inf['pairs']:
  exact=next(x for x in s1['pairs'] if x['pair_id']==pair['pair_id']);pair_rec={'pair_id':pair['pair_id'],'pre_item_id':pair['pre_item_id'],'pre_date':pair['pre_date'],'post_item_id':pair['post_item_id'],'post_date':pair['post_date'],'relative_orbit':pair['relative_orbit'],'direction':pair['orbit_direction'],'phase6b_common_valid_pixels':exact['common_valid_pixels_all_four'],'phase6b_common_valid_fraction':exact['common_valid_fraction_of_aoi'],'scenes_pixel_validated':all(next(s for s in s1['scenes'] if s['item_id']==iid)['status']=='raster_verified' for iid in (pair['pre_item_id'],pair['post_item_id'])),'models':{}}
  maskpath=ROOT/exact['coverage_raster']['path']
  with rasterio.open(maskpath) as md:aoi=md.read(1)>0;maskprof=md.profile.copy()
  for side,iid in [('pre',pair['pre_item_id']),('post',pair['post_item_id'])]:
   values={}
   for model in ('scratch','pretrained'):values[model]=scene_r[(iid,model)][0]
   common=scene_r[(iid,'scratch')][1]&scene_r[(iid,'pretrained')][1]&aoi
   xor=(values['scratch']>=.5)!=(values['pretrained']>=.5);d=np.abs(values['scratch']-values['pretrained']);vals=d[common]
   cells=[]
   for iy in range(4):
    for ix in range(4):
     y0,y1=iy*aoi.shape[0]//4,(iy+1)*aoi.shape[0]//4;x0,x1=ix*aoi.shape[1]//4,(ix+1)*aoi.shape[1]//4;am=aoi[y0:y1,x0:x1];cc=common[y0:y1,x0:x1];xx=xor[y0:y1,x0:x1]
     cells.append({'row':iy,'column':ix,'aoi_pixels':int(am.sum()),'common_valid_pixels':int(cc.sum()),'xor_pixels':int((xx&cc).sum()),'xor_fraction':float((xx&cc).sum()/max(cc.sum(),1))})
   pair_rec['models'][side]={'valid_pixels':int(common.sum()),'invalid_pixels_in_rectangular_raster':int(common.size-common.sum()),'xor_pixels':int((xor&common).sum()),'xor_fraction':float((xor&common).sum()/max(common.sum(),1)),'absolute_probability_difference':stats(vals),'grid_4x4':cells}
   heat.append((pair['pair_id'],side,pair_rec['models'][side]['grid_4x4']))
  pairs.append(pair_rec)
 # Draw an auditable 4x4 disagreement grid for each pair/date; values are percent of common valid pixels.
 img=Image.new('RGB',(1200,600),'white');draw=ImageDraw.Draw(img)
 for idx,(pid,side,cells) in enumerate(heat):
  x0=(idx%4)*300;y0=(idx//4)*300;draw.text((x0+8,y0+6),f'{pid} · {side}',fill='black')
  for c in cells:
   x=x0+18+c['column']*64;y=y0+34+c['row']*56;v=c['xor_fraction'];color=(int(245-175*v),int(249-110*v),int(250-90*v));draw.rectangle((x,y,x+55,y+45),fill=color,outline='#334')
   draw.text((x+4,y+5),f"{v*100:.1f}%",fill='black')
 img.save(FIG)
 ckpt={}
 for name,record in inf['checkpoints'].items():
  p=ROOT/record['path'];ckpt[name]={**record,'actual_sha256':sha(p),'hash_valid':sha(p)==record['sha256']}
 status='pass' if all(x['hash_matches_manifest'] and x['valid_count_matches_manifest'] and x['statistics']['min']>=0 and x['statistics']['max']<=1 for x in audit) and all(x['hash_valid'] for x in ckpt.values()) else 'qc_warning'
 out={'status':status,'created_at_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'configuration':inf['configuration'],'checkpoints':ckpt,'scene_count':len(audit),'scenes':audit,'pairs':pairs,'disagreement_figure':FIG.relative_to(ROOT).as_posix(),'limitations':['Four scene times comprise two separately validated geometries; they are not one continuous orbit series.','Model outputs remain exploratory due to training/RTC measurement-domain mismatch and absence of human-reviewed local references.','Coverage is the Phase 6B provisional AOI and is not village boundary coverage.']}
 OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':status,'scene_outputs':len(audit),'pairs':len(pairs),'manifest':OUT.relative_to(ROOT).as_posix(),'figure':FIG.relative_to(ROOT).as_posix()},indent=2))
if __name__=='__main__':main()
