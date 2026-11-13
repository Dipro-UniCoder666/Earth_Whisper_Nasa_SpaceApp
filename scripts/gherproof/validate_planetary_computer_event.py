"""Independent local QC for Planetary Computer event clips and validity masks."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image, ImageDraw
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/gherproof/manifests/planetary_computer_event_imagery.json"
VALIDATION = ROOT / "data/gherproof/manifests/planetary_computer_scene_validation.json"
MASK_NAME = "data/gherproof/processed/sentinel1/planetary_computer/2026-01-07_2026-01-19_rtc_validity_masks_10m_utm45n.tif"
FIGURE = ROOT / "data/gherproof/processed/sentinel1/planetary_computer/coverage_validity.png"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    outputs = [entry for entry in manifest.get("outputs", []) if entry.get("kind") == "two-polarization-analysis-ready-clip"]
    if len(outputs) != 2:
        raise RuntimeError("Expected two locally generated analysis-ready date clips")
    qc = []
    grids = []
    masks = []
    for entry in sorted(outputs, key=lambda x: x["date"]):
        path = ROOT / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(entry["path"])
        digest = sha256(path)
        with rasterio.open(path) as ds:
            arr = ds.read(masked=True)
            raw = ds.read()
            dataset_mask = ds.dataset_mask() > 0
            valid = dataset_mask & ~np.ma.getmaskarray(arr[0]) & ~np.ma.getmaskarray(arr[1])
            if ds.count != 2 or ds.descriptions != ("VV", "VH"):
                raise ValueError(f"Unexpected polarization bands in {entry['path']}")
            if not ds.crs or ds.nodata != -32768 or not np.isfinite(raw[:, dataset_mask]).all():
                raise ValueError(f"CRS, nodata, or finite-pixel validation failed for {entry['path']}")
            stats = {}
            for band, pol in enumerate(("VV", "VH"), start=1):
                values = raw[band-1][valid]
                stats[pol] = {"valid_pixels": int(values.size), "min": float(values.min()) if values.size else None,
                    "p02": float(np.percentile(values, 2)) if values.size else None,
                    "median": float(np.median(values)) if values.size else None,
                    "p98": float(np.percentile(values, 98)) if values.size else None,
                    "max": float(values.max()) if values.size else None,
                    "nan_count": int(np.isnan(raw[band-1]).sum()),
                    "infinite_count": int(np.isinf(raw[band-1]).sum())}
            grid = {"crs": str(ds.crs), "width": ds.width, "height": ds.height,
                    "transform": list(ds.transform), "resolution": list(ds.res), "count": ds.count,
                    "descriptions": list(ds.descriptions), "dtype": list(ds.dtypes), "nodata": ds.nodata}
            grids.append(grid)
            masks.append(valid)
            qc.append({"date": entry["date"], "path": entry["path"], "sha256": digest,
                "manifest_checksum_matches": digest == entry["sha256"], "bytes": path.stat().st_size,
                "metadata": grid, "dataset_mask_valid_pixels": int(dataset_mask.sum()),
                "valid_fraction_of_raster_grid": float(dataset_mask.mean()), "band_statistics": stats,
                "tags": ds.tags(), "band_tags": {"VV": ds.tags(1), "VH": ds.tags(2)}})
    aligned = grids[0] == grids[1]
    same_mask = bool(np.array_equal(masks[0], masks[1]))
    if not aligned or not same_mask or not all(item["manifest_checksum_matches"] for item in qc):
        raise ValueError("Independent output grid/mask/checksum checks failed")

    mask_path = ROOT / MASK_NAME
    with rasterio.open(mask_path) as ds:
        mask_data = ds.read()
        if ds.count != 4 or ds.descriptions != ("2026-01-07_both_VV_VH_valid", "2026-01-19_both_VV_VH_valid",
            "common_both_dates_and_polarizations_valid", "provisional_AOI"):
            raise ValueError("Validity-mask raster schema mismatch")
        if list(ds.transform) != grids[0]["transform"] or str(ds.crs) != grids[0]["crs"]:
            raise ValueError("Validity-mask grid does not match date clips")
        mask_counts = {name: int(mask_data[i].sum()) for i, name in enumerate(ds.descriptions)}
        mask_manifest_row = next((o for o in manifest.get("outputs", []) if o.get("path") == MASK_NAME), None)
        mask_digest = sha256(mask_path)
        if not mask_manifest_row or mask_manifest_row.get("sha256") != mask_digest:
            raise ValueError("Validity-mask checksum does not match the retrieval manifest")
        if not np.array_equal(mask_data[2] > 0, masks[0]):
            raise ValueError("Common-validity band disagrees with GeoTIFF internal dataset mask")
        mask_qc = {"path": MASK_NAME, "sha256": mask_digest, "bytes": mask_path.stat().st_size,
                   "crs": str(ds.crs), "width": ds.width, "height": ds.height,
                   "resolution": list(ds.res), "band_descriptions": list(ds.descriptions),
                   "pixel_counts": mask_counts}
        aoi_geojson = {"type": "Polygon", "coordinates": [[
            [manifest["aoi_wgs84"][0], manifest["aoi_wgs84"][1]],
            [manifest["aoi_wgs84"][2], manifest["aoi_wgs84"][1]],
            [manifest["aoi_wgs84"][2], manifest["aoi_wgs84"][3]],
            [manifest["aoi_wgs84"][0], manifest["aoi_wgs84"][3]],
            [manifest["aoi_wgs84"][0], manifest["aoi_wgs84"][1]]]]}
        projected = transform_geom("EPSG:4326", ds.crs, aoi_geojson, precision=8)
        inside = geometry_mask([projected], out_shape=(ds.height, ds.width), transform=ds.transform, invert=True)
        outside_violations = int(((mask_data[2] > 0) & ~inside).sum())
        mask_qc["provisional_aoi_pixels"] = int(inside.sum())
        mask_qc["common_valid_pixels_inside_aoi"] = int(((mask_data[2] > 0) & inside).sum())
        mask_qc["common_valid_fraction_of_aoi"] = float(mask_qc["common_valid_pixels_inside_aoi"] / max(1, inside.sum()))
        mask_qc["valid_pixels_outside_aoi"] = outside_violations
        if outside_violations:
            raise ValueError("Valid-data mask contains pixels outside the provisional AOI")
        # Simple evidence map: valid pixels, inside-AOI nodata, and outside-AOI are distinct.
        scale = min(800 / ds.width, 700 / ds.height, 1.0)
        size = (max(1, round(ds.width*scale)), max(1, round(ds.height*scale)))
        canvas = Image.new("RGB", (1400, 900), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        draw.text((32, 22), "Sentinel-1 RTC valid-data coverage", fill=(20, 35, 48))
        draw.text((32, 48), "Provisional locality bbox only; valid pixels are not water detections", fill=(60, 70, 78))
        panel_x = (70, 720)
        colors = {"outside": (246, 247, 248), "invalid": (222, 224, 226), "valid": (37, 142, 148)}
        for idx, (day, layer) in enumerate((("2026-01-07", mask_data[0] > 0), ("2026-01-19", mask_data[1] > 0))):
            rgb = np.empty((ds.height, ds.width, 3), dtype=np.uint8)
            rgb[:] = colors["outside"]
            rgb[inside] = colors["invalid"]
            rgb[layer.astype(bool) & inside] = colors["valid"]
            image = Image.fromarray(rgb).resize(size, Image.Resampling.NEAREST)
            x, y = panel_x[idx], 115
            canvas.paste(image, (x, y))
            draw.rectangle((x-1,y-1,x+size[0],y+size[1]), outline=(80,90,95), width=1)
            draw.text((x, y-25), f"{day} both VV and VH valid", fill=(20,35,48))
            draw.text((x, y+size[1]+8), f"{mask_counts[ds.descriptions[idx]]:,} valid pixels", fill=(45,55,60))
        legend_y=850
        for j,(label,color) in enumerate((("Date-specific valid coverage",colors["valid"]),("Inside AOI, no valid observation",colors["invalid"]),("Outside AOI",colors["outside"]))):
            x=80+j*340; draw.rectangle((x,legend_y,x+18,legend_y+18),fill=color,outline=(90,90,90)); draw.text((x+26,legend_y+2),label,fill=(40,45,50))
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(FIGURE)
    mask_qc["coverage_map"] = str(FIGURE.relative_to(ROOT)).replace("\\", "/")
    validation["independent_output_validation"] = {"validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": qc, "all_date_grids_aligned": aligned, "date_internal_masks_identical": same_mask,
        "validity_mask_stack": mask_qc,
        "processing_reproduction": "scripts/gherproof/retrieve_planetary_computer_event.py then scripts/gherproof/validate_planetary_computer_event.py"}
    atomic_json(VALIDATION, validation)
    print(json.dumps({"outputs_validated": len(qc), "grids_aligned": aligned,
        "masks_identical": same_mask, "common_valid_fraction_of_aoi": mask_qc["common_valid_fraction_of_aoi"],
        "coverage_map": mask_qc["coverage_map"]}, indent=2))


if __name__ == "__main__":
    main()
