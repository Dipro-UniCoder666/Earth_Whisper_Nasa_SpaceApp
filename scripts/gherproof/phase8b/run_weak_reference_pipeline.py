"""Build conservative Sentinel-2 weak references and compare existing SAR outputs.

This script never trains models and never writes to Phase 7 products/checkpoints or
the human annotation package. All outputs are scoped to phase8b directories.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

from weak_reference import (
    LABELS, CHANGE_LABELS, classify_change, classify_weak_reference,
    comparison_metrics, normalized_difference, spatial_block_summaries,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/gherproof"
PROC7 = DATA / "processed/phase7"
RAW = DATA / "regional/processed/phase6b/sentinel2"
OUT = DATA / "processed/phase8b"
OPT_OUT = OUT / "optical"
COMP_OUT = OUT / "comparison"
REGISTRY_PATH = DATA / "manifests/evidence_registry.json"
NODATA_FLOAT = -9999.0
NODATA_BYTE = 255
THRESHOLDS = {"ndwi": 0.0, "mndwi": 0.0}
SENSITIVITY = [-0.05, 0.0, 0.05]


class GridRef:
    """Small raster-grid descriptor used after the source dataset is closed."""
    def __init__(self, profile):
        self.profile = profile.copy()
        self.crs = self.profile.get("crs")
        self.transform = self.profile["transform"]
        self.width = self.profile["width"]
        self.height = self.profile["height"]
        self.res = (self.transform.a, abs(self.transform.e))

SCENES = {
    "2026-01-10": {
        "item": "S2B_MSIL2A_20260110T043049_R133_T45QYF_20260110T065859",
        "datetime": "2026-01-10T04:30:49.024000Z", "scl_date": "2026-01-10",
    },
    "2026-01-20": {
        "item": "S2B_MSIL2A_20260120T043009_R133_T45QYF_20260120T062559",
        "datetime": "2026-01-20T04:30:09.024000Z", "scl_date": "2026-01-20",
    },
}
SAR = [
    {"date": "2026-01-09", "utc": "2026-01-09T23:56:06Z", "orbit": 150, "direction": "descending", "s2": "2026-01-10"},
    {"date": "2026-01-12", "utc": "2026-01-12T12:12:34Z", "orbit": 12, "direction": "ascending", "s2": "2026-01-10"},
    {"date": "2026-01-21", "utc": "2026-01-21T23:56:05Z", "orbit": 150, "direction": "descending", "s2": "2026-01-20"},
    {"date": "2026-01-24", "utc": "2026-01-24T12:12:33Z", "orbit": 12, "direction": "ascending", "s2": "2026-01-20"},
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def json_load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_raster(path: Path, array: np.ndarray, ref, description: str, dtype: str, nodata, tags: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = ref.profile.copy()
    profile.update(driver="GTiff", count=1, dtype=dtype, nodata=nodata,
                   compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **profile) as ds:
        ds.write(array.astype(dtype, copy=False), 1)
        ds.set_band_description(1, description)
        ds.update_tags(**{str(k): str(v) for k, v in tags.items()})
    return path


def file_record(path: Path, ref=None):
    with rasterio.open(path) as ds:
        arr = ds.read(1, masked=True)
        data = arr.compressed()
        if data.size and np.issubdtype(data.dtype, np.floating):
            if not np.isfinite(data).all():
                raise RuntimeError(f"nonfinite values in {path}")
        return {
            "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size,
            "crs": ds.crs.to_string() if ds.crs else None, "transform": list(ds.transform),
            "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
            "width": ds.width, "height": ds.height, "resolution": list(ds.res),
            "dtype": ds.dtypes[0], "nodata": ds.nodata, "description": ds.descriptions[0],
            "valid_pixels": int(data.size), "nan_count": int(np.isnan(data).sum()) if np.issubdtype(data.dtype, np.floating) else 0,
            "inf_count": int(np.isinf(data).sum()) if np.issubdtype(data.dtype, np.floating) else 0,
            "reopened": True,
        }


def reproject_average(src_path: Path, dst_ref, band=1):
    with rasterio.open(src_path) as src:
        source = src.read(band, masked=True).astype("float32")
        values = source.filled(np.nan)
        valid = (~np.ma.getmaskarray(source)) & np.isfinite(values)
        dst = np.full((dst_ref.height, dst_ref.width), np.nan, dtype=np.float32)
        dst_valid_fraction = np.zeros(dst.shape, dtype=np.float32)
        reproject(values, dst, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=dst_ref.transform, dst_crs=dst_ref.crs, dst_nodata=np.nan,
                  resampling=Resampling.average)
        reproject(valid.astype(np.float32), dst_valid_fraction, src_transform=src.transform, src_crs=src.crs,
                  dst_transform=dst_ref.transform, dst_crs=dst_ref.crs, resampling=Resampling.average)
        # All four 10 m contributors must be valid; this avoids partial averages at cloud/nodata edges.
        return dst, dst_valid_fraction >= 0.999


def valid_source_mask(path: Path, band=1):
    with rasterio.open(path) as ds:
        ma = ds.read(band, masked=True)
        arr = ma.filled(np.nan)
        valid = (~np.ma.getmaskarray(ma)) & np.isfinite(arr)
        # Sentinel-2 L2A DN 0 is explicitly treated as invalid even if a source mask omits it.
        valid &= arr != 0
        if ds.nodata is not None:
            valid &= arr != ds.nodata
        return valid


def locate_inputs(date: str, scene: dict):
    item = scene["item"]
    raw10 = RAW / "l2a_stored_values_10m" / f"{date}_{item}_B03_B04_B08_10m_utm45n.tif"
    raw20 = RAW / "l2a_stored_values_20m" / f"{date}_{item}_B11_20m_utm45n.tif"
    scl = next((RAW / "scl").glob(f"{date}_{item}_SCL_20m.tif"))
    refl = PROC7 / "sentinel2"
    paths = {"raw10": raw10, "raw20": raw20, "scl": scl,
             "b03_existing": refl / f"{date}_B03_reflectance_10m.tif",
             "b08_existing": refl / f"{date}_B08_reflectance_10m.tif",
             "b11_existing": refl / f"{date}_B11_reflectance_20m.tif"}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError("missing existing optical inputs: " + ", ".join(missing))
    return paths


def build_optical():
    metadata = json_load(DATA / "manifests/phase7_sentinel2_radiometric_metadata.json")
    proc_manifest = json_load(DATA / "manifests/phase7_optical_processing.json")
    scenes_by_id = {x["item_id"]: x for x in metadata["scenes"]}
    opt_records, arrays, summaries, sensitivity = [], {}, [], []
    grid = None
    for date, scene in SCENES.items():
        meta = scenes_by_id.get(scene["item"])
        if not meta:
            raise RuntimeError(f"No L2A product metadata for {scene['item']}")
        if meta.get("datetime") != scene["datetime"]:
            raise RuntimeError(f"Acquisition timestamp mismatch for {scene['item']}")
        # This product's metadata records baseline 05.11, Q=10000, and -1000 per-band offsets.
        quant = int(meta["metadata_assets"]["product-metadata"]["values"]["BOA_QUANTIFICATION_VALUE"][0]["value"])
        offs = meta["metadata_assets"]["product-metadata"]["values"]["BOA_ADD_OFFSET"]
        if quant != 10000 or not offs or any(int(x["value"]) != -1000 for x in offs):
            raise RuntimeError(f"Unexpected L2A quantification or offset in {scene['item']}")
        offmap = proc_manifest["scenes"]
        manifest_scene = next(x for x in offmap if x["date"] == date)
        if manifest_scene["quantification_value"] != quant or any(int(v) != -1000 for v in manifest_scene["offsets"].values()):
            raise RuntimeError(f"Phase 7 reflectance processing metadata disagreement for {date}")
        p = locate_inputs(date, scene)
        with rasterio.open(p["raw20"]) as b11ds:
            ref = GridRef(b11ds.profile)
            profile_grid = (b11ds.crs, b11ds.transform, b11ds.width, b11ds.height, b11ds.res)
            if grid is None:
                grid = profile_grid
            elif profile_grid != grid:
                raise RuntimeError("Selected B11 rasters do not share the same 20 m comparison grid")
            b11dn = b11ds.read(1, masked=True).filled(np.nan).astype(np.float32)
            b11source_valid = valid_source_mask(p["raw20"])
            b11 = (b11dn - 1000.0) / quant
            b11valid = b11source_valid & np.isfinite(b11)
        with rasterio.open(p["raw10"]) as ds10:
            descriptions = [x or "" for x in ds10.descriptions]
            band = {name: next((i + 1 for i, d in enumerate(descriptions) if name in d.upper()), None) for name in ("B03", "B08")}
            if any(v is None for v in band.values()):
                # The project files have a known B03/B04/B08 stack order; assert count and use it only if tags are absent.
                if ds10.count != 3:
                    raise RuntimeError(f"Cannot identify B03/B08 bands in {p['raw10']}: {descriptions}")
                band = {"B03": 1, "B08": 3}
            scaled = {}
            masks20 = {}
            for name, bidx in band.items():
                raw = ds10.read(bidx, masked=True).astype(np.float32)
                dn = raw.filled(np.nan)
                valid10 = (~np.ma.getmaskarray(raw)) & np.isfinite(dn) & (dn != 0)
                refl10 = np.full(dn.shape, np.nan, dtype=np.float32)
                refl10[valid10] = (dn[valid10] - 1000.0) / quant
                temp_path = OUT / "tmp" / f"{date}_{name}_refl10_temp.tif"
                temp = np.where(valid10, refl10, NODATA_FLOAT).astype(np.float32)
                write_raster(temp_path, temp, ds10, f"{name} BOA reflectance, metadata-scaled once", "float32", NODATA_FLOAT, {"offset": -1000, "quantification": quant})
                scaled[name], masks20[name] = reproject_average(temp_path, ref)
                temp_path.unlink(missing_ok=True)
        green, green_v = scaled["B03"], masks20["B03"]
        nir, nir_v = scaled["B08"], masks20["B08"]
        source_bands_valid = green_v & nir_v & b11valid
        spectral_valid = source_bands_valid
        ndwi, ndwi_valid = normalized_difference(green, nir, spectral_valid)
        mndwi, mndwi_valid = normalized_difference(green, b11, spectral_valid)
        spectral_valid &= ndwi_valid & mndwi_valid
        with rasterio.open(p["scl"]) as sd:
            scl = sd.read(1, masked=True).filled(0).astype(np.uint8)
            scl_valid = (~np.ma.getmaskarray(sd.read(1, masked=True))) & (scl != 0)
            if sd.crs != ref.crs or sd.transform != ref.transform or sd.width != ref.width or sd.height != ref.height:
                aligned = np.full((ref.height, ref.width), 0, dtype=np.uint8)
                reproject(scl, aligned, src_transform=sd.transform, src_crs=sd.crs, dst_transform=ref.transform,
                          dst_crs=ref.crs, resampling=Resampling.nearest)
                scl = aligned
                scl_valid = scl != 0
        # If an index has no stable physical denominator, retain otherwise-clear pixels as uncertain, never binary.
        codes = classify_weak_reference(scl, ndwi, mndwi, spectral_valid, **{f"{k}_threshold": v for k, v in THRESHOLDS.items()})
        clear_observed = scl_valid & np.isin(scl, [2, 4, 5, 6, 7])
        codes[clear_observed & source_bands_valid & ~spectral_valid] = 3
        codes[clear_observed & ~source_bands_valid] = 0
        # Classes 0,1,3,8,9,10,11 and invalid source pixels remain invalid.
        arrays[date] = {"codes": codes, "ndwi": ndwi, "mndwi": mndwi, "observed": clear_observed & source_bands_valid,
                        "source_bands_valid": source_bands_valid, "spectral_valid": spectral_valid, "scl": scl, "ref_profile": ref.profile.copy(),
                        "transform": ref.transform, "crs": ref.crs, "shape": (ref.height, ref.width)}
        date_dir = OPT_OUT / date
        tags = {"algorithm": "SCL class and dual-index conservative agreement", "threshold_ndwi": THRESHOLDS["ndwi"],
                "threshold_mndwi": THRESHOLDS["mndwi"], "grid": "native Sentinel-2 B11 20m grid EPSG:32645",
                "B03_B08_resampling": "area-weighted average 10m to native B11 20m; require all source 10m pixels valid",
                "spectral_formula": "reflectance=(DN+BOA_ADD_OFFSET)/BOA_QUANTIFICATION_VALUE; NDWI=(B03-B08)/(B03+B08); MNDWI=(B03-B11)/(B03+B11)",
                "weak_water": "SCL 6 and NDWI>=0 and MNDWI>=0", "weak_nonwater": "SCL 4 or 5 and NDWI<0 and MNDWI<0",
                "uncertain": "SCL 2,4,5,6,7 with missing/low-signal or contradictory spectral support; class 7 retained as uncertain",
                "invalid_scl": "0,1,3,8,9,10,11, source nodata; cloud/shadow/defective classes excluded"}
        for kind, data, desc in (("weak_reference", codes, "0 invalid; 1 weak_water; 2 weak_nonwater; 3 uncertain"),
                                 ("weak_water_mask", np.where(np.isin(codes, [1, 2]), (codes == 1).astype(np.uint8), NODATA_BYTE), "1 weak water; 0 weak nonwater; 255 uncertain/invalid"),
                                 ("weak_nonwater_mask", np.where(np.isin(codes, [1, 2]), (codes == 2).astype(np.uint8), NODATA_BYTE), "1 weak nonwater; 0 weak water; 255 uncertain/invalid"),
                                 ("uncertainty_mask", np.where(codes == 0, NODATA_BYTE, (codes == 3).astype(np.uint8)), "1 uncertain optical reference; 0 weak binary class; 255 invalid"),
                                 ("ndwi_20m", np.where(ndwi_valid, ndwi, NODATA_FLOAT), "NDWI from 20m area-averaged B03/B08"),
                                 ("mndwi_20m", np.where(mndwi_valid, mndwi, NODATA_FLOAT), "MNDWI from area-averaged B03 and native B11"),
                                 ("scl_class", scl, "Sentinel-2 SCL class code")):
            dt = "uint8" if kind in ("weak_reference", "weak_water_mask", "weak_nonwater_mask", "uncertainty_mask", "scl_class") else "float32"
            nd = NODATA_BYTE if dt == "uint8" else NODATA_FLOAT
            outpath = date_dir / f"{kind}.tif"
            write_raster(outpath, data, ref, desc, dt, nd, {**tags, "acquisition_datetime_utc": scene["datetime"], "source_item": scene["item"]})
            opt_records.append({"kind": kind, **file_record(outpath), "acquisition_date": date, "source_item": scene["item"]})
        counts = {LABELS[i]: int(np.count_nonzero(codes == i)) for i in LABELS}
        denom_mask = codes != 0
        counts["weak_label_coverage_fraction_of_clear_observations"] = float(np.count_nonzero(np.isin(codes, [1, 2])) / max(1, np.count_nonzero(clear_observed)))
        counts["clear_observation_pixels"] = int(clear_observed.sum())
        counts["valid_dual_index_pixels"] = int(spectral_valid.sum())
        summaries.append({"date": date, "acquisition_datetime_utc": scene["datetime"], "item_id": scene["item"],
                          "counts": counts, "ndwi_valid_pixels": int(ndwi_valid.sum()), "mndwi_valid_pixels": int(mndwi_valid.sum()),
                          "index_invalid_low_signal_or_missing": int(np.count_nonzero(clear_observed & ~spectral_valid)),
                          "reflectance_crosscheck": validate_existing_reflectance(p, quant)})
        for t in SENSITIVITY:
            c = classify_weak_reference(scl, ndwi, mndwi, spectral_valid, t, t)
            sensitivity.append({"date": date, "threshold_ndwi": t, "threshold_mndwi": t,
                                "weak_water_pixels": int((c == 1).sum()), "weak_nonwater_pixels": int((c == 2).sum()),
                                "uncertain_pixels": int((c == 3).sum()), "invalid_pixels": int((c == 0).sum()),
                                "water_count_change_vs_primary": int((c == 1).sum() - (codes == 1).sum()),
                                "interpretation": "predeclared optical-only sensitivity; not chosen by SAR agreement"})
    # Pre/post temporal candidates on only jointly observed pixels.
    pre, post = arrays["2026-01-10"], arrays["2026-01-20"]
    change = classify_change(pre["codes"], post["codes"], pre["observed"], post["observed"])
    with rasterio.open(locate_inputs("2026-01-10", SCENES["2026-01-10"])["raw20"]) as ref:
        outpath = OPT_OUT / "temporal_change" / "2026-01-10_to_2026-01-20_change_candidates.tif"
        write_raster(outpath, change, ref, "0 invalid; 1 persistent water candidate; 2 possible new water; 3 possible water loss; 4 stable nonwater; 5 uncertain change",
                     "uint8", NODATA_BYTE, {"algorithm": "pre/post transition of independent optical weak-reference codes", "pre_date": "2026-01-10", "post_date": "2026-01-20", "thresholds": json.dumps(THRESHOLDS), "limitation": "two optical observations; change is not confirmed flood or incident attribution"})
        change_record = file_record(outpath)
        candidate = np.where(np.isin(change, [1, 2, 3, 4]), (change == 2).astype(np.uint8), NODATA_BYTE)
        candidate_path = OPT_OUT / "temporal_change" / "possible_new_water_candidate.tif"
        write_raster(candidate_path, candidate, ref, "1 possible optical new-water candidate; 0 other certain optical transitions; 255 uncertain or invalid",
                     "uint8", NODATA_BYTE, {"pre_date": "2026-01-10", "post_date": "2026-01-20", "definition": "pre weak_nonwater and post weak_water on joint valid pixels", "interpretation": "candidate only; not confirmed flood or incident attribution"})
        candidate_record = file_record(candidate_path)
    change_counts = {CHANGE_LABELS[i]: int((change == i).sum()) for i in CHANGE_LABELS}
    return arrays, {"status": "generated_independent_optical_weak_reference", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "methodology": {"thresholds_fixed_before_model_comparison": THRESHOLDS, "threshold_sensitivity": SENSITIVITY,
                                    "reflectance_source": "Phase 6B original stored-value SAFE-derived raster inputs; metadata offsets re-applied once for this derivation; existing Phase 7 scaled rasters used for cross-check only",
                                    "reflectance_formula": "(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE", "source_dn_zero_is_nodata": True,
                                    "BOA_quantification_value_per_scene": {d: 10000 for d in SCENES}, "BOA_add_offset_by_band_each_scene": {d: {"B03": -1000, "B08": -1000, "B11": -1000} for d in SCENES},
                                    "native_resolutions_m": {"B03": 10, "B08": 10, "B11": 20}, "common_grid": "EPSG:32645 native B11 20m grid; average 10m reflectance with all four inputs valid",
                                    "index_minimum_denominator": 0.02, "negative_reflectance": "excluded from normalized-difference index validity", "scl_interpretation": "water candidate 6; non-water candidates 4/5; 2/7 uncertain; 0/1/3/8/9/10/11 invalid", "water_rule": "SCL 6 AND NDWI>=0 AND MNDWI>=0", "nonwater_rule": "SCL 4/5 AND NDWI<0 AND MNDWI<0", "uncertain_rule": "conflicting indicators or SCL 2/7; clear context with unusable/low-signal index retained uncertain", "model_prediction_used_in_label_creation": False},
                    "scenes": summaries, "threshold_sensitivity": sensitivity,
                    "temporal_change": {"pre_date": "2026-01-10", "post_date": "2026-01-20", "counts": change_counts, "raster": change_record,
                                        "outputs": [{"kind": "temporal_change", "acquisition_date": None, **change_record}, {"kind": "possible_new_water_candidate", "acquisition_date": None, **candidate_record}],
                                        "jointly_observed_pixels": int((pre["observed"] & post["observed"]).sum()),
                                        "limitations": ["Only two optical observations; changes may reflect aquaculture, crop, irrigation, wet soil, rainfall or classification variability.", "No attribution to Pallimangal or a breach is supported."]},
                    "outputs": opt_records, "limitations": ["Weak references are automated optical indicators, not human labels or field truth.", "SCL class 6 may include permanent/aquaculture water; not flood attribution.", "SCL 4/5 and index signs can be confused by vegetation, wet soil, shadow, turbidity and mixed pixels.", "Only Jan 10 and Jan 20 optical reflectance/index scenes are available for this comparison."]}


def validate_existing_reflectance(paths, quant):
    # Compare existing phase7 reflectance against the original DN-derived result on jointly valid pixels.
    summaries = {}
    for band, srcpath in (("B03", paths["raw10"]), ("B08", paths["raw10"])):
        with rasterio.open(srcpath) as ds:
            desc = [x or "" for x in ds.descriptions]
            bidx = next((i + 1 for i, d in enumerate(desc) if band in d.upper()), 1 if band == "B03" else 3)
            raw = ds.read(bidx, masked=True).astype(np.float32)
            dn = raw.filled(np.nan)
            valid = (~np.ma.getmaskarray(raw)) & np.isfinite(dn) & (dn != 0)
            derived = (dn[valid] - 1000.0) / quant
        with rasterio.open(paths[f"{band.lower()}_existing"]) as existing:
            ex = existing.read(1, masked=True).astype(np.float32)
            values = ex.filled(np.nan)
            aligned_valid = valid & (~np.ma.getmaskarray(ex)) & np.isfinite(values)
            diff = np.abs(values[aligned_valid] - ((dn[aligned_valid] - 1000.0) / quant))
            summaries[band] = {"overlap_pixels": int(aligned_valid.sum()), "max_abs_difference": float(diff.max()) if diff.size else None,
                               "allclose_at_1e-6": bool(np.all(diff <= 1e-6)) if diff.size else False,
                               "existing_reflectance_path": paths[f"{band.lower()}_existing"].relative_to(ROOT).as_posix()}
    # B11 lives on the 20 m grid and should agree directly with its existing scaled product.
    with rasterio.open(paths["raw20"]) as rawds, rasterio.open(paths["b11_existing"]) as exds:
        raw = rawds.read(1, masked=True).astype(np.float32)
        dn = raw.filled(np.nan)
        ex = exds.read(1, masked=True).astype(np.float32)
        ev = ex.filled(np.nan)
        m = (~np.ma.getmaskarray(raw)) & (~np.ma.getmaskarray(ex)) & np.isfinite(dn) & np.isfinite(ev) & (dn != 0)
        diff = np.abs(ev[m] - ((dn[m] - 1000.0) / quant))
        summaries["B11"] = {"overlap_pixels": int(m.sum()), "max_abs_difference": float(diff.max()) if diff.size else None,
                             "allclose_at_1e-6": bool(np.all(diff <= 1e-6)) if diff.size else False,
                             "existing_reflectance_path": paths["b11_existing"].relative_to(ROOT).as_posix()}
    return summaries


def date_offset(sar_utc: str, optical_utc: str):
    a = datetime.fromisoformat(sar_utc.replace("Z", "+00:00"))
    b = datetime.fromisoformat(optical_utc.replace("Z", "+00:00"))
    hours = (a - b).total_seconds() / 3600.0
    return {"difference_hours_sar_minus_s2": round(hours, 3), "absolute_difference_hours": round(abs(hours), 3)}


def warp_probability(path: Path, ref):
    with rasterio.open(path) as src:
        prob = src.read(1, masked=True).astype(np.float32)
        arr = prob.filled(np.nan)
        valid = (~np.ma.getmaskarray(prob)) & np.isfinite(arr)
        if src.nodata is not None:
            valid &= arr != src.nodata
        p20 = np.full((ref.height, ref.width), np.nan, np.float32)
        fraction = np.zeros(p20.shape, np.float32)
        reproject(arr, p20, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=ref.transform, dst_crs=ref.crs, dst_nodata=np.nan, resampling=Resampling.average)
        reproject(valid.astype(np.float32), fraction, src_transform=src.transform, src_crs=src.crs,
                  dst_transform=ref.transform, dst_crs=ref.crs, resampling=Resampling.average)
        ok = (fraction >= 0.999) & np.isfinite(p20) & (p20 >= 0) & (p20 <= 1)
        return p20, ok


def build_comparisons(optical_arrays):
    inference = json_load(DATA / "manifests/phase7_inference_manifest.json")
    raster_qc = json_load(DATA / "manifests/phase7_raster_qc_manifest.json")
    registry = json_load(REGISTRY_PATH)
    inference_records = [x for x in registry["records"] if x.get("evidence_category") == "model_prediction" and x.get("evidence_id", "").startswith("prediction-") and x.get("evidence_id", "").endswith("-probability")]
    model_paths = {}
    for model in ("scratch", "pretrained"):
        for s in SAR:
            candidate = next((x for x in inference_records if x.get("metadata", {}).get("model") == model and x.get("acquisition_date") == s["date"]), None)
            if not candidate or not candidate.get("derived_file", {}).get("path"):
                # Phase 8 registry records store probability products in derived_file for these scenes.
                raise RuntimeError(f"Registry probability product missing: {model} {s['date']}")
            path = ROOT / candidate["derived_file"]["path"]
            if not path.is_file():
                raise FileNotFoundError(path)
            model_paths[(model, s["date"])] = (path, candidate)
    results, output_records, time_matches = [], [], []
    for s in SAR:
        refopt = optical_arrays[s["s2"]]
        refpath = PROC7 / "sentinel2" / f"{s['s2']}_MNDWI_20m.tif"
        with rasterio.open(refpath) as ref:
            if ref.crs.to_string() != "EPSG:32645" or tuple(ref.res) != (20.0, 20.0):
                raise RuntimeError(f"Unexpected comparison grid for {refpath}")
            optcodes = refopt["codes"]
            observed = refopt["observed"]
            # Revalidate reference grid shape/transform via generated optical output grid.
            if optcodes.shape != (ref.height, ref.width) or refopt["transform"] != ref.transform:
                raise RuntimeError("Optical and MNDWI common grid mismatch")
            optical_label_valid = np.isin(optcodes, [1, 2])
            optical_source_valid = observed
            sar_utc = s["utc"]
            optical_utc = SCENES[s["s2"]]["datetime"]
            match = {"sentinel1_date": s["date"], "sentinel1_acquisition_datetime_utc": sar_utc,
                     "relative_orbit": s["orbit"], "direction": s["direction"], "sentinel2_date": s["s2"],
                     "sentinel2_acquisition_datetime_utc": optical_utc, **date_offset(sar_utc, optical_utc),
                     "status": "nearest_optical_observation; date-near but not simultaneous", "same_geometry_pairing": False}
            time_matches.append(match)
            model_predictions = {}
            for model in ("scratch", "pretrained"):
                path, record = model_paths[(model, s["date"])]
                prob, sar_valid = warp_probability(path, ref)
                predicted = prob >= 0.5
                common_data = sar_valid & optical_source_valid
                common_labels = sar_valid & optical_label_valid
                metrics = comparison_metrics(optcodes, predicted, common_data)
                metrics["joint_valid_observation_pixels"] = int(common_data.sum())
                metrics["weak_reference_uncertain_with_valid_sar_pixels"] = int((sar_valid & (optcodes == 3)).sum())
                metrics["sar_valid_but_optical_invalid_pixels"] = int((sar_valid & ~optical_source_valid).sum())
                metrics["optical_observed_but_sar_invalid_pixels"] = int((~sar_valid & optical_source_valid).sum())
                metrics["comparison_label"] = "weak_reference_agreement; not local accuracy"
                metrics["date_offset_hours"] = match["difference_hours_sar_minus_s2"]
                metrics["model"] = model
                metrics["sentinel1_date"] = s["date"]
                metrics["sentinel1_relative_orbit"] = s["orbit"]
                metrics["sentinel1_direction"] = s["direction"]
                metrics["sentinel2_date"] = s["s2"]
                metrics["input_probability_path"] = path.relative_to(ROOT).as_posix()
                metrics["input_probability_sha256"] = sha256(path)
                context_rows = []
                for scl_code in (2, 4, 5, 6, 7):
                    cell = sar_valid & optical_source_valid & (refopt["scl"] == scl_code)
                    labeled = cell & optical_label_valid
                    agree = labeled & (((optcodes == 1) & predicted) | ((optcodes == 2) & ~predicted))
                    context_rows.append({"scl_class": scl_code, "sar_and_optical_observed_pixels": int(cell.sum()),
                                         "weak_labeled_pixels": int(labeled.sum()), "uncertain_pixels": int((cell & (optcodes == 3)).sum()),
                                         "model_predicted_water_pixels": int((cell & predicted).sum()),
                                         "agreement_on_weak_labeled_pixels": int(agree.sum()),
                                         "weak_reference_agreement": int(agree.sum()) / int(labeled.sum()) if labeled.any() else None})
                metrics["scl_context_breakdown"] = context_rows
                block_summary, blocks = spatial_block_summaries(optcodes, predicted, common_data, 0, 0)
                block_summary["map_block_centroids_epsg32645"] = []
                # Convert coarse block centers to projected coordinates; do not imply village identities.
                for b in blocks:
                    r0, c0, r1, c1 = b["bounds_pixel_window"][1], b["bounds_pixel_window"][0], b["bounds_pixel_window"][3], b["bounds_pixel_window"][2]
                    x = ref.transform.c + ((c0 + c1) / 2) * ref.transform.a
                    y = ref.transform.f + ((r0 + r1) / 2) * ref.transform.e
                    b["centroid_x"] = x; b["centroid_y"] = y
                block_summary["map_block_centroids_epsg32645"] = [
                    {"block_row": b["block_row"], "block_col": b["block_col"], "x": b["centroid_x"], "y": b["centroid_y"]} for b in blocks]
                metrics["spatial_block_summary"] = block_summary
                metrics["spatial_blocks"] = blocks
                # Threshold sensitivity is evaluated against alternative optical-only references, never tuned to SAR.
                sensitivity_results = []
                for t in SENSITIVITY:
                    c = classify_weak_reference(refopt["scl"], refopt["ndwi"], refopt["mndwi"], refopt["spectral_valid"], t, t)
                    sens = comparison_metrics(c, predicted, sar_valid & refopt["observed"])
                    sensitivity_results.append({"threshold_ndwi": t, "threshold_mndwi": t, **sens})
                metrics["optical_threshold_sensitivity_metrics"] = sensitivity_results
                # Categorical evidence comparison layer; uncertainty and unavailable remain distinct codes.
                agr = np.full(optcodes.shape, NODATA_BYTE, dtype=np.uint8)
                agr[sar_valid & refopt["observed"]] = 4  # optically observed but uncertain or unresolved
                evaluable = sar_valid & optical_label_valid
                agr[evaluable] = 3
                agr[evaluable & predicted & (optcodes == 1)] = 1
                agr[evaluable & ~predicted & (optcodes == 2)] = 2
                agreement = np.full(optcodes.shape, NODATA_BYTE, dtype=np.uint8)
                disagreement = np.full(optcodes.shape, NODATA_BYTE, dtype=np.uint8)
                agreement[evaluable] = 0
                disagreement[evaluable] = 0
                agree_mask = evaluable & (((optcodes == 1) & predicted) | ((optcodes == 2) & ~predicted))
                agreement[agree_mask] = 1
                disagreement[evaluable & ~agree_mask] = 1
                binary_layer = np.where(sar_valid, predicted.astype(np.uint8), NODATA_BYTE)
                cov = np.zeros(optcodes.shape, dtype=np.uint8)
                cov[sar_valid & optical_source_valid] = 1
                cov[sar_valid & ~optical_source_valid] = 2
                cov[~sar_valid & optical_source_valid] = 3
                model_predictions[model] = {"probability": prob, "valid": sar_valid, "binary": predicted}
                stem = f"{s['date']}_{model}"
                for kind, arr, desc, dtype, nodata in (
                    ("probability_20m_mean", np.where(sar_valid, prob, NODATA_FLOAT), "Mean Sentinel-1 probability over valid 10m contributors; 20m", "float32", NODATA_FLOAT),
                    ("model_water_prediction_20m", binary_layer, "1 model-predicted water; 0 model-predicted nonwater; 255 invalid SAR", "uint8", NODATA_BYTE),
                    ("agreement_codes", agr, "1 water candidate agreement; 2 nonwater agreement; 3 weak-reference disagreement; 4 optical uncertain; 255 SAR unavailable", "uint8", NODATA_BYTE),
                    ("sar_optical_agreement_mask", agreement, "1 SAR and optical weak reference agree; 0 disagree; 255 unavailable or uncertain", "uint8", NODATA_BYTE),
                    ("sar_optical_disagreement_mask", disagreement, "1 SAR and optical weak reference disagree; 0 agree; 255 unavailable or uncertain", "uint8", NODATA_BYTE),
                    ("joint_coverage_codes", cov, "1 both valid; 2 SAR only; 3 optical only; 0 neither", "uint8", NODATA_BYTE),
                ):
                    out = COMP_OUT / "sar_optical" / stem / f"{kind}.tif"
                    write_raster(out, arr, ref, desc, dtype, nodata,
                                 {"model": model, "sentinel1_date": s["date"], "sentinel2_date": s["s2"],
                                  "optical_weak_reference_thresholds": json.dumps(THRESHOLDS), "probability_aggregation": "area mean of 10m to aligned 20m cells; require all four SAR contributors valid",
                                  "interpretation": "exploratory cross-sensor evidence comparison; not flood label or local model accuracy"})
                    frec = file_record(out)
                    output_records.append({"kind": kind, "model": model, "date": s["date"], **frec})
                results.append(metrics)
            # Same-date model disagreement and three-way candidate consensus retain disagreement.
            both_valid = model_predictions["scratch"]["valid"] & model_predictions["pretrained"]["valid"]
            sm = model_predictions["scratch"]["binary"]
            pm = model_predictions["pretrained"]["binary"]
            disagreement = np.full(optcodes.shape, NODATA_BYTE, dtype=np.uint8)
            disagreement[both_valid] = 1
            disagreement[both_valid & (sm != pm)] = 2
            consensus = np.full(optcodes.shape, NODATA_BYTE, dtype=np.uint8)
            joint = both_valid & optical_source_valid
            consensus[joint] = 3
            consensus[joint & (optcodes == 3)] = 4
            allwater = joint & (optcodes == 1) & sm & pm
            allnonwater = joint & (optcodes == 2) & ~sm & ~pm
            consensus[allwater] = 1
            consensus[allnonwater] = 2
            for kind, arr, desc in (("model_disagreement_codes", disagreement, "1 models agree; 2 scratch/pretrained binary predictions disagree; 255 unavailable"),
                                    ("multi_source_candidate_codes", consensus, "1 multi_source_candidate_agreement water; 2 all-source weak-nonwater agreement; 3 source disagreement; 4 optical uncertain; 255 unavailable")):
                out = COMP_OUT / "model_consensus" / s["date"] / f"{kind}.tif"
                write_raster(out, arr, ref, desc, "uint8", NODATA_BYTE,
                             {"sentinel1_date": s["date"], "sentinel2_date": s["s2"], "interpretation": "candidate agreement only; never confirmed flood extent"})
                output_records.append({"kind": kind, "date": s["date"], **file_record(out)})
    return results, output_records, time_matches


def register_outputs(optical_manifest, comparison, comparison_outputs):
    registry = json_load(REGISTRY_PATH)
    known = {r["evidence_id"] for r in registry["records"]}
    proc_date = datetime.now(timezone.utc).date().isoformat()
    records = []
    def add(eid, category, title, pathrec, acquisition_date, methodology, limitations, metadata, input_refs):
        if eid in known:
            # Deterministic IDs support safe reruns; update only records created by this phase.
            old = next(r for r in registry["records"] if r["evidence_id"] == eid)
            old.update({"evidence_category": category, "title": title, "acquisition_date": acquisition_date,
                        "processing_date": proc_date,
                        "spatial_coverage": {"crs": pathrec["crs"], "bounds": pathrec["bounds"], "resolution_m": pathrec["resolution"], "width": pathrec["width"], "height": pathrec["height"], "aoi_status": "provisional regional search raster footprint"},
                        "crs": pathrec["crs"], "confidence_or_validation_status": "exploratory", "processing_methodology": methodology,
                        "derived_file": {"path": pathrec["path"], "availability": "available", "bytes": pathrec["bytes"], "sha256": pathrec["sha256"], "checksum_matches_manifest": True},
                        "metadata": metadata, "source_provenance": input_refs, "limitations": limitations})
            return
        records.append({"evidence_id": eid, "evidence_category": category, "title": title, "source_dataset": "GherProof Phase 8B derived evidence",
                        "acquisition_date": acquisition_date, "processing_date": proc_date,
                        "spatial_coverage": {"crs": pathrec["crs"], "bounds": pathrec["bounds"], "resolution_m": pathrec["resolution"], "width": pathrec["width"], "height": pathrec["height"], "aoi_status": "provisional regional search raster footprint"},
                        "crs": pathrec["crs"], "original_file": None,
                        "derived_file": {"path": pathrec["path"], "availability": "available", "bytes": pathrec["bytes"], "sha256": pathrec["sha256"], "checksum_matches_manifest": True},
                        "confidence_or_validation_status": "exploratory", "processing_methodology": methodology,
                        "limitations": limitations, "source_provenance": input_refs, "metadata": metadata})
    optical_refs = ["data/gherproof/manifests/phase7_sentinel2_radiometric_metadata.json", "data/gherproof/manifests/phase7_optical_processing.json"]
    for out in optical_manifest["outputs"]:
        date, kind = out["acquisition_date"], out["kind"]
        cat = "optical_weak_reference" if kind in ("weak_reference", "weak_water_mask", "weak_nonwater_mask", "temporal_change", "possible_new_water_candidate") else "uncertainty_layer" if kind == "uncertainty_mask" else "derived_satellite_measurement"
        eid = f"optical-weakref-{date}-{kind}"
        add(eid, cat, f"Sentinel-2 {date} {kind.replace('_',' ')} on 20m comparison grid", out, date,
            "S2 L2A metadata-scaled reflectance; 10m B03/B08 area-averaged onto native B11 20m; fixed dual-index and SCL consensus",
            optical_manifest["limitations"], {"threshold_configuration": {**THRESHOLDS, "sensitivity": SENSITIVITY}, "algorithm": "dual-index SCL consensus", "validity_mask": "SCL and source pixel validity; low signal excluded from index decisions", "status": "exploratory optical weak reference"}, optical_refs + ["data/gherproof/manifests/phase8b_weak_reference_manifest.json"])
    for out in optical_manifest["temporal_change"]["outputs"]:
        eid = f"optical-weakref-temporal-{out['kind']}"
        add(eid, "optical_weak_reference", f"Sentinel-2 Jan 10 to Jan 20 {out['kind'].replace('_',' ')}", out, None,
            "Transition classification of independently generated optical weak-reference labels on jointly observed pixels",
            optical_manifest["temporal_change"]["limitations"], {"thresholds": THRESHOLDS, "algorithm": out["kind"], "acquisition_dates": ["2026-01-10", "2026-01-20"], "validity_mask": "valid clear SCL and valid source bands on both dates", "status": "exploratory optical change candidate"}, optical_refs + ["data/gherproof/manifests/phase8b_weak_reference_manifest.json"])
    for out in comparison_outputs:
        kind = out["kind"]
        cat = "model_prediction" if kind in ("probability_20m_mean", "model_water_prediction_20m") else "uncertainty_layer" if kind in ("model_disagreement_codes", "joint_coverage_codes") else "model_comparison"
        eid = f"phase8b-{out.get('date')}-{out.get('model','all')}-{kind}"
        add(eid, cat, f"Phase 8B {out.get('date')} {out.get('model','multi-source')} {kind.replace('_',' ')}", out, out.get("date"),
            "Area-average existing 10m Sentinel-1 probability to common 20m S2 B11 grid; joint masks and frozen threshold 0.5",
            ["Weak-reference consistency is not field validation, local accuracy, flood extent or causal attribution.", "Geographic coverage is a provisional raster footprint, not village or enclosure boundaries."],
            {"model": out.get("model"), "threshold_configuration": {"optical": THRESHOLDS, "model_binary": 0.5}, "algorithm": kind,
             "validity_mask": "all four Sentinel-1 10m source cells valid plus optical observation mask", "status": "exploratory cross-sensor comparison"},
            ["data/gherproof/manifests/phase7_inference_manifest.json", "data/gherproof/manifests/phase8b_weak_reference_comparison.json", "data/gherproof/manifests/phase8b_weak_reference_manifest.json"])
    registry["records"].extend(records)
    counts = {}
    for rec in registry["records"]:
        counts[rec["evidence_category"]] = counts.get(rec["evidence_category"], 0) + 1
    registry["record_count"] = len(registry["records"])
    registry["category_counts"] = dict(sorted(counts.items()))
    registry["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    avail_path = DATA / "manifests/phase8_data_availability.json"
    avail = json_load(avail_path)
    avail["generated_at_utc"] = registry["generated_at_utc"]
    avail["registry_record_count"] = registry["record_count"]
    avail["category_counts"] = registry["category_counts"]
    avail["phase8b"] = {"optical_weak_reference": "generated", "model_comparison": "generated exploratory consistency analysis", "model_readiness": "exploratory_only", "human_reference_status": "human_review_pending", "impact_quantification": "not_approved"}
    files = []
    for rec in registry["records"]:
        for key in ("original_file", "derived_file"):
            f = rec.get(key)
            if f and f.get("path"):
                files.append((ROOT / f["path"], f))
    avail["file_inventory"] = {"available": sum(p.is_file() for p, _ in files), "unavailable": sum(not p.is_file() for p, _ in files),
                                "invalid_path": 0, "checksum_mismatches": sum(p.is_file() and sha256(p) != f.get("sha256") for p, f in files)}
    avail_path.write_text(json.dumps(avail, indent=2) + "\n", encoding="utf-8")
    return records


def main():
    OPT_OUT.mkdir(parents=True, exist_ok=True)
    COMP_OUT.mkdir(parents=True, exist_ok=True)
    arrays, optical_manifest = build_optical()
    # Freeze and persist optical-only thresholds before any SAR prediction is read.
    threshold_config = {"thresholds": THRESHOLDS, "sensitivity": SENSITIVITY,
                        "selection_basis": "neutral normalized-difference sign threshold with independent SCL+NDWI+MNDWI consensus; selected without reading SAR predictions",
                        "frozen_before_sar_comparison": True, "model_prediction_used": False,
                        "created_at_utc": datetime.now(timezone.utc).isoformat()}
    (DATA / "manifests/phase8b_optical_threshold_config.json").write_text(json.dumps(threshold_config, indent=2) + "\n", encoding="utf-8")
    optical_path = DATA / "manifests/phase8b_weak_reference_manifest.json"
    optical_path.write_text(json.dumps(optical_manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    comp_results, comp_outputs, time_matches = build_comparisons(arrays)
    comparison = {"status": "exploratory_weak_reference_consistency_only", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                  "optical_thresholds_fixed_before_sar_comparison": THRESHOLDS, "model_probability_threshold": 0.5,
                  "temporal_matches": time_matches, "per_model_acquisition_results": comp_results,
                  "outputs": comp_outputs, "model_readiness": "exploratory_only", "human_reference_status": "human_review_pending", "impact_quantification": "not_approved",
                  "aggregate_model_ranking": "not_performed; acquisition geometry and weak-reference limits preclude model selection",
                  "spatial_dependence": "5km block summaries are descriptive variability only; no pixel-independent confidence intervals computed",
                  "limitations": ["Optical weak references are not human truth or field validation.", "Sentinel-1 and Sentinel-2 acquisition times differ; report each exact temporal offset.", "Ascending and descending Sentinel-1 geometries are assessed separately per acquisition and never pooled as a common temporal series.", "The 20m grid is the native Sentinel-2 B11 grid; Sentinel-1 probabilities use area-mean aggregation from 10m with all source cells valid.", "Regional footprint is provisional and cannot support village-specific statistics or impact-area claims.", "No confirmed flooding, embankment failure, crop impact, fish loss or causality is inferred."]}
    comparison_path = DATA / "manifests/phase8b_weak_reference_comparison.json"
    comparison_path.write_text(json.dumps(comparison, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    new_records = register_outputs(optical_manifest, comparison, comp_outputs)
    # Include processing-level product files and comparison manifest in a compact reproducibility QC index.
    all_tifs = sorted([p for p in OUT.rglob("*.tif") if p.is_file()])
    qc = [file_record(p) for p in all_tifs]
    (DATA / "manifests/phase8b_raster_qc_manifest.json").write_text(json.dumps({"status": "all_phase8b_geotiffs_reopened", "raster_count": len(qc), "rasters": qc}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"optical_dates": optical_manifest["scenes"], "temporal_change_counts": optical_manifest["temporal_change"]["counts"],
                      "comparison_count": len(comp_results), "raster_count": len(qc), "new_registry_records": len(new_records),
                      "registry_record_count": json_load(REGISTRY_PATH)["record_count"], "comparison_manifest": comparison_path.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
