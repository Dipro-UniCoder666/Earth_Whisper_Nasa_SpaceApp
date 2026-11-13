"""Train and evaluate a reproducible, event-grouped SAR water U-Net baseline.

Input contract: official Sen1Floods11 v1.1 S1Hand (VV,VH in dB) and LabelHand
(-1 nodata, 0 non-water, 1 water). This learns generic surface-water labels,
not flood-water or GherProof incident labels.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RASTER_ENV = ROOT / "backend/.venv/Lib/site-packages"
if RASTER_ENV.exists():
    sys.path.append(str(RASTER_ENV))

import numpy as np
import rasterio
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import average_precision_score
from shapely.geometry import box, shape

RAW = ROOT / "data/gherproof/raw/sen1floods11/v1.1"
S1_DIR = RAW / "data/flood_events/HandLabeled/S1Hand"
LABEL_DIR = RAW / "data/flood_events/HandLabeled/LabelHand"
SPLIT_DIR = RAW / "splits/flood_handlabeled"
META_FILE = RAW / "Sen1Floods11_Metadata.geojson"


class ConvBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.body = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.GroupNorm(min(8, out_ch), out_ch), nn.SiLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.GroupNorm(min(8, out_ch), out_ch), nn.SiLU(inplace=True),
        )
        self.skip = nn.Identity() if in_ch == out_ch else nn.Conv2d(in_ch, out_ch, 1, bias=False)

    def forward(self, x):
        return self.body(x) + self.skip(x)


class AttentionGate(nn.Module):
    def __init__(self, gate_ch: int, skip_ch: int, inner: int):
        super().__init__()
        self.g = nn.Conv2d(gate_ch, inner, 1, bias=False)
        self.x = nn.Conv2d(skip_ch, inner, 1, bias=False)
        self.psi = nn.Sequential(nn.SiLU(inplace=True), nn.Conv2d(inner, 1, 1), nn.Sigmoid())

    def forward(self, gate, skip):
        alpha = self.psi(self.g(gate) + self.x(skip))
        return skip * alpha


class AttentionUNet(nn.Module):
    """Compact four-scale attention U-Net with residual convolution blocks."""
    def __init__(self, in_ch: int = 2, base: int = 16):
        super().__init__()
        widths = [base, base * 2, base * 4, base * 8]
        self.enc1 = ConvBlock(in_ch, widths[0])
        self.enc2 = ConvBlock(widths[0], widths[1])
        self.enc3 = ConvBlock(widths[1], widths[2])
        self.bridge = ConvBlock(widths[2], widths[3])
        self.pool = nn.MaxPool2d(2)
        self.up3 = nn.ConvTranspose2d(widths[3], widths[2], 2, 2)
        self.att3 = AttentionGate(widths[2], widths[2], widths[1])
        self.dec3 = ConvBlock(widths[2] * 2, widths[2])
        self.up2 = nn.ConvTranspose2d(widths[2], widths[1], 2, 2)
        self.att2 = AttentionGate(widths[1], widths[1], widths[0])
        self.dec2 = ConvBlock(widths[1] * 2, widths[1])
        self.up1 = nn.ConvTranspose2d(widths[1], widths[0], 2, 2)
        self.att1 = AttentionGate(widths[0], widths[0], max(4, widths[0] // 2))
        self.dec1 = ConvBlock(widths[0] * 2, widths[0])
        self.head = nn.Conv2d(widths[0], 1, 1)

    def forward(self, x):
        x1 = self.enc1(x)
        x2 = self.enc2(self.pool(x1))
        x3 = self.enc3(self.pool(x2))
        z = self.bridge(self.pool(x3))
        u3 = self.up3(z)
        z = self.dec3(torch.cat([u3, self.att3(u3, x3)], dim=1))
        u2 = self.up2(z)
        z = self.dec2(torch.cat([u2, self.att2(u2, x2)], dim=1))
        u1 = self.up1(z)
        z = self.dec1(torch.cat([u1, self.att1(u1, x1)], dim=1))
        return self.head(z)


def _read_split(filename: str) -> list[dict[str, str]]:
    rows = []
    with (SPLIT_DIR / filename).open(newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0].endswith("_S1Hand.tif"):
                rows.append({"s1": Path(row[0]).name, "label": Path(row[1]).name})
    return rows


def _event_geometries() -> list[tuple[str, Any]]:
    geojson = json.loads(META_FILE.read_text(encoding="utf-8"))
    return [(str(f["properties"]["ID"]), shape(f["geometry"])) for f in geojson["features"]]


def _event_for_chip(filename: str, event_geoms: list[tuple[str, Any]]) -> tuple[str, float]:
    path = S1_DIR / filename
    with rasterio.open(path) as ds:
        if ds.crs is None:
            raise RuntimeError(f"No CRS in event grouping chip: {filename}")
        b = ds.bounds
        if ds.crs.to_epsg() != 4326:
            from rasterio.warp import transform_bounds
            b = transform_bounds(ds.crs, "EPSG:4326", *b, densify_pts=21)
        footprint = box(*b)
    ranked = sorted(((footprint.intersection(g).area / max(footprint.area, 1e-12), event_id)
                     for event_id, g in event_geoms), reverse=True)
    if not ranked or ranked[0][0] < 0.5:
        raise RuntimeError(f"Chip cannot be assigned to an official event polygon with >=50% overlap: {filename}; best={ranked[:1]}")
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < 0.1:
        raise RuntimeError(f"Ambiguous event polygon assignment for {filename}: {ranked[:2]}")
    return ranked[0][1], float(ranked[0][0])


def _inspect_chip(row: dict[str, str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    with rasterio.open(S1_DIR / row["s1"]) as src:
        if src.count != 2 or (src.width, src.height) != (512, 512):
            raise RuntimeError(f"Unexpected Sentinel-1 raster shape/bands: {row['s1']} {src.count} {src.width}x{src.height}")
        if src.crs is None:
            raise RuntimeError(f"Missing CRS in {row['s1']}")
        image = src.read().astype(np.float32)
        nodata = src.nodata
        image_profile = {"crs": str(src.crs), "transform": list(src.transform), "bounds": list(src.bounds),
                         "res": list(src.res), "nodata": nodata, "units": src.units,
                         "descriptions": list(src.descriptions)}
    with rasterio.open(LABEL_DIR / row["label"]) as src:
        if src.count != 1 or (src.width, src.height) != (512, 512):
            raise RuntimeError(f"Unexpected label shape/bands: {row['label']} {src.count} {src.width}x{src.height}")
        image_transform = rasterio.Affine(*image_profile["transform"])
        if (src.crs != rasterio.crs.CRS.from_string(image_profile["crs"])
                or not np.allclose(tuple(src.transform), tuple(image_transform), rtol=0, atol=1e-10)):
            raise RuntimeError(f"S1/label georeferencing mismatch for {row['s1']}")
        labels = src.read(1)
    label_values = set(np.unique(labels).tolist())
    if not label_values.issubset({-1, 0, 1}):
        raise RuntimeError(f"Unexpected Sen1Floods11 hand-label codes {label_values}: {row['label']}")
    valid = np.isfinite(image).all(axis=0) & (labels >= 0)
    if nodata is not None and np.isfinite(nodata):
        valid &= np.all(image != nodata, axis=0)
    clean_labels = np.where(labels >= 0, labels, 255).astype(np.uint8, copy=False)
    return image, clean_labels, valid, image_profile


class ChipDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], stats: tuple[np.ndarray, np.ndarray], patch: int | None,
                 cache: bool = True, seed: int = 0):
        self.rows = rows
        self.mean, self.std = stats
        self.patch = patch
        self.cache_enabled = cache
        self.cache: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        self.rng = random.Random(seed)

    def __len__(self):
        return len(self.rows)

    def _load(self, idx: int):
        if idx not in self.cache:
            image, label, valid, _ = _inspect_chip(self.rows[idx])
            image = np.clip(image, -60, 20)
            image = (image - self.mean[:, None, None]) / self.std[:, None, None]
            image[:, ~valid] = 0
            if self.cache_enabled:
                self.cache[idx] = (image.astype(np.float32), label, valid)
            return image.astype(np.float32), label, valid
        return self.cache[idx]

    def __getitem__(self, idx: int):
        image, label, valid = self._load(idx)
        label = np.where(label == 255, 0, label).astype(np.uint8, copy=False)
        h, w = label.shape
        patch = self.patch
        if patch and patch < h and patch < w:
            y = self.rng.randrange(0, h - patch + 1)
            x = self.rng.randrange(0, w - patch + 1)
            image, label, valid = image[:, y:y+patch, x:x+patch], label[y:y+patch, x:x+patch], valid[y:y+patch, x:x+patch]
            k = self.rng.randrange(4)
            image = np.rot90(image, k, axes=(1, 2)).copy()
            label = np.rot90(label, k).copy()
            valid = np.rot90(valid, k).copy()
            if self.rng.random() < 0.5:
                image, label, valid = image[:, :, ::-1].copy(), label[:, ::-1].copy(), valid[:, ::-1].copy()
        return torch.from_numpy(image), torch.from_numpy(label.astype(np.float32))[None], torch.from_numpy(valid.astype(np.float32))[None]


def _stats(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    sums = np.zeros(2, dtype=np.float64)
    sums2 = np.zeros(2, dtype=np.float64)
    count = 0
    minv = np.full(2, np.inf)
    maxv = np.full(2, -np.inf)
    profiles = []
    for row in rows:
        image, _, valid, profile = _inspect_chip(row)
        profiles.append(profile)
        if not valid.any():
            continue
        vals = np.clip(image[:, valid], -60, 20).astype(np.float64)
        sums += vals.sum(axis=1)
        sums2 += np.square(vals).sum(axis=1)
        minv = np.minimum(minv, vals.min(axis=1))
        maxv = np.maximum(maxv, vals.max(axis=1))
        count += vals.shape[1]
    if count == 0:
        raise RuntimeError("No valid pixels in training split")
    mean = sums / count
    std = np.sqrt(np.maximum(sums2 / count - mean * mean, 1e-8))
    geometry = {"unique_crs": sorted({p["crs"] for p in profiles}),
                "unique_shape": sorted({(512, 512)}),
                "unique_resolutions": sorted({tuple(round(x, 10) for x in p["res"]) for p in profiles}),
                "per_band_min": minv.tolist(), "per_band_max": maxv.tolist(),
                "train_valid_pixels_for_normalization": int(count)}
    if len(geometry["unique_crs"]) != 1 or len(geometry["unique_resolutions"]) != 1:
        raise RuntimeError(f"Inconsistent train raster georeferencing: {geometry}")
    return mean.astype(np.float32), std.astype(np.float32), geometry


def _loss(logits, y, valid, pos_weight):
    bce = F.binary_cross_entropy_with_logits(logits, y, reduction="none", pos_weight=pos_weight)
    bce = (bce * valid).sum() / valid.sum().clamp_min(1)
    prob = torch.sigmoid(logits) * valid
    target = y * valid
    dice = 1 - (2 * (prob * target).sum() + 1) / (prob.sum() + target.sum() + 1)
    return bce + dice


@torch.inference_mode()
def _evaluate(model, rows, stats, device, batch_size: int = 1) -> dict[str, Any]:
    ds = ChipDataset(rows, stats, patch=None, cache=False)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)
    tn = fp = fn = tp = 0
    truths: list[np.ndarray] = []
    scores: list[np.ndarray] = []
    model.eval()
    for x, y, valid in loader:
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device.type == "cuda"):
            logits = model(x)
        prob = torch.sigmoid(logits).float().cpu().numpy()[:, 0]
        target = y.cpu().numpy()[:, 0].astype(np.uint8)
        mask = valid.cpu().numpy()[:, 0] > 0
        pred = prob >= 0.5
        tn += int(((~pred) & (target == 0) & mask).sum())
        fp += int((pred & (target == 0) & mask).sum())
        fn += int(((~pred) & (target == 1) & mask).sum())
        tp += int((pred & (target == 1) & mask).sum())
        truths.append(target[mask])
        scores.append(prob[mask])
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    iou = tp / max(tp + fp + fn, 1)
    y_true = np.concatenate(truths) if truths else np.array([], dtype=np.uint8)
    y_score = np.concatenate(scores) if scores else np.array([], dtype=np.float32)
    ap = float(average_precision_score(y_true, y_score)) if y_true.size and np.unique(y_true).size == 2 else None
    return {"iou": iou, "precision": precision, "recall": recall, "f1": f1,
            "pr_auc_average_precision": ap,
            "confusion_matrix_rows_true_0_1_cols_pred_0_1": [[tn, fp], [fn, tp]],
            "valid_pixels": int(tn + fp + fn + tp), "water_prevalence": float(y_true.mean()) if y_true.size else None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--patience", type=int, default=4)
    ap.add_argument("--patch", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-train", type=int, default=0, help="smoke test only; do not report its metrics")
    args = ap.parse_args()
    if not META_FILE.exists():
        raise FileNotFoundError("Run prepare_sen1floods11.py first")

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.set_num_threads(max(1, min(6, os.cpu_count() or 1)))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    rows_train = _read_split("flood_train_data.csv")
    rows_val = _read_split("flood_valid_data.csv")
    rows_test = _read_split("flood_test_data.csv")
    rows_bolivia = _read_split("flood_bolivia_data.csv")
    event_geoms = _event_geometries()

    # Map all chips through official event polygons. The Bolivia list remains an
    # untouched event-level spatial holdout. Within official train chips, hold
    # out one entire event for model selection; the random official val/test
    # splits are retained but not used because they can share event footprints.
    all_rows = {r["s1"]: r for group in (rows_train, rows_val, rows_test, rows_bolivia) for r in group}
    event_map: dict[str, dict[str, Any]] = {}
    valid_fraction: dict[str, float] = {}
    for filename in sorted(all_rows):
        event_id, overlap = _event_for_chip(filename, event_geoms)
        event_map[filename] = {"event_id": event_id, "polygon_overlap_fraction": overlap}
        _, _, valid, _ = _inspect_chip(all_rows[filename])
        valid_fraction[filename] = float(valid.mean())
    empty_by_official_split = {
        split: sum(valid_fraction[r["s1"]] == 0 for r in rows)
        for split, rows in (("train", rows_train), ("valid", rows_val), ("test", rows_test), ("bolivia", rows_bolivia))
    }
    usable_train = [r for r in rows_train if valid_fraction[r["s1"]] > 0]
    usable_bolivia = [r for r in rows_bolivia if valid_fraction[r["s1"]] > 0]
    train_events = Counter(event_map[r["s1"]]["event_id"] for r in usable_train)
    bolivia_events = {event_map[r["s1"]]["event_id"] for r in rows_bolivia}
    if len(bolivia_events) != 1:
        raise RuntimeError(f"Expected dedicated Bolivia event holdout, found events {sorted(bolivia_events)}")
    holdout_event = sorted(train_events.items(), key=lambda item: (-item[1], item[0]))[0][0]
    train_rows = [r for r in usable_train if event_map[r["s1"]]["event_id"] != holdout_event]
    val_rows = [r for r in usable_train if event_map[r["s1"]]["event_id"] == holdout_event]
    test_rows = usable_bolivia
    if not train_rows or not val_rows or not test_rows:
        raise RuntimeError("Event-grouped training/validation/Bolivia test partition is empty")
    if set(event_map[r["s1"]]["event_id"] for r in train_rows) & set(event_map[r["s1"]]["event_id"] for r in val_rows):
        raise RuntimeError("Event leakage detected between training and validation")

    if args.max_train:
        train_rows = train_rows[:args.max_train]
        val_rows = val_rows[:max(1, min(4, len(val_rows)))]
        test_rows = test_rows[:max(1, min(4, len(test_rows)))]
    stats = _stats(train_rows)
    mean, std, geo_qc = stats
    # Class-weight from a bounded deterministic sampling of training labels.
    pos = neg = 0
    for row in train_rows:
        _, labels, valid, _ = _inspect_chip(row)
        pos += int(((labels == 1) & valid).sum())
        neg += int(((labels == 0) & valid).sum())
    pos_weight = torch.tensor([min(10.0, max(1.0, neg / max(pos, 1)))], device=device)
    train_ds = ChipDataset(train_rows, stats[:2], args.patch, seed=args.seed)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    model = AttentionUNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    checkpoint_dir = ROOT / "models/gherproof"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "sen1floods11_attention_unet.pt"
    best = -1.0
    stale = 0
    history = []
    start = time.time()
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for x, y, valid in train_loader:
            x, y, valid = x.to(device), y.to(device), valid.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device.type == "cuda"):
                loss = _loss(model(x), y, valid, pos_weight)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite training loss at epoch {epoch + 1}")
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            losses.append(float(loss.detach().cpu()))
        val_metrics = _evaluate(model, val_rows, (mean, std), device)
        scheduler.step(val_metrics["iou"])
        record = {"epoch": epoch + 1, "mean_train_loss": float(np.mean(losses)),
                  "validation_event_id": holdout_event, "validation_event_iou": val_metrics["iou"],
                  "validation_metrics": val_metrics, "lr": optimizer.param_groups[0]["lr"]}
        history.append(record)
        print(json.dumps(record), flush=True)
        if val_metrics["iou"] > best + 1e-5:
            best, stale = val_metrics["iou"], 0
            torch.save({"state_dict": model.state_dict(), "architecture": "AttentionUNet", "base_channels": 16,
                        "input_bands": ["VV_dB", "VH_dB"], "normalization_mean": mean.tolist(),
                        "normalization_std": std.tolist(), "seed": args.seed, "epoch": epoch + 1,
                        "validation_event_id": holdout_event, "validation": val_metrics,
                        "training_subset": "Sen1Floods11 v1.1 official flood_train_data minus full validation event",
                        "dataset_manifest": "data/gherproof/manifests/sen1floods11_download_manifest.json"}, checkpoint_path)
        else:
            stale += 1
        if stale >= args.patience:
            break

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    bolivia_metrics = _evaluate(model, test_rows, (mean, std), device)
    report = {
        "status": "smoke_test_only" if args.max_train else "completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "Sen1Floods11 v1.1 hand-labeled Sentinel-1",
        "task": "generic surface-water segmentation; labels are not incident-specific flood labels",
        "architecture": "4-scale residual attention U-Net, trained from scratch; no compatible pretrained two-polarization SAR checkpoint supplied or verified",
        "device": str(device), "torch_version": torch.__version__, "cuda_available": torch.cuda.is_available(),
        "mixed_precision": device.type == "cuda",
        "seed": args.seed, "patch_size": args.patch, "batch_size": args.batch_size,
        "train_chips": len(train_rows), "validation_chips": len(val_rows), "validation_event_id": holdout_event,
        "bolivia_event_test_chips": len(test_rows), "bolivia_event_ids": sorted(bolivia_events),
        "empty_valid_chips_skipped_by_official_split": empty_by_official_split,
        "official_random_validation_chips_retained_not_used": len(rows_val),
        "official_random_test_chips_retained_not_used": len(rows_test),
        "event_group_counts_official_train": dict(train_events),
        "normalization": {"mean_db": mean.tolist(), "std_db": std.tolist(), "input_qc": geo_qc},
        "class_counts_train": {"water": pos, "non_water": neg, "positive_weight": float(pos_weight.item())},
        "epochs_completed": len(history), "best_validation_event_iou": best,
        "validation_event_metrics": checkpoint["validation"],
        "bolivia_event_holdout_metrics": bolivia_metrics,
        "checkpoint": str(checkpoint_path.relative_to(ROOT)).replace("\\", "/"),
        "checkpoint_sha256": __import__("hashlib").sha256(checkpoint_path.read_bytes()).hexdigest(),
        "training_history": history, "elapsed_seconds": round(time.time() - start, 1),
        "limitations": ["A benchmark water segmentation score is not waterlogging accuracy or local Sujatpur performance.",
                        "The Bolivia event holdout has only 15 chips; uncertainty and domain shift remain substantial.",
                        "Sen1Floods11 dataset licensing is unclear/proprietary in official catalog metadata; do not redistribute.",
                        "No January Sujatpur image inference was performed by this script."],
    }
    out = ROOT / "data/gherproof/manifests/sen1floods11_training_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result_manifest": str(out.relative_to(ROOT)), "checkpoint": str(checkpoint_path.relative_to(ROOT)),
                      "status": report["status"], "epochs": len(history), "bolivia_iou": bolivia_metrics["iou"]}, indent=2))


if __name__ == "__main__":
    main()
