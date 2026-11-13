"""Register processed validated NISAR GCOV observations and temporal layers."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import rasterio

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/gherproof"
OUT = DATA / "processed/nisar/validated"
REGISTRY_PATH = DATA / "manifests/evidence_registry.json"
PRODUCTS = (
    ("2026-10-23", 33, 6593445888, "NISAR_L2_PR_GCOV_033_170_A_013_4005_DHDH_A_20261023T232918_20261023T232952_P05036_N_F_J_001"),
    ("2026-11-04", 34, 6568280064, "NISAR_L2_PR_GCOV_034_170_A_013_4005_DHDH_A_20261104T232918_20261104T232952_P05036_N_F_J_001"),
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "availability": "available", "bytes": path.stat().st_size, "sha256": digest(path)}


def raster_metadata(path: Path) -> dict:
    with rasterio.open(path) as ds:
        return {"crs": ds.crs.to_string(), "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
                "width": ds.width, "height": ds.height, "resolution_m": list(ds.res), "count": ds.count,
                "dtype": list(ds.dtypes), "nodata": ds.nodata, "band_descriptions": list(ds.descriptions)}


def source_url(name: str) -> str:
    return f"https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/{name}/{name}.h5"


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = [r for r in registry["records"] if not r.get("evidence_id", "").startswith("nisar-gcov-")]
    run_date = datetime.now(timezone.utc).date().isoformat()
    for date, cycle, source_bytes, product in PRODUCTS:
        for frequency, suffix, bandwidth, resolution in (("A", "", 40, 10), ("B", "_frequencyB_80m", 5, 80)):
            prefix = OUT / f"nisar_{date}_track170_ascending_validated{suffix}"
            details = json.loads(Path(f"{prefix}_manifest.json").read_text(encoding="utf-8"))
            gamma = OUT / f"{prefix.name}_gamma0_power.tif"
            valid = OUT / f"{prefix.name}_valid_mask.tif"
            quality = OUT / f"{prefix.name}_quality.tif"
            raster = raster_metadata(gamma)
            frequency_label = f"Frequency {frequency} · {resolution} m"
            evidence_id = f"nisar-gcov-{date}-track170-ascending-validated" + ("-frequencyB" if frequency == "B" else "")
            records.append({
                "evidence_id": evidence_id,
                "evidence_category": "verified_satellite_observation",
                "title": f"NISAR L-band validated GCOV {frequency_label} HH/HV · {date}",
                "source_dataset": "NASA-ISRO NISAR L2 GCOV via ASF DAAC",
                "source": "NASA/ISRO NISAR; Alaska Satellite Facility DAAC",
                "acquisition_date": date,
                "processing_date": run_date,
                "spatial_coverage": {"crs": raster["crs"], "bounds": raster["bounds"], "resolution_m": raster["resolution_m"],
                                     "width": raster["width"], "height": raster["height"],
                                     "aoi_status": "provisional regional search envelope; not an authoritative boundary",
                                     "valid_pixel_fraction_HHHH": details["HHHH"]["valid_fraction_of_aoi_pixels"],
                                     "valid_pixel_fraction_HVHV": details["HVHV"]["valid_fraction_of_aoi_pixels"]},
                "crs": raster["crs"],
                "original_file": {"availability": "not_downloaded", "url": source_url(product), "bytes": source_bytes,
                                  "note": "Only regional HDF5 windows were fetched by authenticated HTTP Range; complete source product not downloaded."},
                "derived_file": file_record(gamma),
                "confidence_or_validation_status": "verified",
                "processing_methodology": f"NISAR L2 GCOV frequency{frequency} HHHH/HVHV diagonal terms copied as dimensionless linear gamma0 power, {resolution} m native grid; focused-data mask and per-polarization validity bits applied; raw masks retained separately; gamma0-to-sigma0 factor not applied.",
                "limitations": [
                    "Acquired in October/November 2026; not evidence for the reported January 2026 incident.",
                    "The provisional regional envelope is not an exact village, site or fisheries-enclosure boundary.",
                    "Gamma0 power is radar backscatter, not water probability or confirmed flood extent.",
                    "Complete source HDF5 was not downloaded; a full source checksum was not independently recomputed.",
                    "NISAR data were not used as inputs to Sentinel-1-trained models.",
                ],
                "metadata": {"mission": "NASA-ISRO NISAR", "product": product, "product_level": "L2 GCOV", "maturity": "VALIDATED",
                             "crid": "P05036", "acquisition_datetime_utc": f"{date}T23:29:18Z", "cycle": cycle,
                             "relative_orbit": 170, "orbit_direction": "ascending", "instrument_band": "L-band",
                             "frequency_grid": f"frequency{frequency}", "range_bandwidth_mhz": bandwidth,
                             "product_polarizations": ["HH", "HV"], "covariance_terms": ["HHHH", "HVHV"],
                             "measurements": {"HHHH": details["HHHH"], "HVHV": details["HVHV"]},
                             "mask_file": file_record(valid), "quality_file": file_record(quality),
                             "mean_number_of_looks_in_aoi": details["mean_number_of_looks_in_aoi"],
                             "valid_mask_rule": details["valid_mask_rule"], "source_file_bytes": source_bytes,
                             "full_source_hdf5_downloaded": False,
                             "attribution": "NASA/ISRO NISAR data distributed by ASF DAAC; cite the product ID and ASF DAAC, following NASA Earthdata data-use policy."},
            })

    comparison = json.loads((OUT / "nisar_temporal_comparison_manifest.json").read_text(encoding="utf-8"))
    for frequency in ("A", "B"):
        grid = comparison["frequency_grids"][f"frequency{frequency}"]
        output = OUT / grid["output"]
        raster = raster_metadata(output)
        suffix = "-frequencyB" if frequency == "B" else ""
        records.append({
            "evidence_id": f"nisar-gcov-change-2026-10-23-to-2026-11-04-track170{suffix}",
            "evidence_category": "derived_satellite_measurement",
            "title": f"NISAR exploratory Frequency {frequency} gamma0 change, Oct 23 → Nov 4, 2026 (HH/HV, dB)",
            "source_dataset": "Derived from NASA-ISRO NISAR L2 GCOV via ASF DAAC",
            "acquisition_date": None, "processing_date": run_date,
            "spatial_coverage": {"crs": raster["crs"], "bounds": raster["bounds"], "resolution_m": raster["resolution_m"],
                                 "width": raster["width"], "height": raster["height"], "aoi_status": "provisional regional search envelope"},
            "crs": raster["crs"], "original_file": None, "derived_file": file_record(output),
            "confidence_or_validation_status": "derived_exploratory",
            "processing_methodology": f"10log10(later linear gamma0 / earlier linear gamma0), per like polarization on native frequency{frequency} grid using common valid mask.",
            "limitations": ["Temporal backscatter change only; not a water/flood probability or January incident evidence.",
                            "Surface moisture, vegetation, roughness, irrigation/aquaculture, rainfall, tidal influence, speckle and acquisition effects may contribute."],
            "metadata": {"dates": comparison["dates"], "frequency_grid": f"frequency{frequency}",
                         "source_evidence_ids": [f"nisar-gcov-{date}-track170-ascending-validated" + ("-frequencyB" if frequency == "B" else "") for date in ("2026-10-23", "2026-11-04")],
                         "polarizations": ["HHHH", "HVHV"], "units": "dB ratio", "statistics": grid["polarizations"],
                         "common_mask": file_record(OUT / grid["common_mask"])},
        })
    registry["records"] = records
    registry["record_count"] = len(records)
    counts: dict[str, int] = {}
    for record in records:
        counts[record["evidence_category"]] = counts.get(record["evidence_category"], 0) + 1
    registry["category_counts"] = counts
    registry["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    registry["repository"] = "Earth Whisper / DHARA"
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"record_count": len(records), "nisar_evidence_ids": [r["evidence_id"] for r in records if r["evidence_id"].startswith("nisar-gcov-")]}, indent=2))


if __name__ == "__main__":
    main()
