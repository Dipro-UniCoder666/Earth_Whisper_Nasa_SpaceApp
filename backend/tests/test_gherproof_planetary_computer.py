from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "gherproof"))
import retrieve_planetary_computer_event as pipeline


class Response:
    def __init__(self, status: int, payload=None, headers=None):
        self.status_code = status
        self._payload = payload or {}
        self.headers = headers or {}
        self.ok = 200 <= status < 400

    def json(self):
        return self._payload

    def close(self):
        pass


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, json=None, timeout=None):
        self.calls.append((method, url, json, timeout))
        return self.responses.pop(0)


def item(item_id: str, *, orbit=114):
    return {"id": item_id, "properties": {"platform": "sentinel-1a",
        "sat:relative_orbit": orbit, "sat:orbit_state": "ascending",
        "sar:instrument_mode": "IW", "sar:polarizations": ["VV", "VH"]}}


def test_unsigned_href_removes_signed_query_and_fragment():
    assert pipeline.unsigned_href("https://host/data.tif?sig=secret#part") == "https://host/data.tif"


@pytest.mark.parametrize("date,item_id", [
    ("2026-01-07", "S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_rtc"),
    ("2026-01-19", "S1A_IW_GRDH_1SDV_20260119T120427_20260119T120452_062836_07E1D9_rtc"),
])
def test_crosswalk_accepts_matching_acquisition_fields_despite_provider_suffix(date, item_id):
    assert pipeline.choose([item(item_id)], date)["id"] == item_id


def test_crosswalk_rejects_wrong_orbit():
    candidate = item("S1A_IW_GRDH_1SDV_20260107T120428_20260107T120453_062661_07DB1B_rtc", orbit=113)
    assert pipeline.choose([candidate], "2026-01-07") is None


def test_stac_search_follows_next_page_and_records_all_items():
    first = Response(200, {"features": [item("one")], "links": [{"rel": "next", "href": pipeline.API + "/search?page=2", "method": "GET"}]})
    second = Response(200, {"features": [item("two")], "links": []})
    session = Session([first, second])
    items, record = pipeline.search(session, pipeline.RTC, "2026-01-07")
    assert [x["id"] for x in items] == ["one", "two"]
    assert record["result_count"] == 2
    assert record["pages_read"] == 2


def test_rate_limit_retry_and_retry_after(monkeypatch):
    sleeps = []
    monkeypatch.setattr(pipeline.time, "sleep", lambda delay: sleeps.append(delay))
    session = Session([Response(429, headers={"Retry-After": "2"}), Response(200, {"ok": True})])
    assert pipeline.request(session, "GET", pipeline.API).json() == {"ok": True}
    assert len(session.calls) == 2
    assert sleeps and 2 <= sleeps[0] < 2.25


def test_failed_response_does_not_echo_signed_query_string():
    session = Session([Response(403)])
    with pytest.raises(RuntimeError) as error:
        pipeline.request(session, "GET", "https://blob.test/a.tif?sig=very-secret")
    assert "very-secret" not in str(error.value)
    assert "HTTP 403" in str(error.value)
