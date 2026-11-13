"""Fine-tune the SSL4EO S1 MoCo ResNet50 on the frozen Phase 2 event split."""
from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "backend/.venv/Lib/site-packages"), str(ROOT / "scripts/gherproof")])
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
import train_sen1floods11 as baseline
from resnet50_sar_unet import ResNet50SARUNet

WEIGHTS = ROOT / "data/gherproof/raw/pretrained_sar/resnet50_sentinel1_all_moco.pth"
PRETRAINED_MEAN = np.array([-12.54847273, -20.19237134], dtype=np.float32)
PRETRAINED_STD = np.array([5.25697717, 5.91150917], dtype=np.float32)


def build_split():
    split = json.loads((ROOT / "data/gherproof/manifests/sen1floods11_training_results.json").read_text())
    validation_event = str(split["validation_event_id"])
    event_geom = baseline._event_geometries()
    train_all = baseline._read_split("flood_train_data.csv")
    bolivia = baseline._read_split("flood_bolivia_data.csv")
    train_rows, val_rows = [], []
    for row in train_all:
        event, _ = baseline._event_for_chip(row["s1"], event_geom)
        _, _, valid, _ = baseline._inspect_chip(row)
        if valid.any():
            (val_rows if event == validation_event else train_rows).append(row)
    if {baseline._event_for_chip(r["s1"], event_geom)[0] for r in train_rows} & {validation_event}:
        raise RuntimeError("Validation event leaked into fine-tuning set")
    if not train_rows or not val_rows or not bolivia:
        raise RuntimeError("Frozen Phase 2 event split is incomplete")
    return train_rows, val_rows, bolivia, validation_event


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--patch", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not WEIGHTS.is_file():
        raise FileNotFoundError(f"Verified pretrained encoder weights are missing: {WEIGHTS}")
    torch.manual_seed(args.seed); np.random.seed(args.seed); random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
        torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    else:
        torch.set_num_threads(min(8, torch.get_num_threads()))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rows, val_rows, _, val_event = build_split()
    model = ResNet50SARUNet()
    encoder_weights = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
    model.load_ssl4eo_backbone(encoder_weights)
    # Fine-tune the high-level encoder stages plus the decoder; freeze early
    # generic features to keep this small CPU/GPU experiment tractable.
    for name, parameter in model.encoder.named_parameters():
        parameter.requires_grad = name.startswith(("layer3.", "layer4."))
    model.to(device)
    stats = (PRETRAINED_MEAN, PRETRAINED_STD)
    train_ds = baseline.ChipDataset(rows, stats, args.patch, cache=True, seed=args.seed)
    generator = torch.Generator().manual_seed(args.seed)
    loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0, generator=generator)
    positive = negative = 0
    for row in rows:
        _, labels, valid, _ = baseline._inspect_chip(row)
        positive += int(((labels == 1) & valid).sum()); negative += int(((labels == 0) & valid).sum())
    pos_weight = torch.tensor([min(10.0, max(1.0, negative / max(positive, 1)))], device=device)
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=1e-4, weight_decay=1e-4)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    checkpoint_path = ROOT / "models/gherproof/sen1floods11_resnet50_moco_unet.pt"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    best, stale, history = -1.0, 0, []
    started = time.time()
    for epoch in range(args.epochs):
        model.train()
        model.encoder.conv1.eval(); model.encoder.bn1.eval(); model.encoder.layer1.eval(); model.encoder.layer2.eval()
        losses = []
        for x, y, valid in loader:
            x, y, valid = x.to(device), y.to(device), valid.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device.type == "cuda"):
                loss = baseline._loss(model(x), y, valid, pos_weight)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite loss at epoch {epoch + 1}")
            scaler.scale(loss).backward(); scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer); scaler.update(); losses.append(float(loss.detach().cpu()))
        metrics = baseline._evaluate(model, val_rows, stats, device)
        scheduler.step(metrics["iou"])
        row = {"epoch": epoch + 1, "train_loss": float(np.mean(losses)), "validation_event_id": val_event,
               "validation_metrics": metrics, "learning_rate": optimizer.param_groups[0]["lr"]}
        history.append(row); print(json.dumps(row), flush=True)
        if metrics["iou"] > best + 1e-5:
            best, stale = metrics["iou"], 0
            torch.save({"state_dict": model.state_dict(), "architecture": "ResNet50SARUNet",
                        "pretrained_source": "TorchGeo/SSL4EO-S12 Sentinel-1 GRD MoCo ResNet50 backbone",
                        "pretrained_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
                        "input_bands": ["VV_dB", "VH_dB"], "normalization_mean": PRETRAINED_MEAN.tolist(),
                        "normalization_std": PRETRAINED_STD.tolist(), "seed": args.seed,
                        "epoch": epoch + 1, "validation_event_id": val_event,
                        "validation": metrics, "frozen_encoder_stages": ["stem", "layer1", "layer2"],
                        "training_subset": "same 210 valid Sen1Floods11 official-train chips as scratch Phase 2, excluding event 11"}, checkpoint_path)
        else:
            stale += 1
        if stale >= args.patience:
            break
    result = {"status": "completed", "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "architecture": "ResNet50 SAR encoder-decoder; compatible MoCo encoder weights; fine-tune layers 3/4 and decoder",
              "device": str(device), "torch_version": torch.__version__, "cuda_available": torch.cuda.is_available(),
              "mixed_precision": device.type == "cuda", "seed": args.seed, "patch": args.patch,
              "batch_size": args.batch_size, "train_chips": len(rows), "validation_chips": len(val_rows),
              "validation_event_id": val_event, "epochs_completed": len(history), "best_validation_iou": best,
              "checkpoint": str(checkpoint_path.relative_to(ROOT)).replace("\\", "/"),
              "checkpoint_sha256": hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(),
              "pretrained_weight_manifest": "data/gherproof/manifests/sar_pretrained_weights_manifest.json",
              "normalization_mean_db": PRETRAINED_MEAN.tolist(), "normalization_std_db": PRETRAINED_STD.tolist(),
              "history": history, "elapsed_seconds": round(time.time() - started, 2),
              "test_set_used_for_selection": False,
              "limitations": ["Sen1Floods11 benchmark-only metrics do not estimate Sujatpur accuracy.",
                              "Only two encoder stages are fine-tuned due local compute limits.",
                              "Official Sen1Floods11 license remains ambiguous/proprietary; no redistribution."]}
    out = ROOT / "data/gherproof/manifests/sen1floods11_pretrained_finetune_results.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result_manifest": str(out.relative_to(ROOT)), "checkpoint": result["checkpoint"],
                      "epochs": len(history), "best_validation_iou": best}, indent=2))


if __name__ == "__main__":
    main()
