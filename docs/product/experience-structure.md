# Earth Whisper — Product Experience Structure

## Four experiences

### 1. Landing (`/`)
A single hero section — no feature grid, no "how it works," no scroll
depth. Its only job is to communicate what Earth Whisper is and offer one
action: **Begin the Investigation**, which routes to `/investigate`.

### 2. Investigation start (`/investigate`)
A location search / coordinate entry interface — **"Where do you want to
investigate?"** Backed by a real, provider-agnostic geocoding service
(OpenStreetMap Nominatim). Submitting a location routes to
`/investigate/map`.

### 3. Investigation map (`/investigate/map`)
A real Leaflet + OpenStreetMap map showing the selected location,
candidate anomalies as circle overlays, a chronological NISAR observation
timeline, and a candidate panel with the measured coherence comparison.
Selecting **"Investigate This Change"** routes to
`/investigate/case/:candidateId`.

### 4. Evidence board (`/investigate/case/:candidateId`)
Assembles and displays the **Earth Event Fingerprint**: six independent
evidence clues (radar, terrain, weather, optical, fire, water), each
labeled measured / demonstration / unavailable, plus an uncertainty
panel. No cause is determined here.

## Section status

| Section | Status |
|---|---|
| Location | **Implemented.** Search, coordinates, map, NISAR coverage lookup. |
| Observation | **Implemented.** NISAR observation dates, coherence, orbit/track info. Before/after imagery not yet available (see Evidence → optical). |
| Change detection | **Partially implemented.** Candidate anomalies are shown on the map with spatial extent (area) and temporal information; automated detection is not implemented — Candidate #1 is a human-identified prototype. |
| Evidence | **Partially implemented.** Terrain, rainfall, water, fire clues exist as demonstration data; optical is honestly reported unavailable; radar is measured. |
| Investigation | Not implemented. Competing hypotheses and evidence-consistency comparison are a future prompt. |
| Case file | Not implemented. Simple View / Science View. |
| AI Investigator | Not implemented. |

Each remaining section has a corresponding `features/` directory already
scaffolded in `app/src/features/` (`casefile`, `investigator`) so
implementation can proceed feature-by-feature without restructuring the
app.

## Branding rules

- The **application** is named **Earth Whisper**.
- The **team** is named **AquaByte**.
- These names are never reversed.
- Earth Whisper is described as "Built for NASA Space Apps Challenge 2026"
  — never presented as an official NASA product.
