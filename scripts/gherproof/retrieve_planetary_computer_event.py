"""Retrieve and validate the Jan 2026 GherProof scenes from public MPC Sentinel-1 RTC.

Uses anonymous STAC and the official Planetary Computer SAS endpoint. SAS values
are held in memory only; signed URLs are never written or printed. Outputs are
AOI-clipped RTC products, not full-scene downloads.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import numpy as np
import rasterio
import requests
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import Resampling, transform_bounds, transform_geom

ROOT = Path(__file__).resolve().parents[2]
API = "https://planetarycomputer.microsoft.com/api/stac/v1"
SAS_API = "https://planetarycomputer.microsoft.com/api/sas/v1/token"
RTC = "sentinel-1-rtc"
GRD = "sentinel-1-grd"
DATES = ("2026-01-07", "2026-01-19")
AOI = tuple(json.loads((ROOT / "data/gherproof/manifests/enclosure_boundary_provenance.json").read_text(encoding="utf-8"))
            ["provisional_locality_search_window_wgs84"]["bbox"])
TARGET_CRS = "EPSG:32645"  # UTM zone 45N contains this locality (89.15-89.30 E).
RESOLUTION = 10.0
NODATA = -32768.0
OUT_DIR = ROOT / "data/gherproof/processed/sentinel1/planetary_computer"
RAW_DIR = ROOT / "data/gherproof/raw/event_sentinel1/planetary_computer"
MANIFEST = ROOT / "data/gherproof/manifests/planetary_computer_event_imagery.json"
VALIDATION = ROOT / "data/gherproof/manifests/planetary_computer_scene_validation.json"
USER_AGENT = "EarthWhisper-GherProof/Phase4B"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def unsigned_href(href: str) -> str:
    p = urlsplit(href)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def request(session: requests.Session, method: str, url: str, *, json_body=None, timeout=(10, 45)) -> requests.Response:
    """Bounded retry for transient service failures; never expose signed query strings."""
    last_error = None
    for attempt in range(5):
        try:
            response = session.request(method, url, json=json_body, timeout=timeout)
            if response.status_code == 429 or response.status_code in {500, 502, 503, 504}:
                if attempt == 4:
                    raise RuntimeError(f"HTTP {response.status_code} after bounded retries at {urlsplit(url).hostname}")
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = min(30.0, max(1.0, float(retry_after))) if retry_after else min(16.0, 2.0**attempt)
                except ValueError:
                    delay = min(16.0, 2.0**attempt)
                response.close()
                time.sleep(delay + random.random() * 0.25)
                continue
            if not response.ok:
                raise RuntimeError(f"HTTP {response.status_code} from {urlsplit(url).hostname}; response body omitted")
            return response
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_error = type(exc).__name__
            if attempt == 4:
                break
            time.sleep(min(16.0, 2.0**attempt) + random.random() * 0.25)
    raise RuntimeError(f"Request failed after bounded retries: {last_error or 'unknown transport error'}")


def search(session: requests.Session, collection: str, day: str) -> tuple[list[dict], dict]:
    body = {"collections": [collection], "bbox": list(AOI),
            "datetime": f"{day}T00:00:00Z/{day}T23:59:59Z", "limit": 100}
    first = request(session, "POST", API + "/search", json_body=body)
    payload = first.json()
    items = list(payload.get("features", []))
    pages = 1
    while any(link.get("rel") == "next" for link in payload.get("links", [])):
        if pages >= 20:
            raise RuntimeError("STAC pagination exceeded 20 pages; refusing unbounded search")
        nxt = next(link for link in payload["links"] if link.get("rel") == "next")
        method = nxt.get("method", "GET").upper()
        if method == "POST":
            payload = request(session, "POST", nxt["href"], json_body=nxt.get("body", body)).json()
        else:
            payload = request(session, "GET", nxt["href"]).json()
        items.extend(payload.get("features", []))
        pages += 1
    return items, {"collection": collection, "datetime": body["datetime"], "bbox_wgs84": list(AOI),
                   "method": "POST /search", "limit_per_page": 100, "pages_read": pages,
                   "result_count": len(items), "result_item_ids": [it.get("id") for it in items]}


def choose(items: list[dict], date: str) -> dict | None:
    expected_scene = next((r["scene_id"] for r in json.loads((ROOT / "data/gherproof/manifests/event_imagery_manifest.json").read_text(encoding="utf-8"))["records"] if r["date"] == date), "")
    expected_parts = expected_scene.split("_")
    if len(expected_parts) < 8:
        return None
    matches = []
    for item in items:
        props = item.get("properties", {})
        item_parts = item.get("id", "").split("_")
        # MPC omits the provider-specific CDSE product-instance suffix, but
        # preserves platform/mode, both sensing times, relative orbit and datatake.
        same_acquisition_id = len(item_parts) >= 8 and item_parts[:8] == expected_parts[:8]
        if (props.get("platform", "").lower() == "sentinel-1a"
                and props.get("sat:relative_orbit") == 114
                and props.get("sat:orbit_state") == "ascending"
                and props.get("sar:instrument_mode") == "IW"
                and set(props.get("sar:polarizations", [])) >= {"VV", "VH"}
                and same_acquisition_id):
            matches.append(item)
    if not matches:
        return None
    matches.sort(key=lambda it: it.get("properties", {}).get("datetime", ""))
    return matches[0]


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def asset_metadata(session: requests.Session, item: dict, pol: str, token: str,
                   target_transform, target_width: int, target_height: int,
                   aoi_mask: np.ndarray) -> tuple[np.ndarray, dict]:
    asset = item["assets"].get(pol.lower())
    if not asset:
        raise RuntimeError(f"Required {pol} asset missing from STAC item")
    href = unsigned_href(asset["href"])
    signed = href + "?" + token
    # Verify actual COG range responses before GDAL opens the remote object.
    try:
        with session.get(signed, headers={"Range": "bytes=0-16383"}, stream=True,
                         timeout=(10, 30), allow_redirects=True) as response:
            if response.status_code != 206:
                raise RuntimeError(f"{pol} range read returned HTTP {response.status_code}")
            content_range = response.headers.get("Content-Range", "")
            first = next(response.iter_content(16384), b"")
            if len(first) < 8 or first[:4] not in (b"II*\x00", b"MM\x00*") or not content_range:
                raise RuntimeError(f"{pol} range response is not a readable TIFF header")
    except requests.RequestException as exc:
        raise RuntimeError(f"{pol} COG range request failed: {type(exc).__name__}") from exc

    with rasterio.Env(GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_CONNECTTIMEOUT="10",
                      GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="2",
                      CPL_VSIL_CURL_USE_HEAD="NO", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(signed) as source:
            source_meta = {"crs": str(source.crs), "width": source.width, "height": source.height,
                           "transform": list(source.transform), "bounds": list(source.bounds),
                           "resolution": list(source.res), "dtype": source.dtypes[0],
                           "count": source.count, "nodata": source.nodata,
                           "units": source.units[0], "scale": source.scales[0], "offset": source.offsets[0],
                           "descriptions": list(source.descriptions), "tags": source.tags(),
                           "band_tags": source.tags(1), "mask_flags": [str(x) for x in source.mask_flag_enums[0]],
                           "asset_type": asset.get("type"), "asset_roles": asset.get("roles"),
                           "asset_href": href, "http_content_range": content_range}
            vrt_options = {"crs": TARGET_CRS, "transform": target_transform,
                           "width": target_width, "height": target_height,
                           "resampling": Resampling.nearest, "nodata": source.nodata or NODATA,
                           "src_nodata": source.nodata or NODATA, "dtype": "float32"}
            with WarpedVRT(source, **vrt_options) as vrt:
                data = vrt.read(1, masked=True, out_dtype="float32")
    values = np.asarray(data.compressed(), dtype=np.float32)
    values = values[np.isfinite(values)]
    valid = (~np.ma.getmaskarray(data)) & np.isfinite(np.asarray(data.filled(NODATA))) & aoi_mask
    if source_meta["nodata"] is not None:
        valid &= np.asarray(data.filled(NODATA)) != source_meta["nodata"]
    if not values.size:
        stats = {"valid_pixels_in_aoi": 0, "min": None, "p02": None, "median": None, "p98": None, "max": None}
    else:
        aoi_values = np.asarray(data.data)[valid]
        stats = {"valid_pixels_in_aoi": int(valid.sum()), "aoi_pixels": int(aoi_mask.sum()),
                 "valid_fraction_of_aoi": float(valid.sum() / max(1, aoi_mask.sum())),
                 "min": float(aoi_values.min()), "p02": float(np.percentile(aoi_values, 2)),
                 "median": float(np.median(aoi_values)), "p98": float(np.percentile(aoi_values, 98)),
                 "max": float(aoi_values.max()), "nan_count_in_aoi": int(np.isnan(np.asarray(data.data)[aoi_mask]).sum()),
                 "infinite_count_in_aoi": int(np.isinf(np.asarray(data.data)[aoi_mask]).sum())}
    return np.asarray(data.filled(NODATA), dtype=np.float32), {**source_meta, "statistics_on_common_grid": stats}


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/geo+json, application/json"})
    collection_metadata = {}
    for collection in (RTC, GRD):
        doc = request(session, "GET", f"{API}/collections/{collection}").json()
        collection_metadata[collection] = {"title": doc.get("title"), "license": doc.get("license"),
            "extent": doc.get("extent"), "providers": doc.get("providers"),
            "msft:requires_account": doc.get("msft:requires_account"),
            "item_asset_schemas": doc.get("item_assets"), "description": doc.get("description")}
    manifest = {"created_at_utc": utcnow(), "provider": "Microsoft Planetary Computer",
                "api": API, "authentication": "anonymous STAC and public SAS token endpoint; no account key",
                "collection_priority": [RTC, GRD], "collections": collection_metadata, "aoi_wgs84": list(AOI),
                "aoi_status": "broad provisional locality search window; not Pallimangal boundary",
                "searches": [], "selected_scenes": [], "assets": [], "limitations": []}
    searches = {}
    for collection in (RTC, GRD):
        for day in DATES:
            print(f"STAC search: collection={collection}, date={day}", flush=True)
            items, query = search(session, collection, day)
            manifest["searches"].append(query)
            searches[(collection, day)] = items
    scenes = {}
    for day in DATES:
        item = choose(searches[(RTC, day)], day)
        collection = RTC
        if item is None:
            item = choose(searches[(GRD, day)], day)
            collection = GRD
        if item is None:
            manifest["selected_scenes"].append({"date": day, "status": "not_found"})
            continue
        scenes[day] = (collection, item)
        item_copy = json.loads(json.dumps(item))
        for a in item_copy.get("assets", {}).values():
            a["href"] = unsigned_href(a["href"])
        item_path = RAW_DIR / "stac_items" / f"{day}_{collection}_{item['id']}.json"
        save_json(item_path, item_copy)
        p = item.get("properties", {})
        manifest["selected_scenes"].append({"date": day, "status": "catalogue_match",
            "collection": collection, "item_id": item["id"], "provider_datetime": p.get("datetime"),
            "platform": p.get("platform"), "relative_orbit": p.get("sat:relative_orbit"),
            "orbit_direction": p.get("sat:orbit_state"), "instrument_mode": p.get("sar:instrument_mode"),
            "polarizations": p.get("sar:polarizations"), "product_type": p.get("sar:product_type"),
            "processing_level": p.get("s1:processing_level"), "product_timeliness": p.get("s1:product_timeliness"),
            "processing_datetime": p.get("s1:processing_datetime"), "orbit_source": p.get("s1:orbit_source"),
            "absolute_orbit": p.get("sat:absolute_orbit"), "datatake_id": p.get("s1:datatake_id"),
            "processing_version": p.get("s1:processing_version"),
            "footprint": item.get("geometry"), "collection_license": collection_metadata[collection].get("license"),
            "cdse_reference_identifier": next((r.get("product_identifier") for r in json.loads((ROOT / "data/gherproof/manifests/event_imagery_manifest.json").read_text(encoding="utf-8"))["records"] if r.get("date") == day), None),
            "crosswalk_basis": "shared sensing start/stop timestamps, orbit and datatake fields plus STAC platform/mode/polarization; alternative RTC representation, not the same file",
            "metadata_path": str(item_path.relative_to(ROOT)).replace("\\", "/"),
            "asset_keys": list(item.get("assets", {}).keys())})
    save_json(MANIFEST, manifest)
    if len(scenes) != 2 or any(scenes[d][0] != RTC for d in DATES):
        manifest["limitations"].append("Both exact-date RTC scenes were not found; no RTC/GRD mixed processing was attempted.")
        save_json(MANIFEST, manifest)
        raise SystemExit("Both matching RTC scenes are required; see the alternative-provider manifest.")

    token_response = request(session, "GET", SAS_API + "/" + RTC, timeout=(10, 45)).json()
    token = token_response.get("token")
    if not token:
        raise RuntimeError("MPC SAS endpoint response had no token; body omitted")
    manifest["sas_token_expiry_utc"] = token_response.get("msft:expiry")

    west, south, east, north = transform_bounds("EPSG:4326", TARGET_CRS, *AOI, densify_pts=21)
    left = math.floor(west / RESOLUTION) * RESOLUTION
    bottom = math.floor(south / RESOLUTION) * RESOLUTION
    right = math.ceil(east / RESOLUTION) * RESOLUTION
    top = math.ceil(north / RESOLUTION) * RESOLUTION
    width, height = int(round((right-left)/RESOLUTION)), int(round((top-bottom)/RESOLUTION))
    transform = from_origin(left, top, RESOLUTION, RESOLUTION)
    aoi_geojson = {"type": "Polygon", "coordinates": [[[AOI[0],AOI[1]],[AOI[2],AOI[1]],
        [AOI[2],AOI[3]],[AOI[0],AOI[3]],[AOI[0],AOI[1]]]]}
    projected_aoi = transform_geom("EPSG:4326", TARGET_CRS, aoi_geojson, precision=8)
    aoi_mask = geometry_mask([projected_aoi], out_shape=(height,width), transform=transform, invert=True)

    arrays: dict[tuple[str,str], np.ndarray] = {}
    qc_records = []
    for day in DATES:
        collection, item = scenes[day]
        p = item.get("properties", {})
        for pol in ("vv", "vh"):
            try:
                print(f"Reading remote RTC COG window: date={day}, polarization={pol.upper()}", flush=True)
                arr, qc = asset_metadata(session, item, pol, token, transform, width, height, aoi_mask)
                arrays[(day, pol.upper())] = arr
                qc_records.append({"date": day, "item_id": item["id"], "collection": collection,
                                   "polarization": pol.upper(), "status": "asset_accessible", "raster_qc": qc})
                manifest["assets"].append({"date": day, "item_id": item["id"], "collection": collection,
                    "polarization": pol.upper(), "unsigned_asset_href": unsigned_href(item["assets"][pol]["href"]),
                    "signed_url_persisted": False, "full_scene_downloaded": False,
                    "verification_scope": "remote COG range/header and AOI pixel-window validation plus local clipped output QC",
                    "status": "asset_accessible",
                    "raster_qc": qc, "product_datetime": p.get("datetime")})
                save_json(MANIFEST, manifest)
            except Exception as exc:
                qc_records.append({"date": day, "item_id": item["id"], "collection": collection,
                                   "polarization": pol.upper(), "status": "access_failed",
                                   "error": f"{type(exc).__name__}: raster access or validation failed; details withheld"})
                manifest["assets"].append({"date": day, "item_id": item["id"], "collection": collection,
                    "polarization": pol.upper(), "unsigned_asset_href": unsigned_href(item["assets"].get(pol, {}).get("href", "")),
                    "signed_url_persisted": False, "full_scene_downloaded": False, "status": "access_failed",
                    "error": f"{type(exc).__name__}: raster access or validation failed; details withheld"})
                save_json(MANIFEST, manifest)

    date_valid = {}
    for day in DATES:
        date_valid[day] = aoi_mask.copy()
        for pol in ("VV", "VH"):
            if (day, pol) in arrays:
                arr = arrays[(day, pol)]
                date_valid[day] &= np.isfinite(arr) & (arr != NODATA)
            else:
                date_valid[day][:] = False
    common_valid = aoi_mask.copy()
    for key, array in arrays.items():
        common_valid &= np.isfinite(array) & (array != NODATA)
    common_count = int(common_valid.sum())
    basic_scene_match = all(
        item.get("properties", {}).get("platform", "").lower() == "sentinel-1a"
        and item.get("properties", {}).get("sat:relative_orbit") == 114
        and item.get("properties", {}).get("sat:orbit_state") == "ascending"
        and item.get("properties", {}).get("sar:instrument_mode") == "IW"
        and set(item.get("properties", {}).get("sar:polarizations", [])) >= {"VV", "VH"}
        for _, item in scenes.values())
    if len(arrays) != 4:
        pair_class = "not_evaluated"
    elif not basic_scene_match or common_count == 0:
        pair_class = "unsuitable"
    else:
        pair_class = "conditionally_suitable"
    outputs = []
    if pair_class == "conditionally_suitable":
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for day in DATES:
            out = OUT_DIR / f"{day}_sentinel1_rtc_vv_vh_10m_utm45n.tif"
            temp = out.with_suffix(out.suffix + ".part")
            profile = {"driver": "GTiff", "height": height, "width": width, "count": 2,
                       "dtype": "float32", "crs": TARGET_CRS, "transform": transform,
                       "nodata": NODATA, "compress": "DEFLATE", "predictor": 3,
                       "tiled": True, "blockxsize": 256, "blockysize": 256, "BIGTIFF": "IF_SAFER"}
            with rasterio.Env(GDAL_TIFF_INTERNAL_MASK="YES"):
                with rasterio.open(temp, "w", **profile) as dst:
                    for band, pol in enumerate(("VV", "VH"), start=1):
                        arr = arrays[(day, pol)].copy()
                        arr[~common_valid] = NODATA
                        dst.write(arr, band)
                        dst.set_band_description(band, pol)
                        dst.update_tags(band, polarization=pol, measurement="gamma0",
                                        units="not_declared_in_raster_metadata",
                                        source_collection=RTC, source_item=scenes[day][1]["id"])
                    dst.write_mask(common_valid.astype("uint8") * 255)
                    dst.update_tags(source_provider="Microsoft Planetary Computer", collection=RTC,
                        item_id=scenes[day][1]["id"], acquisition_datetime=scenes[day][1]["properties"].get("datetime", ""),
                        processing="AOI clip and nearest-neighbour reprojection to shared EPSG:32645 10m grid; no value normalization",
                        validity="all four source VV/VH date assets valid, plus inside provisional AOI",
                        aoi_status="provisional locality only; not verified enclosure boundary")
            os.replace(temp, out)
            with rasterio.open(out) as check:
                check.read(1, window=((0,min(64,height)),(0,min(64,width))), masked=True)
                checksum = sha256(out)
                outputs.append({"date": day, "kind": "two-polarization-analysis-ready-clip",
                    "path": str(out.relative_to(ROOT)).replace("\\", "/"),
                    "bytes": out.stat().st_size, "sha256": checksum, "crs": str(check.crs),
                    "width": check.width, "height": check.height, "resolution": list(check.res),
                    "transform": list(check.transform), "band_descriptions": list(check.descriptions),
                    "nodata": check.nodata, "common_valid_pixels": common_count,
                    "valid_fraction_of_aoi": common_count / max(1, int(aoi_mask.sum()))})
        for a in manifest["assets"]:
            a["status"] = "verified"
            a["note"] = "Source COG range-read and Rasterio window validated; clipped analysis-ready output checksummed. Full scene not downloaded."
            out_row = next(o for o in outputs if o.get("date") == a["date"])
            a["analysis_output_path"] = out_row["path"]
            a["analysis_output_band"] = 1 if a["polarization"] == "VV" else 2
            a["analysis_output_sha256"] = out_row["sha256"]
        for scene in manifest["selected_scenes"]:
            if scene.get("date") in DATES:
                scene["status"] = "verified"
        mask_out = OUT_DIR / "2026-01-07_2026-01-19_rtc_validity_masks_10m_utm45n.tif"
        mask_temp = mask_out.with_suffix(mask_out.suffix + ".part")
        mask_profile = {"driver": "GTiff", "height": height, "width": width, "count": 4,
                        "dtype": "uint8", "crs": TARGET_CRS, "transform": transform,
                        "nodata": None, "compress": "DEFLATE", "tiled": True,
                        "blockxsize": 256, "blockysize": 256}
        with rasterio.open(mask_temp, "w", **mask_profile) as dst:
            mask_layers = (("2026-01-07_both_VV_VH_valid", date_valid[DATES[0]]),
                           ("2026-01-19_both_VV_VH_valid", date_valid[DATES[1]]),
                           ("common_both_dates_and_polarizations_valid", common_valid),
                           ("provisional_AOI", aoi_mask))
            for band, (name, mask) in enumerate(mask_layers, start=1):
                dst.write(mask.astype("uint8"), band)
                dst.set_band_description(band, name)
            dst.update_tags(source_provider="Microsoft Planetary Computer", collection=RTC,
                interpretation="Validity-only masks; 1=valid/inside as named, 0=invalid or outside. Not water labels.",
                aoi_status="provisional locality only; not verified enclosure boundary")
        os.replace(mask_temp, mask_out)
        with rasterio.open(mask_out) as check:
            outputs.append({"kind": "validity-mask-stack", "path": str(mask_out.relative_to(ROOT)).replace("\\", "/"),
                "bytes": mask_out.stat().st_size, "sha256": sha256(mask_out), "crs": str(check.crs),
                "width": check.width, "height": check.height, "resolution": list(check.res),
                "band_descriptions": list(check.descriptions), "nodata": check.nodata,
                "common_valid_pixels": common_count})
        manifest["processing"] = {"target_crs": TARGET_CRS, "resolution_m": RESOLUTION,
            "resampling": "nearest", "source_measurement": "RTC gamma0; band metadata declares Scale=linear and SARPixelContent=intensity; raster units field is absent; no dB conversion or per-date normalization",
            "nodata": NODATA, "common_valid_pixels": common_count,
            "aoi_pixels": int(aoi_mask.sum()), "common_valid_fraction": common_count/max(1,int(aoi_mask.sum())),
            "outputs": outputs}
    else:
        manifest["limitations"].append("No analysis-ready products created: source validity does not overlap the provisional AOI or expected acquisition identity failed.")
    manifest["anonymous_access_check"] = {"stac_catalogue": "success", "sas_signing": "success",
        "asset_range_reads": "success" if len(arrays) == 4 else "partial", "account_key_used": False,
        "collection_metadata_msft_requires_account": collection_metadata[RTC].get("msft:requires_account"),
        "observed": "Anonymous SAS endpoint and asset range requests returned successful responses; no subscription key was supplied."}
    manifest["pair_assessment"] = {"classification": pair_class,
        "same_expected_platform_orbit_direction_mode_polarizations": basic_scene_match,
        "all_four_asset_reads_succeeded": len(arrays) == 4,
        "common_valid_pixels_all_dates_polarizations": common_count,
        "common_valid_fraction_of_provisional_aoi": common_count/max(1,int(aoi_mask.sum())),
        "rationale": ("Matched acquisition geometry and same RTC collection; conditionally suitable for cautious backscatter comparison. Does not establish event causation or water classification; processing baseline, moisture/crop/rainfall effects and absence of an authoritative enclosure boundary remain limitations." if pair_class == "conditionally_suitable" else "The pre/post pair could not be fully evaluated; see per-asset statuses and limitations.")}
    manifest["outputs"] = outputs
    manifest["updated_at_utc"] = utcnow()
    save_json(MANIFEST, manifest)
    validation = {"updated_at_utc": utcnow(), "source_manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "collection_license": "CC-BY-4.0", "attribution": "Sentinel-1 RTC provided by Microsoft Planetary Computer; RTC processing by Catalyst; underlying Sentinel-1 mission data by ESA/Copernicus.",
        "aoi_wgs84": list(AOI), "aoi_status": "provisional locality search window only",
        "analysis_grid": {"crs": TARGET_CRS, "resolution_m": RESOLUTION, "width": width, "height": height,
                          "transform": list(transform), "nodata": NODATA},
        "assets": qc_records, "common_valid_pixels": common_count,
        "common_valid_fraction_of_aoi": common_count/max(1,int(aoi_mask.sum())),
        "pair_assessment": manifest["pair_assessment"], "outputs": outputs,
        "limitations": ["No authoritative Pallimangal enclosure geometry exists; coverage is measured only for the broad provisional locality bbox.",
                         "Gamma0 RTC backscatter is not a water probability or flood label.",
                         "Temporal backscatter differences may reflect crop stage, soil moisture, irrigation, rainfall, aquaculture, roughness or residual processing effects.",
                         "RTC source products are read remotely by byte ranges; full original scenes were not downloaded."]}
    save_json(VALIDATION, validation)
    print(json.dumps({"search_counts": [{"collection": q["collection"], "date": q["datetime"][:10], "count": q["result_count"]} for q in manifest["searches"]],
                      "assets_read": len(arrays), "pair_classification": pair_class,
                      "common_valid_fraction": manifest["pair_assessment"]["common_valid_fraction_of_provisional_aoi"],
                      "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
