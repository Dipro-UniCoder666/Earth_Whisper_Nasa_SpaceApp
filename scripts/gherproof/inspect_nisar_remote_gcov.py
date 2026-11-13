"""Inspect an ASF DAAC NISAR GCOV HDF5 over authenticated byte-range HTTP.

The script reads metadata only; it does not download a complete HDF5 scene.
ASF/Earthdata credentials are resolved by Requests from the user's local
credential configuration (for example .netrc) and are never printed.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import hashlib
import math
from typing import Any

import h5py
import requests
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds, transform_geom
from pathlib import Path


DEFAULT_PRODUCTS = {
    "2026-10-23": (
        "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/"
        "NISAR_L2_PR_GCOV_033_170_A_013_4005_DHDH_A_20261023T232918_20261023T232952_P05036_N_F_J_001/"
        "NISAR_L2_PR_GCOV_033_170_A_013_4005_DHDH_A_20261023T232918_20261023T232952_P05036_N_F_J_001.h5"
    ),
    "2026-11-04": (
        "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/"
        "NISAR_L2_PR_GCOV_034_170_A_013_4005_DHDH_A_20261104T232918_20261104T232952_P05036_N_F_J_001/"
        "NISAR_L2_PR_GCOV_034_170_A_013_4005_DHDH_A_20261104T232918_20261104T232952_P05036_N_F_J_001.h5"
    ),
}


class HTTPRangeFile(io.RawIOBase):
    """Small seekable file object backed by authenticated HTTP Range reads."""

    def __init__(self, url: str, block_size: int = 1 << 20, timeout: int = 45):
        super().__init__()
        self.url = url
        self.block_size = block_size
        self.timeout = timeout
        self.session = requests.Session()  # honors local .netrc without exposing it
        self.position = 0
        self.blocks: dict[int, bytes] = {}
        self.request_count = 0
        self.bytes_read = 0
        response = self.session.get(
            self.url,
            headers={"Range": "bytes=0-0"},
            timeout=self.timeout,
            stream=True,
        )
        self.request_count += 1
        if response.status_code != 206:
            status = response.status_code
            response.close()
            raise OSError(f"ASF range probe failed with HTTP {status}; credentials are not reported")
        content_range = response.headers.get("Content-Range", "")
        match = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
        if not match:
            response.close()
            raise OSError("ASF response omitted a valid Content-Range total")
        self.size = int(match.group(1))
        response.close()

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new_position = offset
        elif whence == io.SEEK_CUR:
            new_position = self.position + offset
        elif whence == io.SEEK_END:
            new_position = self.size + offset
        else:
            raise ValueError("invalid seek mode")
        if new_position < 0:
            raise ValueError("negative seek position")
        self.position = min(new_position, self.size)
        return self.position

    def _get_block(self, block_start: int) -> bytes:
        if block_start not in self.blocks:
            block_end = min(self.size - 1, block_start + self.block_size - 1)
            response = self.session.get(
                self.url,
                headers={"Range": f"bytes={block_start}-{block_end}"},
                timeout=self.timeout,
                stream=True,
            )
            self.request_count += 1
            if response.status_code != 206:
                status = response.status_code
                response.close()
                raise OSError(f"ASF range read failed with HTTP {status}; credentials are not reported")
            block = response.content
            response.close()
            expected = block_end - block_start + 1
            if len(block) != expected:
                raise OSError(f"Short range response: expected {expected} bytes, received {len(block)}")
            self.blocks[block_start] = block
            self.bytes_read += len(block)
        return self.blocks[block_start]

    def readinto(self, buffer: bytearray | memoryview) -> int:
        if self.position >= self.size:
            return 0
        needed = min(len(buffer), self.size - self.position)
        written = 0
        while written < needed:
            block_start = (self.position // self.block_size) * self.block_size
            block = self._get_block(block_start)
            offset = self.position - block_start
            amount = min(needed - written, len(block) - offset)
            buffer[written : written + amount] = block[offset : offset + amount]
            self.position += amount
            written += amount
        return written

    def close(self) -> None:
        if not self.closed:
            self.session.close()
        super().close()


def json_safe(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return json_safe(value.tolist())
    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except (ValueError, TypeError):
            pass
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, h5py.Reference):
        return "<HDF5 object reference>"
    return str(value)


def inspect(product_date: str, extract_dir: Path | None = None, aoi_path: Path | None = None, frequency: str = "A") -> dict[str, Any]:
    url = DEFAULT_PRODUCTS[product_date]
    remote = HTTPRangeFile(url)
    with h5py.File(remote, "r") as h5:
        root_attrs = {key: json_safe(value) for key, value in h5.attrs.items()}
        grid = h5[f"/science/LSAR/GCOV/grids/frequency{frequency}"]
        grids = h5["/science/LSAR/GCOV/grids"]
        datasets: list[dict[str, Any]] = []

        def collect(name: str, obj: h5py.Dataset | h5py.Group) -> None:
            if isinstance(obj, h5py.Dataset):
                attrs = {key: json_safe(value) for key, value in obj.attrs.items()}
                datasets.append(
                    {
                        "name": name,
                        "shape": list(obj.shape),
                        "dtype": str(obj.dtype),
                        "chunks": obj.chunks,
                        "compression": obj.compression,
                        "fill_value": json_safe(obj.fillvalue),
                        "attributes": attrs,
                    }
                )
        grid.visititems(collect)
        result = {
            "date": product_date,
            "url": url,
            "size_bytes": remote.size,
            "root_groups": list(h5.keys()),
            "root_attributes": root_attrs,
            f"frequency_{frequency.lower()}_entries": list(grid.keys()),
            "frequency_grid_groups": list(grids.keys()),
            "frequency_a_datasets": datasets,
            "remote_range_requests": remote.request_count,
            "remote_bytes_read": remote.bytes_read,
            "full_product_downloaded": False,
            "epsg": int(grid["projection"].attrs["epsg_code"]),
            "x_spacing_m": float(grid["xCoordinateSpacing"][()]),
            "y_spacing_m": float(grid["yCoordinateSpacing"][()]),
            "x_first_center_m": float(grid["xCoordinates"][0]),
            "x_last_center_m": float(grid["xCoordinates"][-1]),
            "y_first_center_m": float(grid["yCoordinates"][0]),
            "y_last_center_m": float(grid["yCoordinates"][-1]),
        }
        if "frequencyB" in grids:
            frequency_b = grids["frequencyB"]
            result["frequency_b_entries"] = list(frequency_b.keys())
            result["frequency_b_covariance_terms"] = {
                name: {"shape": list(frequency_b[name].shape), "dtype": str(frequency_b[name].dtype),
                       "units": json_safe(frequency_b[name].attrs.get("units")),
                       "long_name": json_safe(frequency_b[name].attrs.get("long_name"))}
                for name in ("HHHH", "HVHV") if name in frequency_b
            }
        if extract_dir is not None:
            if aoi_path is None:
                raise ValueError("--aoi is required with --extract-dir")
            result["extraction"] = extract_region(product_date, remote, grid, extract_dir, aoi_path, frequency)
        return result


def extract_region(product_date: str, remote: HTTPRangeFile, grid: h5py.Group,
                   output_dir: Path, aoi_path: Path, frequency: str) -> dict[str, Any]:
    """Write just the transformed provisional regional AOI window and GCOV masks."""
    aoi_doc = json.loads(aoi_path.read_text(encoding="utf-8"))
    geometry = aoi_doc["features"][0]["geometry"]
    aoi_bounds = tuple(float(v) for v in __import__("shapely.geometry", fromlist=["shape"]).shape(geometry).bounds)
    epsg = int(grid["projection"].attrs["epsg_code"])
    bounds = transform_bounds("EPSG:4326", f"EPSG:{epsg}", *aoi_bounds, densify_pts=41)
    xs = grid["xCoordinates"][:]
    ys = grid["yCoordinates"][:]
    cols = np.flatnonzero((xs >= bounds[0]) & (xs <= bounds[2]))
    rows = np.flatnonzero((ys >= bounds[1]) & (ys <= bounds[3]))
    if not len(cols) or not len(rows):
        raise ValueError("AOI does not intersect product coordinate vectors")
    c0, c1 = int(cols[0]), int(cols[-1]) + 1
    r0, r1 = int(rows[0]), int(rows[-1]) + 1
    xres = abs(float(grid["xCoordinateSpacing"][()]))
    yres = abs(float(grid["yCoordinateSpacing"][()]))
    if xres <= 0 or yres <= 0:
        raise ValueError("Product has invalid coordinate spacing")
    transform = from_origin(float(xs[c0]) - xres / 2, float(ys[r0]) + yres / 2, xres, yres)
    output_dir.mkdir(parents=True, exist_ok=True)
    aoi_projected = transform_geom("EPSG:4326", f"EPSG:{epsg}", geometry, precision=3)
    inside_aoi = geometry_mask([aoi_projected], out_shape=(r1-r0, c1-c0), transform=transform, invert=True)
    hh = grid["HHHH"][r0:r1, c0:c1].astype(np.float32)
    hv = grid["HVHV"][r0:r1, c0:c1].astype(np.float32)
    gcov_mask = grid["mask"][r0:r1, c0:c1].astype(np.uint8)
    exception = grid["inputDataExceptionMask"][r0:r1, c0:c1].astype(np.uint16)
    looks = grid["numberOfLooks"][r0:r1, c0:c1].astype(np.float32)
    # GCOV mask 0 is partially-focused/invalid; 255 is outside acquisition.
    # Exception-mask validity bits independently assert fully-focused HH (256) and HV (512).
    hh_valid = inside_aoi & (gcov_mask > 0) & (gcov_mask < 255) & ((exception & 256) != 0) & np.isfinite(hh)
    hv_valid = inside_aoi & (gcov_mask > 0) & (gcov_mask < 255) & ((exception & 512) != 0) & np.isfinite(hv)
    # Preserve measured linear gamma0 power; invalid pixels are nodata, not zero backscatter.
    hh[~hh_valid] = -9999.0
    hv[~hv_valid] = -9999.0
    suffix = "" if frequency == "A" else "_frequencyB_80m"
    prefix = output_dir / f"nisar_{product_date}_track170_ascending_validated{suffix}"
    common = {
        "driver": "GTiff", "width": c1-c0, "height": r1-r0, "crs": f"EPSG:{epsg}",
        "transform": transform, "tiled": True, "compress": "deflate", "predictor": 3,
        "BIGTIFF": "IF_SAFER",
    }
    provenance_tags = {
        "mission": "NASA-ISRO NISAR", "source": "ASF DAAC", "product_date": product_date,
        "frequency_grid": f"frequency{frequency}",
        "product_maturity": "VALIDATED", "relative_orbit": "170", "orbit_direction": "ascending",
        "polarizations": "HH,HV", "measurement": "GCOV diagonal covariance power; linear gamma0; units 1",
        "processing_note": "Regional AOI window extracted from remote HDF5 via authenticated HTTP Range; full source product not downloaded.",
        "mask_rule": "GCOV subswath mask in 1..254 plus per-pol focused validity bit (HH=256, HV=512); outside AOI is nodata.",
        "source_product_url": DEFAULT_PRODUCTS[product_date],
    }
    with rasterio.open(f"{prefix}_gamma0_power.tif", "w", count=2, dtype="float32", nodata=-9999.0, **common) as dst:
        dst.write(hh, 1); dst.write(hv, 2)
        dst.set_band_description(1, "HHHH gamma0 covariance power (linear, unit 1)")
        dst.set_band_description(2, "HVHV gamma0 covariance power (linear, unit 1)")
        dst.update_tags(**provenance_tags, rtc_gamma_to_sigma_factor_applied="false")
    with rasterio.open(f"{prefix}_valid_mask.tif", "w", count=2, dtype="uint8", nodata=0, **{**common, "predictor": 2}) as dst:
        dst.write(hh_valid.astype(np.uint8), 1); dst.write(hv_valid.astype(np.uint8), 2)
        dst.set_band_description(1, "HHHH fully-focused valid-data mask")
        dst.set_band_description(2, "HVHV fully-focused valid-data mask")
        dst.update_tags(**provenance_tags)
    with rasterio.open(f"{prefix}_quality.tif", "w", count=2, dtype="uint16", nodata=65535, **{**common, "predictor": 2}) as dst:
        dst.write(gcov_mask.astype(np.uint16), 1); dst.write(exception, 2)
        dst.set_band_description(1, "GCOV subswath mask; 0 invalid, 255 outside scene")
        dst.set_band_description(2, "inputDataExceptionMask; raw bits preserved")
        dst.update_tags(**provenance_tags)
    def stats(values: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
        v = values[mask]
        if not v.size:
            return {"valid_pixels": 0, "valid_fraction_of_aoi_pixels": 0.0}
        return {"valid_pixels": int(v.size), "valid_fraction_of_aoi_pixels": float(v.size / inside_aoi.sum()),
                "min": float(np.min(v)), "median": float(np.median(v)), "p05": float(np.percentile(v, 5)),
                "p95": float(np.percentile(v, 95)), "max": float(np.max(v))}
    manifest = {
        "product_date": product_date, "frequency_grid": f"frequency{frequency}", "source_url": DEFAULT_PRODUCTS[product_date],
        "source_file_bytes": remote.size, "source_full_downloaded": False,
        "remote_range_requests": remote.request_count, "remote_bytes_read": remote.bytes_read,
        "aoi_source": str(aoi_path).replace("\\", "/"), "aoi_is_authoritative_boundary": False,
        "crs": f"EPSG:{epsg}", "transform": list(transform), "width": c1-c0, "height": r1-r0,
        "resolution_m": [xres, yres], "window": {"row_start": r0, "row_stop": r1, "col_start": c0, "col_stop": c1},
        "aoi_pixels": int(inside_aoi.sum()), "valid_mask_rule": provenance_tags["mask_rule"],
        "HHHH": stats(grid["HHHH"][r0:r1, c0:c1], hh_valid),
        "HVHV": stats(grid["HVHV"][r0:r1, c0:c1], hv_valid),
        "mean_number_of_looks_in_aoi": float(np.nanmean(np.where(inside_aoi, looks, np.nan))),
        "output_files": [f"{prefix.name}_gamma0_power.tif", f"{prefix.name}_valid_mask.tif", f"{prefix.name}_quality.tif"],
    }
    manifest_path = prefix.with_name(f"{prefix.name}_manifest.json")
    checksums = {}
    for filename in (f"{prefix.name}_gamma0_power.tif", f"{prefix.name}_valid_mask.tif", f"{prefix.name}_quality.tif"):
        path = output_dir / filename
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        checksums[filename] = {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}
    manifest["output_checksums"] = checksums
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", choices=sorted(DEFAULT_PRODUCTS), required=True)
    parser.add_argument("--frequency", choices=("A", "B"), default="A")
    parser.add_argument("--extract-dir", type=Path)
    parser.add_argument("--aoi", type=Path)
    args = parser.parse_args()
    result = inspect(args.date, args.extract_dir, args.aoi, args.frequency)
    output = result["extraction"] if args.extract_dir is not None else result
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
