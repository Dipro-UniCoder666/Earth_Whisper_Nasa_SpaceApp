import numpy as np
import csv
from scipy import ndimage

# ---------------------------------------------------------
# NISAR exact-AOI grid
# ---------------------------------------------------------
mask = np.load("step2_exact_aoi_mask.npy").astype(bool)

# Coherence arrays
arrays = {
    "GUNW_023_HH": np.load("GUNW_023_HH_coherence.npy"),
    "GUNW_025_VV": np.load("GUNW_025_VV_coherence.npy"),
    "GUNW_026_VV": np.load("GUNW_026_VV_coherence.npy"),
    "GUNW_029_HH": np.load("GUNW_029_HH_coherence.npy"),
}

# ---------------------------------------------------------
# Recreate connected-component labels
# ---------------------------------------------------------
structure = np.ones((3, 3), dtype=np.uint8)

labels_hh, _ = ndimage.label(
    np.load("HH_023_to_029_coherence_change_exact_aoi.npy") <= -0.20,
    structure=structure
)

labels_vv, _ = ndimage.label(
    np.load("VV_025_to_026_coherence_change_exact_aoi.npy") <= -0.20,
    structure=structure
)

# ---------------------------------------------------------
# Read retained candidate IDs
# ---------------------------------------------------------
with open("step2_candidate_regions_exact_aoi.csv", newline="") as f:
    candidates = list(csv.DictReader(f))

print("Candidates:", len(candidates))
print("Calculating region-level temporal fingerprints...")
print()

output = []

for i, candidate in enumerate(candidates, 1):

    comparison = candidate["comparison"]
    region_id = int(candidate["region_id"])

    if comparison.startswith("HH"):
        labels = labels_hh
    else:
        labels = labels_vv

    region_mask = (labels == region_id) & mask

    n = int(region_mask.sum())

    if n == 0:
        continue

    row = dict(candidate)
    row["n_pixels"] = n

    values = {}

    for name, arr in arrays.items():

        v = arr[region_mask]

        v = v[np.isfinite(v)]
        v = v[(v > 0) & (v <= 1)]

        if len(v) == 0:
            median = np.nan
            mean = np.nan
        else:
            median = float(np.median(v))
            mean = float(np.mean(v))

        values[name] = median

        row[name + "_median"] = median
        row[name + "_mean"] = mean

    # -----------------------------------------------------
    # HH temporal change
    # -----------------------------------------------------
    if np.isfinite(values["GUNW_023_HH"]) and np.isfinite(values["GUNW_029_HH"]):
        row["HH_023_to_029_change"] = (
            values["GUNW_029_HH"] -
            values["GUNW_023_HH"]
        )
    else:
        row["HH_023_to_029_change"] = np.nan

    # -----------------------------------------------------
    # VV temporal change
    # -----------------------------------------------------
    if np.isfinite(values["GUNW_025_VV"]) and np.isfinite(values["GUNW_026_VV"]):
        row["VV_025_to_026_change"] = (
            values["GUNW_026_VV"] -
            values["GUNW_025_VV"]
        )
    else:
        row["VV_025_to_026_change"] = np.nan

    output.append(row)

# ---------------------------------------------------------
# Write result
# ---------------------------------------------------------
fieldnames = list(output[0].keys())

outfile = "step2_region_temporal_fingerprint.csv"

with open(outfile, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)

print("DONE")
print("Output:", outfile)
print("Regions:", len(output))
