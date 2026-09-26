from osgeo import gdal, osr
import numpy as np
import csv
from collections import deque

# ------------------------------------------------------------
# NISAR exact AOI grid
# ------------------------------------------------------------
NISAR_X0 = 206713.617
NISAR_Y0 = 2492071.936
NISAR_DX = 20.0
NISAR_DY = -20.0

# ------------------------------------------------------------
# Load exact NISAR arrays
# ------------------------------------------------------------
mask = np.load("step2_exact_aoi_mask.npy")
hh = np.load("HH_023_to_029_coherence_change_exact_aoi.npy")
vv = np.load("VV_025_to_026_coherence_change_exact_aoi.npy")

# ------------------------------------------------------------
# Sentinel-1 dB change raster
# ------------------------------------------------------------
s1_file = "S1D_20260703_to_20260715_Sandhya_VV_dB_change.tif"

ds = gdal.Open(s1_file, gdal.GA_ReadOnly)

if ds is None:
    raise RuntimeError("Could not open Sentinel-1 change raster.")

s1 = ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
gt = ds.GetGeoTransform()

print("Sentinel-1 raster:", s1.shape)
print("NISAR change grid:", mask.shape)

# ------------------------------------------------------------
# UTM 46N -> WGS84 transformation
# ------------------------------------------------------------
src_srs = osr.SpatialReference()
src_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
src_srs.ImportFromEPSG(32646)

dst_srs = osr.SpatialReference()
dst_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
dst_srs.ImportFromEPSG(4326)

transform = osr.CoordinateTransformation(src_srs, dst_srs)


def utm_to_lonlat(x, y):
    result = transform.TransformPoint(float(x), float(y))
    return result[0], result[1]


# ------------------------------------------------------------
# 8-connected component labeling
# ------------------------------------------------------------
def label_components(binary):

    rows, cols = binary.shape
    labels = np.zeros((rows, cols), dtype=np.int32)
    current = 0

    neighbors = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for r in range(rows):
        for c in range(cols):

            if not binary[r, c] or labels[r, c] != 0:
                continue

            current += 1
            labels[r, c] = current

            q = deque([(r, c)])

            while q:

                cr, cc = q.popleft()

                for dr, dc in neighbors:

                    nr = cr + dr
                    nc = cc + dc

                    if (
                        0 <= nr < rows and
                        0 <= nc < cols and
                        binary[nr, nc] and
                        labels[nr, nc] == 0
                    ):
                        labels[nr, nc] = current
                        q.append((nr, nc))

    return labels, current


candidate_masks = {
    "HH_023_to_029": (hh <= -0.20) & mask,
    "VV_025_to_026": (vv <= -0.20) & mask
}

with open("step2_candidate_regions_geographic.csv", newline="") as f:
    region_rows = list(csv.DictReader(f))

components = {}

for comparison, cmask in candidate_masks.items():

    labels, num = label_components(cmask)

    components[comparison] = labels

    print(comparison, "raw components:", num)


# ------------------------------------------------------------
# Verify that CSV region IDs exist in reconstructed labels
# ------------------------------------------------------------
for comparison in components:

    ids = {
        int(r["region_id"])
        for r in region_rows
        if r["comparison"] == comparison
    }

    labels = components[comparison]

    found = sum(np.any(labels == rid) for rid in ids)

    print(
        comparison,
        "CSV regions:", len(ids),
        "IDs found:", found
    )


# ------------------------------------------------------------
# Convert a NISAR pixel center to Sentinel-1 pixel
# ------------------------------------------------------------
def nisar_pixel_to_s1(row, col):

    # NISAR pixel center
    x = NISAR_X0 + (col + 0.5) * NISAR_DX
    y = NISAR_Y0 + (row + 0.5) * NISAR_DY

    lon, lat = utm_to_lonlat(x, y)

    scol = int((lon - gt[0]) / gt[1])
    srow = int((lat - gt[3]) / gt[5])

    return srow, scol


# ------------------------------------------------------------
# Process each exact NISAR candidate
# ------------------------------------------------------------
results = []

for region in region_rows:

    comparison = region["comparison"]
    region_id = int(region["region_id"])

    labels = components[comparison]

    rr, cc = np.where(labels == region_id)

    if len(rr) == 0:
        continue

    s1_values = []

    for nr, nc in zip(rr, cc):

        sr, sc = nisar_pixel_to_s1(nr, nc)

        # Sentinel-1 is finer resolution than NISAR.
        # Collect a 4x4 neighborhood around each NISAR pixel center.
        r0 = max(0, sr - 2)
        r1 = min(s1.shape[0], sr + 3)
        c0 = max(0, sc - 2)
        c1 = min(s1.shape[1], sc + 3)

        vals = s1[r0:r1, c0:c1]

        vals = vals[np.isfinite(vals)]
        vals = vals[vals != 0]

        if vals.size:
            s1_values.extend(vals.tolist())

    if not s1_values:
        continue

    values = np.asarray(s1_values, dtype=np.float32)

    results.append({
        "comparison": comparison,
        "region_id": region_id,
        "nisar_pixels": len(rr),
        "area_m2": float(region["area_m2"]),
        "lon": float(region["lon"]),
        "lat": float(region["lat"]),
        "s1_n": len(values),
        "s1_mean_db": float(np.mean(values)),
        "s1_median_db": float(np.median(values)),
        "s1_min_db": float(np.min(values)),
        "s1_max_db": float(np.max(values)),
        "s1_p25_db": float(np.percentile(values, 25)),
        "s1_p75_db": float(np.percentile(values, 75)),
        "s1_pct_le_minus1db": float(np.mean(values <= -1) * 100),
        "s1_pct_le_minus2db": float(np.mean(values <= -2) * 100),
        "s1_pct_le_minus3db": float(np.mean(values <= -3) * 100)
    })


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------
fieldnames = [
    "comparison",
    "region_id",
    "nisar_pixels",
    "area_m2",
    "lon",
    "lat",
    "s1_n",
    "s1_mean_db",
    "s1_median_db",
    "s1_min_db",
    "s1_max_db",
    "s1_p25_db",
    "s1_p75_db",
    "s1_pct_le_minus1db",
    "s1_pct_le_minus2db",
    "s1_pct_le_minus3db"
]

with open(
    "step2_nisar_s1_exact_overlap.csv",
    "w",
    newline=""
) as f:

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
print()
print("EXACT OVERLAP COMPLETE")
print("NISAR candidates:", len(region_rows))
print("Candidates with S1 overlap:", len(results))
print("Output: step2_nisar_s1_exact_overlap.csv")

print()
print("Strongest exact-overlap Sentinel-1 decreases:")

results.sort(key=lambda x: x["s1_median_db"])

for x in results[:20]:

    print(
        x["comparison"],
        "region", x["region_id"],
        "NISAR pixels", x["nisar_pixels"],
        "S1 n", x["s1_n"],
        "median", round(x["s1_median_db"], 4),
        "mean", round(x["s1_mean_db"], 4),
        "<=-2dB", round(x["s1_pct_le_minus2db"], 2), "%"
    )
