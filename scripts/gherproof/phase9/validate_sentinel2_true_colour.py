"""Validate registered true-colour rasters and refresh measured coverage metadata."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import rasterio

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "data/gherproof/manifests/fisheries_context_manifest.json"
REGISTRY = ROOT / "data/gherproof/manifests/evidence_registry.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    checks = []
    for observation in manifest["sentinel2_true_colour"]["observations"]:
        path = ROOT / observation["path"]
        with rasterio.open(path) as dataset:
            assert dataset.count == 3
            assert dataset.crs.to_epsg() == 32645
            assert dataset.res == (10.0, 10.0)
            assert dataset.descriptions == ("B04 surface reflectance", "B03 surface reflectance", "B02 surface reflectance")
            valid_pixels = int((dataset.dataset_mask() > 0).sum())
            checks.append({"date": observation["date"], "width": dataset.width, "height": dataset.height, "crs": dataset.crs.to_string(), "resolution_m": dataset.res[0], "valid_pixels": valid_pixels, "bounds": list(dataset.bounds), "sha256": sha256(path)})
        record = next(item for item in registry["records"] if item["evidence_id"] == observation["evidence_id"])
        record["evidence_category"] = "derived_satellite_measurement"
        record["spatial_coverage"]["valid_pixels"] = valid_pixels
        record["derived_file"]["sha256"] = checks[-1]["sha256"]
        record["derived_file"]["bytes"] = path.stat().st_size
        observation["valid_pixels"] = valid_pixels
        observation["sha256"] = checks[-1]["sha256"]
        observation["bytes"] = path.stat().st_size
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
