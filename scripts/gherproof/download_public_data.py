"""Download the verified S1GFloods archive with size/hash checks.

The source archive is research/non-commercial according to the authors' repo.
This script does not extract it or redistribute it.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "gherproof" / "raw" / "S1GFloods.rar"
URL = "https://huggingface.co/datasets/Tamer-Saleh/S1GFloods/resolve/main/S1GFloods.rar"
EXPECTED_SIZE = 673_724_972
EXPECTED_SHA256 = "4f1b57c342c661853dec0d7384709ce4bb9e53097ab31cd060cd4a3f915e3e67"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    partial = DEST.with_suffix(DEST.suffix + ".part")
    already_valid = DEST.is_file() and DEST.stat().st_size == EXPECTED_SIZE
    if already_valid:
        existing_hash = hashlib.sha256()
        with DEST.open("rb") as stream:
            for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                existing_hash.update(chunk)
        already_valid = existing_hash.hexdigest() == EXPECTED_SHA256

    if not already_valid:
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with requests.get(URL, headers=headers, stream=True, timeout=(30, 120)) as response:
            if offset and response.status_code == 200:
                offset = 0
                partial.unlink(missing_ok=True)
            response.raise_for_status()
            if offset and response.status_code != 206:
                raise RuntimeError(f"Expected HTTP 206 to resume, got {response.status_code}")
            if offset and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                raise RuntimeError("Server returned an unexpected Content-Range while resuming")
            with partial.open("ab" if offset else "wb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        stream.write(chunk)
        size = partial.stat().st_size
    else:
        size = DEST.stat().st_size
    if size != EXPECTED_SIZE:
        raise RuntimeError(f"Downloaded {size} bytes; expected {EXPECTED_SIZE}")
    digest = hashlib.sha256()
    verified_path = DEST if already_valid else partial
    with verified_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != EXPECTED_SHA256:
        raise RuntimeError(f"SHA-256 mismatch: {digest.hexdigest()}")
    if not already_valid:
        os.replace(partial, DEST)
    manifest = {
        "dataset": "Tamer-Saleh/S1GFloods",
        "source_url": URL,
        "retrieved_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "bytes": size,
        "sha256": digest.hexdigest(),
        "license_metadata": "Hugging Face dataset card reports CC-BY-4.0; official author repository says non-commercial/research only. Treat as restricted pending clarification.",
        "path": str(DEST.relative_to(ROOT)).replace("\\", "/"),
        "extracted": False,
    }
    out = ROOT / "data" / "gherproof" / "manifests" / "public_dataset_downloads.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    existing_records = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    existing_records = [row for row in existing_records if row.get("dataset") != manifest["dataset"]]
    existing_records.append(manifest)
    out.write_text(json.dumps(existing_records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
