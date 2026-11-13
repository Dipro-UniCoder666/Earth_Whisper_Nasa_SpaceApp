"""Inspect downloaded event COGs, cross-check acquisition pairs, and report limits."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RASTER_ENV = ROOT / "backend/.venv/Lib/site-packages"
if RASTER_ENV.exists():
    sys.path.append(str(RASTER_ENV))
import numpy as np
import rasterio
from rasterio.warp import transform_bounds


def inspect(path: Path) -> dict[str, Any]:
    with rasterio.open(path) as ds:
        if not ds.crs or ds.count != 1 or min(ds.width, ds.height) < 1:
            raise ValueError("Missing CRS, unexpected band count, or empty raster")
        stats = {"min": None, "p02": None, "median": None, "p98": None, "max": None,
                 "valid_pixels": 0, "total_pixels": int(ds.width * ds.height)}
        # Windowed scan bounds memory use and collects exact valid sample population values.
        rng = np.random.default_rng(42)
        sample = np.empty(0, dtype=np.float32)
        seen = 0
        minimum, maximum = float("inf"), float("-inf")
        sample_cap = 500_000
        nan_pixels = infinite_pixels = 0
        for _, win in ds.block_windows(1):
            raw = ds.read(1, window=win)
            if np.issubdtype(raw.dtype, np.floating):
                nan_pixels += int(np.isnan(raw).sum())
                infinite_pixels += int(np.isinf(raw).sum())
            a = ds.read(1, window=win, masked=True)
            vals = np.asarray(a.compressed())
            vals = vals[np.isfinite(vals)]
            if not vals.size:
                continue
            minimum = min(minimum, float(vals.min())); maximum = max(maximum, float(vals.max()))
            new_seen = seen + int(vals.size)
            if new_seen <= sample_cap:
                sample = np.concatenate((sample, vals.astype(np.float32, copy=False)))
            else:
                # Reservoir merge: choose a hypergeometric share from this
                # block and the existing uniform reservoir for bounded RAM.
                take_new = int(rng.hypergeometric(vals.size, seen, sample_cap))
                from_old = rng.choice(sample, sample_cap - take_new, replace=False) if take_new < sample_cap else np.empty(0, dtype=np.float32)
                from_new = rng.choice(vals, take_new, replace=False) if take_new else np.empty(0, dtype=np.float32)
                sample = np.concatenate((from_old, from_new)).astype(np.float32, copy=False)
            seen = new_seen
        if seen:
            stats.update(min=minimum, p02=float(np.percentile(sample, 2)),
                         median=float(np.median(sample)), p98=float(np.percentile(sample, 98)),
                         max=maximum, valid_pixels=seen, percentile_method="deterministic_seed_42_reservoir_sample",
                         percentile_sample_count=int(sample.size), nodata_or_masked_pixels=int(ds.width * ds.height - seen),
                         nan_pixels=nan_pixels, infinite_pixels=infinite_pixels)
        wgs84_bounds = list(transform_bounds(ds.crs, "EPSG:4326", *ds.bounds, densify_pts=21))
        try:
            relative_path = str(path.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            relative_path = str(path)
        return {"path": relative_path, "driver": ds.driver,
                "crs": str(ds.crs), "width": ds.width, "height": ds.height, "transform": list(ds.transform),
                "bounds": list(ds.bounds), "bounds_wgs84": wgs84_bounds, "resolution": list(ds.res), "dtype": ds.dtypes[0],
                "nodata": ds.nodata, "units": ds.units[0], "scale": ds.scales[0], "offset": ds.offsets[0],
                "mask_flags": [str(x) for x in ds.mask_flag_enums[0]],
                "descriptions": list(ds.descriptions), "tags": ds.tags(), "band_tags": ds.tags(1),
                "statistics": stats}


def _same_grid(a: dict, b: dict) -> bool:
    return a["crs"] == b["crs"] and [a["width"], a["height"]] == [b["width"], b["height"]] and np.allclose(a["transform"], b["transform"], atol=1e-8, rtol=0)


def main() -> None:
    manifest_path = ROOT / "data/gherproof/manifests/event_imagery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalogue = json.loads((ROOT / "data/gherproof/manifests/event_satellite_catalogue.json").read_text(encoding="utf-8"))
    aoi = catalogue.get("bbox_wgs84")
    records = manifest.get("records", [])
    by_scene: dict[str, dict[str, dict]] = {}
    failures = []
    for rec in records:
        if not rec.get("path"):
            rec["verification_status"] = rec.get("status", "not_downloaded")
            continue
        path = ROOT / rec["path"]
        try:
            if not path.is_file():
                raise FileNotFoundError("Manifest path is missing")
            if path.stat().st_size != rec.get("catalogue_bytes"):
                raise ValueError("Local byte size differs from catalogue asset size")
            qc = inspect(path)
            if aoi:
                left = max(qc["bounds_wgs84"][0], aoi[0]); bottom = max(qc["bounds_wgs84"][1], aoi[1])
                right = min(qc["bounds_wgs84"][2], aoi[2]); top = min(qc["bounds_wgs84"][3], aoi[3])
                overlap = max(0.0, right - left) * max(0.0, top - bottom)
                total = max(1e-12, (aoi[2] - aoi[0]) * (aoi[3] - aoi[1]))
                qc["provisional_bbox_overlap_fraction_degree_area"] = overlap / total
                qc["coverage_reference"] = "broad provisional catalogue search box, not Pallimangal enclosure"
            rec["verification_status"] = "verified"
            rec["raster_qc"] = qc
            by_scene.setdefault(rec["scene_id"], {})[rec["polarization"]] = qc
        except Exception as exc:
            rec["verification_status"] = "incompatible" if path.exists() else "download_failed"
            rec["verification_error"] = str(exc)[:240]
            failures.append({"scene_id": rec.get("scene_id"), "polarization": rec.get("polarization"), "error": str(exc)[:240]})
    scenes: dict[str, Any] = {}
    for scene_id, bands in by_scene.items():
        vv, vh = bands.get("VV"), bands.get("VH")
        intersection = None
        if vv and vh and vv["crs"] == vh["crs"]:
            left, bottom = max(vv["bounds"][0], vh["bounds"][0]), max(vv["bounds"][1], vh["bounds"][1])
            right, top = min(vv["bounds"][2], vh["bounds"][2]), min(vv["bounds"][3], vh["bounds"][3])
            intersection = [left, bottom, right, top] if left < right and bottom < top else None
        scenes[scene_id] = {"available_polarizations": sorted(bands),
                            "vv_vh_same_grid": _same_grid(vv, vh) if vv and vh else False,
                            "vv_vh_bounds_intersection": intersection}
    dates: dict[str, dict] = {}
    for rec in records:
        date = rec.get("date")
        if date:
            dates.setdefault(date, {})[rec.get("polarization", "")] = rec
    pair = {"dates": sorted(dates), "pre_event_date": "2026-01-07", "post_event_date": "2026-01-19",
            "pre_days_before_reported_incident": 7, "post_days_after_reported_incident": 5,
            "same_platform_orbit_direction_mode_product_family": None,
            "all_four_verified": False, "vv_vh_within_scene_grid_aligned": False,
            "pre_post_grid_compatible": False, "radiometric_comparability": "not_established",
            "terrain_correction_status": "not_established", "suitable_for_change_inference": False,
            "suitability_class": "not_evaluated",
            "suitability_reason": "Actual pre/post VV/VH raster products are not all locally verified."}
    if len(dates) == 2:
        all_verified = all(r.get("verification_status") == "verified" for group in dates.values() for r in group.values()) and all(set(group) >= {"VV", "VH"} for group in dates.values())
        pair["all_four_verified"] = all_verified
        pair["vv_vh_within_scene_grid_aligned"] = all(s.get("vv_vh_same_grid") for s in scenes.values()) and len(scenes) == 2
        pair["same_platform_orbit_direction_mode_product_family"] = all(
            len({r.get(k) for r in records if r.get("date") == day}) == 1
            for k in ("platform", "relative_orbit", "direction", "instrument_mode", "product_type", "processing_level")
            for day in dates)
        if all_verified:
            pre = next(r["raster_qc"] for r in records if r["date"] == "2026-01-07" and r["polarization"] == "VV")
            post = next(r["raster_qc"] for r in records if r["date"] == "2026-01-19" and r["polarization"] == "VV")
            pair["pre_post_grid_compatible"] = _same_grid(pre, post)
            units = {r["raster_qc"].get("units") for r in records}
            pair["radiometric_comparability"] = "same declared raster unit; calibration baseline still requires metadata verification" if len(units) == 1 and None not in units else "not established: raster unit/calibration metadata absent or inconsistent"
    if pair["all_four_verified"]:
        basic_geometry_ok = (pair["same_platform_orbit_direction_mode_product_family"] is True
                             and pair["vv_vh_within_scene_grid_aligned"] is True
                             and pair["pre_post_grid_compatible"] is True)
        if not basic_geometry_ok:
            pair["suitability_class"] = "unsuitable"
            pair["suitability_reason"] = "Verified rasters fail the same-platform/orbit/mode or pixel-grid compatibility checks."
        else:
            pair["suitability_class"] = "conditionally_suitable"
            pair["suitability_reason"] = "Basic product/grid compatibility passed; calibration, terrain correction, masks, valid coverage, and study-area adequacy still need confirmation."
    validation = {"updated_at_utc": datetime.now(timezone.utc).isoformat(), "input_manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
                  "asset_results": [{"date": r.get("date"), "scene_id": r.get("scene_id"), "polarization": r.get("polarization"),
                                     "status": r.get("verification_status", r.get("status")), "raster_qc": r.get("raster_qc"),
                                     "error": r.get("verification_error", r.get("error"))} for r in records],
                  "scene_results": scenes, "pre_post_assessment": pair,
                  "failures": failures,
                  "limitations": ["GRD/COG presence alone does not prove radiometric calibration or terrain correction.",
                                  "No common-grid reprojection is run until the source measurement units and processing provenance are established.",
                                  "No event water inference is emitted by this validator."]}
    manifest["records"] = records
    manifest["pre_post_assessment"] = pair
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    out = ROOT / "data/gherproof/manifests/event_imagery_validation.json"
    out.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(out.relative_to(ROOT)), "validated_assets": sum(r.get("verification_status") == "verified" for r in records),
                      "pre_post_suitable": pair["suitable_for_change_inference"]}, indent=2))


if __name__ == "__main__":
    main()
