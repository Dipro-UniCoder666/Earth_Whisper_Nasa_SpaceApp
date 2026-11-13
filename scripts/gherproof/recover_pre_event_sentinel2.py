"""Fetch a small January 13, 2026 Sentinel-2 locality overview via public PC COGs.

This is contextual imagery over the existing broad locality search box. It is
not an enclosure delineation, and scene cloud metadata is not a local cloud mask.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[2]
BBOX = [89.15, 22.93, 89.30, 23.08]
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign"


def _rasterio():
    if str(ROOT / "backend/.venv/Lib/site-packages") not in sys.path:
        sys.path.append(str(ROOT / "backend/.venv/Lib/site-packages"))
    import rasterio
    return rasterio


def main() -> None:
    response = requests.post(STAC, json={
        "collections": ["sentinel-2-l2a"], "bbox": BBOX,
        "datetime": "2026-01-01T00:00:00Z/2026-01-14T23:59:59Z", "limit": 100,
        "query": {"eo:cloud_cover": {"lt": 10}},
    }, timeout=90)
    response.raise_for_status()
    candidates = response.json().get("features", [])
    candidates = [x for x in candidates if x.get("properties", {}).get("datetime", "")[:10] == "2026-01-13"
                  and "visual" in x.get("assets", {})]
    if not candidates:
        raise RuntimeError("No 2026-01-13 cloud-filtered Sentinel-2 visual asset found in the provisional box")
    item = sorted(candidates, key=lambda x: x.get("properties", {}).get("eo:cloud_cover", 100))[0]
    href = item["assets"]["visual"]["href"]
    signed_resp = requests.get(SIGN, params={"href": href}, timeout=30)
    signed_resp.raise_for_status()
    signed = signed_resp.json().get("href")
    if not signed:
        raise RuntimeError("Planetary Computer signer did not return a signed HREF")

    rasterio = _rasterio()
    from rasterio.windows import from_bounds
    from rasterio.warp import transform_bounds
    from PIL import Image

    output = ROOT / "data/gherproof/processed/sentinel2"
    output.mkdir(parents=True, exist_ok=True)
    tif_path = output / "2026-01-13_sentinel2_visual_provisional_locality.tif"
    png_path = output / "2026-01-13_sentinel2_visual_provisional_locality.png"
    # Read only the small COG window corresponding to the existing broad search box.
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with rasterio.open(signed) as src:
            bounds = transform_bounds("EPSG:4326", src.crs, *BBOX, densify_pts=21)
            window = from_bounds(*bounds, transform=src.transform).round_offsets().round_lengths()
            window = window.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
            arr = src.read(window=window)
            profile = src.profile.copy()
            profile.update(width=int(window.width), height=int(window.height),
                           transform=rasterio.windows.transform(window, src.transform), compress="deflate")
            with rasterio.open(tif_path, "w", **profile) as dst:
                dst.write(arr)
            raster_qc = {"crs": str(src.crs), "full_dimensions": [src.width, src.height],
                         "window": [int(window.col_off), int(window.row_off), int(window.width), int(window.height)],
                         "resolution": list(src.res), "bands": src.count, "dtype": list(src.dtypes),
                         "nodata": src.nodata, "crop_bounds": list(rasterio.windows.bounds(window, src.transform)),
                         "rgb_pixel_percentiles": [[float(np.nanpercentile(arr[b], q)) for q in [2, 50, 98]] for b in range(min(3, arr.shape[0]))]}
    rgb = np.moveaxis(arr[:3], 0, -1).astype(np.float32)
    lo, hi = np.nanpercentile(rgb, [2, 98])
    if hi <= lo:
        raise RuntimeError("Sentinel-2 overview has no usable contrast")
    vis = np.clip((rgb - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)
    Image.fromarray(vis, mode="RGB").save(png_path)
    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Microsoft Planetary Computer Sentinel-2 L2A STAC and public time-limited SAS access",
        "item_id": item["id"], "acquisition_datetime": item["properties"].get("datetime"),
        "platform": item["properties"].get("platform"), "tile": item["properties"].get("s2:mgrs_tile"),
        "scene_cloud_cover_fraction": item["properties"].get("eo:cloud_cover"),
        "source_bbox_wgs84": BBOX, "bbox_status": "broad provisional locality only; not a verified enclosure polygon",
        "asset": "visual true-colour GeoTIFF", "raster_qc": raster_qc,
        "outputs": [str(p.relative_to(ROOT)).replace("\\", "/") for p in (tif_path, png_path)],
        "limitations": ["Scene-level cloud estimate does not replace pixel-level cloud/shadow screening.",
                        "No exact enclosure point or boundary was found in OSM or published source metadata.",
                        "This broad crop was not used to draw an enclosure polygon or infer land-use labels."],
    }
    path = ROOT / "data/gherproof/manifests/pre_event_sentinel2_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path.relative_to(ROOT)), "item": item["id"],
                      "acquired": manifest["acquisition_datetime"], "outputs": manifest["outputs"],
                      "raster_qc": raster_qc}, indent=2))


if __name__ == "__main__":
    main()
