"""Bounded direct smoke check of the DHARA NISAR raster metadata and previews."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.api.gherproof import get_layer_metadata, get_layer_preview, get_layers  # noqa: E402


def main() -> None:
    ids = [
        "nisar-gcov-2026-10-23-track170-ascending-validated",
        "nisar-gcov-2026-11-04-track170-ascending-validated",
        "nisar-gcov-change-2026-10-23-to-2026-11-04-track170",
        "nisar-gcov-2026-10-23-track170-ascending-validated-frequencyB",
        "nisar-gcov-2026-11-04-track170-ascending-validated-frequencyB",
        "nisar-gcov-change-2026-10-23-to-2026-11-04-track170-frequencyB",
    ]
    layer_ids = {layer["evidence_id"] for layer in get_layers()["layers"]}
    missing = sorted(set(ids) - layer_ids)
    if missing:
        raise RuntimeError(f"NISAR map layers are not registered: {missing}")
    print("registered map layers", flush=True)
    metadata = {layer_id: get_layer_metadata(layer_id, asset="derived") for layer_id in ids}
    print("raster metadata opened", flush=True)
    previews = {}
    for layer_id, band in ((ids[0], 1), (ids[0], 2), (ids[2], 1), (ids[3], 1), (ids[3], 2), (ids[5], 1)):
        print(f"rendering {layer_id} band {band}", flush=True)
        response = get_layer_preview(layer_id, bbox="89.43,23.04,89.45,23.06", band=band, width=240, asset="derived", rgb=False)
        previews[f"{layer_id}:band{band}"] = {"status": response.status_code, "media_type": response.media_type,
                                               "preview_bounds": response.headers.get("X-Preview-Bounds-WGS84"),
                                               "display": response.headers.get("X-Preview-Display"),
                                               "body_iterator_type": type(response.body_iterator).__name__}
    print(json.dumps({"registered_ids": ids, "metadata": metadata, "previews": previews}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
