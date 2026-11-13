"""Re-evaluate a trained water segmentation checkpoint with PR-AUC and AP."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import auc, average_precision_score, precision_recall_curve
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend/.venv/Lib/site-packages"))
sys.path.insert(0, str(ROOT / "scripts/gherproof"))
import train_sen1floods11 as train


@torch.inference_mode()
def evaluate(model, rows, stats, device):
    ds = train.ChipDataset(rows, stats, patch=None, cache=False)
    loader = DataLoader(ds, batch_size=1, shuffle=False, num_workers=0)
    tn = fp = fn = tp = 0
    truth, score = [], []
    model.eval()
    for x, y, valid in loader:
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device.type == "cuda"):
            logits = model(x)
        p = torch.sigmoid(logits).float().cpu().numpy()[:, 0]
        yv = y.cpu().numpy()[:, 0].astype(np.uint8)
        mask = valid.cpu().numpy()[:, 0] > 0
        pred = p >= 0.5
        tn += int(((~pred) & (yv == 0) & mask).sum())
        fp += int((pred & (yv == 0) & mask).sum())
        fn += int(((~pred) & (yv == 1) & mask).sum())
        tp += int((pred & (yv == 1) & mask).sum())
        truth.append(yv[mask]); score.append(p[mask])
    ytrue = np.concatenate(truth); yscore = np.concatenate(score)
    precision_curve, recall_curve, _ = precision_recall_curve(ytrue, yscore)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "threshold": 0.5,
        "iou": tp / max(tp + fp + fn, 1), "precision": precision, "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "pr_auc_trapezoidal": float(auc(recall_curve[::-1], precision_curve[::-1])),
        "average_precision": float(average_precision_score(ytrue, yscore)),
        "confusion_matrix_rows_true_0_1_cols_pred_0_1": [[tn, fp], [fn, tp]],
        "valid_pixels": int(ytrue.size), "water_prevalence": float(ytrue.mean()),
        "chip_count": len(rows),
    }


def main():
    model_path = ROOT / "models/gherproof/sen1floods11_attention_unet.pt"
    if not model_path.is_file():
        raise FileNotFoundError("A completed training checkpoint is required before independent evaluation")
    ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
    model = train.AttentionUNet(base=int(ckpt.get("base_channels", 16)))
    model.load_state_dict(ckpt["state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    stats = (np.asarray(ckpt["normalization_mean"], dtype=np.float32),
             np.asarray(ckpt["normalization_std"], dtype=np.float32))
    rows_train = train._read_split("flood_train_data.csv")
    rows_bolivia = train._read_split("flood_bolivia_data.csv")
    geoms = train._event_geometries()
    groups = {}
    for row in rows_train + rows_bolivia:
        groups[row["s1"]] = train._event_for_chip(row["s1"], geoms)[0]
    counts = Counter(groups[r["s1"]] for r in rows_train)
    val_event = ckpt["validation_event_id"]
    train_val = [r for r in rows_train if groups[r["s1"]] == val_event]
    test = rows_bolivia
    val = evaluate(model, train_val, stats, device)
    bolivia = evaluate(model, test, stats, device)
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint": str(model_path.relative_to(ROOT)).replace("\\", "/"),
        "checkpoint_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "validation_event_id": val_event,
        "event_group_counts_official_train": dict(counts),
        "validation_event": val,
        "independent_bolivia_event_test": bolivia,
        "interpretation": "Metrics describe Sen1Floods11 water/non-water benchmark labels only. Bolivia is geographically/event held out; neither result estimates Sujatpur accuracy or waterlogging performance.",
        "threshold_selection": "fixed 0.5; not tuned on Bolivia",
    }
    path = ROOT / "data/gherproof/manifests/sen1floods11_independent_evaluation.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path.relative_to(ROOT)), "validation_iou": val["iou"],
                      "validation_pr_auc": val["pr_auc_trapezoidal"], "bolivia_iou": bolivia["iou"],
                      "bolivia_pr_auc": bolivia["pr_auc_trapezoidal"]}, indent=2))


if __name__ == "__main__":
    main()
