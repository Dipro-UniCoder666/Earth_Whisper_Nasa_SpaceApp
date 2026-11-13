import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/gherproof"))
import verify_event_imagery as verify
import recover_event_imagery as recovery


def make_raster(path, array, crs="EPSG:32645", transform=None, nodata=-9999):
    with rasterio.open(path, "w", driver="GTiff", height=array.shape[0], width=array.shape[1], count=1,
                       dtype=array.dtype, crs=crs, transform=transform or from_origin(500000, 2500000, 10, 10), nodata=nodata) as dst:
        dst.write(array, 1)


def test_raster_metadata_and_bounded_statistics(tmp_path):
    raster = tmp_path / "scene.tif"
    array = np.arange(100, dtype=np.float32).reshape(10, 10)
    array[0, 0] = -9999
    make_raster(raster, array)
    result = verify.inspect(raster)
    assert result["crs"] == "EPSG:32645"
    assert result["resolution"] == [10.0, 10.0]
    assert result["statistics"]["valid_pixels"] == 99
    assert result["statistics"]["min"] == 1.0
    assert result["statistics"]["max"] == 99.0
    assert result["statistics"]["percentile_sample_count"] <= 500_000


def test_scene_grid_alignment_requires_crs_dimensions_and_transform():
    a = {"crs": "EPSG:32645", "width": 100, "height": 100, "transform": [10, 0, 500000, 0, -10, 2500000, 0, 0, 1]}
    assert verify._same_grid(a, dict(a))
    assert not verify._same_grid(a, {**a, "crs": "EPSG:4326"})
    assert not verify._same_grid(a, {**a, "transform": [10, 0, 500010, 0, -10, 2500000, 0, 0, 1]})


def test_non_georeferenced_or_multiband_product_is_rejected(tmp_path):
    raster = tmp_path / "bad.tif"
    with rasterio.open(raster, "w", driver="GTiff", height=2, width=2, count=2, dtype="uint8") as dst:
        dst.write(np.zeros((2, 2), dtype=np.uint8), 1)
        dst.write(np.zeros((2, 2), dtype=np.uint8), 2)
    with pytest.raises(ValueError, match="Missing CRS"):
        verify.inspect(raster)


def test_resumed_download_checks_bytes_and_opens_actual_raster(tmp_path, monkeypatch):
    raster = tmp_path / "source.tif"
    make_raster(raster, np.arange(100, dtype=np.float32).reshape(10, 10))
    content = raster.read_bytes()
    target = tmp_path / "download" / "VV.tif"
    target.parent.mkdir()
    partial = target.with_suffix(target.suffix + ".part")
    cut = len(content) // 2
    partial.write_bytes(content[:cut])

    class Auth:
        def get(self, url, **kwargs):
            assert kwargs["headers"]["Range"] == f"bytes={cut}-"
            class DownloadResponse:
                status_code = 206
                headers = {"Content-Range": f"bytes {cut}-{len(content)-1}/{len(content)}"}
                def __enter__(self): return self
                def __exit__(self, *_args): return False
                def raise_for_status(self): pass
                def iter_content(self, _size): yield content[cut:]
            return DownloadResponse()

    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    result = recovery._download(Auth(), "https://zipper.dataspace.copernicus.eu/product", target, len(content))
    assert result["status"] == "verified"
    assert result["bytes"] == len(content)
    assert len(result["sha256"]) == 64
    assert rasterio.open(target).count == 1
