"""Build provenance-tracked regional fisheries context from existing Clark and ESA rasters."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine
from rasterio.features import geometry_mask
from rasterio.warp import Resampling, reproject, transform_bounds, transform_geom

ROOT = Path(__file__).resolve().parents[3]
AOI_PATH = ROOT / "data/gherproof/regional/six_village_regional_search_extent.geojson"
REGISTRY_PATH = ROOT / "data/gherproof/manifests/evidence_registry.json"
OUTPUT_DIR = ROOT / "data/gherproof/processed/fisheries_context"
MANIFEST_PATH = ROOT / "data/gherproof/manifests/fisheries_context_manifest.json"
CLARK_PATH = ROOT / "data/gherproof/reference/clark_2022_locality_context_15m_utm45n.tif"
CHANGE_PATH = ROOT / "data/gherproof/processed/phase8b/optical/temporal_change/2026-01-10_to_2026-01-20_change_candidates.tif"
WORLD_COVER_URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
    "ESA_WorldCover_10m_2021_v200_N21E087_Map.tif"
)
CRS = "EPSG:32645"
CLASS_NAMES = {
    10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland",
    50: "Built-up", 60: "Bare / sparse vegetation", 70: "Snow / ice",
    80: "Permanent water bodies", 90: "Herbaceous wetland", 95: "Mangroves",
    100: "Moss / lichen",
}
CLARK_NAMES = {1: "Mangrove", 2: "Coastal wetland", 3: "Pond aquaculture", 4: "Water", 5: "Other landcover", 6: "Missing"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def projected_aoi(geometry: dict[str, Any]) -> dict[str, Any]:
    return transform_geom("EPSG:4326", CRS, geometry, precision=3)


def aoi_grid(geometry: dict[str, Any], resolution: int) -> tuple[Affine, int, int, dict[str, Any]]:
    geo_bounds = rasterio.features.bounds(geometry)
    bounds = transform_bounds("EPSG:4326", CRS, *geo_bounds, densify_pts=21)
    left = math.floor(bounds[0] / resolution) * resolution
    bottom = math.floor(bounds[1] / resolution) * resolution
    right = math.ceil(bounds[2] / resolution) * resolution
    top = math.ceil(bounds[3] / resolution) * resolution
    width, height = (right - left) // resolution, (top - bottom) // resolution
    return Affine(resolution, 0, left, 0, -resolution, top), width, height, projected_aoi(geometry)


def class_counts(values: np.ndarray, valid: np.ndarray, names: dict[int, str], cell_area: float) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for code, count in zip(*np.unique(values[valid], return_counts=True)):
        if int(code) == 0:
            continue
        output[str(int(code))] = {
            "class_name": names.get(int(code), f"Class {int(code)}"),
            "pixels": int(count),
            "area_km2_nominal": round(float(count * cell_area / 1_000_000), 6),
        }
    return output


def warp_to_grid(source: rasterio.io.DatasetReader, transform: Affine, crs: str, width: int, height: int) -> np.ndarray:
    destination = np.zeros((height, width), dtype=np.uint8)
    reproject(
        source=rasterio.band(source, 1), destination=destination,
        src_transform=source.transform, src_crs=source.crs, src_nodata=source.nodata,
        dst_transform=transform, dst_crs=crs, dst_nodata=0,
        resampling=Resampling.nearest, init_dest_nodata=True,
    )
    return destination


def registry_record(evidence_id: str, title: str, source: str, path: Path, year: int, coverage: dict[str, Any], method: str, limitations: list[str], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "evidence_category": "historical_landcover_context",
        "title": title,
        "source_dataset": source,
        "acquisition_date": str(year),
        "processing_date": datetime.now(timezone.utc).date().isoformat(),
        "spatial_coverage": coverage,
        "crs": CRS,
        "original_file": None,
        "derived_file": {
            "path": path.relative_to(ROOT).as_posix(), "availability": "available",
            "bytes": path.stat().st_size, "sha256": sha256(path), "checksum_matches_manifest": True,
        },
        "confidence_or_validation_status": "provisional",
        "processing_methodology": method,
        "limitations": limitations,
        "source_provenance": ["data/gherproof/manifests/fisheries_context_manifest.json"],
        "metadata": metadata,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    geo = json.loads(AOI_PATH.read_text(encoding="utf-8"))["features"][0]["geometry"]
    transform10, width10, height10, aoi_projected = aoi_grid(geo, 10)
    aoi_mask10 = geometry_mask([aoi_projected], (height10, width10), transform=transform10, invert=True, all_touched=False)
    worldcover_path = OUTPUT_DIR / "ESA_WorldCover_2021_10m_provisional_AOI_UTM45N.tif"
    worldcover_vsi = "/vsicurl/" + WORLD_COVER_URL
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_USE_HEAD="NO"):
        with rasterio.open(worldcover_vsi) as source:
            wcover = np.zeros((height10, width10), dtype=np.uint8)
            reproject(
                source=rasterio.band(source, 1), destination=wcover,
                src_transform=source.transform, src_crs=source.crs, src_nodata=source.nodata,
                dst_transform=transform10, dst_crs=CRS, dst_nodata=0,
                resampling=Resampling.nearest, init_dest_nodata=True,
            )
    wvalid = aoi_mask10 & (wcover != 0)
    profile = {
        "driver": "GTiff", "height": height10, "width": width10, "count": 1,
        "dtype": "uint8", "crs": CRS, "transform": transform10,
        "nodata": 0, "compress": "deflate", "predictor": 2, "tiled": True,
        "blockxsize": 512, "blockysize": 512,
    }
    with rasterio.open(worldcover_path, "w", **profile) as output:
        output.write(np.where(aoi_mask10, wcover, 0).astype(np.uint8), 1)
        output.set_band_description(1, "ESA WorldCover 2021 land-cover class")
        output.update_tags(
            source=WORLD_COVER_URL,
            attribution="© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.",
            aoi_status="provisional regional search extent; not village or enclosure boundary",
            resampling="nearest neighbour",
        )

    world_counts = class_counts(wcover, wvalid, CLASS_NAMES, 100)
    with rasterio.open(CLARK_PATH) as clark:
        clark_values = clark.read(1, masked=True)
        clark_inside = geometry_mask([transform_geom("EPSG:4326", clark.crs, geo)], clark.shape, transform=clark.transform, invert=True, all_touched=False)
        cvals = np.asarray(clark_values.data)
        cvalid = clark_inside & ~np.ma.getmaskarray(clark_values) & (cvals != 0)
        clark_counts = class_counts(cvals, cvalid, CLARK_NAMES, 225)
        clark_valid_area = int(cvalid.sum()) * 225 / 1_000_000

    with rasterio.open(CHANGE_PATH) as change:
        change_values = change.read(1, masked=True)
        change_data = np.asarray(change_values.data)
        change_valid = ~np.ma.getmaskarray(change_values) & (change_data != 255)
        aoi_mask20 = geometry_mask([transform_geom("EPSG:4326", change.crs, geo)], (change.height, change.width), transform=change.transform, invert=True, all_touched=False)
        change_aoi_valid = change_valid & aoi_mask20
        clark20 = np.zeros((change.height, change.width), dtype=np.uint8)
        with rasterio.open(CLARK_PATH) as clark:
            reproject(rasterio.band(clark, 1), clark20, src_transform=clark.transform, src_crs=clark.crs, src_nodata=clark.nodata, dst_transform=change.transform, dst_crs=change.crs, dst_nodata=0, resampling=Resampling.nearest)
        world20 = np.zeros((change.height, change.width), dtype=np.uint8)
        with rasterio.open(worldcover_path) as worldcover:
            world20 = warp_to_grid(worldcover, change.transform, change.crs, change.width, change.height)
        newwater = (change_data == 2) & change_aoi_valid
        loss = (change_data == 3) & change_aoi_valid
        clark_support = change_aoi_valid & (clark20 != 0)
        world_support = change_aoi_valid & (world20 != 0)

        def overlaps(candidate: np.ndarray, classes: np.ndarray, support: np.ndarray, names: dict[int, str]) -> dict[str, Any]:
            denominator = int(candidate.sum())
            supported = candidate & support
            counts: dict[str, Any] = {}
            for code, count in zip(*np.unique(classes[supported], return_counts=True)):
                if code == 0:
                    continue
                counts[str(int(code))] = {
                    "class_name": names.get(int(code), f"Class {int(code)}"),
                    "candidate_cells": int(count),
                    "pct_of_all_candidates": round(100 * int(count) / max(1, denominator), 3),
                }
            return {"candidate_cells": denominator, "candidate_cells_with_context_coverage": int(supported.sum()), "context_coverage_pct": round(100 * int(supported.sum()) / max(1, denominator), 3), "overlap_by_class": counts}

        candidate_clark = overlaps(newwater, clark20, clark_support, CLARK_NAMES)
        candidate_worldcover = overlaps(newwater, world20, world_support, CLASS_NAMES)
        loss_worldcover = overlaps(loss, world20, world_support, CLASS_NAMES)
        model_overlaps: dict[str, Any] = {}
        for model in ("scratch", "pretrained"):
            model_path = ROOT / f"data/gherproof/processed/phase8b/comparison/sar_optical/2026-01-12_{model}/model_water_prediction_20m.tif"
            with rasterio.open(model_path) as prediction:
                prediction_values = prediction.read(1, masked=True)
                pred = np.asarray(prediction_values.data)
                pred_valid = ~np.ma.getmaskarray(prediction_values) & (pred != 255)
                pred_aoi = geometry_mask([transform_geom("EPSG:4326", prediction.crs, geo)], pred.shape, transform=prediction.transform, invert=True, all_touched=False)
                pred_water = (pred == 1) & pred_valid & pred_aoi
                model_clark = np.zeros(pred.shape, dtype=np.uint8)
                with rasterio.open(CLARK_PATH) as clark:
                    reproject(rasterio.band(clark, 1), model_clark, src_transform=clark.transform, src_crs=clark.crs, src_nodata=clark.nodata, dst_transform=prediction.transform, dst_crs=prediction.crs, dst_nodata=0, resampling=Resampling.nearest)
                support = pred_water & (model_clark != 0)
                aqua = support & (model_clark == 3)
                model_overlaps[model] = {
                    "predicted_water_cells": int(pred_water.sum()),
                    "predicted_water_cells_with_Clark_coverage": int(support.sum()),
                    "predicted_water_cells_over_Clark_2022_pond_aquaculture": int(aqua.sum()),
                    "pct_of_predictions_over_Clark_pond_class_on_supported_cells": round(100 * int(aqua.sum()) / max(1, int(support.sum())), 3),
                    "prediction_evidence_id": f"prediction-{model}-2026-01-12-probability",
                    "limitations": ["Phase 8B thresholded model cells are exploratory and unvalidated locally.", "Clark 2022 class 3 is historical context, not a 2026 fish-farm inventory.", "Nearest-neighbour grid transfer does not define parcel boundaries."],
                }

    with rasterio.open(worldcover_path) as ds:
        world_bounds = [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top]
    limitations = [
        "The source geometry is a provisional regional search rectangle, not a village or enclosure boundary.",
        "Clark 2022 coverage is partial; its mapped class area is only the covered footprint inside the provisional AOI.",
        "Clark class 3 is a 2022 pond-aquaculture class, not a verified active 2026 fisheries asset or Pallimangal boundary.",
        "WorldCover 2021 is historical land-cover context, not current 2026 ground truth.",
        "Possible-water candidates and model predictions are exploratory and are not damage, flood, or waterlogging labels.",
    ]
    manifest: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_area": {"evidence_id": "geography-provisional-regional-aoi", "status": "provisional_regional_search_extent", "geometry": str(AOI_PATH.relative_to(ROOT)).replace("\\", "/"), "crs": "EPSG:4326"},
        "clark_2022": {
            "source": "Clark Labs Bangladesh Land Cover and Change Maps 2022 v1",
            "source_url": "https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/",
            "license": "Clark's page states non-commercial use only and requires permission for other uses; source archive is not redistributed.",
            "local_raster": str(CLARK_PATH.relative_to(ROOT)).replace("\\", "/"),
            "crs": CRS, "native_resolution_m": 15, "class_legend": {str(k): v for k, v in CLARK_NAMES.items()},
            "valid_covered_aoi_cells": int(cvalid.sum()), "valid_covered_aoi_area_km2": round(clark_valid_area, 6),
            "mapped_classes_in_raster_footprint": clark_counts,
            "pond_aquaculture_class_3_area_km2_in_covered_footprint": clark_counts.get("3", {}).get("area_km2_nominal", 0.0),
            "new_water_candidate_overlap": candidate_clark,
            "model_prediction_overlap": model_overlaps,
            "limitations": limitations,
        },
        "worldcover_2021": {
            "source": "ESA WorldCover 10 m 2021 v200 Map",
            "source_url": WORLD_COVER_URL,
            "accessed_utc": datetime.now(timezone.utc).isoformat(),
            "attribution": "© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.",
            "license": "Creative Commons Attribution 4.0 International License",
            "local_subset": str(worldcover_path.relative_to(ROOT)).replace("\\", "/"),
            "crs": CRS, "resolution_m": 10, "bounds": world_bounds, "pixel_count": [width10, height10],
            "valid_aoi_pixels": int(wvalid.sum()), "valid_aoi_area_km2_nominal": round(int(wvalid.sum()) * 100 / 1_000_000, 6),
            "class_legend": {str(k): v for k, v in CLASS_NAMES.items()}, "class_counts": world_counts,
            "possible_new_water_candidate_overlap": candidate_worldcover,
            "possible_water_loss_candidate_overlap": loss_worldcover,
            "limitations": ["WorldCover 2021 is not current 2026 ground truth.", "WorldCover 2020 and 2021 must not be treated as a genuine change series because algorithm versions differ.", "The study AOI is provisional."],
        },
        "department_of_fisheries": {
            "source": "Bangladesh Department of Fisheries, Yearbook of Fisheries Statistics 2024–25 summary table",
            "source_url": "https://fisheries.portal.gov.bd/pages/static-pages/6922e13e933eb65569e2b13e",
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "year": "2024–25",
            "aquaculture_production_lakh_metric_tonnes": 31.07,
            "total_fish_production_lakh_metric_tonnes": 51.11,
            "geographic_level": "Bangladesh national aggregate",
            "limitations": ["National total only; no Manirampur or Pallimangal estimate is available from this figure.", "Not used for incident impact quantification."],
        },
        "limitations": limitations,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = registry["records"]
    records = [record for record in records if record.get("evidence_id") not in {"clark-2022-aquaculture-context", "worldcover-2021-landcover-context"}]
    registry["records"] = records
    new_records = [
        registry_record("clark-2022-aquaculture-context", "Clark 2022 historical pond-aquaculture context", "Clark Labs Bangladesh Land Cover 2022", CLARK_PATH, 2022, {"crs": CRS, "resolution_m": 15, "valid_covered_aoi_area_km2": round(clark_valid_area, 6), "partial_aoi_coverage": True}, "Existing 15 m Clark class raster; class counts use pixel centers within the provisional AOI; candidate/model overlap uses nearest-neighbour transfer to the 20 m analytical grid.", limitations + ["Clark Labs' download page restricts use to non-commercial purposes unless permission is obtained."], {"class_legend": {str(k): v for k, v in CLARK_NAMES.items()}, "pond_aquaculture_class": 3, "pond_aquaculture_pixels_in_covered_footprint": clark_counts.get("3", {}).get("pixels", 0), "pond_aquaculture_area_km2_in_covered_footprint": clark_counts.get("3", {}).get("area_km2_nominal", 0.0), "candidate_overlap": candidate_clark, "model_overlap": model_overlaps, "licensing": "Non-commercial only per Clark source page; do not redistribute raw source data."}),
        registry_record("worldcover-2021-landcover-context", "ESA WorldCover 2021 historical land-cover context", "ESA WorldCover 10 m 2021 v200", worldcover_path, 2021, {"crs": CRS, "resolution_m": 10, "bounds": world_bounds, "valid_aoi_area_km2_nominal": round(int(wvalid.sum()) * 100 / 1_000_000, 6)}, "Remote COG AOI-window subset, nearest-neighbour reprojected to EPSG:32645 at 10 m; pixels outside the provisional AOI are NoData.", limitations + ["Not a 2026 land-cover map."], {"class_legend": {str(k): v for k, v in CLASS_NAMES.items()}, "class_counts": world_counts, "new_water_candidate_overlap": candidate_worldcover, "water_loss_candidate_overlap": loss_worldcover, "attribution": "© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.", "license": "CC BY 4.0"}),
    ]
    records.extend(new_records)
    registry["records"] = records
    registry["record_count"] = len(records)
    registry["category_counts"] = {category: sum(1 for r in records if r.get("evidence_category") == category) for category in sorted({r.get("evidence_category") for r in records})}
    registry["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"clark_aquaculture_km2_partial_coverage": manifest["clark_2022"]["pond_aquaculture_class_3_area_km2_in_covered_footprint"], "worldcover_class_counts": world_counts, "candidate_overlaps": {"clark": candidate_clark, "worldcover": candidate_worldcover}, "model_overlaps": model_overlaps, "worldcover_output": str(worldcover_path), "worldcover_sha256": sha256(worldcover_path)}, indent=2))


if __name__ == "__main__":
    main()
