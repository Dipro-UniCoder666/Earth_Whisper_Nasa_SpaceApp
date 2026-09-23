# Earth Whisper

**Where Earth's Changes Tell Their Story**

Built by **AquaByte** for **NASA Space Apps Challenge 2026** — Challenge:
*Dancing with the SARs*.

Earth Whisper is an interactive Earth-observation investigation experience
built on NASA–ISRO NISAR radar data. Rather than presenting a raw
"before/after change map," it treats every detected anomaly as a
scientific investigation: reconstructing how the change evolved through
time, connecting it with independent environmental evidence, comparing
competing explanations, and clearly communicating uncertainty.

This project has completed **Prompts 1–3** of a six-prompt development
process: the application shell and landing experience, real location
search with a Leaflet/OpenStreetMap investigation map and NISAR
observation timeline, and a six-clue evidence engine that assembles an
Earth Event Fingerprint. Candidate-cause comparison, the AI Investigator,
and the final case file are **not yet implemented** — see
[What has not yet been implemented](#what-has-not-yet-been-implemented).

---

## Project structure

```
Earth_Whisper/
├── AquaByte_NISAR/     Existing QGIS/NISAR scientific workspace — preserved, untouched
├── app/                React + TypeScript + Vite frontend (this prompt's main deliverable)
├── backend/            Planned FastAPI backend — structure only, not yet implemented
├── data/               Reserved storage for demo/processed/metadata data
├── docs/               Architecture, scientific principles, evidence-engine design, product docs
├── scripts/            Reserved for future data/build scripts
└── README.md           This file
```

## What was preserved

`AquaByte_NISAR/` — the team's existing QGIS/GDAL outputs (coherence
rasters, coherence-change and anomaly-cluster rasters, candidate anomaly
geopackages, unwrapped-phase products) — was **not modified, renamed,
moved, or deleted**. It sits alongside the new `app/` and `backend/`
directories exactly as uploaded.

## What was built

A complete, production-quality **React + TypeScript + Vite** frontend at
`app/`, delivering four experiences:

### `/` — Landing page
A single hero section: the Earth Whisper name, tagline, a short
explanation, a custom Earth/NISAR SVG visual (calm stylized globe, slow
satellite-pass arcs, a radar sweep, a highlighted anomaly with subtle
"NISAR OBSERVATION" / "CHANGE DETECTED" annotations), and one call to
action — **Begin the Investigation** — which routes to `/investigate`.
No feature grid, no marketing sections, no fake statistics.

### `/investigate` — Investigation start
A welcome screen — **"Where do you want to investigate?"** — with a real
location search field (backed by OpenStreetMap Nominatim), latitude/
longitude inputs, and a shortcut to the team's prototype candidate
location. Submitting routes to `/investigate/map`.

### `/investigate/map` — Investigation map
A real **Leaflet + React-Leaflet + OpenStreetMap** map (no Google Maps),
styled to feel like a scientific instrument rather than a consumer map
app. Supports zoom, pan, click-to-select, a candidate-anomaly circle
overlay, and a layer control (NISAR footprint and raster overlays are
reserved, disabled entries for a future prompt). Selecting a location
looks up nearby candidate anomalies from the NISAR service, shows a
chronological observation timeline (JUN → JUL → AUG → SEP), and — when a
candidate is selected — a compact panel with its measured coherence
comparison and an **"Investigate This Change"** button.

### `/investigate/case/:candidateId` — Evidence board
Given a selected candidate, assembles an **Earth Event Fingerprint**: six
independent evidence "clues" (radar, terrain, weather, optical, fire,
water), each showing what was observed, its source, date, and explicit
limitations — with no cause determination. Radar is genuinely measured
data from `AquaByte_NISAR`; terrain, weather, fire, and water are clearly
labeled demonstration placeholders; optical is honestly reported as not
yet available (never faked). An uncertainty panel summarizes what is
known, uncertain, and cannot be concluded.

Architecture for what remains (`features/casefile`, `features/investigator`)
is scaffolded with typed placeholders — see `docs/architecture/overview.md`.

## Running the application

```bash
cd app
npm install
npm run dev
```

Then open the printed local URL (typically `http://localhost:5173`).

- `npm run build` — production build (type-checks with `tsc -b`, then
  builds with Vite).
- `npm run preview` — serve the production build locally.

## Dependencies installed (`app/`)

- `react`, `react-dom` — UI framework
- `react-router-dom` — routing (`/`, `/investigate`, `/investigate/map`, `/investigate/case/:candidateId`)
- `lucide-react` — icon set
- `leaflet`, `react-leaflet`, `@types/leaflet` — investigation map (Prompt 2)
- `tailwindcss` v4 + `@tailwindcss/vite` — styling
- `typescript`, `vite`, `@vitejs/plugin-react` — tooling (from the Vite
  `react-ts` template)

No AI-related packages have been installed yet — those arrive with the
AI Investigator in a later prompt. Geocoding uses the browser `fetch` API
against OpenStreetMap Nominatim directly, so no additional client library
was needed for location search.

## Confirming the routes

- **`/` is the landing hero.** See `app/src/pages/LandingPage.tsx`.
- **`/investigate` is the investigation start screen** (location search). See
  `app/src/pages/InvestigationPage.tsx`.
- **`/investigate/map` is the Leaflet investigation map**, with the NISAR
  observation timeline and candidate panel. See
  `app/src/pages/InvestigationMapPage.tsx`.
- **`/investigate/case/:candidateId` is the evidence board**, assembling
  and displaying the Earth Event Fingerprint. See
  `app/src/pages/CaseInvestigationPage.tsx`.

All four are registered in `app/src/router.tsx`.

## What has NOT yet been implemented

Per the project brief, Prompts 1–3 deliberately exclude:

- Live NISAR / ASF catalog integration and NASA data downloading (the
  NISAR service is real architecture over a labeled demonstration dataset)
- GDAL / raster processing
- Real automated anomaly/change detection (Candidate #1 is a
  human-identified prototype from the team's QGIS work, not an algorithm)
- Real DEM, rainfall (GPM/IMERG), Sentinel-2/Landsat, or FIRMS integration
  — the evidence engine's service interfaces exist and are called from the
  UI, but return clearly labeled demonstration data or an honest
  "unavailable" result
- Candidate-cause comparison / hypothesis scoring (the evidence engine
  collects clues only — it does not weigh them against each other)
- Causal inference of any kind
- The AI Investigator (LLM-backed explanation layer)
- Real Earth Event Case File generation (Simple View / Science View)
- The backend API itself (structure only exists in `backend/`; all of
  Prompts 1–3 run entirely client-side against local demonstration data)

None of the above has been simulated or faked with invented findings —
in line with Earth Whisper's core scientific principle: the system says
"demonstration data," "not yet available," or "undetermined" rather than
inventing values. See `docs/science/scientific-principles.md`.

## Documentation

- [`docs/architecture/overview.md`](docs/architecture/overview.md) — system layers and repo layout
- [`docs/science/scientific-principles.md`](docs/science/scientific-principles.md) — the non-negotiable scientific rules
- [`docs/evidence-engine/design-notes.md`](docs/evidence-engine/design-notes.md) — future evidence-fusion design
- [`docs/product/experience-structure.md`](docs/product/experience-structure.md) — the two-experience product structure
- [`app/README.md`](app/README.md) — frontend-specific setup and structure
- [`backend/README.md`](backend/README.md) — backend plan (not yet implemented)
