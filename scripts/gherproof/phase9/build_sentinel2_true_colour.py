"""Build AOI-only true-colour Sentinel-2 composites from registered S2B scenes.

The unsigned COG URLs come from saved Microsoft Planetary Computer STAC items.
At runtime, each URL is signed with the public Planetary Computer SAS endpoint;
the temporary signed URL is never persisted or printed.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[3]
STAC_DIR = ROOT / "data/gherproof/raw/phase6b/stac_items"
TEMPLATE_DIR = ROOT / "data/gherproof/processed/phase7/sentinel2"
OUTPUT_DIR = ROOT / "data/gherproof/processed/fisheries_context"
MANIFEST_PATH = ROOT / "data/gherproof/manifests/fisheries_context_manifest.json"
REGISTRY_PATH = ROOT / "data/gherproof/manifests/evidence_registry.json"
SAS_SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = registry["records"]
    results = []
    session = requests.Session()
    for date in ("2026-01-10", "2026-01-20"):
        compact = date.replace("-", "")
        stac_path = next(STAC_DIR.glob(f"sentinel-2-l2a_S2B_MSIL2A_{compact}*.json"))
        item = json.loads(stac_path.read_text(encoding="utf-8"))
        sources = {band: item["assets"][band]["href"] for band in ("B02", "B03", "B04")}
        template_path = TEMPLATE_DIR / f"{date}_B03_reflectance_10m.tif"
        output_path = OUTPUT_DIR / f"{date}_S2_true_colour_B04_B03_B02_10m.tif"
        with rasterio.open(template_path) as template:
            profile = template.profile.copy()
            width, height = template.width, template.height
            transform = template.transform
            common_valid = template.read_masks(1) > 0
            # The existing B03/B04 reflectance products and source B02 share this
            # S2B item, tile, acquisition and 10 m UTM grid.
            bands = {}
            # Reuse the already processed and radiometrically verified green/red
            # bands. Only the missing blue band is retrieved from its COG.
            for band in ("B03", "B04"):
                local_band = TEMPLATE_DIR / f"{date}_{band}_reflectance_10m.tif"
                with rasterio.open(local_band) as src:
                    if src.transform != template.transform or src.crs != template.crs or src.shape != template.shape:
                        raise RuntimeError(f"registered {band} grid does not align with the template")
                    values = src.read(1, masked=True)
                    valid = ~np.ma.getmaskarray(values) & common_valid
                    bands[band] = np.where(valid, values.data, -9999.0).astype(np.float32)
            signed_response = session.get(SAS_SIGN, params={"href": sources["B02"]}, timeout=30)
            signed_response.raise_for_status()
            signed_href = signed_response.json()["href"]
            with rasterio.Env(
                GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_USE_HEAD="NO",
                GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1",
            ):
                with rasterio.open("/vsicurl/" + signed_href) as src:
                    if src.crs != template.crs or src.res != template.res:
                        raise RuntimeError("B02 source grid does not match registered reflectance grid")
                    col = round((transform.c - src.transform.c) / src.transform.a)
                    row = round((transform.f - src.transform.f) / src.transform.e)
                    if col < 0 or row < 0 or col + width > src.width or row + height > src.height:
                        raise RuntimeError("B02 source does not cover the prepared regional grid")
                    dn = src.read(1, window=Window(col, row, width, height), masked=True)
                    valid = ~np.ma.getmaskarray(dn) & (np.asarray(dn.data) != 0) & common_valid
                    reflectance = (np.asarray(dn.data, dtype=np.float32) - 1000.0) / 10000.0
                    bands["B02"] = np.where(valid, reflectance, -9999.0).astype(np.float32)
        profile.update(count=3, dtype="float32", nodata=-9999.0, compress="deflate", predictor=3)
        with rasterio.open(output_path, "w", **profile) as dst:
            for index, band in enumerate(("B04", "B03", "B02"), start=1):
                dst.write(bands[band], index)
                dst.set_band_description(index, f"{band} surface reflectance")
            dst.update_tags(
                source_stac_item=item["id"], source_asset_names="B04,B03,B02",
                source_provider="Microsoft Planetary Computer Sentinel-2 L2A COGs",
                source_acquisition_time=item["properties"]["datetime"],
                reflectance_formula="(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE",
                boa_add_offset="-1000", boa_quantification_value="10000",
                clear_mask_source="Registered Phase 7 B03 reflectance validity mask (SCL clear codes 2,4,5,6)",
                display_note="Natural-colour band order RGB=B04,B03,B02; reflectance values, not visually stretched",
                study_area_status="provisional regional AOI grid",
            )
        results.append({
            "evidence_id": f"s2-true-colour-{date}", "date": date,
            "path": output_path.relative_to(ROOT).as_posix(), "bytes": output_path.stat().st_size,
            "sha256": sha256(output_path), "width": width, "height": height,
            "crs": str(profile["crs"]), "resolution_m": 10,
            "valid_pixels": int(np.count_nonzero(np.logical_and.reduce([bands[band] != -9999.0 for band in ("B04", "B03", "B02")]))) ,
            "source_stac_item": item["id"], "source_assets": sources,
            "source_scene_datetime": item["properties"]["datetime"],
            "processed_utc": datetime.now(timezone.utc).isoformat(),
        })
    manifest["sentinel2_true_colour"] = {
        "provider": "Microsoft Planetary Computer Sentinel-2 L2A",
        "access_method": "Planetary Computer public SAS signing API; temporary signed URLs are not saved",
        "processing": "AOI grid clipped from same S2B acquisition; B04/B03/B02 reflectance, offset -1000 and quantification 10000; clear mask inherited from existing Phase 7 B03 validity mask",
        "band_order": ["B04 red", "B03 green", "B02 blue"],
        "display_stretch": "0–0.4 reflectance linear display stretch in preview service",
        "observations": results,
        "limitations": ["Provisional regional search extent, not an enclosure boundary.", "Cloud/shadow and all validity treatment follows the existing Phase 7 B03 mask; no independent new mask was generated.", "True-colour imagery is contextual observation, not ground truth for water or incident impact."],
    }
    for result in results:
        evidence_id = result["evidence_id"]
        records[:] = [record for record in records if record.get("evidence_id") != evidence_id]
        records.append({
            "evidence_id": evidence_id, "evidence_category": "derived_satellite_measurement",
            "title": f"Sentinel-2 true-colour RGB observation {result['date']}",
            "source_dataset": result["source_stac_item"], "acquisition_date": result["date"],
            "processing_date": datetime.now(timezone.utc).date().isoformat(),
            "spatial_coverage": {"crs": result["crs"], "width": result["width"], "height": result["height"], "valid_pixels": result["valid_pixels"]},
            "crs": result["crs"], "original_file": None,
            "derived_file": {"path": result["path"], "availability": "available", "bytes": result["bytes"], "sha256": result["sha256"], "checksum_matches_manifest": True},
            "confidence_or_validation_status": "verified", "processing_methodology": "AOI-only three-band surface-reflectance composite from the same S2B L2A scene as registered Phase 7 products; R=B04, G=B03, B=B02; source DN converted to reflectance and masked by existing Phase 7 clear-valid B03 mask.",
            "limitations": ["Provisional regional AOI, not a site/enclosure boundary.", "Reflectance composite is visual context, not water classification or incident confirmation."],
            "source_provenance": [stac_path.relative_to(ROOT).as_posix(), "data/gherproof/manifests/phase7_optical_processing.json", "data/gherproof/manifests/fisheries_context_manifest.json"],
            "metadata": {"band_order": ["B04", "B03", "B02"], "display": "linear reflectance stretch 0 to 0.4", "source_scene_datetime": result["source_scene_datetime"], "provider": "Microsoft Planetary Computer Sentinel-2 L2A"},
        })
    registry["record_count"] = len(records)
    registry["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
