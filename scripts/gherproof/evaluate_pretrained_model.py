"""Fair event-group comparison for scratch vs fine-tuned SAR segmentation.

The self-supervised encoder alone is explicitly recorded as not supporting
direct water inference because it has no segmentation head or water labels.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "backend/.venv/Lib/site-packages"), str(ROOT / "scripts/gherproof")])
import numpy as np
import torch
from sklearn.metrics import auc, average_precision_score, precision_recall_curve
from torch.utils.data import DataLoader
import train_sen1floods11 as baseline
from resnet50_sar_unet import ResNet50SARUNet

SCRATCH = ROOT / "models/gherproof/sen1floods11_attention_unet.pt"
FINE_TUNED = ROOT / "models/gherproof/sen1floods11_resnet50_moco_unet.pt"
PRETRAINED_MEAN = np.array([-12.54847273, -20.19237134], dtype=np.float32)
PRETRAINED_STD = np.array([5.25697717, 5.91150917], dtype=np.float32)


@torch.inference_mode()
def evaluate(model, rows, stats, device):
    loader = DataLoader(baseline.ChipDataset(rows, stats, patch=None, cache=False), batch_size=1, shuffle=False, num_workers=0)
    tn = fp = fn = tp = 0
    truth, scores = [], []
    model.eval()
    for x, y, valid in loader:
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device.type == "cuda"):
            probability = torch.sigmoid(model(x)).float().cpu().numpy()[:, 0]
        label = y.cpu().numpy()[:, 0].astype(np.uint8)
        mask = valid.cpu().numpy()[:, 0] > 0
        prediction = probability >= 0.5
        tn += int(((~prediction) & (label == 0) & mask).sum())
        fp += int((prediction & (label == 0) & mask).sum())
        fn += int(((~prediction) & (label == 1) & mask).sum())
        tp += int((prediction & (label == 1) & mask).sum())
        truth.append(label[mask]); scores.append(probability[mask])
    ytrue = np.concatenate(truth); yscore = np.concatenate(scores)
    precision_curve, recall_curve, _ = precision_recall_curve(ytrue, yscore)
    precision, recall = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    return {"threshold": 0.5, "iou": tp / max(tp + fp + fn, 1), "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / max(precision + recall, 1e-12),
            "pr_auc_trapezoidal": float(auc(recall_curve[::-1], precision_curve[::-1])),
            "average_precision": float(average_precision_score(ytrue, yscore)),
            "confusion_matrix_true_0_1_pred_0_1": [[tn, fp], [fn, tp]], "valid_pixels": int(ytrue.size),
            "water_prevalence": float(ytrue.mean()), "chips": len(rows)}


def speed(model, device):
    sample = torch.zeros((1, 2, 256, 256), device=device)
    model.eval()
    with torch.inference_mode():
        model(sample)
        start = time.perf_counter()
        model(sample)
        if device.type == "cuda": torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
    return {"input_patch": [256, 256], "single_patch_seconds": elapsed,
            "single_patch_ms": elapsed * 1000, "parameter_count": sum(p.numel() for p in model.parameters()),
            "peak_cuda_bytes": torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None}


def main():
    torch.set_num_threads(min(8, torch.get_num_threads()))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_rows = baseline._read_split("flood_train_data.csv")
    bolivia_rows = baseline._read_split("flood_bolivia_data.csv")
    geoms = baseline._event_geometries()
    event_by_chip = {r["s1"]: baseline._event_for_chip(r["s1"], geoms)[0] for r in train_rows + bolivia_rows}
    scratch_ckpt = torch.load(SCRATCH, map_location="cpu", weights_only=False)
    event_id = str(scratch_ckpt["validation_event_id"])
    val_rows = [r for r in train_rows if event_by_chip[r["s1"]] == event_id and baseline._inspect_chip(r)[2].any()]
    test_rows = [r for r in bolivia_rows if baseline._inspect_chip(r)[2].any()]
    scratch_model = baseline.AttentionUNet(base=int(scratch_ckpt.get("base_channels", 16)))
    scratch_model.load_state_dict(scratch_ckpt["state_dict"]); scratch_model.to(device)
    scratch_stats = (np.asarray(scratch_ckpt["normalization_mean"], np.float32), np.asarray(scratch_ckpt["normalization_std"], np.float32))
    scratch_eval_file = ROOT / "data/gherproof/manifests/sen1floods11_independent_evaluation.json"
    scratch_results = json.loads(scratch_eval_file.read_text())
    payload = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "device": str(device),
               "split_protocol": {"training": "210 usable chips from official train split excluding all event 11 chips",
                                  "validation": f"event {event_id}, {len(val_rows)} usable chips",
                                  "test": f"separate Bolivia event 1, {len(test_rows)} chips",
                                  "threshold": 0.5, "test_used_for_selection": False},
               "experiment_1_scratch_baseline": {"checkpoint": str(SCRATCH.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": hashlib.sha256(SCRATCH.read_bytes()).hexdigest(),
                    "validation": scratch_results["validation_event"], "bolivia_test": scratch_results["independent_bolivia_event_test"],
                    "inference_speed": speed(scratch_model, device)},
               "experiment_2_direct_pretrained_inference": {"status": "not_applicable_task_incompatible",
                    "reason": "Published MoCo weights are an encoder-only self-supervised representation (no segmentation decoder, no water/non-water output layer, and no water-label convention). Direct probabilities/masks would be fabricated; no inference metrics are produced."},
               "experiment_3_pretrained_finetune": {"status": "not_run_checkpoint_missing"}}
    if FINE_TUNED.is_file():
        ckpt = torch.load(FINE_TUNED, map_location="cpu", weights_only=False)
        model = ResNet50SARUNet(); model.load_state_dict(ckpt["state_dict"], strict=True); model.to(device)
        stats = (np.asarray(ckpt["normalization_mean"], np.float32), np.asarray(ckpt["normalization_std"], np.float32))
        result = {"status": "evaluated", "checkpoint": str(FINE_TUNED.relative_to(ROOT)).replace("\\", "/"),
                  "sha256": hashlib.sha256(FINE_TUNED.read_bytes()).hexdigest(),
                  "validation_event": evaluate(model, val_rows, stats, device),
                  "bolivia_event_test": evaluate(model, test_rows, stats, device),
                  "inference_speed": speed(model, device),
                  "normalization_mean_db": stats[0].tolist(), "normalization_std_db": stats[1].tolist()}
        payload["experiment_3_pretrained_finetune"] = result
    out = ROOT / "data/gherproof/manifests/pretrained_model_comparison.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(out.relative_to(ROOT)),
                      "finetune_status": payload["experiment_3_pretrained_finetune"]["status"],
                      "direct_inference": payload["experiment_2_direct_pretrained_inference"]["status"]}, indent=2))


if __name__ == "__main__":
    main()
