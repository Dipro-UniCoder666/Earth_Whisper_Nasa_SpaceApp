import csv
from pyproj import Transformer

rows = list(csv.DictReader(open("step2_candidate_regions_exact_aoi.csv")))
rows = sorted(rows, key=lambda r: int(r["pixels"]), reverse=True)[:30]

t = Transformer.from_crs("EPSG:32646", "EPSG:4326", always_xy=True)

print("comparison,region_id,pixels,area_m2,lon,lat,mean_change")

for r in rows:
    col = float(r["centroid_col"])
    row = float(r["centroid_row"])

    easting = 206730 + col * 20
    northing = 2492070 - row * 20

    lon, lat = t.transform(easting, northing)

    print(
        r["comparison"],
        r["region_id"],
        r["pixels"],
        r["area_m2"],
        f"{lon:.6f}",
        f"{lat:.6f}",
        r["mean_change"],
        sep=","
    )
