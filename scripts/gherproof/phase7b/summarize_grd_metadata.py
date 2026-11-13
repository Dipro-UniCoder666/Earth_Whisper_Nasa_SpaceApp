"""Extract concise, checksummed SAFE product/calibration/noise metadata audit."""
from __future__ import annotations
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];RAW=ROOT/'data/gherproof/raw/phase7b/grd_metadata';STAC=ROOT/'data/gherproof/manifests/phase7b_grd_counterpart_manifest.json';OUT=ROOT/'data/gherproof/manifests/phase7b_grd_metadata_summary.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def text(root,name):
 for x in root.iter():
  if x.tag.split('}')[-1]==name:return x.text
 return None
def main():
 stac=json.loads(STAC.read_text());rows=[]
 for item in stac['records']:
  if item['status']!='exact_counterpart_found':continue
  iid=item['match']['id'];base=RAW/iid;rec={'grd_item_id':iid,'rtc_item_id':item['rtc_item_id'],'stac':item['match']['properties'],'safe_manifest':None,'polarizations':{}}
  p=base.with_name(base.name+'_safe-manifest.xml')
  root=ET.parse(p).getroot();rec['safe_manifest']={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'product_class':text(root,'productClass'),'product_type':text(root,'productType'),'mission_id':text(root,'missionId'),'safe_start_time':text(root,'startTime'),'safe_stop_time':text(root,'stopTime')}
  for pol in ('vv','vh'):
   cr=base.with_name(base.name+f'_schema-calibration-{pol}.xml');nr=base.with_name(base.name+f'_schema-noise-{pol}.xml');ct=ET.parse(cr).getroot();nt=ET.parse(nr).getroot()
   cv=next((x for x in ct.iter() if x.tag.split('}')[-1]=='calibrationVectorList'),None);nv=next((x for x in nt.iter() if x.tag.split('}')[-1]=='noiseVectorList'),None)
   lut={}
   if cv is not None:
    for itemlut in ('sigmaNought','betaNought','gamma','dn'):
     vals=[]
     for node in ct.iter():
      if node.tag.split('}')[-1]==itemlut and node.text:
       vals.extend(node.text.split())
     if vals:lut[itemlut]={'stored_values':len(vals),'min':float(min(map(float,vals))),'max':float(max(map(float,vals)))}
   rec['polarizations'][pol]={'calibration_xml':{'path':cr.relative_to(ROOT).as_posix(),'sha256':sha(cr),'product_type':text(ct,'productType'),'polarisation':text(ct,'polarisation'),'start_time':text(ct,'startTime'),'stop_time':text(ct,'stopTime'),'absolute_calibration_constant':float(text(ct,'absoluteCalibrationConstant')) if text(ct,'absoluteCalibrationConstant') else None,'calibration_vector_count':len(list(cv)) if cv is not None else 0,'lut_summary':lut},'noise_xml':{'path':nr.relative_to(ROOT).as_posix(),'sha256':sha(nr),'product_type':text(nt,'productType'),'polarisation':text(nt,'polarisation'),'noise_vector_count':len(list(nv)) if nv is not None else 0}}
  rows.append(rec)
 out={'status':'metadata_extracted','product_count':len(rows),'records':rows,'limitations':['Calibration LUTs and thermal-noise vectors exist, but the acquired COG samples have no map CRS/geotransform and are uint16 raw measurement DNs.','Full orbit application, noise/border-noise handling, calibrated backscatter conversion and terrain-corrected geocoding were not run.','Raw DN summaries are not compared numerically with model training dB or RTC Gamma0.']};OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'product_count':len(rows),'manifest':OUT.relative_to(ROOT).as_posix(),'calibration_vectors':[[r['grd_item_id'],{k:v['calibration_xml']['calibration_vector_count'] for k,v in r['polarizations'].items()}] for r in rows]},indent=2))
if __name__=='__main__':main()
