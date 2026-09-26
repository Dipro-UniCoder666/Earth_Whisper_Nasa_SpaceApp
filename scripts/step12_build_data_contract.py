#!/usr/bin/env python3
"""Step 12B - build the backend data contract from the verified Step 8/10 outputs.

This script is a deterministic DERIVATION step. It joins existing verified CSV
outputs by candidate_key and reorganises them into one JSON contract for the
read-only backend API. It does not recompute, rescale or round any scientific
measurement, does not create scores or probabilities, and does not label any
physical event.

Identity rule: candidate_key = comparison + "_" + region_id. region_id alone is
never used as a unique identifier.
"""

import csv
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO_ROOT, "data")
STEP6 = os.path.join(DATA, "step6_feature_engine")
STEP10 = os.path.join(DATA, "step10_ai_investigator")
OUT_DIR = os.path.join(DATA, "step12_backend")
OUT_PATH = os.path.join(OUT_DIR, "earth_whisper_candidates.json")

AOI = {
    "name": "Sandhya River near Babuganj, Barishal, Bangladesh",
    "wkt": "POLYGON((90.15 22.47,90.22 22.47,90.22 22.51,90.15 22.51,90.15 22.47))",
}
INVESTIGATION_PERIOD = "June–September 2026"

SOURCES = {
    "step10": "data/step10_ai_investigator/step10_candidate_investigations.csv",
    "step10_manifest": "data/step10_ai_investigator/step10_investigator_manifest.json",
    "step8c": "data/step6_feature_engine/step8c_evidence_matrix.csv",
    "step8e": "data/step6_feature_engine/step8e_uncertainty_annotations.csv",
    "step8f": "data/step6_feature_engine/step8f_cross_radar_consistency.csv",
}

DASHBOARD_SUMMARY = {
    "exact_aoi_valid_pixels": 79874,
    "nisar_comparisons": [
        {
            "comparison": "HH_023_to_029",
            "observation_pairs": ["20 Jun 2026 → 02 Jul 2026", "31 Aug 2026 → 12 Sep 2026"],
            "polarization": "HH",
            "mean_change": -0.013475091,
            "median_change": -0.011641301,
        },
        {
            "comparison": "VV_025_to_026",
            "observation_pairs": ["14 Jul 2026 → 31 Aug 2026", "26 Jul 2026 → 19 Aug 2026"],
            "polarization": "VV",
            "mean_change": 0.025675088,
            "median_change": 0.023278385,
        },
    ],
    "sentinel1_threshold_counts": {
        "median_delta_db_le_minus_2": 27,
        "median_delta_db_le_minus_3": 14,
        "median_delta_db_le_minus_5": 6,
    },
    "dual_radar_stable_patterns": 11,
    "stability_bands": {
        "low_k_sensitivity": 171,
        "moderate_k_sensitivity": 28,
        "high_k_sensitivity": 12,
    },
    "optical_tested_regions": 6,
    "optical_inconclusive_regions": 6,
    "optical_not_tested_regions": 205,
    "rainfall_context": {
        "event_day_mm": 5.835263,
        "three_day_mm": 13.056936,
        "seven_day_mm": 32.511207,
        "fourteen_day_mm": 131.931329,
        "maximum_daily_mm": 42.598942,
        "wet_days_gt_5mm": 9,
    },
}

MISSING = ("", "nan", "none", "null", "na", "n/a")


def load_csv(rel_path):
    full = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
    if not os.path.exists(full):
        raise SystemExit("ERROR: required source file is missing: " + rel_path)
    with open(full, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def is_missing(value):
    return value is None or str(value).strip().lower() in MISSING


def num(value):
    """Parse a source value to a number, preserving null for unavailable data."""
    if is_missing(value):
        return None
    text = str(value).strip()
    try:
        as_float = float(text)
    except ValueError:
        return None
    if as_float.is_integer() and "." not in text and "e" not in text.lower():
        return int(as_float)
    return as_float


def text(value):
    return None if is_missing(value) else str(value).strip()


def source_record(row):
    """Keep the verified source row available without changing its values."""
    return {key: text(value) for key, value in row.items()}


def main():
    step8c = {r["candidate_key"]: r for r in load_csv(SOURCES["step8c"])}
    step8e = {r["candidate_key"]: r for r in load_csv(SOURCES["step8e"])}
    step8f = {r["candidate_key"]: r for r in load_csv(SOURCES["step8f"])}
    step10_rows = load_csv(SOURCES["step10"])
    step10 = {r["candidate_key"]: r for r in step10_rows}

    keys = sorted(step8f.keys())
    if not keys:
        raise SystemExit("ERROR: no candidate records found in step8f")

    missing_joins = [k for k in keys if k not in step8c or k not in step8e]
    if missing_joins:
        raise SystemExit("ERROR: candidates missing from step8c/step8e join: "
                         + ", ".join(missing_joins[:10]))
    orphan_step10 = [k for k in step10 if k not in step8f]
    if orphan_step10:
        raise SystemExit("ERROR: Step 10 candidates not present in step8f: "
                         + ", ".join(orphan_step10[:10]))

    def sort_key(key):
        comparison, _, region = key.rpartition("_")
        try:
            return (comparison, int(region))
        except ValueError:
            return (comparison, 0)

    candidates = []
    for key in sorted(keys, key=sort_key):
        c, e, f = step8c[key], step8e[key], step8f[key]
        s10 = step10.get(key)
        comparison = f["comparison"]
        region_id = int(float(f["region_id"]))

        if key != comparison + "_" + str(region_id):
            raise SystemExit("ERROR: identity rule violated for key: " + key)

        record = {
            "candidate_key": key,
            "comparison": comparison,
            "region_id": region_id,
            "lon": num(f["lon"]),
            "lat": num(f["lat"]),
            "area_m2": num(f["area_m2"]),
            "investigated": s10 is not None,
            "nisar_change": num(f["nisar_change"]),
            "nisar_change_strength": num(f["nisar_change_strength"]),
            "nisar_signal_percentile": num(f["nisar_signal_percentile"]),
            "nisar_signal_band": text(f["nisar_signal_band"]),
            "s1_median_db": num(c["s1_median_db"]),
            "s1_min_db": num(c["s1_min_db"]),
            "s1_max_db": num(c["s1_max_db"]),
            "s1_pct_le_minus3db": num(c["s1_pct_le_minus3db"]),
            "s1_anomaly_percentile": num(f["s1_anomaly_percentile"]),
            "s1_anomaly_stability": text(f["s1_anomaly_stability"]),
            "cross_radar_status": text(f["cross_radar_status"]),
            "optical_status": text(f["optical_status_for_fusion"]),
            "rainfall_context_status": text(e["rainfall_context_status"]),
            "comparison_population_size": num(f.get("comparison_population_size") or e["comparison_population_size"]),
            "anomaly_stability_band": text(e["anomaly_stability_band"]),
            "evidence_limitation": text(e["evidence_limitation"]),
            "observation_summary": text(s10["observation_summary"]) if s10 else None,
            "inference_summary": text(s10["inference_summary"]) if s10 else None,
            "limitation_summary": text(s10["limitation_summary"]) if s10 else None,
            "nisar": {
                "nisar_change": num(f["nisar_change"]),
                "nisar_change_strength": num(f["nisar_change_strength"]),
                "nisar_signal_percentile": num(f["nisar_signal_percentile"]),
                "nisar_signal_band": text(f["nisar_signal_band"]),
            },
            "sentinel1": {
                "s1_median_db": num(c["s1_median_db"]),
                "s1_min_db": num(c["s1_min_db"]),
                "s1_max_db": num(c["s1_max_db"]),
                "s1_pct_le_minus3db": num(c["s1_pct_le_minus3db"]),
                "s1_anomaly_percentile": num(f["s1_anomaly_percentile"]),
                "s1_anomaly_stability": text(f["s1_anomaly_stability"]),
                "comparison_aware_anomaly_percentile": num(e["comparison_aware_anomaly_percentile"]),
                "comparison_aware_k_score_std": num(e["comparison_aware_k_score_std"]),
            },
            "cross_radar": {
                "cross_radar_status": text(f["cross_radar_status"]),
                "nisar_signal_band": text(f["nisar_signal_band"]),
                "s1_anomaly_band": text(f["s1_anomaly_band"]),
            },
            "optical": {
                "optical_status": text(f["optical_status_for_fusion"]),
                "optical_tested": text(c["optical_tested"]),
                "optical_observation_count": num(c["optical_observation_count"]),
                "optical_valid_observation_count": num(c["optical_valid_observation_count"]),
                "optical_max_valid_pixels": num(c["optical_max_valid_pixels"]),
                "optical_max_high_aerosol_fraction": num(c["optical_max_high_aerosol_fraction"]),
            },
            "environmental": {
                "rainfall_context_status": text(e["rainfall_context_status"]),
                "rainfall_role": "environmental_context_only",
                "gunw_023_rainfall_14day_mm": num(c.get("gunw_023_rainfall_14day_mm")),
                "gunw_025_rainfall_14day_mm": num(c.get("gunw_025_rainfall_14day_mm")),
                "gunw_026_rainfall_14day_mm": num(c.get("gunw_026_rainfall_14day_mm")),
                "gunw_029_rainfall_14day_mm": num(c.get("gunw_029_rainfall_14day_mm")),
            },
            "uncertainty": {
                "comparison_population_size": num(f.get("comparison_population_size") or e["comparison_population_size"]),
                "anomaly_stability_band": text(e["anomaly_stability_band"]),
                "evidence_limitation": text(e["evidence_limitation"]),
            },
            "observations": {
                "observation_summary": text(s10["observation_summary"]) if s10 else None,
                "inference_summary": text(s10["inference_summary"]) if s10 else None,
                "limitation_summary": text(s10["limitation_summary"]) if s10 else None,
            },
            "provenance": {
                "identity": SOURCES["step8f"],
                "geometry": SOURCES["step8f"],
                "nisar": SOURCES["step8f"],
                "sentinel1_measurements": SOURCES["step8c"],
                "comparison_aware_anomaly": SOURCES["step8e"],
                "cross_radar": SOURCES["step8f"],
                "optical": SOURCES["step8c"],
                "environmental": SOURCES["step8c"],
                "uncertainty": SOURCES["step8e"],
                "step10_text": SOURCES["step10"] if s10 else None,
                "note": ("values are copied verbatim from the listed verified outputs; "
                         "missing values are preserved as null and never replaced with zero"),
            },
            "source_records": {
                "step8c_evidence_matrix": source_record(c),
                "step8e_uncertainty_annotations": source_record(e),
                "step8f_cross_radar_consistency": source_record(f),
                "step10_candidate_investigations": source_record(s10) if s10 else None,
            },
        }
        candidates.append(record)

    populations = {}
    for record in candidates:
        populations[record["comparison"]] = populations.get(record["comparison"], 0) + 1

    contract = {
        "project": "Earth Whisper",
        "aoi": AOI,
        "investigation_period": INVESTIGATION_PERIOD,
        "candidate_count": len(candidates),
        "investigated_candidate_count": sum(1 for r in candidates if r["investigated"]),
        "comparison_populations": populations,
        "dashboard_summary": DASHBOARD_SUMMARY,
        "source_files": SOURCES,
        "identity_rule": "candidate_key = comparison + '_' + region_id",
        "candidates": candidates,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(contract, fh, indent=2, sort_keys=False)
        fh.write("\n")

    print("wrote " + os.path.relpath(OUT_PATH, REPO_ROOT))
    print("candidates: " + str(len(candidates)))
    print("investigated: " + str(contract["investigated_candidate_count"]))
    print("comparison populations: " + json.dumps(populations, sort_keys=True))
    unique_regions = len(set(r["region_id"] for r in candidates))
    print("unique region ids: " + str(unique_regions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
