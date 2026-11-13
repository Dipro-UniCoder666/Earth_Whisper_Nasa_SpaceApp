"""Validate matching NISAR subsets and write a non-classificatory gamma0 change layer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/gherproof/processed/nisar/validated"
DATES = ("2026-10-23", "2026-11-04")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    products = {}
    for frequency, suffix in (("A", ""), ("B", "_frequencyB_80m")):
        src = [DATA / f"nisar_{date}_track170_ascending_validated{suffix}" for date in DATES]
        rasters = [rasterio.open(f"{prefix}_gamma0_power.tif") for prefix in src]
        masks = [rasterio.open(f"{prefix}_valid_mask.tif") for prefix in src]
        try:
            a, b = rasters
            checks = {
                "same_crs": a.crs == b.crs,
                "same_transform": a.transform == b.transform,
                "same_dimensions": (a.width, a.height) == (b.width, b.height),
                "same_resolution": a.res == b.res,
                "same_nodata": a.nodata == b.nodata,
                "valid_masks_aligned": masks[0].transform == masks[1].transform and (masks[0].width, masks[0].height) == (masks[1].width, masks[1].height),
            }
            if not all(checks.values()):
                raise RuntimeError(f"NISAR frequency-{frequency} temporal inputs are not aligned: {checks}")
            power0, power1 = a.read(), b.read()
            valid0, valid1 = masks[0].read() > 0, masks[1].read() > 0
            valid = valid0 & valid1 & np.isfinite(power0) & np.isfinite(power1) & (power0 > 0) & (power1 > 0)
            delta = np.full(power0.shape, -9999.0, dtype=np.float32)
            delta[valid] = (10.0 * np.log10(power1[valid] / power0[valid])).astype(np.float32)
            resolution = int(round(abs(a.res[0])))
            out = DATA / f"nisar_2026-10-23_to_2026-11-04_track170{suffix}_gamma0_change_db.tif"
            profile = a.profile.copy()
            profile.update(count=2, dtype="float32", nodata=-9999.0, compress="deflate", predictor=3, BIGTIFF="IF_SAFER")
            with rasterio.open(out, "w", **profile) as dst:
                dst.write(delta[0], 1); dst.write(delta[1], 2)
                dst.set_band_description(1, "HHHH gamma0 change, 10log10(Nov04/Oct23), dB")
                dst.set_band_description(2, "HVHV gamma0 change, 10log10(Nov04/Oct23), dB")
                dst.update_tags(mission="NASA-ISRO NISAR", source="ASF DAAC", product_maturity="VALIDATED",
                                relative_orbit="170", orbit_direction="ascending", comparison_dates="2026-10-23/2026-11-04",
                                frequency_grid=f"frequency{frequency}", resolution_m=str(resolution),
                                units="dB ratio of like-for-like linear gamma0 covariance power",
                                interpretation="Exploratory temporal backscatter change only; not a water/flood probability or fisheries impact map.",
                                limitations="Two later observations only; not January event evidence; surface, vegetation, moisture and acquisition noise effects remain.")
            aoi_manifest_path = DATA / f"nisar_{DATES[0]}_track170_ascending_validated{suffix}_manifest.json"
            aoi_pixels = int(json.loads(aoi_manifest_path.read_text(encoding="utf-8"))["aoi_pixels"])
            stats = {}
            for band, pol in enumerate(("HHHH", "HVHV")):
                values = delta[band][valid[band]]
                stats[pol] = {"valid_pixels": int(values.size), "valid_fraction_of_aoi": float(values.size / aoi_pixels),
                              "min_db": float(values.min()), "p05_db": float(np.percentile(values, 5)),
                              "median_db": float(np.median(values)), "p95_db": float(np.percentile(values, 95)), "max_db": float(values.max())}
            validity_path = DATA / f"nisar_2026-10-23_to_2026-11-04_track170{suffix}_common_valid_mask.tif"
            with rasterio.open(validity_path, "w", **{**profile, "count": 2, "dtype": "uint8", "nodata": 0, "predictor": 2}) as dst:
                dst.write(valid.astype(np.uint8)); dst.set_band_description(1, "HHHH common valid mask"); dst.set_band_description(2, "HVHV common valid mask")
                dst.update_tags(mission="NASA-ISRO NISAR", frequency_grid=f"frequency{frequency}", comparison_dates="2026-10-23/2026-11-04")
            products[f"frequency{frequency}"] = {
                "resolution_m": list(a.res), "alignment_checks": checks, "crs": a.crs.to_string(),
                "bounds": list(a.bounds), "dimensions": [a.width, a.height], "aoi_pixels": aoi_pixels,
                "polarizations": stats,
                "inputs": [{"path": p.name, "sha256": sha256(p)} for prefix in src for p in (Path(f"{prefix}_gamma0_power.tif"), Path(f"{prefix}_valid_mask.tif"))],
                "output": out.name, "output_sha256": sha256(out), "common_mask": validity_path.name,
            }
        finally:
            for ds in rasters + masks:
                ds.close()
    result = {"status": "processed_nonclassificatory_temporal_comparison", "dates": list(DATES),
              "interpretation_limits": ["Not a water map, flood map, or probability.", "Later regional dates only; unrelated to the January 2026 reported incident.", "No local field labels or exact enclosure geometry."],
              "frequency_grids": products}
    (DATA / "nisar_temporal_comparison_manifest.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
