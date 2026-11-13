"""Independent Rasterio QC for the DHARA NISAR regional products."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/gherproof/processed/nisar/validated"
OUT = ROOT / "data/gherproof/manifests/nisar_raster_qc_manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    tifs = sorted(DATA.glob("*.tif"))
    files = []
    group_reference = {}
    for path in tifs:
        with rasterio.open(path) as ds:
            frequency = ds.tags().get("frequency_grid") or ("frequencyB" if "frequencyB" in path.name else "frequencyA")
            signature = (ds.crs, ds.transform, ds.width, ds.height)
            aligned = signature == group_reference.setdefault(frequency, signature)
            band_stats = []
            for i in range(1, ds.count + 1):
                raw = ds.read(i, masked=True)
                arr = np.asarray(raw.compressed() if np.ma.isMaskedArray(raw) else raw).astype(np.float64)
                finite = np.isfinite(arr)
                vals = arr[finite]
                band_stats.append({
                    "band": i, "description": ds.descriptions[i-1], "dtype": ds.dtypes[i-1],
                    "valid_pixels": int(vals.size), "masked_pixels": int(ds.width * ds.height - vals.size),
                    "nan_count": int(np.isnan(arr).sum()), "infinite_count": int(np.isinf(arr).sum()),
                    "min": float(vals.min()) if vals.size else None,
                    "p05": float(np.percentile(vals, 5)) if vals.size else None,
                    "median": float(np.median(vals)) if vals.size else None,
                    "p95": float(np.percentile(vals, 95)) if vals.size else None,
                    "max": float(vals.max()) if vals.size else None,
                })
            files.append({
                "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path),
                "crs": ds.crs.to_string() if ds.crs else None,
                "transform": list(ds.transform), "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
                "width": ds.width, "height": ds.height, "resolution": list(ds.res), "count": ds.count,
                "dtype": list(ds.dtypes), "nodata": ds.nodata, "band_descriptions": list(ds.descriptions),
                "frequency_grid_group": frequency, "aligned_to_group_reference": aligned, "tags": ds.tags(), "bands": band_stats,
            })
    if not files:
        raise FileNotFoundError("No NISAR GeoTIFF outputs were found")
    result = {
        "status": "rasterio_qc_complete", "software": {"rasterio": rasterio.__version__, "numpy": np.__version__},
        "file_count": len(files), "all_comparable_group_alignments_pass": all(f["aligned_to_group_reference"] for f in files),
        "grid_groups": {group: {"count": sum(1 for f in files if f["frequency_grid_group"] == group),
                                "dimensions": sorted({(f["width"], f["height"]) for f in files if f["frequency_grid_group"] == group}),
                                "resolutions": sorted({tuple(f["resolution"]) for f in files if f["frequency_grid_group"] == group})}
                        for group in sorted(group_reference)},
        "all_have_crs": all(f["crs"] for f in files), "all_no_nan_or_infinite": all(b["nan_count"] == 0 and b["infinite_count"] == 0 for f in files for b in f["bands"]),
        "files": files,
        "limitations": ["Raster validity is based on explicit NISAR masks carried into the processing outputs.",
                        "The provisional AOI is not an official village/site/enclosure boundary.",
                        "Raster QC does not constitute water classification or field validation."],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "files"} | {"files": [{"path": f["path"], "group": f["frequency_grid_group"], "aligned": f["aligned_to_group_reference"], "crs": f["crs"], "resolution": f["resolution"]} for f in files]}, indent=2))


if __name__ == "__main__":
    main()
