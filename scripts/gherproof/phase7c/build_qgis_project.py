"""Build a prediction-blind QGIS XML project and visual annotation guide.

QGIS is not installed in the current runtime. This creates portable QGS XML and
validates its XML/data-source paths; opening in QGIS must be verified on a host
with QGIS before claiming application-level compatibility.
"""
from __future__ import annotations
from pathlib import Path
import os
import sqlite3
import hashlib,json
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'data/gherproof/reference/phase7c'
QGS=OUT/'gherproof_optical_annotation.qgs'
CRS='EPSG:32645'

def add_layer(tree,projectlayers,layer_id,name,source,provider,kind,checked,fields=None):
    ET.SubElement(tree,'layer-tree-layer',{'id':layer_id,'name':name,'source':source,'providerKey':provider,'checked':'Qt::Checked' if checked else 'Qt::Unchecked','expanded':'1'})
    attrs={'type':kind,'name':name,'hasScaleBasedVisibilityFlag':'0','styleCategories':'AllStyleCategories'}
    layer=ET.SubElement(projectlayers,'maplayer',attrs)
    ET.SubElement(layer,'id').text=layer_id
    ET.SubElement(layer,'datasource').text=source
    ET.SubElement(layer,'layername').text=name
    spatial=ET.SubElement(layer,'srs');srs=ET.SubElement(spatial,'spatialrefsys');ET.SubElement(srs,'authid').text=CRS;ET.SubElement(srs,'description').text='WGS 84 / UTM zone 45N';ET.SubElement(srs,'projectionacronym').text='utm';ET.SubElement(srs,'ellipsoid').text='EPSG:7030';ET.SubElement(srs,'geographicflag').text='false'
    ET.SubElement(layer,'provider').text=provider
    ET.SubElement(layer,'extent')
    if layer_id in ('optical_pre','optical_post'):
        renderer=ET.SubElement(layer,'rasterrenderer',{'type':'multibandcolor','opacity':'1','alphaBand':'-1','invertColor':'0','gradient':'BlackToWhite','maxOversampling':'2'})
        ET.SubElement(renderer,'redBand').text='1';ET.SubElement(renderer,'greenBand').text='2';ET.SubElement(renderer,'blueBand').text='3'
        for channel in ('red','green','blue'):
            ce=ET.SubElement(renderer,f'{channel}ContrastEnhancement');ET.SubElement(ce,'minValue').text='0';ET.SubElement(ce,'maxValue').text='0.4';ET.SubElement(ce,'algorithm').text='StretchToMinimumMaximum'
    if kind=='vector':
        ET.SubElement(layer,'vectorjoins')
        ET.SubElement(layer,'layerDependencies')
        ET.SubElement(layer,'dataProvider')
        if fields:
            form=ET.SubElement(layer,'attributeEditorForm',{'tabLayout':'tab','title':'Optical reference annotation'})
            containers=ET.SubElement(form,'attributeEditorContainer',{'name':'Label review','showLabel':'1','columnCount':'1'})
            with sqlite3.connect(OUT/'gherproof_optical_reference_samples_editable.gpkg') as con:
                actual=[r[1] for r in con.execute('pragma table_info(samples)') if r[1]!='geom']
            indices={n:i for i,n in enumerate(actual)}
            for field in fields:
                if field in indices: ET.SubElement(containers,'attributeEditorField',{'name':field,'index':str(indices[field]),'showLabel':'1'})
            if name.startswith('07 —'):
                renderer=ET.SubElement(layer,'renderer-v2',{'type':'singleSymbol','symbollevels':'0','enableorderby':'0'})
                symbols=ET.SubElement(renderer,'symbols');symbol=ET.SubElement(symbols,'symbol',{'type':'marker','name':'0','alpha':'1','clip_to_extent':'1','force_rhr':'0'})
                sym_layer=ET.SubElement(symbol,'layer',{'class':'SimpleMarker','enabled':'1','pass':'0'})
                options=ET.SubElement(sym_layer,'Option',{'type':'Map'})
                for key,value in [('name','circle'),('color','255,193,7,255'),('outline_color','35,51,66,255'),('outline_width','0.35'),('size','2.4'),('size_unit','MM')]:
                    ET.SubElement(options,'Option',{'name':key,'type':'QString','value':value})
    return layer

def build_project():
    root=ET.Element('qgis',{'projectname':'GherProof optical human reference annotation','version':'3.34.0-Prizren','saveUserFull':'true'})
    ET.SubElement(root,'homePath',{'path':'.'});ET.SubElement(root,'title').text='GherProof — prediction-blind optical reference review (Jan 10 / Jan 20, 2026)'
    pc=ET.SubElement(root,'projectCrs');ss=ET.SubElement(pc,'spatialrefsys');ET.SubElement(ss,'authid').text=CRS;ET.SubElement(ss,'description').text='WGS 84 / UTM zone 45N';ET.SubElement(ss,'projectionacronym').text='utm';ET.SubElement(ss,'ellipsoid').text='EPSG:7030';ET.SubElement(ss,'geographicflag').text='false'
    tree=ET.SubElement(root,'layer-tree-group',{'name':'','checked':'Qt::Checked','expanded':'1'});layers=ET.SubElement(root,'projectlayers')
    # Inputs: no Sentinel-1 model predictions or model disagreement layers are included.
    composite10=OUT/'2026-01-10_S2_false_colour_B08_B04_B03.tif';composite20=OUT/'2026-01-20_S2_false_colour_B08_B04_B03.tif'
    add_layer(tree,layers,'optical_pre','01 — Sentinel-2 Jan 10 false colour (R=B08, G=B04, B=B03)',composite10.name,'gdal','raster',True)
    add_layer(tree,layers,'optical_post','02 — Sentinel-2 Jan 20 false colour (R=B08, G=B04, B=B03)',composite20.name,'gdal','raster',False)
    g=ROOT/'data/gherproof/regional/processed/phase6b/sentinel2'
    scl10=next((g/'scl').glob('2026-01-10_S2B*_SCL_20m.tif'));scl20=next((g/'scl').glob('2026-01-20_S2B*_SCL_20m.tif'))
    clear10=next((g/'clear_masks').glob('2026-01-10_S2B*_clear_20m.tif'));clear20=next((g/'clear_masks').glob('2026-01-20_S2B*_clear_20m.tif'))
    add_layer(tree,layers,'scl_pre','03 — Jan 10 S2B SCL classes (toggle for inspection)',Path(os.path.relpath(scl10,OUT)).as_posix(),'gdal','raster',False)
    add_layer(tree,layers,'scl_post','04 — Jan 20 S2B SCL classes (toggle for inspection)',Path(os.path.relpath(scl20,OUT)).as_posix(),'gdal','raster',False)
    add_layer(tree,layers,'clear_pre','05 — Jan 10 SCL clear-pixel mask',Path(os.path.relpath(clear10,OUT)).as_posix(),'gdal','raster',False)
    add_layer(tree,layers,'clear_post','06 — Jan 20 SCL clear-pixel mask',Path(os.path.relpath(clear20,OUT)).as_posix(),'gdal','raster',False)
    gpkg='gherproof_optical_reference_samples_editable.gpkg|layername=samples'
    fields=['sample_id','pre_label','pre_confidence','pre_notes','post_label','post_confidence','post_notes','reviewed_status','sampling_stratum','split_group','sample_weight','pre_reviewer','post_reviewer','pre_review_date','post_review_date','pre_label_source','post_label_source','needs_second_review_reason','pre_second_label','pre_second_confidence','pre_second_notes','post_second_label','post_second_confidence','post_second_notes','second_reviewer','second_review_date','pre_review_disagreement','post_review_disagreement']
    add_layer(tree,layers,'samples','07 — Editable optical reference samples (450; no predictions)',gpkg,'ogr','vector',True,fields)
    aoi=Path('../../regional/six_village_regional_search_extent.geojson')
    add_layer(tree,layers,'aoi','08 — Provisional regional search extent (not village boundaries)',aoi.as_posix(),'ogr','vector',True)
    ET.SubElement(root,'visibility-presets')
    ET.SubElement(root,'projectViewSettings')
    canvas=ET.SubElement(root,'mapcanvas',{'name':'theMapCanvas','annotationsVisible':'1','rotation':'0'})
    extent=ET.SubElement(canvas,'extent')
    for key,val in [('xmin','729410'),('ymin','2536410'),('xmax','760520'),('ymax','2557970')]: ET.SubElement(extent,key).text=val
    ET.SubElement(canvas,'rotation').text='0';ET.SubElement(canvas,'projectionsEnabled').text='1';ET.SubElement(canvas,'destinationsrs').append(ET.Element('spatialrefsys'))
    ET.indent(root,space='  ')
    ET.ElementTree(root).write(QGS,encoding='utf-8',xml_declaration=True)
    parsed=ET.parse(QGS).getroot();sources=[x.text for x in parsed.findall('./projectlayers/maplayer/datasource')]
    missing=[]
    for src in sources:
        f=src.split('|')[0];p=(OUT/f).resolve()
        if not p.exists(): missing.append((src,str(p)))
    if missing: raise FileNotFoundError(f'QGIS project source paths missing: {missing}')
    if any('phase7/inference' in s.lower() or 'probability' in s.lower() or 'disagreement' in s.lower() for s in sources): raise ValueError('Predictions must not be part of the blinded project')
    return sources

def guide_image():
    w,h=1500,2250;im=Image.new('RGB',(w,h),'#f7f8fa');d=ImageDraw.Draw(im)
    try: title=ImageFont.truetype('arial.ttf',52);head=ImageFont.truetype('arial.ttf',32);body=ImageFont.truetype('arial.ttf',26)
    except OSError: title=head=body=ImageFont.load_default()
    y=55
    def wrap(text,font,width=1350):
        nonlocal y
        words=text.split();line=''
        for word in words:
            trial=(line+' '+word).strip()
            if d.textbbox((0,0),trial,font=font)[2]>width and line:
                d.text((75,y),line,fill='#1f2937',font=font);y+=font.size+12;line=word
            else:line=trial
        if line:d.text((75,y),line,fill='#1f2937',font=font);y+=font.size+16
    def section(text):
        nonlocal y
        y+=14;d.rounded_rectangle((55,y,1445,y+54),radius=10,fill='#dceafe');d.text((75,y+7),text,fill='#12345b',font=head);y+=68
    d.text((55,y),'GherProof | Optical Reference Review',fill='#12345b',font=title);y+=80
    wrap('Offline reviewer guide • Sentinel-2 observations: 10 January and 20 January 2026 • Labels are human optical interpretations, not field-verified ground truth.',body)
    section('1. Open and review the project')
    wrap('Open gherproof_optical_annotation.qgs in QGIS. The project has no Sentinel-1 model predictions or disagreement layers. Turn on the Jan 10 or Jan 20 composite as needed; the SCL and clear-mask layers are initially hidden and can be toggled for validity context.',body)
    wrap('Select a sample point and edit its attributes. Preserve sample_id, coordinates, sampling_stratum, spatial_block, split_group, inclusion_probability and sample_weight. Do not change split assignments.',body)
    section('2. Assign each date separately')
    wrap('For Jan 10 enter pre_label, pre_confidence and pre_notes. For Jan 20 enter post_label, post_confidence and post_notes. Record reviewer, review date and label source for each assigned date label. Use water, non_water, uncertain or invalid. Confidence is high, medium or low. Use reviewed_status=reviewed only after reviewing both date slots; use needs_second_review if either needs another reviewer.',body)
    section('3. Interpretation cues')
    wrap('Open water: coherent dark/low-reflectance patches or channels with spatial continuity. Confirm surrounding context; shallow or turbid water can be bright and may resemble soil.',body)
    wrap('Aquaculture ponds: regular pond cells and embankments may indicate managed ponds, not event inundation. Do not infer fish loss or breach from imagery.',body)
    wrap('Vegetated water: vegetation can obscure water and create mixed spectral response. If water cannot be confidently distinguished, choose uncertain.',body)
    wrap('Wet soil: damp or saturated soil may resemble shallow water; look for texture, field boundaries and continuity, but do not guess.',body)
    wrap('Dry soil and agricultural vegetation: exposed dry fields, crop rows and uniform vegetation are non_water only when water is not visibly present at the sample. Record crop/soil context in notes without assigning a crop type from assumption.',body)
    wrap('Shadow: terrain/building/cloud shadow may appear dark. Use shape and context; choose uncertain if unresolved.',body)
    wrap('Cloud and cloud shadow: inspect SCL and the clear mask. If obscured/invalid at the point, label invalid; partial ambiguity is uncertain.',body)
    wrap('Mixed pixels: a 10 m pixel can contain water, vegetation, soil, roads or pond edge. Choose uncertain where the dominant surface cannot be identified.',body)
    section('4. Independence and data handling')
    wrap('Do not look up or use any model map while labeling. Stratum values are blind codes; do not use them to infer the expected answer. Labels are not field verification. Keep uncertain and invalid distinct. The split is frozen: calibration and validation are development subsets; test is the final independent evaluation subset.',body)
    wrap('Keep an untouched copy before editing. Optional second-review fields are provided for both dates. If two reviewers label the same point, record their separate labels/confidence and mark agree, disagree or unresolved; do not overwrite the first reviewer record. A second reviewer should inspect uncertain samples and a shared subset when available.',body)
    im.save(OUT/'GHERPROOF_OPTICAL_ANNOTATION_GUIDE.png')

if __name__=='__main__':
    src=build_project();guide_image()
    def checksum(p):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1<<20),b''):h.update(b)
        return h.hexdigest()
    mp=ROOT/'data/gherproof/manifests/phase7c_annotation_workflow_manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
    manifest.update({'qgis_project_sha256':checksum(QGS),'qgis_project_layers':src,'qgis_primary_view_has_model_outputs':False,'annotation_guide_image_sha256':checksum(OUT/'GHERPROOF_OPTICAL_ANNOTATION_GUIDE.png'),'qgis_open_test':'blocked_qgis_not_installed'})
    mp.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print({'project':str(QGS.relative_to(ROOT)),'layers':len(src),'guide':str((OUT/'GHERPROOF_OPTICAL_ANNOTATION_GUIDE.png').relative_to(ROOT))})
