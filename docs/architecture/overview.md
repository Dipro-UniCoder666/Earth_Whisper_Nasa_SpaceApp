# Earth Whisper — Architecture Overview

## System layers

```
Scientific layer       NISAR SAR → InSAR / surface-change analysis
Computational layer     Temporal feature extraction → Anomaly detection → Spatial + temporal analysis
Evidence layer          NASA / appropriate environmental datasets → Data fusion / correlation
Interpretation layer    Candidate-cause analysis → Evidence + uncertainty
User layer              Interactive GIS → Timeline → Event Case File
```

## Current implementation status (after Prompt 3)

| Layer | Status |
|---|---|
| Scientific layer | Prototype QGIS/GDAL work exists in `AquaByte_NISAR/` (untouched). Its measured coherence values are now served through `features/investigation/services/nisarService.ts` and used as the one real ("measured") clue in the evidence engine. |
| Computational layer | Not implemented as a backend service. NISAR observation/pair modeling exists client-side in `app/src/features/investigation/`. |
| Evidence layer | **Partially implemented.** `app/src/features/evidence/` collects six independent clues (radar, terrain, weather, optical, fire, water) into an `EarthEventFingerprint`. Radar is measured; terrain/weather/fire/water are clearly labeled demonstration data; optical is honestly reported unavailable. No candidate-cause comparison is performed yet. |
| Interpretation layer | Not implemented. Type definitions exist in `app/src/data/eventTypes.ts` and `app/src/features/investigator/types.ts`. Candidate-cause comparison is scoped for a future prompt. |
| User layer | **Implemented.** Landing page (`/`), application shell (`/investigate`), a real Leaflet/OpenStreetMap investigation map with location search and NISAR observation timeline (`/investigate/map`), and an evidence board (`/investigate/case/:candidateId`) are live. See `docs/product/`. |

## Frontend feature map (as of Prompt 3)

```
app/src/features/
├── investigation/   Location search, Leaflet map, NISAR observation model,
│                     candidate anomalies — /investigate/map
├── evidence/         Six-clue evidence engine, Earth Event Fingerprint —
│                     /investigate/case/:candidateId
├── casefile/         Types only — reserved for the Simple/Science View
│                     case file UI in a future prompt
└── investigator/     Types only — reserved for the AI explanation layer
                      in a future prompt
```

## Repository layout

```
Earth_Whisper/
├── AquaByte_NISAR/    Existing QGIS/NISAR scientific workspace — do not modify
├── app/               React + TypeScript + Vite frontend
├── backend/           Planned FastAPI backend (not yet implemented)
├── data/              Demo, processed, and metadata storage (empty, reserved)
├── docs/              This documentation
└── scripts/           Reserved for future data/build scripts
```

## Frontend ↔ backend contract (future)

The frontend's `DemoEvent` type (`app/src/data/eventTypes.ts`) is the
intended shared contract. When the backend is implemented, its Pydantic
models in `backend/app/models` should mirror this shape so the case file
UI can consume real API responses with minimal changes.

## Why the frontend and scientific workspace are kept separate

`AquaByte_NISAR/` holds the team's existing QGIS outputs (coherence
rasters, anomaly cluster polygons, centroids). The frontend never reads
these files directly. Once the backend exists, it will be the only layer
that touches `AquaByte_NISAR/` or any future NISAR data pipeline — keeping
UI concerns and scientific/geospatial processing cleanly separated, as
required by the project brief.
