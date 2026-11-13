"""Download the Clark Bangladesh aquaculture archive with resume/hash checks.

The archive is copyrighted/restricted to non-commercial use per Clark's
download page. Do not redistribute it.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
URL = "https://clarkcga-aquaculture.s3.amazonaws.com/data/v1.0/zip/bangladesh/Bangladesh_Landcover_Change_Maps_1999_2014_2018_2020_2022.zip"
DEST = ROOT / "data/gherproof/raw/Clark_Bangladesh_Aquaculture_1999_2022.zip"
EXPECTED_SIZE = 46_943_637
EXPECTED_SHA256 = "5c070d8e06d73a79d282b99047f096174701106291a25b012e573c1bb742ee5a"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    part = DEST.with_suffix(DEST.suffix + ".part")
    already_valid = DEST.is_file() and DEST.stat().st_size == EXPECTED_SIZE
    if already_valid:
        check = hashlib.sha256()
        with DEST.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                check.update(chunk)
        already_valid = check.hexdigest() == EXPECTED_SHA256
    if not already_valid:
        offset = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with requests.get(URL, headers=headers, stream=True, timeout=(30, 120)) as response:
            if offset and response.status_code == 200:
                offset = 0
                part.unlink(missing_ok=True)
            response.raise_for_status()
            if offset and response.status_code != 206:
                raise RuntimeError(f"Expected HTTP 206 to resume, got {response.status_code}")
            if offset and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                raise RuntimeError("Server returned an unexpected Content-Range while resuming")
            with part.open("ab" if offset else "wb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        stream.write(chunk)
    target = DEST if already_valid else part
    if target.stat().st_size != EXPECTED_SIZE:
        raise RuntimeError(f"Wrong byte size: {target.stat().st_size} != {EXPECTED_SIZE}")
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    actual_hash = digest.hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise RuntimeError(f"SHA-256 mismatch: {actual_hash}")
    if not already_valid:
        os.replace(part, DEST)
    manifest_path = ROOT / "data/gherproof/manifests/public_dataset_downloads.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    records = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    records = [x for x in records if x.get("dataset") != "Clark Bangladesh aquaculture maps"]
    records.append({
        "dataset": "Clark Bangladesh aquaculture maps",
        "source_url": URL,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "bytes": EXPECTED_SIZE,
        "sha256": actual_hash,
        "license": "Non-commercial restriction on source page; archive metadata says CC-BY-4.0. Do not redistribute; clarify rights before commercial use.",
        "path": str(DEST.relative_to(ROOT)).replace("\\", "/"),
        "extracted": False,
    })
    manifest_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records[-1], indent=2))


if __name__ == "__main__":
    main()
