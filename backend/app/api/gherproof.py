"""DHARA event provenance API; never serves unverified predictions."""

from io import BytesIO
import json
import logging
from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.services import gherproof_service as service
from app.services import gherproof_screening_service as screening
from app.services import gherproof_report_service as reports
from app.schemas.gherproof_evidence import EvidenceListResponse, LayerMetadataResponse, ReportIndexResponse, SceneResponse, ScreeningStatusResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gherproof", tags=["DHARA"])


@router.get("/status")
def get_status():
    # Preserve the original event-case fields consumed by the current UI while
    # adding the regional Phase 8 readiness contract at the same stable route.
    return {**service.status(), **screening.screening_status()}


@router.get("/catalogue")
def get_catalogue():
    return service.catalogue()


@router.get("/evidence-report")
def get_evidence_report():
    return JSONResponse(
        service.evidence_report(),
        headers={"Content-Disposition": 'attachment; filename="dhara-event-evidence.json"'},
    )


@router.get("/boundary")
def get_boundary():
    return service.boundary_record()


@router.put("/boundary")
def put_boundary(feature: dict):
    try:
        return service.save_boundary(feature)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/context/sentinel2")
def get_sentinel2_context():
    path = service.DATA / "processed" / "sentinel2" / "2026-01-13_sentinel2_visual_provisional_locality.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Contextual imagery is unavailable")
    return FileResponse(path, media_type="image/png", filename=path.name)


@router.get("/weak-reference")
def get_weak_reference():
    """Return optical weak-reference summary and registered layers, never as ground truth."""
    return screening.weak_reference()


@router.get("/comparisons")
def get_weak_reference_comparisons():
    """Return model-to-optical weak-reference consistency metrics and coverage products."""
    return screening.comparisons()


@router.get("/scenarios/{scenario_id}")
def get_demonstration_scenario(scenario_id: str):
    try:
        result = screening.scenario(scenario_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if not result:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return result


@router.get("/model-comparison")
def get_model_comparison():
    path = service.DATA / "manifests" / "pretrained_model_comparison.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Pretrained model comparison has not completed")
    return FileResponse(path, media_type="application/json", filename=path.name)


# Phase 8 evidence-aware regional screening endpoints. Existing event and
# boundary routes above remain compatible and unchanged.
@router.get("/screening/status", response_model=ScreeningStatusResponse)
def get_screening_status():
    return screening.screening_status()


@router.get("/evidence", response_model=EvidenceListResponse)
def get_evidence(
    category: str | None = Query(None),
    status: str | None = Query(None),
    acquisition_date: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    allowed={"verified_satellite_observation","catalogue_metadata","derived_satellite_measurement","historical_landcover_context","model_prediction","optical_reference_interpretation","optical_weak_reference","model_comparison","uncertainty_layer","news_reported_event","provisional_geographic_reference","human_verified_evidence"}
    states={"verified","derived","exploratory","provisional","unavailable","under_review"}
    if category and category not in allowed: raise HTTPException(422,"Unknown evidence category")
    if status and status not in states: raise HTTPException(422,"Unknown evidence status")
    return screening.evidence_list(category,status,acquisition_date,offset,limit)


@router.get("/scenes", response_model=SceneResponse)
def get_screening_scenes(): return screening.scenes()


@router.get("/predictions")
def get_predictions(model: str | None = Query(None,pattern=r"^(scratch|pretrained)$")):
    return screening.predictions(model)


@router.get("/optical")
def get_optical_evidence(): return screening.optical()


@router.get("/coverage")
def get_screening_coverage(): return screening.coverage()


@router.get("/limitations")
def get_screening_limitations(): return screening.limitations()


@router.get("/layers")
def get_layers():
    items=[]
    for r in screening.registry().get('records',[]):
        for asset in ('derived','original'):
            f=r.get(f'{asset}_file') or {}
            if f.get('availability')=='available' and f.get('path','').lower().endswith(('.tif','.tiff')):
                items.append({'evidence_id':r['evidence_id'],'asset':asset,'title':r['title'],'status':r['confidence_or_validation_status'],'evidence_category':r['evidence_category'],'url':f"/api/gherproof/layers/{r['evidence_id']}/file?asset={asset}",'metadata_url':f"/api/gherproof/layers/{r['evidence_id']}",'crs':r.get('crs'),'acquisition_date':r.get('acquisition_date'),'sha256':f.get('sha256')})
    return {'count':len(items),'layers':items}


@router.get("/layers/{evidence_id}", response_model=LayerMetadataResponse)
def get_layer_metadata(evidence_id: str, asset: str = Query('derived',pattern=r"^(derived|original)$")):
    try:return screening.raster_metadata(evidence_id,asset)
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc
    except FileNotFoundError as exc:raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    except RuntimeError as exc:raise HTTPException(503,str(exc)) from exc


@router.get("/layers/{evidence_id}/file")
def get_layer_file(evidence_id: str,asset: str=Query('derived',pattern=r"^(derived|original)$")):
    try:r,path=screening.raster_path(evidence_id,asset)
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc
    except FileNotFoundError as exc:raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    return FileResponse(path,media_type='image/tiff',filename=path.name,headers={'Cache-Control':'public, max-age=3600','X-Evidence-Id':evidence_id,'X-Evidence-Status':r['confidence_or_validation_status']})


@router.get("/layers/{evidence_id}/preview.png")
def get_layer_preview(evidence_id: str, bbox: str = Query(..., description='west,south,east,north in EPSG:4326'), band: int = Query(1, ge=1), width: int = Query(900, ge=64, le=1200), asset: str = Query('derived', pattern=r"^(derived|original)$"), rgb: bool = Query(False)):
    """Render a bounded, transparent PNG preview from a registered raster window.

    This is a visualization of stored raster values, not a water classification.
    """
    try:
        vals = [float(x.strip()) for x in bbox.split(',')]
        if len(vals) != 4 or not all(__import__('math').isfinite(x) for x in vals):
            raise ValueError('bbox must contain four finite numbers')
        west, south, east, north = vals
        if west >= east or south >= north or west < -180 or east > 180 or south < -90 or north > 90:
            raise ValueError('bbox must be ordered longitude/latitude bounds in EPSG:4326')
        record, path = screening.raster_path(evidence_id, asset)
        env = screening.ROOT / 'backend/.venv/Lib/site-packages'
        if env.exists() and str(env) not in sys.path:
            sys.path.append(str(env))
        import numpy as np
        import rasterio
        from PIL import Image
        from rasterio.enums import Resampling
        from rasterio.warp import transform_bounds
        from rasterio.windows import Window, from_bounds

        display_path = path
        if rgb:
            acquisition_date = record.get('acquisition_date')
            if evidence_id == f"s2-true-colour-{acquisition_date}" and acquisition_date in ('2026-01-10', '2026-01-20'):
                # Registered three-band reflectance raster; R/G/B are B04/B03/B02.
                display_path = path
            elif evidence_id == f"s2-{acquisition_date}-B08" and acquisition_date in ('2026-01-10', '2026-01-20'):
                # Legacy, explicitly-labelled false-colour composite.
                display_path = screening.ROOT / 'data/gherproof/reference/phase7c' / f'{acquisition_date}_S2_false_colour_B08_B04_B03.tif'
            else:
                raise ValueError('RGB preview is available only for registered Jan 10/20 Sentinel-2 RGB evidence')
            if not display_path.is_file():
                raise FileNotFoundError('Registered Sentinel-2 RGB composite is unavailable')

        with rasterio.open(display_path) as ds:
            if ds.crs is None:
                raise ValueError('Raster CRS is missing')
            if not rgb and band > ds.count:
                raise ValueError(f'Band {band} exceeds raster band count {ds.count}')
            projected = transform_bounds('EPSG:4326', ds.crs, west, south, east, north, densify_pts=21)
            win = from_bounds(*projected, transform=ds.transform).round_offsets().round_lengths()
            c0, r0 = max(0, int(win.col_off)), max(0, int(win.row_off))
            c1, r1 = min(ds.width, int(win.col_off + win.width)), min(ds.height, int(win.row_off + win.height))
            if c1 <= c0 or r1 <= r0:
                raise FileNotFoundError('Requested map extent does not overlap the raster')
            win = Window(c0, r0, c1-c0, r1-r0)
            out_h = max(1, min(1200, round(width * win.height / max(win.width, 1))))
            values = ds.read([1, 2, 3] if rgb else band, window=win, out_shape=(3, out_h, width) if rgb else (out_h, width), resampling=Resampling.nearest, masked=True)
            raw = np.asarray(values.data, dtype='float32')
            if rgb:
                valid = np.isfinite(raw).all(axis=0) & ~np.ma.getmaskarray(values).any(axis=0)
            else:
                valid = np.isfinite(raw) & ~np.ma.getmaskarray(values)
            key = evidence_id.lower()
            rgba = np.zeros((raw.shape[1], raw.shape[2], 4) if rgb else (*raw.shape, 4), dtype='uint8')

            if rgb:
                # True-colour composites and the labelled legacy false-colour
                # products use the same fixed visualization range, not a class scale.
                for channel in range(3):
                    rgba[..., channel] = (np.clip(np.nan_to_num(raw[channel], nan=0.0) / 0.4, 0, 1) * 255).astype('uint8')
                rgba[..., 3] = np.where(valid, 255, 0).astype('uint8')
            elif 'temporal_change' in key:
                # Phase 8B composite classes: 0 invalid, 1 persistent water,
                # 2 possible new water, 3 possible water loss, 4 stable nonwater,
                # 5 uncertain. Use a legend-compatible display palette.
                palette = {
                    0: (105, 116, 126, 150), 1: (28, 91, 126, 205),
                    2: (56, 199, 229, 225), 3: (232, 76, 176, 225),
                    4: (116, 132, 124, 105), 5: (151, 158, 165, 195),
                }
                for code, color in palette.items():
                    rgba[valid & (raw == code)] = color
            elif 'clark-2022-aquaculture-context' in key:
                palette = {
                    1: (30, 112, 112, 220), 2: (80, 150, 170, 220),
                    3: (25, 197, 170, 238), 4: (39, 115, 190, 210),
                    5: (138, 143, 113, 90), 6: (158, 160, 164, 170),
                }
                for code, color in palette.items():
                    rgba[valid & (raw == code)] = color
            elif 'worldcover-2021-landcover-context' in key:
                palette = {
                    10: (0, 100, 0, 205), 20: (255, 187, 34, 205), 30: (255, 255, 76, 205),
                    40: (240, 150, 255, 205), 50: (250, 0, 0, 220), 60: (180, 180, 180, 185),
                    70: (240, 240, 240, 220), 80: (0, 100, 200, 210), 90: (0, 150, 160, 210),
                    95: (0, 207, 117, 210), 100: (250, 230, 160, 205),
                }
                for code, color in palette.items():
                    rgba[valid & (raw == code)] = color
            elif any(term in key for term in ('weakref', 'weak_reference', 'agreement', 'disagreement', 'coverage-code', 'coverage_codes')):
                palette = {
                    0: (110, 125, 139, 115), 1: (27, 150, 164, 210), 2: (47, 79, 110, 205),
                    3: (224, 163, 67, 220), 4: (191, 76, 61, 220), 5: (121, 91, 173, 220),
                }
                for code, color in palette.items():
                    rgba[valid & (raw == code)] = color
            elif any(term in key for term in ('mask', 'binary', 'candidate')):
                rgba[valid & (raw > 0)] = (27, 145, 176, 215)
                rgba[valid & (raw <= 0)] = (0, 0, 0, 0)
            elif 'uncertainty' in key or 'entropy' in key:
                scaled = np.clip(np.nan_to_num(raw, nan=0.0), 0, 1)
                rgba[..., 0] = (215 + 40 * scaled).astype('uint8')
                rgba[..., 1] = (170 - 120 * scaled).astype('uint8')
                rgba[..., 2] = (55 + 30 * scaled).astype('uint8')
                rgba[..., 3] = np.where(valid, 210, 0).astype('uint8')
            elif evidence_id.startswith('nisar-gcov-change-'):
                # Signed temporal gamma0 ratio: blue=lower, neutral=near zero, red=higher.
                # This is a display stretch only and does not imply water likelihood.
                if valid.any():
                    limit = max(float(np.percentile(np.abs(raw[valid]), 98)), 1e-6)
                    scaled = np.clip(np.nan_to_num(raw / limit, nan=0.0), -1, 1)
                    negative = valid & (scaled < 0)
                    positive = valid & (scaled >= 0)
                    magnitude = np.abs(scaled)
                    rgba[negative, 0] = (245 - 195 * magnitude[negative]).astype('uint8')
                    rgba[negative, 1] = (245 - 55 * magnitude[negative]).astype('uint8')
                    rgba[negative, 2] = 245
                    rgba[positive, 0] = 245
                    rgba[positive, 1] = (245 - 190 * magnitude[positive]).astype('uint8')
                    rgba[positive, 2] = (245 - 190 * magnitude[positive]).astype('uint8')
                    rgba[..., 3] = np.where(valid, 210, 0).astype('uint8')
            else:
                # Generic display stretch: percentile-scaled stored measurement only.
                if valid.any():
                    lo, hi = np.percentile(raw[valid], [2, 98])
                    scaled = np.clip(np.nan_to_num((raw - lo) / max(float(hi-lo), 1e-9), nan=0.0), 0, 1)
                    rgba[..., 0] = (28 + 205 * scaled).astype('uint8')
                    rgba[..., 1] = (74 + 130 * scaled).astype('uint8')
                    rgba[..., 2] = (120 + 70 * (1-scaled)).astype('uint8')
                    rgba[..., 3] = np.where(valid, 205, 0).astype('uint8')
            image = Image.fromarray(rgba, mode='RGBA')
            output = BytesIO()
            image.save(output, format='PNG', optimize=True)
            bounds = ds.window_bounds(win)
            geographic_bounds = transform_bounds(ds.crs, 'EPSG:4326', *bounds, densify_pts=21)
        return StreamingResponse(BytesIO(output.getvalue()), media_type='image/png', headers={
            'Cache-Control': 'private, max-age=300', 'X-Evidence-Id': evidence_id,
            'X-Evidence-Status': record['confidence_or_validation_status'],
            'X-Preview-Display': ('S2 true-colour RGB B04/B03/B02' if evidence_id.startswith('s2-true-colour-') else 'S2 false-colour B08/B04/B03') + ', reflectance display stretch 0-0.4' if rgb else ('NISAR signed gamma0 change display stretch: blue=lower, red=higher; not water classification' if evidence_id.startswith('nisar-gcov-change-') else 'display-only raster preview'),
            'X-Preview-Bounds-WGS84': ','.join(f'{v:.8f}' for v in geographic_bounds),
        })
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, f'Unable to render raster preview: {type(exc).__name__}') from exc


@router.get("/layers/{evidence_id}/clip")
def get_layer_clip(evidence_id: str,bbox: str=Query(...,description='xmin,ymin,xmax,ymax in EPSG:4326'),asset: str=Query('derived',pattern=r"^(derived|original)$")):
    try:
        vals=[float(x.strip()) for x in bbox.split(',')]
        if len(vals)!=4 or not all(__import__('math').isfinite(x) for x in vals):raise ValueError('bbox must contain four finite numbers')
        west,south,east,north=vals
        if west>=east or south>=north or west < -180 or east > 180 or south < -90 or north > 90:raise ValueError('bbox must be ordered longitude/latitude bounds in EPSG:4326')
        r,path=screening.raster_path(evidence_id,asset)
        env=screening.ROOT/'backend/.venv/Lib/site-packages'
        if env.exists() and str(env) not in sys.path:sys.path.append(str(env))
        import rasterio
        from rasterio.windows import from_bounds,Window
        from rasterio.warp import transform_bounds
        from rasterio.io import MemoryFile
        with rasterio.open(path) as ds:
            if ds.crs is None:raise ValueError('Raster has no CRS and cannot be clipped geographically')
            projected=transform_bounds('EPSG:4326',ds.crs,west,south,east,north,densify_pts=21)
            win=from_bounds(*projected,transform=ds.transform).round_offsets().round_lengths()
            col0=max(0,int(win.col_off));row0=max(0,int(win.row_off));col1=min(ds.width,int(win.col_off+win.width));row1=min(ds.height,int(win.row_off+win.height))
            if col1<=col0 or row1<=row0:raise ValueError('Requested bounds do not overlap this raster')
            win=Window(col0,row0,col1-col0,row1-row0)
            if win.width*win.height>4_000_000:raise OverflowError('Clip exceeds 4 million pixels; request a smaller bounding box')
            data=ds.read(window=win,masked=True);profile=ds.profile.copy();profile.update(width=int(win.width),height=int(win.height),transform=ds.window_transform(win),compress='deflate')
            with MemoryFile() as mem:
                with mem.open(**profile) as dst:
                    dst.write(data.filled(ds.nodata if ds.nodata is not None else 0))
                    if ds.nodata is None and np_ma_masked(data):dst.write_mask((~data.mask.any(axis=0)).astype('uint8')*255)
                    for i,desc in enumerate(ds.descriptions,1):
                        if desc:dst.set_band_description(i,desc)
                    dst.update_tags(EVIDENCE_ID=evidence_id,EVIDENCE_STATUS=r['confidence_or_validation_status'],CLIP_BBOX_EPSG4326=bbox)
                payload=mem.read()
        return StreamingResponse(BytesIO(payload),media_type='image/tiff',headers={'Content-Disposition':f'attachment; filename="{evidence_id}_clip.tif"','Cache-Control':'no-store','X-Evidence-Status':r['confidence_or_validation_status']})
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc
    except FileNotFoundError as exc:raise HTTPException(404,str(exc)) from exc
    except OverflowError as exc:raise HTTPException(413,str(exc)) from exc
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    except Exception as exc:
        if isinstance(exc,HTTPException):raise
        raise HTTPException(422,f'Unable to clip raster: {type(exc).__name__}') from exc


def np_ma_masked(data):
    try:return bool(data.mask.any())
    except AttributeError:return False


@router.get("/geography/{evidence_id}")
def get_evidence_geojson(evidence_id: str):
    try:r,path=screening.geojson_path(evidence_id)
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc
    except FileNotFoundError as exc:raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    try:
        geo=json.loads(path.read_text(encoding='utf-8'))
        from shapely.geometry import shape
        if geo.get('type')=='Feature':features=[geo]
        elif geo.get('type')=='FeatureCollection' and isinstance(geo.get('features'),list):features=geo['features']
        else:raise ValueError('invalid GeoJSON type')
        if not features:raise ValueError('empty GeoJSON feature collection')
        for feature in features:
            if feature.get('type')!='Feature' or not isinstance(feature.get('geometry'),dict):raise ValueError('invalid GeoJSON feature')
            geom=shape(feature['geometry'])
            if geom.is_empty or not geom.is_valid:raise ValueError('invalid GeoJSON geometry')
            if evidence_id=='geography-provisional-regional-aoi':
                x0,y0,x1,y1=geom.bounds
                if x0 < -180 or x1 > 180 or y0 < -90 or y1 > 90:raise ValueError('provisional AOI must use longitude/latitude coordinates')
    except FileNotFoundError:
        logger.warning('Registered optional GeoJSON is unavailable: evidence_id=%s path=%s', evidence_id, path)
        return JSONResponse(status_code=404, content={'status':'unavailable','evidence_id':evidence_id,'reason':'Registered GeoJSON evidence is not present in this checkout.'})
    except (json.JSONDecodeError,ValueError) as exc:raise HTTPException(422,'Stored GeoJSON failed validation') from exc
    return JSONResponse(geo,headers={'Cache-Control':'public, max-age=3600','X-Evidence-Id':evidence_id,'X-Evidence-Status':r['confidence_or_validation_status']})


@router.get("/reports", response_model=ReportIndexResponse)
def list_screening_reports():
    docs=service.ROOT/'docs';names=['GHERPROOF_PHASE4_REPORT.md','GHERPROOF_PHASE4B_REPORT.md','GHERPROOF_PHASE5_REPORT.md','GHERPROOF_PHASE6_REPORT.md','GHERPROOF_PHASE6B_REPORT.md','GHERPROOF_PHASE7_REPORT.md','GHERPROOF_PHASE7B_REPORT.md','GHERPROOF_PHASE7C_REPORT.md']
    return {'generated_at_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'reports':[{'name':n,'available':(docs/n).is_file(),'url':f'/api/gherproof/reports/files/{n}'} for n in names],'evidence_summary':screening.registry().get('category_counts',{})}


@router.get("/reports/files/{name}")
def get_screening_report_file(name:str):
    allowed={'GHERPROOF_PHASE4_REPORT.md','GHERPROOF_PHASE4B_REPORT.md','GHERPROOF_PHASE5_REPORT.md','GHERPROOF_PHASE6_REPORT.md','GHERPROOF_PHASE6B_REPORT.md','GHERPROOF_PHASE7_REPORT.md','GHERPROOF_PHASE7B_REPORT.md','GHERPROOF_PHASE7C_REPORT.md','GHERPROOF_GRD_PROCESSING_COMPATIBILITY.md','GHERPROOF_OPTICAL_ANNOTATION_WORKFLOW.md','GHERPROOF_INDEPENDENT_EVALUATION_PROTOCOL.md'}
    if name not in allowed:raise HTTPException(404,'Report not found')
    path=service.ROOT/'docs'/name
    if not path.is_file():raise HTTPException(404,'Report not available')
    return FileResponse(path,media_type='text/markdown',filename=path.name,headers={'Cache-Control':'public, max-age=3600'})


@router.get("/reports/summary")
def get_generated_screening_report():return reports.build_report()


@router.get("/reports/summary.md")
def get_generated_screening_report_markdown():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(reports.build_markdown(),media_type='text/markdown; charset=utf-8')
