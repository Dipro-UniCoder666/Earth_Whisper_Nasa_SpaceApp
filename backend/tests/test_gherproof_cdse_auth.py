import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/gherproof"))
from cdse_auth import CDSEAuth, CDSEAuthError, _totp


class Response:
    def __init__(self, status, body=None, headers=None):
        self.status_code = status
        self.ok = status < 400
        self.is_redirect = False
        self.headers = headers or {}
        self._body = body or {}
        self.closed = False

    def json(self):
        return self._body

    def close(self):
        self.closed = True


class Session:
    def __init__(self):
        self.posts = []
        self.gets = []
        self.responses = []

    def post(self, url, data, timeout):
        self.posts.append(data)
        return self.responses.pop(0)

    def get(self, url, **kwargs):
        self.gets.append(kwargs)
        return self.responses.pop(0)


def test_no_credentials_fail_before_network(tmp_path):
    session = Session()
    auth = CDSEAuth(session, tmp_path, environ={})
    assert not auth.credentials_available
    with pytest.raises(CDSEAuthError, match="not configured"):
        auth.authenticate()
    assert session.posts == []


def test_rfc6238_totp_vector():
    # RFC 6238 SHA-1 test vector at 59 seconds, six digits.
    assert _totp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", now=59) == "287082"


def test_password_auth_uses_current_totp_code_without_logging(tmp_path):
    session = Session()
    session.responses = [Response(200, {"access_token": "secret-token", "expires_in": 600, "refresh_token": "refresh"})]
    auth = CDSEAuth(session, tmp_path, environ={"CDSE_USERNAME": "user", "CDSE_PASSWORD": "password", "CDSE_TOTP_CODE": "123456"})
    assert auth.authenticate() == "secret-token"
    assert session.posts[0]["totp"] == "123456"
    assert session.posts[0]["client_id"] == "cdse-public"


def test_401_refreshes_once_then_stops(tmp_path):
    session = Session()
    session.responses = [
        Response(200, {"access_token": "first", "expires_in": 600, "refresh_token": "refresh"}),
        Response(401),
        Response(200, {"access_token": "second", "expires_in": 600, "refresh_token": "refresh2"}),
        Response(200),
    ]
    auth = CDSEAuth(session, tmp_path, environ={"CDSE_USERNAME": "user", "CDSE_PASSWORD": "password"})
    response = auth.get("https://zipper.dataspace.copernicus.eu/asset")
    assert response.status_code == 200
    assert len(session.posts) == 2
    assert session.posts[1]["grant_type"] == "refresh_token"


def test_expired_access_token_uses_refresh_token_before_download(tmp_path):
    session = Session()
    session.responses = [
        Response(200, {"access_token": "first", "expires_in": 600, "refresh_token": "refresh"}),
        Response(200, {"access_token": "renewed", "expires_in": 600, "refresh_token": "refresh2"}),
        Response(200),
    ]
    auth = CDSEAuth(session, tmp_path, environ={"CDSE_USERNAME": "user", "CDSE_PASSWORD": "password"})
    auth.authenticate()
    auth.expires_at = 0
    response = auth.get("https://zipper.dataspace.copernicus.eu/asset")
    assert response.status_code == 200
    assert session.posts[1]["grant_type"] == "refresh_token"
    assert session.gets[0]["headers"]["Authorization"] == "Bearer renewed"


def test_bearer_token_is_not_forwarded_to_external_signed_storage(tmp_path):
    session = Session()
    session.responses = [
        Response(200, {"access_token": "private", "expires_in": 600}),
        Response(302, headers={"Location": "https://signed-storage.example/object?sig=opaque"}),
        Response(200),
    ]
    auth = CDSEAuth(session, tmp_path, environ={"CDSE_USERNAME": "user", "CDSE_PASSWORD": "password"})
    auth.get("https://zipper.dataspace.copernicus.eu/asset")
    assert session.gets[0]["headers"]["Authorization"] == "Bearer private"
    assert "Authorization" not in session.gets[1]["headers"]


def test_auth_error_does_not_include_provider_body(tmp_path):
    session = Session()
    session.responses = [Response(401, {"error_description": "private-account-detail"})]
    auth = CDSEAuth(session, tmp_path, environ={"CDSE_USERNAME": "user", "CDSE_PASSWORD": "password"})
    with pytest.raises(CDSEAuthError) as error:
        auth.authenticate()
    assert "private-account-detail" not in str(error.value)
