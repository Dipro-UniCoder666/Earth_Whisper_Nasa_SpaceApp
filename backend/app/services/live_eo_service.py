"""Bounded, metadata-only Earth observation acquisition.

This service discovers NISAR GUNW collection/granule metadata through NASA's
Earthdata CMR API. It deliberately does not download or process raster data;
the verified investigation contract remains the scientific result source.
"""

from __future__ import annotations

import json
import logging
import os
import copy
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LOGGER = logging.getLogger(__name__)
DEFAULT_CACHE_TTL_SECONDS = 900
_METADATA_CACHE: Dict[str, Dict[str, Any]] = {}


class LiveAcquisitionError(RuntimeError):
    """Raised when the live metadata request is unavailable or malformed."""


class LiveEOService:
    def __init__(self, opener: Any = urlopen) -> None:
        self._opener = opener

    def acquire_nisar_metadata(self, latitude: float, longitude: float) -> Dict[str, Any]:
        cache_key = self._cache_key(latitude, longitude)
        if os.environ.get("LIVE_EO_ENABLED", "true").lower() not in {"1", "true", "yes"}:
            return self._cached_or_unavailable(cache_key, "live acquisition disabled by configuration")

        started_at = datetime.now(timezone.utc).isoformat()
        LOGGER.info("live_eo_attempt source=NASA_EARTHDATA_CMR lat=%s lon=%s", latitude, longitude)
        try:
            collection_payload = self._get_json(
                "/search/collections.json",
                {
                    "keyword": "NISAR GUNW",
                    "has_granules": "true",
                    "include_has_granules": "true",
                    "page_size": "10",
                },
            )
            collection = self._select_gunw_collection(collection_payload)
            if not collection:
                return self._cached_or_unavailable(cache_key, "no NISAR GUNW collection was discovered", started_at)

            concept_id = collection.get("id")
            if not isinstance(concept_id, str) or not concept_id:
                return self._cached_or_unavailable(cache_key, "discovered collection did not include a concept id", started_at)

            granule_payload = self._get_json(
                "/search/granules.json",
                {
                    "collection_concept_id": concept_id,
                    "point": f"{longitude},{latitude}",
                    "page_size": "5",
                    "sort_key": "-start_date",
                },
            )
            feed = granule_payload.get("feed")
            if not isinstance(feed, dict):
                raise LiveAcquisitionError("CMR granule response had no valid feed object")
            granules = feed.get("entry")
            if not isinstance(granules, list):
                raise LiveAcquisitionError("CMR granule response had no valid entry list")

            retrieved_at = datetime.now(timezone.utc).isoformat()
            LOGGER.info(
                "live_eo_success source=NASA_EARTHDATA_CMR collection=%s granules=%s processing=metadata_only",
                concept_id,
                len(granules),
            )
            result = {
                "status": "success" if granules else "unavailable",
                "source_status": "LIVE",
                "source": "NASA_EARTHDATA_CMR",
                "product_type": "NISAR_GUNW",
                "collection": self._collection_summary(collection, concept_id),
                "granules": [self._granule_summary(granule) for granule in granules],
                "attempted_at": started_at,
                "retrieved_at": retrieved_at,
                "processing_status": "metadata_only",
                "reason": None if granules else "no matching granules at the selected point",
            }
            if result["status"] == "success":
                self._store_cache(cache_key, result)
                return result
            return self._cached_or_unavailable(cache_key, result["reason"], started_at)
        except (LiveAcquisitionError, HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            LOGGER.warning("live_eo_fallback source=NASA_EARTHDATA_CMR reason=%s", exc)
            return self._cached_or_unavailable(cache_key, str(exc), started_at)

    def _get_json(self, path: str, params: Dict[str, str]) -> Dict[str, Any]:
        base_url = os.environ.get("NASA_CMR_BASE_URL", "https://cmr.earthdata.nasa.gov").rstrip("/")
        request = Request(f"{base_url}{path}?{urlencode(params)}", headers=self._headers())
        timeout = float(os.environ.get("LIVE_EO_TIMEOUT_SECONDS", "3"))
        with self._opener(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise LiveAcquisitionError("CMR response was not a JSON object")
        return payload

    @staticmethod
    def _headers() -> Dict[str, str]:
        headers = {"Accept": "application/json", "Client-Id": "earth-whisper"}
        token = os.environ.get("NASA_EARTHDATA_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _select_gunw_collection(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        feed = payload.get("feed")
        if not isinstance(feed, dict):
            raise LiveAcquisitionError("CMR collection response had no valid feed object")
        entries = feed.get("entry")
        if not isinstance(entries, list):
            raise LiveAcquisitionError("CMR collection response had no valid entry list")
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            searchable = " ".join(str(entry.get(key, "")) for key in ("short_name", "entry_title", "dataset_id")).upper()
            if "NISAR" in searchable and "GUNW" in searchable:
                return entry
        return None

    @staticmethod
    def _granule_summary(granule: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(granule, dict):
            raise LiveAcquisitionError("CMR granule entry was malformed")
        return {
            "concept_id": granule.get("id"),
            "producer_granule_id": granule.get("producer_granule_id"),
            "title": granule.get("title"),
            "time_start": granule.get("time_start"),
            "time_end": granule.get("time_end"),
            "acquisition_timestamps": {
                "time_start": granule.get("time_start"),
                "time_end": granule.get("time_end"),
            },
            "download_urls": LiveEOService._download_urls(granule),
            "source_metadata": {
                key: granule.get(key)
                for key in ("provider", "dataset_id", "collection_concept_id", "native_id", "revision_id", "browse_flag", "online_access_flag")
                if granule.get(key) is not None
            },
        }

    @staticmethod
    def _collection_summary(collection: Dict[str, Any], concept_id: str) -> Dict[str, Any]:
        return {
            "concept_id": concept_id,
            "short_name": collection.get("short_name"),
            "entry_title": collection.get("entry_title"),
            "source_metadata": {
                key: collection.get(key)
                for key in ("provider", "dataset_id", "version_id", "revision_id", "native_id")
                if collection.get(key) is not None
            },
        }

    @staticmethod
    def _download_urls(granule: Dict[str, Any]) -> list[Dict[str, Any]]:
        relationships = granule.get("related_urls") or granule.get("RelatedUrls") or granule.get("links") or []
        if not isinstance(relationships, list):
            return []
        urls = []
        for relationship in relationships:
            if not isinstance(relationship, dict):
                continue
            relationship_type = " ".join(str(relationship.get(key, "")) for key in ("type", "Type", "rel", "description", "Description")).upper()
            url = relationship.get("url") or relationship.get("URL") or relationship.get("href")
            if isinstance(url, str) and any(marker in relationship_type for marker in ("GET DATA", "GETDATA", "DOWNLOAD", "DATA")):
                urls.append({"url": url, "type": relationship.get("type") or relationship.get("Type") or relationship.get("rel")})
        return urls

    @staticmethod
    def _cache_key(latitude: float, longitude: float) -> str:
        return f"nisar-gunw:{latitude:.4f}:{longitude:.4f}"

    @staticmethod
    def _cache_ttl_seconds() -> float:
        try:
            return max(0.001, float(os.environ.get("LIVE_EO_CACHE_TTL_SECONDS", str(DEFAULT_CACHE_TTL_SECONDS))))
        except ValueError:
            return DEFAULT_CACHE_TTL_SECONDS

    @classmethod
    def _store_cache(cls, cache_key: str, result: Dict[str, Any]) -> None:
        _METADATA_CACHE[cache_key] = {
            "expires_at": time.monotonic() + cls._cache_ttl_seconds(),
            "result": copy.deepcopy(result),
        }

    @classmethod
    def _cached_or_unavailable(cls, cache_key: str, reason: str, attempted_at: Optional[str] = None) -> Dict[str, Any]:
        cached = _METADATA_CACHE.get(cache_key)
        if cached and cached.get("expires_at", 0) > time.monotonic() and cls._valid_cached_result(cached.get("result")):
            result = copy.deepcopy(cached["result"])
            result.update({
                "source_status": "CACHED_LIVE",
                "cache_served_at": datetime.now(timezone.utc).isoformat(),
                "cache_expires_at": datetime.fromtimestamp(time.time() + (cached["expires_at"] - time.monotonic()), timezone.utc).isoformat(),
                "live_failure_reason": reason,
            })
            LOGGER.info("live_eo_cached source=NASA_EARTHDATA_CMR cache_key=%s", cache_key)
            return result
        if cached:
            _METADATA_CACHE.pop(cache_key, None)
        return cls._unavailable(reason, attempted_at)

    @staticmethod
    def _valid_cached_result(result: Any) -> bool:
        return bool(
            isinstance(result, dict)
            and result.get("status") == "success"
            and result.get("source") == "NASA_EARTHDATA_CMR"
            and isinstance(result.get("collection"), dict)
            and isinstance(result.get("granules"), list)
            and result["granules"]
        )

    @classmethod
    def clear_cache(cls) -> None:
        """Clear process-local metadata cache; intended for tests and operators."""
        _METADATA_CACHE.clear()

    @staticmethod
    def _unavailable(reason: str, attempted_at: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "unavailable",
            "source_status": "VERIFIED_STATIC",
            "source": "NASA_EARTHDATA_CMR",
            "product_type": "NISAR_GUNW",
            "collection": None,
            "granules": [],
            "attempted_at": attempted_at or datetime.now(timezone.utc).isoformat(),
            "retrieved_at": None,
            "processing_status": "not_processed",
            "reason": reason,
        }
