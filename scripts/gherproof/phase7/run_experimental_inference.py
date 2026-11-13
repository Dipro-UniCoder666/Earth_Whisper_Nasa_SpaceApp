"""Run separate, gated experimental U-Net inference on the Phase 6B S1 pairs."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.extend([str(ROOT/'backend/.venv/Lib/site-packages'),str(ROOT/'scripts/gherproof'),str(ROOT/'scripts/gherproof/phase7')])
import numpy as np
import rasterio
import torch
from model_inputs import linear_gamma0_to_db,normalize_db,tile_starts
import train_sen1floods11 as scratch_arch
from resnet50_sar_unet import ResNet50SARUNet

S1=ROOT/'data/gherproof/manifests/phase6b_sentinel1_pixel_validation.json'
RAD=ROOT/'data/gherproof/manifests/phase7_radiometric_compatibility.json'
OUT=ROOT/'data/gherproof/processed/phase7/inference'
MAN=ROOT/'data/gherproof/manifests/phase7_inference_manifest.json'
NODATA=-9999.0
CKPTS={'scratch':ROOT/'models/gherproof/sen1floods11_attention_unet.pt','pretrained':ROOT/'models/gherproof/sen1floods11_resnet50_moco_unet.pt'}
EXPECTED={'scratch':'fcb244de72d51da9760d089ed5909d0cfdfda41af2e8def76aae203aadf5a040','pretrained':'084b41f06ea0f1049b53c6708fed0a78e081a38704677dce7e172e67e2b8d9f0'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(path,a,ref,desc,valid,tags):
 path.parent.mkdir(parents=True,exist_ok=True); p=ref.profile.copy();p.update(driver='GTiff',count=1,dtype='float32',nodata=NODATA,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256)
 data=np.full(a.shape,NODATA,np.float32);data[valid]=a[valid].astype(np.float32)
 with rasterio.open(path,'w',**p) as ds: ds.write(data,1);ds.set_band_description(1,desc);ds.update_tags(**tags)
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,'valid_pixels':int(valid.sum())}
def model_load(name,ckpt):
 model=scratch_arch.AttentionUNet(base=int(ckpt.get('base_channels',16))) if name=='scratch' else ResNet50SARUNet()
 model.load_state_dict(ckpt['state_dict'],strict=True);model.eval();return model
def predict(model,db,valid,mean,std):
 x,_=normalize_db(db,valid,mean,std,band_names=('VV','VH'))
 h,w=valid.shape; patch=256; overlap=64; ys=tile_starts(h,patch,overlap);xs=tile_starts(w,patch,overlap)
 # Raised-cosine blend avoids hard seams while retaining nonzero edge weights.
 one=np.hanning(patch+2)[1:-1].astype(np.float32); weight=np.maximum(np.outer(one,one),0.05)
 accum=np.zeros((h,w),np.float32); denom=np.zeros((h,w),np.float32); checks=[]
 with torch.inference_mode():
  for y in ys:
   for xx in xs:
    tile=x[:,y:y+patch,xx:xx+patch]
    if tile.shape[1:]!=(patch,patch):
     padded=np.zeros((2,patch,patch),np.float32);padded[:,:tile.shape[1],:tile.shape[2]]=tile;tile=padded
    tensor=torch.from_numpy(tile[None]).to(next(model.parameters()).device)
    logits=model(tensor)
    if logits.shape!=(1,1,patch,patch) or not torch.isfinite(logits).all():raise RuntimeError(f'Unstable model output shape/value: {tuple(logits.shape)}')
    probs=torch.sigmoid(logits)[0,0].cpu().numpy()
    if not np.isfinite(probs).all() or probs.min()<0 or probs.max()>1:raise RuntimeError('Probability out of range')
    checks.append(float(probs[128,128]))
    hh=min(patch,h-y);ww=min(patch,w-xx);wt=weight[:hh,:ww]
    accum[y:y+hh,xx:xx+ww]+=probs[:hh,:ww]*wt;denom[y:y+hh,xx:xx+ww]+=wt
 out=np.zeros((h,w),np.float32);covered=denom>0;out[covered]=accum[covered]/denom[covered]
 if not covered.all():raise RuntimeError('Tile overlap reassembly left uncovered pixels')
 # Deterministic repeated tile smoke check on first region, same model/input.
 test=torch.from_numpy(x[None,:,:patch,:patch]).to(next(model.parameters()).device)
 with torch.inference_mode(): again=torch.sigmoid(model(test))[0,0,128,128].item()
 if abs(again-checks[0])>1e-6:raise RuntimeError('Model smoke output is not repeatable')
 out[~valid]=0
 return out,{'tile_count':len(ys)*len(xs),'tile_patch':patch,'overlap':overlap,'covered_pixels':int(covered.sum()),'repeatability_abs_difference':abs(again-checks[0]),'input_finite_on_valid':bool(np.isfinite(x[:,valid]).all()),'invalid_normalized_zero':bool((x[:,~valid]==0).all())}
def main():
 torch.set_num_threads(4)
 if not torch.cuda.is_available(): device='cpu'
 else: device='cuda'
 if device!='cpu': print('CUDA available; using CUDA')
 rad=json.loads(RAD.read_text()); stats=rad['training_source']['preprocess']; s1=json.loads(S1.read_text()); scene={s['item_id']:s for s in s1['scenes']}
 models={}; ckptmeta={}
 for name,p in CKPTS.items():
  actual=sha(p)
  if actual!=EXPECTED[name]:raise RuntimeError(f'{name} checkpoint digest mismatch; inference denied')
  cp=torch.load(p,map_location='cpu',weights_only=False);models[name]=model_load(name,cp).to(device)
  ckptmeta[name]={'path':p.relative_to(ROOT).as_posix(),'sha256':actual,'architecture':cp.get('architecture'),'mean':cp['normalization_mean'],'std':cp['normalization_std'],'threshold':0.5,'benchmark_only':True}
 outputs={}; scene_records=[]
 for pair in s1['pairs']:
  ids=[pair['pre_item_id'],pair['post_item_id']]
  pair_cache={name:{} for name in models}
  for iid in ids:
   row=scene[iid];src=ROOT/row['analysis_product']['path'];date=row['item_metadata']['datetime'][:10]
   with rasterio.open(src) as ds:
    linear=ds.read().astype(np.float32); nodata=ds.nodata;ref=ds
    db,bvalid,valid=linear_gamma0_to_db(linear,band_names=('VV','VH'),representation='linear_gamma0',nodata=nodata)
    if valid.sum()==0:raise RuntimeError(f'No usable pixels for {iid}')
    for name,model in models.items():
     prob,smoke=predict(model,db,valid,ckptmeta[name]['mean'],ckptmeta[name]['std'])
     key=f'{iid}_{name}';pred=prob>=0.5; entropy=-(np.clip(prob,1e-7,1-1e-7)*np.log2(np.clip(prob,1e-7,1-1e-7))+(1-np.clip(prob,1e-7,1-1e-7))*np.log2(1-np.clip(prob,1e-7,1-1e-7)))
     base=OUT/'scenes'/name
     rec={'item_id':iid,'date':date,'pair_id':pair['pair_id'],'model':name,'valid_pixels':int(valid.sum()),'water_pixels_threshold_0_5':int((pred&valid).sum()),'exploratory_area_km2_at_10m':float((pred&valid).sum()*100/1e6),'threshold_sensitivity':{str(t):int(((prob>=t)&valid).sum()) for t in (.4,.5,.6)},'smoke':smoke}
     rec['probability']=write(base/f'{date}_{iid}_{name}_water_probability.tif',prob,ds,'Experimental water-class probability; not locally validated',valid,{'model':name,'checkpoint_sha256':ckptmeta[name]['sha256'],'threshold':'0.5 fixed from benchmark','input':'RTC Gamma0 linear converted once to dB; clipped [-60,20]; checkpoint z-score','claim':'experimental only; no local labels'})
     rec['mask']=write(base/f'{date}_{iid}_{name}_mask_0p5.tif',pred.astype(np.float32),ds,'Experimental model class at fixed p>=0.5',valid,{'class':'model predicted water-like class; not verified water','threshold':'0.5'})
     rec['uncertainty']=write(base/f'{date}_{iid}_{name}_binary_entropy.tif',entropy,ds,'Binary entropy of model probability; 0 certain by model, 1 maximally uncertain',valid,{'interpretation':'model uncertainty proxy only'})
     outputs[key]={'probability':prob,'mask':pred,'valid':valid,'ref':src,'record':rec};scene_records.append(rec)
  for name in models:
   a=outputs[f'{ids[0]}_{name}'];b=outputs[f'{ids[1]}_{name}'];valid=a['valid']&b['valid'];prob_diff=b['probability']-a['probability'];new=b['mask']&~a['mask']&valid
   with rasterio.open(a['ref']) as ref:
    stem=OUT/'pairs'/name/pair['pair_id'];pair_rec={'pair_id':pair['pair_id'],'model':name,'pre_date':pair['pre_date'],'post_date':pair['post_date'],'relative_orbit':pair['relative_orbit'],'direction':pair['orbit_direction'],'common_valid_pixels':int(valid.sum()),'exploratory_new_water_candidate_pixels':int(new.sum()),'exploratory_new_water_candidate_area_km2':float(new.sum()*100/1e6)}
    tags={'pair_id':pair['pair_id'],'model':name,'checkpoint_sha256':ckptmeta[name]['sha256'],'interpretation':'exploratory pre/post model change; not verified inundation or breach'}
    pair_rec['probability_difference']=write(stem/'probability_post_minus_pre.tif',prob_diff,ref,'Post minus pre model probability (unitless)',valid,tags)
    pair_rec['new_water_candidate']=write(stem/'new_water_candidate.tif',new.astype(np.float32),ref,'Post class water-like and pre class not water-like',valid,tags)
    outputs[f'pair_{pair["pair_id"]}_{name}']=pair_rec
  # Binary and probability disagreements are saved separately; no model averaging.
  a=outputs[f'{ids[0]}_scratch'];b=outputs[f'{ids[0]}_pretrained'];v=a['valid']&b['valid']
  with rasterio.open(a['ref']) as ref:
   stem=OUT/'disagreement'/pair['pair_id']; xor=a['mask']^b['mask']; diff=np.abs(a['probability']-b['probability'])
   outputs[f'disagreement_{pair["pair_id"]}']={'binary_xor_pixels':int((xor&v).sum()),'binary_xor_fraction':float((xor&v).sum()/max(v.sum(),1)),'xor':write(stem/'binary_xor_pre.tif',xor.astype(np.float32),ref,'Model binary disagreement (pre)',v,{'models':'scratch vs pretrained','averaging':'none'}),'probability_difference':write(stem/'absolute_probability_difference_pre.tif',diff,ref,'Absolute model probability disagreement (pre)',v,{'models':'scratch vs pretrained','averaging':'none'})}
  a=outputs[f'{ids[1]}_scratch'];b=outputs[f'{ids[1]}_pretrained'];v=a['valid']&b['valid']
  with rasterio.open(a['ref']) as ref:
   stem=OUT/'disagreement'/pair['pair_id'];xor=a['mask']^b['mask'];diff=np.abs(a['probability']-b['probability'])
   outputs[f'disagreement_{pair["pair_id"]}_post']={'binary_xor_pixels':int((xor&v).sum()),'binary_xor_fraction':float((xor&v).sum()/max(v.sum(),1)),'xor':write(stem/'binary_xor_post.tif',xor.astype(np.float32),ref,'Model binary disagreement (post)',v,{'models':'scratch vs pretrained','averaging':'none'}),'probability_difference':write(stem/'absolute_probability_difference_post.tif',diff,ref,'Absolute model probability disagreement (post)',v,{'models':'scratch vs pretrained','averaging':'none'})}
 manifest={'status':'experimental_inference_completed','device':device,'pairs':[{k:v for k,v in p.items() if k in ('pair_id','pre_date','post_date','pre_item_id','post_item_id','relative_orbit','orbit_direction','temporal_offsets_days')} for p in s1['pairs']],'checkpoints':ckptmeta,'configuration':{'bands':['VV','VH'],'representation_source':'linear RTC Gamma0 intensity','conversion':'10*log10(value) once; positive finite only','clip_db':[-60,20],'normalization':'checkpoint mean/std','patch':256,'overlap':64,'threshold':0.5,'threshold_sensitivity':[0.4,0.5,0.6],'mask':'common valid VV/VH; invalid normalized to zero and excluded from outputs'},'scenes':scene_records,'pair_outputs':{k:v for k,v in outputs.items() if k.startswith('pair_')},'model_disagreement':{k:v for k,v in outputs.items() if k.startswith('disagreement_')},'limitations':['RTC Gamma0 dB is not identical to training GRD dB; outputs are exploratory and not locally validated.','The provisional regional AOI is not an official village boundary.','Predicted water-like class and pre/post candidates do not prove flood, breach, drainage failure, affected cropland or causation.','No permanent-water removal: no authoritative permanent-water/pond reference layer was available.']}
 MAN.parent.mkdir(parents=True,exist_ok=True);MAN.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({'manifest':MAN.relative_to(ROOT).as_posix(),'scene_outputs':len(scene_records),'pairs':len(s1['pairs']),'models':list(models),'device':device},indent=2))
if __name__=='__main__':main()
