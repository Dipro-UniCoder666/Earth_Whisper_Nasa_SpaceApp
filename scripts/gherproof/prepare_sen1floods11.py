"""Fetch the focused, official Sen1Floods11 v1.1 hand-labeled SAR subset.

Only the S1Hand and LabelHand layers, official split lists, and event metadata
are retrieved. The weak-label and optical products are intentionally omitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
BUCKET = "sen1floods11"
BASE = f"https://storage.googleapis.com/{BUCKET}/v1.1"
API = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o"
SPLIT_NAMES = (
    "flood_train_data.csv", "flood_valid_data.csv", "flood_test_data.csv",
    "flood_bolivia_data.csv",
)
SPLIT_PREFIX = "splits/flood_handlabeled/"
S1_PREFIX = "data/flood_events/HandLabeled/S1Hand/"
LABEL_PREFIX = "data/flood_events/HandLabeled/LabelHand/"
EVENT_META = "Sen1Floods11_Metadata.geojson"


def _listing(session: requests.Session, prefix: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    token = None
    while True:
        params: dict[str, Any] = {"prefix": f"v1.1/{prefix}", "maxResults": 1000}
        if token:
            params["pageToken"] = token
        response = session.get(API, params=params, timeout=45)
        response.raise_for_status()
        body = response.json()
        for item in body.get("items", []):
            name = item["name"]
            if name.startswith("v1.1/"):
                result[name[len("v1.1/"):]] = item
        token = body.get("nextPageToken")
        if not token:
            return result


def _download(session: requests.Session, object_name: str, dest: Path,
              expected: dict[str, Any] | None = None) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/{object_name}"
    expected_size = int(expected["size"]) if expected and expected.get("size") else None
    part = dest.with_suffix(dest.suffix + ".part")
    if dest.exists() and expected_size is not None and dest.stat().st_size == expected_size:
        size, digest = _hash(dest)
        remote_md5 = expected.get("md5Hash") if expected else None
        verified = False
        if remote_md5:
            import base64
            check = hashlib.md5()
            with dest.open("rb") as stream:
                for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                    check.update(chunk)
            verified = base64.b64encode(check.digest()).decode("ascii") == remote_md5
            if not verified:
                raise RuntimeError(f"Existing file GCS MD5 mismatch for {object_name}")
        return {"status": "already_present_verified", "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
                "bytes": size, "sha256": digest, "source_object": object_name,
                "gcs_md5_verified": verified}

    offset = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}
    with session.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
        if offset and response.status_code == 200:
            offset = 0
            part.unlink(missing_ok=True)
        response.raise_for_status()
        if offset and response.status_code != 206:
            raise RuntimeError(f"Resume expected HTTP 206, received {response.status_code}: {object_name}")
        if offset and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
            raise RuntimeError(f"Unexpected Content-Range while resuming {object_name}")
        mode = "ab" if offset else "wb"
        with part.open(mode) as stream:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    stream.write(chunk)
    size, digest = _hash(part)
    if expected_size is not None and size != expected_size:
        raise RuntimeError(f"Size mismatch for {object_name}: {size} != {expected_size}")
    remote_md5 = expected.get("md5Hash") if expected else None
    if remote_md5:
        import base64
        md5 = hashlib.md5()
        with part.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                md5.update(chunk)
        actual_remote_md5 = base64.b64encode(md5.digest()).decode("ascii")
        if actual_remote_md5 != remote_md5:
            raise RuntimeError(f"GCS MD5 mismatch for {object_name}")
    os.replace(part, dest)
    return {"status": "downloaded_verified", "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "bytes": size, "sha256": digest, "source_object": object_name,
            "gcs_md5_verified": bool(remote_md5)}


def _hash(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _csv_names(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.reader(stream):
            if len(row) >= 2 and row[0].strip().endswith("_S1Hand.tif"):
                rows.append((Path(row[0].strip()).name, Path(row[1].strip()).name))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only", action="store_true", help="fetch official metadata and split lists only")
    args = parser.parse_args()
    raw = ROOT / "data/gherproof/raw/sen1floods11/v1.1"
    manifests = ROOT / "data/gherproof/manifests"
    raw.mkdir(parents=True, exist_ok=True)
    manifests.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "EarthWhisper-GherProof/1.0 (research data provenance)"

    listings = {
        "splits": _listing(session, SPLIT_PREFIX),
        "s1": _listing(session, S1_PREFIX),
        "labels": _listing(session, LABEL_PREFIX),
    }
    records: list[dict[str, Any]] = []
    pairs_by_split: dict[str, list[tuple[str, str]]] = {}
    split_dir = raw / SPLIT_PREFIX
    for name in SPLIT_NAMES:
        object_name = SPLIT_PREFIX + name
        rec = _download(session, object_name, split_dir / name, listings["splits"].get(object_name))
        rec["role"] = "official_split"
        records.append(rec)
        pairs_by_split[name.removeprefix("flood_").removesuffix("_data.csv")] = _csv_names(split_dir / name)

    meta_obj = EVENT_META
    # Fetch the small known metadata object directly instead of listing the
    # bucket's many thousands of STAC catalog objects.
    meta_record = _download(session, meta_obj, raw / meta_obj, None)
    meta_record["role"] = "official_event_metadata"
    records.append(meta_record)

    if not args.metadata_only:
        listed_s1, listed_labels = listings["s1"], listings["labels"]
        s1_count, label_count = len(listed_s1), len(listed_labels)
        if s1_count != 446 or label_count != 446:
            raise RuntimeError(f"Expected 446 official hand-labeled pairs; found S1={s1_count}, labels={label_count}")
        # Train, validation, ordinary test and the separately designated Bolivia holdout.
        pairs: dict[tuple[str, str], set[str]] = {}
        for split_name, rows in pairs_by_split.items():
            for s1_name, label_name in rows:
                pairs[(s1_name, label_name)] = {"split": split_name}
        if len(pairs) != 446:
            raise RuntimeError(f"Expected 446 unique official pairs, found {len(pairs)}")
        tasks = sorted(pairs.items())
        for (s1_name, label_name), _info in tasks:
            if s1_name not in {Path(n).name for n in listed_s1} or label_name not in {Path(n).name for n in listed_labels}:
                raise RuntimeError(f"Official split references object absent from hand-labeled source listing: {s1_name}")
        jobs = []
        for (s1_name, label_name), info in tasks:
            jobs.extend([
                (S1_PREFIX + s1_name, listed_s1[S1_PREFIX + s1_name], info["split"], "S1"),
                (LABEL_PREFIX + label_name, listed_labels[LABEL_PREFIX + label_name], info["split"], "label"),
            ])

        def fetch(job):
            obj, expected, split, layer = job
            worker = requests.Session()
            worker.headers["User-Agent"] = "EarthWhisper-GherProof/1.0 (research data provenance)"
            rec = _download(worker, obj, raw / obj, expected)
            rec.update({"role": "hand_labeled_chip", "split": split, "layer": layer})
            return rec

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(fetch, job) for job in jobs]
            for i, future in enumerate(as_completed(futures), start=1):
                records.append(future.result())
                if i % 100 == 0 or i == len(futures):
                    print(f"Verified {i}/{len(futures)} Sen1Floods11 layer files", flush=True)

    output = {
        "dataset": "Sen1Floods11 v1.1 hand-labeled Sentinel-1 subset",
        "source": "https://github.com/cloudtostreet/Sen1Floods11",
        "bucket": f"gs://{BUCKET}/v1.1/",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "subset": "official S1Hand + LabelHand, four published split files, and event metadata; no weak labels or S2",
        "license_note": "No explicit permissive dataset license identified in official repository readme; source STAC collections declare proprietary. Use only within source terms, do not redistribute; request clarification from Cloud to Street.",
        "splits": {name: len(rows) for name, rows in pairs_by_split.items()},
        "records": records,
    }
    out = manifests / "sen1floods11_download_manifest.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(out.relative_to(ROOT)), "splits": output["splits"],
                      "record_count": len(records), "downloaded": sum(x["status"] == "downloaded_verified" for x in records)}, indent=2))


if __name__ == "__main__":
    main()
