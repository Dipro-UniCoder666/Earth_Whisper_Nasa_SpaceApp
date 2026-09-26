import numpy as np
import pandas as pd
from pathlib import Path


ROOT = Path(
    "/mnt/d/Earth_Whisper_Nasa/Earth_Whisper/data/step6_feature_engine"
)

SRC = ROOT / "ml_input_s1_baseline_scaled.csv"
OUT = ROOT / "step7d_knn_anomaly_results.csv"


FEATURES = [
    "s1_median_db_z",
    "s1_min_db_z",
    "s1_max_db_z",
    "s1_pct_le_minus3db_z",
]

K_VALUES = [5, 10, 20]


df = pd.read_csv(SRC)

X = df[FEATURES].to_numpy(dtype=float)

if X.shape != (211, 4):
    raise ValueError(
        f"Expected feature matrix shape (211, 4), got {X.shape}"
    )

if not np.isfinite(X).all():
    raise ValueError("Feature matrix contains non-finite values.")


# ------------------------------------------------------------
# Pairwise Euclidean distances
# ------------------------------------------------------------

# Squared-distance identity:
# ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x.y

squared_norms = np.sum(X * X, axis=1, keepdims=True)

D2 = (
    squared_norms
    + squared_norms.T
    - 2.0 * (X @ X.T)
)

# Numerical round-off can produce tiny negative values.
D2 = np.maximum(D2, 0.0)

D = np.sqrt(D2)

# Exclude self-distance.
np.fill_diagonal(D, np.inf)


# ------------------------------------------------------------
# kNN anomaly scores
# ------------------------------------------------------------

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


for k in K_VALUES:

    if k >= len(df):
        raise ValueError(f"k={k} is too large for {len(df)} records.")

    nearest = np.partition(D, kth=k - 1, axis=1)[:, :k]

    # Mean distance to k nearest neighbours.
    score = nearest.mean(axis=1)

    result[f"knn_k{k}_mean_distance"] = score


# ------------------------------------------------------------
# Combined stability indicator
# ------------------------------------------------------------

score_cols = [
    f"knn_k{k}_mean_distance"
    for k in K_VALUES
]

# Rank percentile, not probability.
for c in score_cols:
    result[c + "_percentile"] = (
        result[c].rank(method="average", pct=True)
    )


# Mean of the three percentile positions.
result["knn_stability_percentile"] = result[
    [c + "_percentile" for c in score_cols]
].mean(axis=1)


# Spread across k settings.
result["knn_k_score_std"] = result[score_cols].std(
    axis=1,
    ddof=0,
)


# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

print("=" * 90)
print("STEP 7D — kNN ANOMALY DETECTION")
print("=" * 90)

print("\nInput shape:", X.shape)
print("k values:", K_VALUES)

for k in K_VALUES:
    c = f"knn_k{k}_mean_distance"
    print(f"\n{k}-NN mean-distance statistics:")
    print(result[c].describe().round(6).to_string())

print("\nStability percentile statistics:")
print(
    result["knn_stability_percentile"]
    .describe()
    .round(6)
    .to_string()
)

# Show only the most isolated candidates for inspection.
top = result.nlargest(
    15,
    "knn_stability_percentile"
)

print("\nTop 15 highest kNN anomaly-percentile candidates:")
print(
    top[
        [
            "candidate_key",
            "comparison",
            "region_id",
            "area_m2",
            "knn_k5_mean_distance",
            "knn_k10_mean_distance",
            "knn_k20_mean_distance",
            "knn_stability_percentile",
            "knn_k_score_std",
        ]
    ]
    .to_string(index=False)
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

result.to_csv(OUT, index=False)

print("\nOutput:")
print(OUT)

print("\nInterpretation note:")
print(
    "Higher kNN distance means greater statistical isolation in the "
    "selected Sentinel-1 feature space. This is an anomaly indicator, "
    "not an event probability or physical-change confirmation."
)
