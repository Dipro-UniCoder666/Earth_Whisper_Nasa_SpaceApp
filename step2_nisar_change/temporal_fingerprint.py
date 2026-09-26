from osgeo import gdal
import numpy as np
import csv

# NISAR exact grid
X0 = 206713.617
Y0 = 2492071.936
DX = 20.0
DY = -20.0

files = {
    "GUNW_023_HH": "GUNW_023_HH_coherence.npy",
    "GUNW_025_VV": "GUNW_025_VV_coherence.npy",
    "GUNW_026_VV": "GUNW_026_VV_coherence.npy",
    "GUNW_029_HH": "GUNW_029_HH_coherence.npy"
}

# Read the six strongest candidates from the ranking
with open("step2_nisar_s1_ranked.csv", newline="") as f:
    rows = list(csv.DictReader(f))

# First six ranked candidates
top = rows[:6]

arrays = {
    name: np.load(path)
    for name, path in files.items()
}

print("Temporal fingerprint for top 6 candidates")
print()

for r in top:

    lon = float(r["lon"])
    lat = float(r["lat"])

    # Convert geographic coordinate approximately back to NISAR UTM.
    # Use GDAL OSR for correct coordinate transformation.
    from osgeo import osr

    src = osr.SpatialReference()
    src.ImportFromEPSG(4326)
    src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    dst = osr.SpatialReference()
    dst.ImportFromEPSG(32646)
    dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    transform = osr.CoordinateTransformation(src, dst)

    x, y, _ = transform.TransformPoint(lon, lat)

    col = int((x - X0) / DX)
    row = int((y - Y0) / DY)

    print(
        "Region", r["region_id"],
        "|", r["comparison"],
        "| lon", lon,
        "| lat", lat
    )

    for name, arr in arrays.items():

        r0 = max(0, row - 1)
        r1 = min(arr.shape[0], row + 2)
        c0 = max(0, col - 1)
        c1 = min(arr.shape[1], col + 2)

        values = arr[r0:r1, c0:c1]

        values = values[np.isfinite(values)]
        values = values[values > 0]

        if values.size:
            print(
                " ",
                name,
                "median =", round(float(np.median(values)), 4),
                "mean =", round(float(np.mean(values)), 4)
            )
        else:
            print(" ", name, "NO VALID DATA")

    print()

