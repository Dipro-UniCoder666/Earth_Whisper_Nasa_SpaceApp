import numpy as np
import pandas as pd
from pathlib import Path


ROOT = Path(
    "/mnt/d/Earth_Whisper_Nasa/Earth_Whisper/data/step6_feature_engine"
)

SRC = ROOT / "ml_input_s1_baseline_scaled.csv"
OUT = ROOT / "step8b_comparison_aware_knn.csv"

FEATURES = [
    "s1_median_db_z",
    "s1_min_db_z",
    "s1_max_db_z",
    "s1_pct_le_minus3db_z",
]

K_VALUES = [3, 5, 8]


def knn_scores(X, k):
    n = len(X)

    if k >= n:
        raise ValueError(
            f"k={k} is invalid for group size {n}; must be smaller than group size."
        )

    norms = np.sum(X * X, axis=1, keepdims=True)

    d2 = norms + norms.T - 2.0 * (X @ X.T)
    d2 = np.maximum(d2, 0.0)

    d = np.sqrt(d2)

    np.fill_diagonal(d, np.inf)

    nearest = np.partition(d, kth=k - 1, axis=1)[:, :k]

    return nearest.mean(axis=1)


df = pd.read_csv(SRC)

if len(df) != 211:
    raise ValueError(f"Expected 211 records, found {len(df)}")

result = df[
    [
        "candidate_key",
        "comparison",
        "region_id",
        "lon",
        "lat",
        "area_m2",
    ]
].copy()

# ------------------------------------------------------------
# Run independently within each comparison type.
# ------------------------------------------------------------

for comparison, idx in df.groupby("comparison").groups.items():

    group = df.loc[idx].copy()
    X = group[FEATURES].to_numpy(dtype=float)

    if not np.isfinite(X).all():
        raise ValueError(
            f"Non-finite ML values in comparison {comparison}"
        )

    print(
        f"Processing {comparison}: {len(group)} candidates"
    )

    for k in K_VALUES:

        score = knn_scores(X, k)

        score_series = pd.Series(
            score,
            index=group.index,
        )

        raw_col = f"cmp_knn_k{k}_mean_distance"

        result.loc[group.index, raw_col] = score_series

        # Percentile is calculated only against the same
        # comparison population.
        percentile = score_series.rank(
            method="average",
            pct=True,
        )

        result.loc[
            group.index,
            f"cmp_knn_k{k}_percentile"
        ] = percentile


# ------------------------------------------------------------
# Stability across k values
# ------------------------------------------------------------

percentile_cols = [
    f"cmp_knn_k{k}_percentile"
    for k in K_VALUES
]

distance_cols = [
    f"cmp_knn_k{k}_mean_distance"
    for k in K_VALUES
]

result["comparison_aware_anomaly_percentile"] = (
    result[percentile_cols].mean(axis=1)
)

result["comparison_aware_k_score_std"] = (
    result[distance_cols].std(axis=1, ddof=0)
)


# ------------------------------------------------------------
# QA
# ------------------------------------------------------------

print("\n" + "=" * 90)
print("STEP 8B — COMPARISON-AWARE kNN")
print("=" * 90)

print("\nRecord counts:")
print(
    result["comparison"].value_counts().to_string()
)

print("\nAnomaly percentile summary by comparison:")
print(
    result.groupby("comparison")[
        [
            "comparison_aware_anomaly_percentile",
            "comparison_aware_k_score_std",
        ]
    ]
    .describe()
    .round(4)
    .to_string()
)

for comparison in result["comparison"].unique():

    g = result[result["comparison"] == comparison]

    print(
        f"\nTop candidates within {comparison}:"
    )

    print(
        g.nlargest(
            min(10, len(g)),
            "comparison_aware_anomaly_percentile",
        )[
            [
                "candidate_key",
                "region_id",
                "area_m2",
                "cmp_knn_k3_percentile",
                "cmp_knn_k5_percentile",
                "cmp_knn_k8_percentile",
                "comparison_aware_anomaly_percentile",
                "comparison_aware_k_score_std",
            ]
        ]
        .to_string(index=False)
    )


if result["candidate_key"].duplicated().any():
    raise ValueError("Duplicate candidate keys detected.")

if result[
    [
        "comparison_aware_anomaly_percentile",
        "comparison_aware_k_score_std",
    ]
].isna().any().any():
    raise ValueError(
        "Missing comparison-aware anomaly results detected."
    )


result.to_csv(OUT, index=False)

print("\nOutput:")
print(OUT)

print(
    "\nInterpretation: anomaly percentiles are calculated "
    "relative to candidates from the same NISAR comparison type."
)
print(
    "These remain statistical anomaly indicators, not event "
    "probabilities or physical-change confirmations."
)
