import earthaccess
import rasterio
import numpy as np
import os
import csv
from pyproj import Transformer

earthaccess.login(strategy="netrc")

out = "/mnt/d/Earth_Whisper_Nasa/Earth_Whisper/data/step4_optical_verification"
os.makedirs(out, exist_ok=True)

candidates = [
    ("1786", 90.1647003, 22.4790948),
    ("207",  90.2196199, 22.5057297),
    ("265",  90.2193002, 22.5057964),
    ("246",  90.1515533, 22.5042809),
    ("970",  90.1977177, 22.4930461),
    ("188",  90.1662475, 22.5055933),
]

dates = {
    "20260626": "HLS.S30.T46QBK.2026177T043231.v2.0",
    "20260914": "HLS.S30.T46QBK.2026257T043231.v2.0",
}

x0 = 199980.0
y0 = 2500020.0
res = 30.0

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32646",
    always_xy=True
)

rows = []

for date, gran in dates.items():

    base = (
        f"https://data.lpdaac.earthdatacloud.nasa.gov/"
        f"lp-prod-protected/HLSS30.020/{gran}/{gran}."
    )

    ras = {}

    for band in ["B03", "B08", "B11", "Fmask"]:
        url = base + band + ".tif"
        ras[band] = rasterio.open(
            earthaccess.open([url])[0]
        )

    for rid, lon, lat in candidates:

        x, y = transformer.transform(lon, lat)

        col = int((x - x0) / res)
        row = int((y0 - y) / res)

        window = (
            (max(0, row - 2), row + 3),
            (max(0, col - 2), col + 3)
        )

        a = {
            band: ras[band].read(
                1,
                window=window
            ).astype(np.float32)
            for band in ras
        }

        f = a["Fmask"].astype(np.uint16)

        bad = (
            ((f >> 1) & 1) |
            ((f >> 2) & 1) |
            ((f >> 3) & 1) |
            ((f >> 4) & 1) |
            (a["B03"] == -9999) |
            (a["B08"] == -9999) |
            (a["B11"] == -9999)
        ).astype(bool)

        ndwi = (
            (a["B03"] - a["B08"]) /
            (a["B03"] + a["B08"])
        )

        mndwi = (
            (a["B03"] - a["B11"]) /
            (a["B03"] + a["B11"])
        )

        valid = (
            (~bad) &
            np.isfinite(ndwi) &
            np.isfinite(mndwi) &
            ((a["B03"] + a["B08"]) != 0) &
            ((a["B03"] + a["B11"]) != 0)
        )

        if valid.any():

            ndwi_valid = ndwi[valid]
            mndwi_valid = mndwi[valid]

            ndwi_median = float(np.median(ndwi_valid))
            mndwi_median = float(np.median(mndwi_valid))

            ndwi_water = int(
                (ndwi_valid > 0.2).sum()
            )

            mndwi_water = int(
                (mndwi_valid > 0.2).sum()
            )

        else:

            ndwi_median = np.nan
            mndwi_median = np.nan
            ndwi_water = 0
            mndwi_water = 0

        rows.append([
            rid,
            date,
            lon,
            lat,
            row,
            col,
            int(valid.sum()),
            valid.size,
            ndwi_median,
            mndwi_median,
            ndwi_water,
            mndwi_water
        ])

    for band in ras:
        ras[band].close()

output = os.path.join(
    out,
    "step4_candidate_optical_screening.csv"
)

with open(output, "w", newline="") as fp:

    writer = csv.writer(fp)

    writer.writerow([
        "region_id",
        "date",
        "longitude",
        "latitude",
        "hls_row",
        "hls_col",
        "valid_pixels",
        "window_pixels",
        "ndwi_median",
        "mndwi_median",
        "ndwi_water_pixels",
        "mndwi_water_pixels"
    ])

    writer.writerows(rows)

print()
print("STEP 4 OPTICAL SCREENING COMPLETE")
print("SAVED:", output)
print()
print("RESULTS:")

for r in rows:
    print(
        r[0],
        r[1],
        "valid=", r[6],
        "/",
        r[7],
        "NDWI=", round(r[8], 4) if np.isfinite(r[8]) else "nan",
        "MNDWI=", round(r[9], 4) if np.isfinite(r[9]) else "nan",
        "NDWI_water=", r[10],
        "MNDWI_water=", r[11]
    )
