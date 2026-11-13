"""Pure, testable functions for conservative Sentinel-2 weak references."""
from __future__ import annotations

import numpy as np


LABELS = {0: "invalid", 1: "weak_water", 2: "weak_nonwater", 3: "uncertain"}
CHANGE_LABELS = {
    0: "invalid", 1: "persistent_water_candidate", 2: "possible_new_water_candidate",
    3: "possible_water_loss_candidate", 4: "stable_nonwater_candidate", 5: "uncertain_change",
}


def reflectance_from_dn(dn, offset: float, quantification: float, nodata=0):
    """Apply Sentinel-2 L2A metadata scaling once; invalid source DN stays invalid."""
    values = np.asarray(dn)
    valid = np.isfinite(values) & (values != nodata) & (quantification > 0)
    result = np.full(values.shape, np.nan, dtype=np.float32)
    result[valid] = (values[valid].astype(np.float32) + offset) / quantification
    return result, valid


def normalized_difference(a, b, valid=None, min_denominator=0.02):
    """Numerically guarded normalized difference; returns index and validity."""
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    denom = a + b
    mask = np.isfinite(a) & np.isfinite(b) & (a >= 0) & (b >= 0) & np.isfinite(denom) & (denom >= min_denominator)
    if valid is not None:
        mask &= np.asarray(valid, dtype=bool)
    out = np.full(a.shape, np.nan, dtype=np.float32)
    out[mask] = (a[mask] - b[mask]) / denom[mask]
    return out, mask


def classify_weak_reference(scl, ndwi, mndwi, spectral_valid, ndwi_threshold=0.0, mndwi_threshold=0.0):
    """Codes: 0 invalid, 1 weak water, 2 weak nonwater, 3 uncertain."""
    scl = np.asarray(scl)
    ndwi = np.asarray(ndwi, dtype=np.float32)
    mndwi = np.asarray(mndwi, dtype=np.float32)
    spec = np.asarray(spectral_valid, dtype=bool) & np.isfinite(ndwi) & np.isfinite(mndwi)
    out = np.zeros(scl.shape, dtype=np.uint8)
    clear_context = spec & np.isin(scl, [2, 4, 5, 6, 7])
    out[clear_context] = 3
    water = spec & (scl == 6) & (ndwi >= ndwi_threshold) & (mndwi >= mndwi_threshold)
    nonwater = spec & np.isin(scl, [4, 5]) & (ndwi < ndwi_threshold) & (mndwi < mndwi_threshold)
    out[water] = 1
    out[nonwater] = 2
    return out


def classify_change(pre, post, pre_valid=None, post_valid=None):
    """Codes: 0 invalid, 1 persistent water, 2 possible new, 3 possible loss, 4 stable nonwater, 5 uncertain."""
    pre, post = np.asarray(pre), np.asarray(post)
    if pre.shape != post.shape:
        raise ValueError("pre/post weak-reference grids must match")
    pv = (pre != 0) if pre_valid is None else np.asarray(pre_valid, bool)
    qv = (post != 0) if post_valid is None else np.asarray(post_valid, bool)
    joint = pv & qv
    out = np.zeros(pre.shape, dtype=np.uint8)
    out[joint] = 5
    out[joint & (pre == 1) & (post == 1)] = 1
    out[joint & (pre == 2) & (post == 1)] = 2
    out[joint & (pre == 1) & (post == 2)] = 3
    out[joint & (pre == 2) & (post == 2)] = 4
    return out


def comparison_metrics(reference, prediction, valid):
    """Weak-reference confusion counts; no local-accuracy semantics implied."""
    ref = np.asarray(reference)
    pred = np.asarray(prediction, dtype=bool)
    mask = np.asarray(valid, dtype=bool) & np.isin(ref, [1, 2])
    water = ref == 1
    nonwater = ref == 2
    tp = int(np.count_nonzero(mask & water & pred))
    fn = int(np.count_nonzero(mask & water & ~pred))
    tn = int(np.count_nonzero(mask & nonwater & ~pred))
    fp = int(np.count_nonzero(mask & nonwater & pred))
    n = tp + fn + tn + fp
    return {
        "common_valid_comparison_pixels": n,
        "weak_water_pixels": tp + fn,
        "weak_nonwater_pixels": tn + fp,
        "uncertain_reference_pixels_excluded": int(np.count_nonzero(np.asarray(valid, bool) & (ref == 3))),
        "invalid_or_no_common_data_pixels": int(ref.size - np.count_nonzero(valid)),
        "agreement_pixels": tp + tn,
        "weak_reference_agreement": (tp + tn) / n if n else None,
        "weak_reference_positive_agreement": tp / (tp + fn) if tp + fn else None,
        "weak_reference_negative_agreement": tn / (tn + fp) if tn + fp else None,
        "confusion_matrix": {"weak_water_predicted_water": tp, "weak_water_predicted_nonwater": fn,
                             "weak_nonwater_predicted_nonwater": tn, "weak_nonwater_predicted_water": fp},
    }


def spatial_block_summaries(reference, prediction, valid, rows, cols, block_pixels=250):
    """Coarse 5 km block variability; does not treat adjacent pixels as independent samples."""
    ref, pred, mask = np.asarray(reference), np.asarray(prediction, bool), np.asarray(valid, bool)
    result = []
    for row0 in range(0, ref.shape[0], block_pixels):
        for col0 in range(0, ref.shape[1], block_pixels):
            sl = np.s_[row0:min(row0 + block_pixels, ref.shape[0]), col0:min(col0 + block_pixels, ref.shape[1])]
            local = mask[sl] & np.isin(ref[sl], [1, 2])
            n = int(local.sum())
            if not n:
                continue
            water = ref[sl] == 1
            nonwater = ref[sl] == 2
            agree = int(np.count_nonzero(local & (((water & pred[sl]) | (nonwater & ~pred[sl])))))
            result.append({"block_row": row0 // block_pixels, "block_col": col0 // block_pixels,
                           "bounds_pixel_window": [col0, row0, min(col0 + block_pixels, ref.shape[1]), min(row0 + block_pixels, ref.shape[0])],
                           "common_valid_pixels": n, "weak_water_pixels": int(np.count_nonzero(local & water)),
                           "weak_nonwater_pixels": int(np.count_nonzero(local & nonwater)),
                           "weak_reference_agreement": agree / n})
    vals = [x["weak_reference_agreement"] for x in result]
    summary = {"block_size_pixels": block_pixels, "block_size_m": block_pixels * 20,
               "block_count_with_valid_labels": len(vals),
               "agreement_median_across_blocks": float(np.median(vals)) if vals else None,
               "agreement_p10_across_blocks": float(np.percentile(vals, 10)) if vals else None,
               "agreement_p90_across_blocks": float(np.percentile(vals, 90)) if vals else None,
               "uncertainty_note": "Descriptive spatial-block variation only; not a pixel-independent confidence interval."}
    return summary, result
