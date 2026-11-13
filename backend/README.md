# Earth Whisper and DHARA API

The FastAPI service continues to serve the Earth Whisper Step 12/11 evidence
contracts. DHARA adds a read-only event provenance API; it does not serve
an inferred flood map or affected-area estimate when those outputs do not
exist. Sandhya and Monda data remain separate.

## Run locally (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Fisheries API write routes are disabled by default. For trusted local development only, explicitly set `GHERPROOF_FISHERIES_WRITES_ENABLED=true`; do not enable this on an unauthenticated network-facing deployment.

## DHARA evidence API

The product is branded DHARA in the application. The `/api/gherproof` prefix,
evidence storage paths and `GHERPROOF_*` environment variable names are
retained for backward compatibility.

- `GET /api/gherproof/status` — reported event status and counts of catalogue matches versus processed scenes.
- `GET /api/gherproof/catalogue` — saved January 2026 Copernicus scene metadata for a provisional locality query window.
- `GET /api/gherproof/evidence-report` — downloadable JSON case-status report with explicit unknowns.

The event catalogue is stored at `../data/gherproof/manifests/event_satellite_catalogue.json`.
Catalogue matches are not processed observations. DHARA serves only event
evidence and manifests from `../data/gherproof/`.

## Tests

```powershell
cd backend
.\.venv\Scripts\python -m pytest
```

The DHARA tests verify truthful empty states, catalogue provenance and
the absence of fabricated area/model outputs.
