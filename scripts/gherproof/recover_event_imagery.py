"""Resume authenticated retrieval of the four catalogue-listed CDSE COGs."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cdse_auth import CDSEAuth, CDSEAuthError


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _raster_metadata(path: Path) -> dict[str, Any]:
    raster_env = ROOT / "backend/.venv/Lib/site-packages"
    if raster_env.exists():
        sys.path.append(str(raster_env))
    import rasterio
    with rasterio.open(path) as ds:
        if ds.count != 1 or ds.crs is None or ds.width < 1 or ds.height < 1:
            raise ValueError("Expected a georeferenced single-band Sentinel-1 COG")
        # Force an actual decode rather than trusting a 200 response or file size.
        sample = ds.read(1, window=rasterio.windows.Window(0, 0, min(64, ds.width), min(64, ds.height)), masked=True)
        valid = sample.compressed()
        if not valid.size:
            raise ValueError("Raster sample contains no valid pixels")
        tags = ds.tags()
        band_tags = ds.tags(1)
        return {"driver": ds.driver, "crs": str(ds.crs), "width": ds.width, "height": ds.height,
                "transform": list(ds.transform), "bounds": list(ds.bounds), "resolution": list(ds.res),
                "dtype": ds.dtypes[0], "nodata": ds.nodata, "band_count": ds.count,
                "band_description": ds.descriptions[0], "units": ds.units[0], "scale": ds.scales[0],
                "offset": ds.offsets[0], "tags": tags, "band_tags": band_tags,
                "sample_valid_pixels": int(valid.size), "sample_min": float(valid.min()),
                "sample_max": float(valid.max()), "sample_median": float(__import__("numpy").median(valid))}


def _provider_hash(expected: str | None) -> str | None:
    if not expected:
        return None
    return {32: "MD5", 40: "SHA-1", 64: "SHA-256"}.get(len(expected), "unidentified")


def _download(auth: CDSEAuth, url: str, target: Path, expected_size: int) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    if target.exists() and target.stat().st_size != expected_size:
        # Preserve a complete-looking but size-invalid file for audit, never overwrite it.
        raise ValueError("Existing file size differs from catalogue; move it aside for manual review")
    if target.exists():
        return {"path": str(target.relative_to(ROOT)).replace("\\", "/"), "bytes": target.stat().st_size,
                "sha256": _sha256(target), "raster_metadata": _raster_metadata(target), "status": "downloaded_unverified"}
    offset = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}
    with auth.get(url, headers=headers, stream=True, allow_redirects=True, timeout=(30, 180)) as response:
        response.raise_for_status()
        if offset and response.status_code == 200:
            part.unlink(missing_ok=True)
            offset = 0
        if offset and response.status_code != 206:
            raise ValueError(f"Resume expected HTTP 206 but received {response.status_code}")
        if offset and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
            raise ValueError("CDSE returned an unexpected range for the resumed download")
        with part.open("ab" if offset else "wb") as output:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    output.write(chunk)
    if part.stat().st_size != expected_size:
        raise ValueError(f"Downloaded byte count {part.stat().st_size} does not match catalogue size {expected_size}")
    metadata = _raster_metadata(part)
    os.replace(part, target)
    return {"path": str(target.relative_to(ROOT)).replace("\\", "/"), "bytes": target.stat().st_size,
            "sha256": _sha256(target), "raster_metadata": metadata, "status": "verified"}


def main() -> None:
    catalogue_path = ROOT / "data/gherproof/manifests/event_satellite_catalogue.json"
    manifest_path = ROOT / "data/gherproof/manifests/event_imagery_manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    catalog = json.loads(catalogue_path.read_text(encoding="utf-8"))
    selected = [s for s in catalog.get("items", []) if s.get("collection") == "sentinel-1-grd"
                and s.get("datetime", "")[:10] in {"2026-01-07", "2026-01-19"}]
    if len(selected) != 2 or any(s.get("relative_orbit") != 114 or s.get("orbit_state", "").lower() != "ascending" for s in selected):
        raise RuntimeError("Expected exactly the January 7/19 relative-orbit-114 ascending Sentinel-1 pair")
    old = {(r.get("date"), r.get("polarization")): r for r in previous.get("records", [])}
    session = requests.Session()
    session.headers["User-Agent"] = "EarthWhisper-GherProof/2.0"
    auth = CDSEAuth(session, ROOT)
    records: list[dict[str, Any]] = []
    assets = 0
    for scene in sorted(selected, key=lambda x: x["datetime"]):
        for pol in ("vv", "vh"):
            item = scene["asset_summary"][pol]
            date = scene["datetime"][:10]
            prior = old.get((date, pol.upper()), {})
            id_parts = scene["id"].split("_")
            rec = {**prior, "date": date, "datetime": scene["datetime"], "scene_id": scene["id"],
                   "product_identifier": scene["id"], "platform": scene.get("platform"),
                   "relative_orbit": scene["relative_orbit"], "direction": scene["orbit_state"],
                   "instrument_mode": scene.get("instrument_mode") or (id_parts[1] if len(id_parts) > 1 else None),
                   "polarization": pol.upper(), "product_type": scene.get("product_type") or (id_parts[2] if len(id_parts) > 2 else None),
                   "processing_level": scene.get("processing_level"), "provider": "Copernicus Data Space Ecosystem",
                   "asset_url": item["https_href"], "catalogue_bytes": int(item["size"]),
                   "catalogue_checksum": item.get("checksum"),
                   "catalogue_checksum_algorithm": _provider_hash(item.get("checksum")),
                   "status": "not_downloaded"}
            target = ROOT / "data/gherproof/raw/event_sentinel1" / date / f"{pol.upper()}.tif"
            if not auth.credentials_available:
                rec["status"] = "authentication_blocked"
                rec["error"] = "CDSE credentials are not configured; no request attempted"
            else:
                try:
                    result = _download(auth, item["https_href"], target, int(item["size"]))
                    rec.update(result)
                    if result["status"] == "verified":
                        assets += 1
                except CDSEAuthError as exc:
                    rec.update(status="authentication_blocked", error=str(exc))
                    auth.auth_blocked = True
                except Exception as exc:
                    rec.update(status="download_failed", error_type=type(exc).__name__, error=str(exc)[:240])
            records.append(rec)
            if auth.auth_blocked:
                # Do not repeat a known invalid-auth request for remaining assets.
                break
        if auth.auth_blocked:
            # Unattempted records still get explicit statuses and retain their exact product identity.
            remaining = [(s, p) for s in sorted(selected, key=lambda x: x["datetime"]) for p in ("vv", "vh")
                         if not any(r["scene_id"] == s["id"] and r["polarization"] == p.upper() for r in records)]
            for scene_left, pol_left in remaining:
                a = scene_left["asset_summary"][pol_left]
                records.append({"date": scene_left["datetime"][:10], "datetime": scene_left["datetime"],
                                "scene_id": scene_left["id"], "product_identifier": scene_left["id"], "platform": scene_left.get("platform"),
                                "relative_orbit": scene_left.get("relative_orbit"), "direction": scene_left.get("orbit_state"),
                                "instrument_mode": scene_left.get("instrument_mode") or scene_left["id"].split("_")[1], "polarization": pol_left.upper(),
                                "product_type": scene_left.get("product_type") or scene_left["id"].split("_")[2], "processing_level": scene_left.get("processing_level"),
                                "provider": "Copernicus Data Space Ecosystem", "asset_url": a["https_href"],
                                "catalogue_bytes": int(a["size"]), "catalogue_checksum": a.get("checksum"),
                                "catalogue_checksum_algorithm": _provider_hash(a.get("checksum")),
                                "status": "authentication_blocked", "error": "Not attempted after CDSE authentication failure"})
            break
    manifest = {"updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "provider": "Copernicus Data Space Ecosystem OData product COG measurement assets",
                "auth_status": "blocked" if not auth.credentials_available or auth.auth_blocked else "authenticated",
                "assets_verified_this_run": assets, "credential_names_checked": ["CDSE_USERNAME", "CDSE_PASSWORD", "CDSE_TOTP_CODE", "CDSE_TOTP_SECRET"],
                "records": records,
                "limits": ["A product is verified only after a local Rasterio open and sample read plus size verification.",
                           "Provider checksum strings are 36 hex characters and are not identified as a standard digest.",
                           "A verified measurement asset does not by itself imply radiometric/terrain-corrected comparability."]}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path.relative_to(ROOT)), "assets": len(records),
                      "verified_this_run": assets, "auth_status": manifest["auth_status"]}, indent=2))


if __name__ == "__main__":
    main()
