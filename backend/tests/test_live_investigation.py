import json
import os
import time
import unittest

from app.services import live_eo_service as live_module
from app.services.investigation_service import InvestigationService
from app.services.live_eo_service import LiveEOService


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _SequenceOpener:
    def __init__(self, responses):
        self.responses = iter(responses)

    def __call__(self, _request, timeout):
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return _Response(response)


def _collection_payload():
    return {"feed": {"entry": [{
        "id": "C123",
        "short_name": "NISAR_GUNW",
        "entry_title": "NISAR GUNW",
        "provider": "ASF",
        "version_id": "1",
    }]}}


def _granule_payload():
    return {"feed": {"entry": [{
        "id": "G456",
        "producer_granule_id": "NISAR_L2_GUNW_EXAMPLE",
        "title": "NISAR GUNW granule",
        "time_start": "2026-09-01T00:00:00Z",
        "time_end": "2026-09-01T00:12:00Z",
        "provider": "ASF",
        "related_urls": [{"type": "GET DATA", "url": "https://example.test/product.h5"}],
    }]}}


class LiveAcquisitionTests(unittest.TestCase):
    def setUp(self):
        LiveEOService.clear_cache()
        self.previous_ttl = os.environ.get("LIVE_EO_CACHE_TTL_SECONDS")

    def tearDown(self):
        LiveEOService.clear_cache()
        if self.previous_ttl is None:
            os.environ.pop("LIVE_EO_CACHE_TTL_SECONDS", None)
        else:
            os.environ["LIVE_EO_CACHE_TTL_SECONDS"] = self.previous_ttl

    def test_live_metadata_success_preserves_provenance(self):
        service = LiveEOService(_SequenceOpener([_collection_payload(), _granule_payload()]))

        result = service.acquire_nisar_metadata(22.49, 90.185)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["source_status"], "LIVE")
        self.assertEqual(result["collection"]["concept_id"], "C123")
        self.assertEqual(result["granules"][0]["concept_id"], "G456")
        self.assertEqual(result["granules"][0]["acquisition_timestamps"]["time_start"], "2026-09-01T00:00:00Z")
        self.assertEqual(result["granules"][0]["download_urls"][0]["url"], "https://example.test/product.h5")
        self.assertIsNotNone(result["retrieved_at"])

    def test_cached_fallback_is_used_after_live_failure(self):
        service = LiveEOService(_SequenceOpener([_collection_payload(), _granule_payload(), TimeoutError("timed out")]))

        live = service.acquire_nisar_metadata(22.49, 90.185)
        cached = service.acquire_nisar_metadata(22.49, 90.185)

        self.assertEqual(live["source_status"], "LIVE")
        self.assertEqual(cached["source_status"], "CACHED_LIVE")
        self.assertEqual(cached["granules"][0]["concept_id"], "G456")
        self.assertEqual(cached["processing_status"], "metadata_only")

    def test_expired_cache_and_malformed_response_fall_back(self):
        os.environ["LIVE_EO_CACHE_TTL_SECONDS"] = "0.01"
        service = LiveEOService(_SequenceOpener([_collection_payload(), _granule_payload(), {"feed": {}}]))

        service.acquire_nisar_metadata(22.49, 90.185)
        time.sleep(0.03)
        expired = service.acquire_nisar_metadata(22.49, 90.185)

        self.assertEqual(expired["source_status"], "VERIFIED_STATIC")
        self.assertEqual(expired["status"], "unavailable")

    def test_invalid_cache_entry_is_ignored(self):
        key = LiveEOService._cache_key(22.49, 90.185)
        live_module._METADATA_CACHE[key] = {"expires_at": time.monotonic() + 60, "result": {"status": "success", "granules": "invalid"}}
        service = LiveEOService(_SequenceOpener([TimeoutError("timed out")]))

        result = service.acquire_nisar_metadata(22.49, 90.185)

        self.assertEqual(result["source_status"], "VERIFIED_STATIC")
        self.assertEqual(result["status"], "unavailable")

    def test_both_locations_preserve_source_status_and_static_science(self):
        class _MetadataLive:
            def __init__(self, status):
                self.status = status

            def acquire_nisar_metadata(self, _latitude, _longitude):
                return {"status": "success", "source_status": self.status, "processing_status": "metadata_only"}

        live_service = InvestigationService(live_service=_MetadataLive("LIVE"))
        cached_service = InvestigationService(live_service=_MetadataLive("CACHED_LIVE"))
        static_service = InvestigationService(live_service=_MetadataLive("VERIFIED_STATIC"))

        for service, expected in ((live_service, "LIVE"), (cached_service, "CACHED_LIVE"), (static_service, "VERIFIED_STATIC")):
            sandhya = service.run("sandhya-river", 22.49, 90.185)
            monda = service.run("monda-uttarakhand", 31.1105, 77.9373)
            self.assertEqual(sandhya["source_status"], expected)
            self.assertEqual(monda["source_status"], expected)
            self.assertEqual(sandhya["provenance"]["scientific_result_status"], "VERIFIED_STATIC")
            self.assertEqual(monda["provenance"]["scientific_result_status"], "VERIFIED_STATIC")


if __name__ == "__main__":
    unittest.main()
