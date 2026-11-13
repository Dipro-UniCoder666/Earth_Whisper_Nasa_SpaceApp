"""Independent raster and event/split quality audit for the downloaded subset."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend/.venv/Lib/site-packages"))
sys.path.insert(0, str(ROOT / "scripts/gherproof"))
import train_sen1floods11 as train


def main() -> None:
    split_names = {"train": "flood_train_data.csv", "valid": "flood_valid_data.csv",
                   "test": "flood_test_data.csv", "bolivia": "flood_bolivia_data.csv"}
    event_geoms = train._event_geometries()
    records = []
    split_event_counts: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    fractions = []
    global_values: list[list[float]] = [[], []]
    for split, filename in split_names.items():
        for row in train._read_split(filename):
            event_id, overlap = train._event_for_chip(row["s1"], event_geoms)
            image, labels, valid, profile = train._inspect_chip(row)
            yvals, ycounts = np.unique(labels, return_counts=True)
            label_hist = {str(int(y)): int(n) for y, n in zip(yvals, ycounts)}
            per_band = []
            for band in range(2):
                vals = image[band][valid]
                quantiles = ([float(v) for v in np.percentile(vals, [1, 50, 99])] if vals.size else None)
                per_band.append(quantiles)
                if vals.size:
                    global_values[band].extend(np.percentile(vals, [1, 50, 99]).astype(float).tolist())
            valid_fraction = float(valid.mean())
            fractions.append(valid_fraction)
            split_event_counts[split][event_id] += 1
            totals["chips"] += 1
            totals[f"{split}_chips"] += 1
            totals["empty_valid_chips"] += int(not valid.any())
            totals["valid_pixels"] += int(valid.sum())
            totals["water_pixels"] += int(((labels == 1) & valid).sum())
            totals["non_water_pixels"] += int(((labels == 0) & valid).sum())
            totals["label_nodata_pixels"] += int((labels == 255).sum())
            records.append({"s1_file": row["s1"], "label_file": row["label"], "official_split": split,
                            "event_id": event_id, "event_polygon_overlap_fraction": overlap,
                            "crs": profile["crs"], "dimensions": [512, 512], "resolution": profile["res"],
                            "nodata": profile["nodata"], "label_values": label_hist,
                            "valid_pixel_fraction": valid_fraction, "valid_pixels": int(valid.sum()),
                            "s1_db_quantiles_p01_median_p99_vv_vh": per_band})
    overlap_sets = {}
    for left in ["train", "valid", "test", "bolivia"]:
        for right in ["train", "valid", "test", "bolivia"]:
            if left < right:
                overlap_sets[f"{left}__{right}"] = sorted(set(split_event_counts[left]) & set(split_event_counts[right]))
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "Sen1Floods11 v1.1 hand-labeled S1Hand/LabelHand",
        "source_raster_contract": "2 bands VV/VH in dB (per official README); labels -1 no-data, 0 non-water, 1 water",
        "checks": {"paired_chip_count": totals["chips"], "all_512x512": all(r["dimensions"] == [512, 512] for r in records),
                   "crs_values": sorted({r["crs"] for r in records}),
                   "resolution_values": sorted({tuple(round(x, 12) for x in r["resolution"]) for r in records}),
                   "event_polygon_assignment_min_overlap": min(r["event_polygon_overlap_fraction"] for r in records),
                   "mask_codes_observed": sorted({k for r in records for k in r["label_values"]})},
        "totals": dict(totals),
        "valid_fraction_summary": {"mean": float(np.mean(fractions)), "median": float(np.median(fractions)),
                                   "min": float(np.min(fractions)), "max": float(np.max(fractions))},
        "event_chip_counts_by_official_split": {s: dict(c) for s, c in split_event_counts.items()},
        "event_overlap_across_official_splits": overlap_sets,
        "per_chip": records,
        "limitations": ["Official train/valid/test files contain the same event polygons; their chip partitions are not event-independent.",
                        "The separate Bolivia list is a distinct geographic/event holdout, but contains only 15 chips.",
                        "Labels identify water/non-water, not flood-vs-permanent-water or local waterlogging.",
                        "Sen1Floods11 has no clear permissive dataset license in official metadata; no redistribution."],
    }
    path = ROOT / "data/gherproof/manifests/sen1floods11_qc_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path.relative_to(ROOT)), "chips": totals["chips"],
                      "mean_valid_fraction": report["valid_fraction_summary"]["mean"],
                      "empty_valid_chips": totals["empty_valid_chips"],
                      "event_overlap": overlap_sets}, indent=2))


if __name__ == "__main__":
    main()
