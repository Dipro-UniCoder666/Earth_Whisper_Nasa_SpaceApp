"""CDSE password-grant authentication with in-memory refresh and optional TOTP.

Secrets are read from process environment or a local, ignored dotenv-style file.
They are never written to manifests, checkpoints, exception messages, or logs.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CONFIG_FILE = ".env.cdse.local"
_ALLOWED = {"CDSE_USERNAME", "CDSE_PASSWORD", "CDSE_TOTP_CODE", "CDSE_TOTP_SECRET", "CDSE_TOTP"}


class CDSEAuthError(RuntimeError):
    """Safe authentication error that never includes provider response bodies."""


class CDSERequestError(RuntimeError):
    """Safe product-request/redirect failure that is not misclassified as auth."""


def _totp(secret: str, now: float | None = None) -> str:
    try:
        key = base64.b32decode(secret.strip().replace(" ", "").upper() + "=" * (-len(secret.strip().replace(" ", "")) % 8))
    except Exception as exc:
        raise CDSEAuthError("CDSE_TOTP_SECRET is not a valid Base32 secret") from exc
    counter = int((time.time() if now is None else now) // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{value:06d}"


class CDSEAuth:
    def __init__(self, session: requests.Session, root: Path, environ: dict[str, str] | None = None):
        self.session = session
        self.root = root
        self.environ = dict(os.environ if environ is None else environ)
        self.values = self._read_values()
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.expires_at = 0.0
        self.auth_blocked = False

    def _read_values(self) -> dict[str, str]:
        values: dict[str, str] = {}
        config = self.environ.get("GHERPROOF_CDSE_ENV_FILE", str(self.root / CONFIG_FILE))
        path = Path(config).expanduser()
        if path.is_file():
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                if key in _ALLOWED:
                    values[key] = value
        values.update({key: value for key in _ALLOWED if (value := self.environ.get(key))})
        # Backward-compatible CDSE_TOTP means a current one-time code, never the secret.
        if not values.get("CDSE_TOTP_CODE") and values.get("CDSE_TOTP"):
            values["CDSE_TOTP_CODE"] = values["CDSE_TOTP"]
        return values

    @property
    def credentials_available(self) -> bool:
        return bool(self.values.get("CDSE_USERNAME") and self.values.get("CDSE_PASSWORD"))

    def _store(self, body: dict[str, Any]) -> None:
        token = body.get("access_token")
        if not isinstance(token, str) or not token:
            raise CDSEAuthError("CDSE token response did not include an access token")
        self.access_token = token
        self.refresh_token = body.get("refresh_token") if isinstance(body.get("refresh_token"), str) else self.refresh_token
        self.expires_at = time.time() + max(0, int(body.get("expires_in", 0)) - 30)

    def _post_token(self, data: dict[str, str], category: str) -> dict[str, Any]:
        try:
            response = self.session.post(TOKEN_URL, data=data, timeout=30)
        except requests.RequestException as exc:
            raise CDSEAuthError("CDSE identity service could not be reached") from exc
        if response.status_code in {400, 401, 403}:
            # The body can contain submitted identity material: deliberately omit it.
            raise CDSEAuthError(f"CDSE {category} failed with HTTP {response.status_code}; check account and current 2FA code")
        if not response.ok:
            raise CDSEAuthError(f"CDSE {category} failed with HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise CDSEAuthError("CDSE identity service returned invalid JSON") from exc

    def authenticate(self, force: bool = False) -> str:
        if self.auth_blocked:
            raise CDSEAuthError("CDSE authentication is blocked after a failed token refresh; stop and check credentials")
        if not force and self.access_token and time.time() < self.expires_at:
            return self.access_token
        if self.refresh_token:
            try:
                self._store(self._post_token({"grant_type": "refresh_token", "refresh_token": self.refresh_token,
                                               "client_id": "cdse-public"}, "refresh"))
                return self.access_token  # type: ignore[return-value]
            except CDSEAuthError:
                self.refresh_token = None
                if not self.credentials_available:
                    self.auth_blocked = True
                    raise
        if not self.credentials_available:
            raise CDSEAuthError("CDSE_USERNAME and CDSE_PASSWORD are not configured")
        data = {"client_id": "cdse-public", "grant_type": "password",
                "username": self.values["CDSE_USERNAME"], "password": self.values["CDSE_PASSWORD"]}
        otp = self.values.get("CDSE_TOTP_CODE")
        secret = self.values.get("CDSE_TOTP_SECRET")
        if otp and secret:
            raise CDSEAuthError("Set only one of CDSE_TOTP_CODE or CDSE_TOTP_SECRET")
        if otp:
            data["totp"] = otp
        elif secret:
            data["totp"] = _totp(secret)
        self._store(self._post_token(data, "password authentication"))
        return self.access_token  # type: ignore[return-value]

    @staticmethod
    def _trusted_host(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host == "dataspace.copernicus.eu" or host.endswith(".dataspace.copernicus.eu")

    def get(self, url: str, **kwargs):
        request_headers = dict(kwargs.pop("headers", {}))
        current = url
        refreshed = False
        # Follow only a bounded number of redirects. Bearer tokens are sent only
        # to CDSE-owned hosts; external signed-storage redirects receive no token.
        for _ in range(8):
            headers = dict(request_headers)
            if self._trusted_host(current):
                headers["Authorization"] = f"Bearer {self.authenticate()}"
            try:
                response = self.session.get(current, headers=headers, allow_redirects=False, **kwargs)
            except requests.RequestException as exc:
                raise CDSERequestError("CDSE product download request failed") from exc
            if response.status_code == 401 and self._trusted_host(current) and not refreshed:
                response.close()
                refreshed = True
                try:
                    self.authenticate(force=True)
                except CDSEAuthError:
                    self.auth_blocked = True
                    raise
                continue
            if response.status_code == 401 and self._trusted_host(current):
                response.close()
                self.auth_blocked = True
                raise CDSEAuthError("CDSE rejected the refreshed access token; stopping further downloads")
            if response.is_redirect or response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("Location")
                response.close()
                if not location:
                    raise CDSERequestError("CDSE redirected without a Location header")
                current = urljoin(current, location)
                continue
            return response
        raise CDSERequestError("CDSE exceeded the allowed redirect limit")
