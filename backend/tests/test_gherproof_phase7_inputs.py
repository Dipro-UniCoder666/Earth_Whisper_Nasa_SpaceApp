import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/gherproof/phase7"))
from model_inputs import linear_gamma0_to_db, normalize_db, tile_starts


def test_gamma0_to_db_masks_bad_values_and_converts_once():
    x = np.array([[[1.0, 10.0, 0.0, -1.0, np.nan, np.inf]],
                  [[0.1, 1.0, 1.0, 1.0, 1.0, 1.0]]], dtype=np.float32)
    db, band_valid, common = linear_gamma0_to_db(
        x, band_names=("VV", "VH"), representation="linear_gamma0")
    assert db[0, 0, :2].tolist() == pytest.approx([0.0, 10.0])
    assert band_valid[0, 0].tolist() == [True, True, False, False, False, False]
    assert common.tolist() == [[True, True, False, False, False, False]]
    with pytest.raises(ValueError):
        linear_gamma0_to_db(db, band_names=("VV", "VH"), representation="db")


@pytest.mark.parametrize("bands", [("VH", "VV"), ("VV",), ("VV", "VH", "HH")])
def test_wrong_order_or_channel_count_rejected(bands):
    with pytest.raises(ValueError):
        linear_gamma0_to_db(np.ones((2, 3, 4)), band_names=bands,
                            representation="linear_gamma0")


def test_normalization_clips_and_zeros_invalid_pixels():
    db = np.array([[[-70.0, 0.0], [-10.0, 25.0]],
                   [[-18.0, -18.0], [-18.0, -18.0]]], dtype=np.float32)
    valid = np.array([[True, False], [True, True]])
    y, mask = normalize_db(db, valid, [-10.0, -18.0], [5.0, 2.0],
                           band_names=("VV", "VH"))
    assert mask.tolist() == valid.tolist()
    assert y[:, 0, 0].tolist() == pytest.approx([-10.0, 0.0])
    assert np.all(y[:, 0, 1] == 0)
    assert y[0, 1, 1] == pytest.approx(6.0)
    assert np.isfinite(y).all()


def test_normalization_rejects_bad_dimensions_stats_and_valid_nonfinite():
    with pytest.raises(ValueError):
        normalize_db(np.ones((2, 3, 4)), np.ones((3, 3), bool), [0, 0], [1, 1], band_names=("VV", "VH"))
    with pytest.raises(ValueError):
        normalize_db(np.ones((2, 3, 4)), np.ones((3, 4), bool), [0, 0], [1, 0], band_names=("VV", "VH"))
    a = np.ones((2, 3, 4)); a[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        normalize_db(a, np.ones((3, 4), bool), [0, 0], [1, 1], band_names=("VV", "VH"))


@pytest.mark.parametrize("length,patch,overlap", [(1, 256, 64), (256, 256, 64), (513, 256, 64), (1024, 256, 0)])
def test_tiles_cover_all_pixels(length, patch, overlap):
    starts = tile_starts(length, patch, overlap)
    covered = np.zeros(length, bool)
    for s in starts:
        covered[s:min(length, s + patch)] = True
    assert covered.all()


@pytest.mark.parametrize("args", [(0, 256, 64), (10, 0, 0), (10, 5, 5), (10, 5, -1)])
def test_invalid_tile_geometry_rejected(args):
    with pytest.raises(ValueError):
        tile_starts(*args)
