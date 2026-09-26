from osgeo import gdal
import numpy as np
import csv
import math

regions_file = "step2_candidate_regions_geographic.csv"
s1_file = "S1D_20260703_to_20260715_Sandhya_VV_dB_change.tif"

with open(regions_file, newline="") as f:
    rows = list(csv.DictReader(f))

ds = gdal.Open(s1_file, gdal.GA_ReadOnly)

if ds is None:
    raise RuntimeError("Could not open Sentinel-1 change raster.")

arr = ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
gt = ds.GetGeoTransform()

def lonlat_to_pixel(lon, lat):
    col = int((lon - gt[0]) / gt[1])
    row = int((lat - gt[3]) / gt[5])
    return row, col

results = []

for r in rows:

    lon = float(r["lon"])
    lat = float(r["lat"])
    nisar_pixels = int(r["pixels"])
    area_m2 = float(r["area_m2"])

    row, col = lonlat_to_pixel(lon, lat)

    radius = max(2, int(math.sqrt(nisar_pixels) / 2))

    r0 = max(0, row - radius)
    r1 = min(arr.shape[0], row + radius + 1)
    c0 = max(0, col - radius)
    c1 = min(arr.shape[1], col + radius + 1)

    values = arr[r0:r1, c0:c1]

    values = values[np.isfinite(values)]
    values = values[values != 0]

    if values.size == 0:
        continue

    results.append({
        "comparison": r["comparison"],
        "region_id": int(r["region_id"]),
        "pixels": nisar_pixels,
        "area_m2": area_m2,
        "lon": lon,
        "lat": lat,
        "s1_n": values.size,
        "s1_mean_db": float(np.mean(values)),
        "s1_median_db": float(np.median(values)),
        "s1_min_db": float(np.min(values)),
        "s1_max_db": float(np.max(values)),
        "s1_pct_le_minus1db": float(np.mean(values <= -1) * 100),
        "s1_pct_le_minus2db": float(np.mean(values <= -2) * 100),
        "s1_pct_le_minus3db": float(np.mean(values <= -3) * 100)
    })

fieldnames = [
    "comparison",
    "region_id",
    "pixels",
    "area_m2",
    "lon",
    "lat",
    "s1_n",
    "s1_mean_db",
    "s1_median_db",
    "s1_min_db",
    "s1_max_db",
    "s1_pct_le_minus1db",
    "s1_pct_le_minus2db",
    "s1_pct_le_minus3db"
]

with open("step2_nisar_s1_crosscheck.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

results.sort(key=lambda x: x["s1_mean_db"])

print("NISAR candidates:", len(rows))
print("Candidates with Sentinel-1 samples:", len(results))
print("Output: step2_nisar_s1_crosscheck.csv")

print()
print("Top 20 candidates by Sentinel-1 mean decrease:")
print("comparison region pixels lon lat s1_n mean_dB median_dB pct_<=-2dB")

for x in results[:20]:
    print(
        x["comparison"],
        x["region_id"],
        x["pixels"],
        round(x["lon"], 7),
        round(x["lat"], 7),
        x["s1_n"],
        round(x["s1_mean_db"], 4),
        round(x["s1_median_db"], 4),
        round(x["s1_pct_le_minus2db"], 2)
    )
