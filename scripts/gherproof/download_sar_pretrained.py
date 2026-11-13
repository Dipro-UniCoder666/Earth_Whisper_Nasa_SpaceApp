"""Download a TorchGeo/SSL4EO Sentinel-1 two-polarization encoder checkpoint."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
URL = "https://huggingface.co/torchgeo/resnet50_sentinel1_all_moco/resolve/main/resnet50_sentinel1_all_moco-906e4356.pth"
SIZE = 94_349_125
SHA256 = "906e4356da0ff06ce0388cba50dd4f310ba6abbee706c5303c129d8aead98082"
DEST = ROOT / "data/gherproof/raw/pretrained_sar/resnet50_sentinel1_all_moco.pth"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    part = DEST.with_suffix(DEST.suffix + ".part")
    if not (DEST.is_file() and DEST.stat().st_size == SIZE and _sha(DEST) == SHA256):
        offset = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with requests.get(URL, headers=headers, stream=True, timeout=(30, 180)) as response:
            if offset and response.status_code == 200:
                part.unlink(missing_ok=True); offset = 0
            response.raise_for_status()
            if offset and (response.status_code != 206 or not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-")):
                raise RuntimeError("Checkpoint server did not honor the byte-range resume")
            with part.open("ab" if offset else "wb") as f:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
        if part.stat().st_size != SIZE or _sha(part) != SHA256:
            raise RuntimeError("Pretrained Sentinel-1 checkpoint size or SHA-256 does not match the official TorchGeo artifact")
        os.replace(part, DEST)
    record = {
        "name": "TorchGeo ResNet50 Sentinel-1 GRD MoCo / SSL4EO-S12",
        "source": "https://huggingface.co/torchgeo/resnet50_sentinel1_all_moco",
        "upstream": "https://github.com/zhu-xlab/SSL4EO-S12",
        "license": "CC-BY-4.0",
        "input_channels": ["Sentinel-1 VV", "Sentinel-1 VH"],
        "size_bytes": DEST.stat().st_size,
        "sha256": _sha(DEST),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "path": str(DEST.relative_to(ROOT)).replace("\\", "/"),
    }
    path = ROOT / "data/gherproof/manifests/sar_pretrained_weights_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
