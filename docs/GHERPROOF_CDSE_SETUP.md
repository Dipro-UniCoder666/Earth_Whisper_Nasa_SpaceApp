# CDSE credentials and Sentinel‑1 recovery (Windows PowerShell)

## Provider and authentication

The four event links are Copernicus Data Space Ecosystem OData measurement COG URLs under `zipper.dataspace.copernicus.eu/odata/v1/Products(...)/Nodes(...)/$value`. Their product identifiers encode Sentinel‑1A IW GRDH scenes acquired 2026‑01‑07 and 2026‑01‑19, relative orbit 114 ascending, VV/VH. CDSE requires an OAuth access token for OData downloads. The documented endpoint uses the public client ID `cdse-public` and password grant; a refresh token is returned and may refresh access tokens. With account 2FA, CDSE's token API accepts a current one-time `totp` code. A TOTP secret is different from that current code; this implementation can generate the current code locally if a Base32 secret is configured.

See the official [CDSE token documentation](https://documentation.dataspace.copernicus.eu/APIs/Token.html), [OData download documentation](https://documentation.dataspace.copernicus.eu/APIs/OData.html), and [FAQ token lifetime](https://documentation.dataspace.copernicus.eu/FAQ.html). Access tokens are short lived (documented as 10 minutes); the client refreshes in memory and retries a 401 once, then stops if authentication still fails.

## Configure secrets without placing them in chat

Register or sign into CDSE using the account owner’s browser. Do not send a password, token, one-time code, or TOTP secret in chat, a ticket, or a source file.

### Option A: current PowerShell process

Set credentials in a PowerShell session. The password prompt does not echo input; the plaintext exists only in the current process environment until that session closes:

```powershell
$env:CDSE_USERNAME = Read-Host 'CDSE account email'
$secure = Read-Host 'CDSE password' -AsSecureString
$env:CDSE_PASSWORD = [System.Net.NetworkCredential]::new('', $secure).Password
Remove-Variable secure
```

If CDSE 2FA is enabled, either enter the short-lived code when prompted by your authenticator and set it only for this run:

```powershell
$env:CDSE_TOTP_CODE = Read-Host 'Current CDSE authenticator code'
```

Older local setup may use `CDSE_TOTP`; the current implementation accepts it only as an alias for that same current one-time code:

```powershell
$env:CDSE_TOTP = Read-Host 'Current CDSE authenticator code'
```

Or set `CDSE_TOTP_SECRET` to the account's Base32 seed only in a protected local machine secret store; the script computes a fresh code. Do not set both. Legacy `CDSE_TOTP` is treated only as a current code, never as a seed. Clear variables after use with `Remove-Item Env:CDSE_USERNAME,Env:CDSE_PASSWORD,Env:CDSE_TOTP_CODE,Env:CDSE_TOTP_SECRET -ErrorAction SilentlyContinue`.

### Option B: ignored local configuration file

Create `.env.cdse.local` at the repository root with only the needed keys:

```text
CDSE_USERNAME=account@example.org
CDSE_PASSWORD=your-local-secret
CDSE_TOTP_CODE=123456
```

Do not add this file to Git. It is covered by `.gitignore`. Restrict it to your Windows account:

```powershell
icacls .env.cdse.local /inheritance:r
icacls .env.cdse.local /grant:r "$($env:USERNAME):(R,W)"
```

The code reads the file locally, never prints its values, and does not persist OAuth access/refresh tokens. Delete the file after retrieval if you no longer need it. `GHERPROOF_CDSE_ENV_FILE` may point to a different protected dotenv-style file.

## Recover and verify

From the repository root, with the `backend/.venv` dependencies installed:

```powershell
py scripts/gherproof/recover_event_imagery.py
py scripts/gherproof/verify_event_imagery.py
```

The downloader resumes `.part` files with HTTP Range, checks status/Content-Range, expected catalogue size, SHA‑256, and opens each COG with Rasterio and reads pixels before marking it verified. The provider checksum fields in this catalogue are 36 hex characters and are not recognized as MD5/SHA; they are recorded but not mislabelled. The verifier records CRS, affine transform, resolution, bounds, NoData, unit/scale metadata and valid-pixel statistics. A downloaded file is not automatically considered a scientifically comparable observation.

Outputs:

- Raw assets: `data/gherproof/raw/event_sentinel1/<date>/VV.tif` and `VH.tif`.
- Download manifest: `data/gherproof/manifests/event_imagery_manifest.json`.
- Validation record: `data/gherproof/manifests/event_imagery_validation.json`.
- Human-readable judgement: `docs/GHERPROOF_EVENT_IMAGERY_VALIDATION.md`.

## Common errors

- `authentication_blocked`: account variables are missing, rejected, or current 2FA code expired. No repeated asset download attempts are made after a failed refresh.
- HTTP 401 after refresh: verify that the account can access CDSE OData products and that the workstation clock is synchronized. Check that no stale or incorrect environment variables are overriding the local config.
- HTTP 403: account/product authorization or access policy issue; inspect CDSE account access and do not try alternative credentials in source.
- `download_failed` with byte-count mismatch: rerun the script to resume the partial file; if the server ignored byte ranges, the script restarts only when it receives a full response.
- `incompatible` or raster open error: preserve the raw file and manifest; do not use it in event inference until the product representation is understood.
- No credentials: the script records all four assets as blocked and exits without contacting the identity service or downloading imagery.
