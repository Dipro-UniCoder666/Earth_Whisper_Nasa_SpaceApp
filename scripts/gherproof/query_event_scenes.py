"""Query Copernicus STAC for event-window scenes over a provisional locality bbox."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
# Broad locality search window around Monirampur. This is not a surveyed enclosure AOI.
BBOX = [89.15, 22.93, 89.30, 23.08]
SEARCH = "https://stac.dataspace.copernicus.eu/v1/search"


def main() -> None:
    out = ROOT / "data/gherproof/manifests"
    out.mkdir(parents=True, exist_ok=True)
    result: list[dict] = []
    for collection in ("sentinel-1-grd", "sentinel-2-l2a"):
        payload = {
            "collections": [collection],
            "bbox": BBOX,
            "datetime": "2026-01-01T00:00:00Z/2026-01-30T23:59:59Z",
            "limit": 100,
        }
        response = requests.post(SEARCH, json=payload, timeout=90)
        response.raise_for_status()
        body = response.json()
        for f in body.get("features", []):
            p = f.get("properties", {})
            result.append({
                "collection": collection,
                "id": f.get("id"),
                "datetime": p.get("datetime"),
                "platform": p.get("platform"),
                "relative_orbit": p.get("sat:relative_orbit"),
                "orbit_state": p.get("sat:orbit_state"),
                "polarizations": p.get("sar:polarizations"),
                "instrument_mode": p.get("sar:instrument_mode"),
                "processing_level": p.get("processing:level"),
                "bbox": f.get("bbox"),
                "geometry": f.get("geometry"),
                "asset_summary": {
                    k: {
                        "href": v.get("href"),
                        "https_href": (v.get("alternate", {}).get("https") or {}).get("href"),
                        "type": v.get("type"),
                        "size": v.get("file:size"),
                        "title": v.get("title"),
                        "nodata": v.get("nodata"),
                        "data_type": v.get("data_type"),
                        "checksum": v.get("file:checksum"),
                        "shape": v.get("proj:shape"),
                    }
                    for k, v in f.get("assets", {}).items()
                    if k in {"Product", "vv", "vh", "visual", "thumbnail", "B02", "B03", "B04", "B08", "SCL"}
                },
            })
    manifest = {
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalog": "Copernicus Data Space Ecosystem STAC API v1",
        "query_period_utc": ["2026-01-01", "2026-01-30"],
        "bbox_wgs84": BBOX,
        "bbox_status": "provisional locality search window, not authoritative enclosure boundary",
        "items": result,
    }
    path = out / "event_satellite_catalogue.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": str(path.relative_to(ROOT)),
        "sentinel1_count": sum(x["collection"] == "sentinel-1-grd" for x in result),
        "sentinel2_count": sum(x["collection"] == "sentinel-2-l2a" for x in result),
        "sentinel1": [{k: x.get(k) for k in ("id", "datetime", "platform", "relative_orbit", "orbit_state", "polarizations")} for x in result if x["collection"] == "sentinel-1-grd"],
        "sentinel2": [{k: x.get(k) for k in ("id", "datetime", "platform")} for x in result if x["collection"] == "sentinel-2-l2a"],
    }, indent=2))


if __name__ == "__main__":
    main()
