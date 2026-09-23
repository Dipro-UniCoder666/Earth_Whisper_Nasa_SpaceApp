# Earth Whisper — Backend

**Status: not yet implemented.** This directory only contains the planned
package structure. No API routes, processing pipelines, or evidence
services exist yet — building them is scoped to later prompts (Prompt 2
onward), once the frontend shell in `../app` is confirmed.

## Planned structure

```
backend/
└── app/
    ├── api/          # FastAPI route handlers (location search, observation
    │                   queries, case file endpoints)
    ├── services/      # Orchestration between processing, evidence, and API layers
    ├── processing/    # NISAR/InSAR analysis (coherence, deformation, temporal
    │                   fingerprinting) — will wrap or call out to the existing
    │                   QGIS/GDAL workflow in ../AquaByte_NISAR
    ├── evidence/       # Evidence-fusion engine: terrain, precipitation, optical,
    │                   fire, water datasets, and candidate-cause comparison
    ├── models/         # Pydantic schemas shared with the frontend's TypeScript
    │                   types in app/src/data/eventTypes.ts
    └── config/         # Settings, environment configuration
```

## Design principle carried over from the frontend

The backend must never fabricate scientific findings. If evidence is
insufficient to support or rule out a hypothesis, the API should return
an explicit `insufficient-evidence` or `undetermined` status — never a
guessed cause or an invented confidence value. See
`../docs/science/scientific-principles.md`.

## Running (once implemented)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`app/main.py` does not exist yet — it will be added when the first real
endpoint is built.
