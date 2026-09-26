# Earth Whisper

**Where Earth's Changes Tell Their Story**

Built by **AquaByte** for **NASA Space Apps Challenge 2026** and the
*Dancing with the SARs* challenge.

Earth Whisper is an interactive Earth-observation investigation experience
built around NASA-ISRO NISAR radar observations. It turns measured radar
change and available environmental context into an understandable evidence
view while keeping uncertainty visible. A radar-signal change is not, by
itself, a confirmed physical event or a confirmed cause.

The current application can demonstrate:

- Selecting the Sandhya River or Monda, Uttarakhand investigation.
- A shared investigation lifecycle with a deliberate scan/loading state.
- Site-specific verified investigation data and evidence.
- NISAR radar observations and coherence-change evidence.
- Contextual evidence where it is available.
- Uncertainty, evidence coverage, and scientific limitations.
- Event Case File actions where supported by the selected investigation.
- The Whisper Lab / Science Mode experience.

The application does not claim live satellite recalculation, causal
attribution, ground-truth validation, or runtime AI confirmation.

---

## Project Structure

```
Earth_Whisper/
|- AquaByte_NISAR/     Existing QGIS/NISAR scientific workspace
|- app/                React + TypeScript + Vite frontend
|- backend/            Read-only FastAPI data and case-file API
|- data/               Generated and processed investigation artifacts
|- docs/               Architecture, science, evidence, and product docs
|- scripts/            Data-contract and scientific processing scripts
`- README.md           This file
```

The `AquaByte_NISAR/` workspace and its scientific outputs are preserved.
They are not replaced by the frontend or backend.

## Current Investigation Architecture

The current `/investigate` flow is:

```
InvestigationPage
        |
useInvestigationLifecycle
        |
site-specific investigation data
       / \\
  Sandhya  Monda
     |       |
Sandhya   Monda-specific
evidence   evidence
       \\   /
 InvestigationResultShell
```

The shared architecture covers the investigation lifecycle and common result
framing. It does not make the two investigations scientifically identical.

### Sandhya River

Sandhya uses the Step 12 candidate/data-contract architecture:

```
candidateService.ts
        |
configured read-only API when available
        |
static earth_whisper_candidates.json fallback
        |
SandhyaInvestigationResults
```

The Sandhya result retains its NISAR evidence, Sentinel-1 cross-check,
temporal fingerprint, rainfall context, optical status, evidence coverage,
uncertainty, interpretation, and limitation sections. Missing or inconclusive
evidence remains explicitly labeled.

### Monda, Uttarakhand

Monda uses its own verified prototype investigation data:

```
mondaInvestigationAdapter
        |
MONDA_INVESTIGATION
        |
useInvestigationLifecycle
        |
InvestigationResults
        |
InvestigationResultShell
```

Monda is not converted into `CandidateDetail` and does not load the Sandhya
candidate contract. Its result retains its own NISAR observation/coherence
values, terrain/elevation, local slope, geographic context, and Monda-specific
scientific wording.

### Shared UI, separate science

Sandhya and Monda share:

- Investigation selection and lifecycle framing.
- The common result presentation shell.
- The common investigation experience and scan transition.

They do not share identical evidence. Sandhya has candidate-level
Sentinel-1, rainfall, optical, temporal, coverage, and uncertainty evidence.
Monda has its own NISAR coherence comparison and NASADEM terrain context.

## Routes

### `/` - Landing page

The Earth Whisper landing experience and entry point to the investigation.

### `/investigate` - Current investigation flow

Select Sandhya River or Monda, inspect the location context, and begin the
corresponding site-specific investigation. The result lifecycle is shared,
but the evidence and data contracts remain site-specific.

### `/investigate/case/:candidateId` - Older evidence-board flow

This route remains architecturally separate from the current Sandhya/Monda
`/investigate` flow. It uses the older local demonstration architecture with
`useInvestigationState`, `demoEvent`, the fingerprint service, and evidence
services for the Earth Event Fingerprint board. It is retained for existing
navigation and demonstrations; its existence does not describe a failure of
the current investigation architecture.

### `/science` - Whisper Lab

The interactive Whisper Lab / Science Mode experience for exploring the
Earth-observation investigation concepts and available prototype evidence.

### `/about` - About

Project and team information.

## Important Frontend Files

- `app/src/pages/InvestigationPage.tsx` - investigation selection and shared lifecycle entry
- `app/src/features/investigation/models/investigationModel.ts` - discriminated shared investigation model and lifecycle types
- `app/src/features/investigation/hooks/useInvestigationLifecycle.ts` - shared loading, scan, completion, error, and reset lifecycle
- `app/src/features/investigation/adapters/mondaInvestigationAdapter.ts` - Monda data adapter
- `app/src/features/investigation/components/InvestigationResultShell.tsx` - common result presentation frame
- `app/src/features/candidates/components/SandhyaInvestigationResults.tsx` - Sandhya-specific evidence result
- `app/src/features/investigation/components/InvestigationResults.tsx` - Monda-specific evidence result
- `app/src/features/candidates/services/candidateService.ts` - Sandhya API/static candidate access
- `app/src/features/investigation/data/investigationSite.ts` - investigation site definitions, including Monda's measurements
- `app/src/features/investigation/caseFile/buildCaseFile.ts` - Monda-specific browser case-file generation

## Backend and Data

The backend is a read-only FastAPI service. It serves the generated Step 12
candidate contract and Step 11 case-file endpoints when configured. The
frontend can also run the Sandhya demonstration using its bundled static
fallback, without a local backend process.

The main generated artifacts are:

- `data/step10_ai_investigator/` - deterministic candidate investigation summaries and manifest
- `data/step11_event_case_file/` - generated event case-file JSON, PDF, methodology, and source records
- `data/step12_backend/earth_whisper_candidates.json` - Step 12 candidate data contract

These artifacts contain precomputed scientific outputs. The browser does not
recalculate raw satellite measurements during an investigation.

## Running the Application

```bash
cd app
npm install
npm run dev
```

Then open the printed local URL, typically `http://localhost:5173`.

- `npm run build` - TypeScript validation followed by a Vite production build
- `npm run preview` - serve the production build locally
- `npm run lint` - run the configured Oxlint check

The map uses Leaflet/OpenStreetMap. Location search uses the browser fetch API
against OpenStreetMap Nominatim when that workflow is used. These external
services are not live NASA evidence integrations.

## What Is Still Unfinished

The following capabilities are not currently implemented as production
features:

- Live NASA/ASF catalog integration and live NASA data downloading.
- Complete packaging of every raw input and environment needed to reproduce
  all derived outputs from scratch.
- Automated causal hypothesis comparison or physical-cause attribution.
- An executable runtime AI Investigator or LLM integration.
- Ground-truth validation against field observations.
- Complete automated frontend/browser regression coverage.
- Deployment configuration for a hosted production environment.

The repository also contains deliberately labeled demonstration or unavailable
evidence services in the older evidence-board route. They do not create new
scientific claims or substitute invented measurements for missing evidence.

## Scientific Boundaries

Earth Whisper reports observations and context, not confirmed causes:

- Radar/coherence change indicates a change in radar-scattering consistency;
  it does not automatically identify erosion, landslide, flooding, or another
  physical cause.
- Sentinel-1 is an independent radar cross-check, not ground truth.
- Rainfall is contextual evidence, not proof that rainfall caused a change.
- Optical evidence can be unavailable or inconclusive.
- Statistical anomaly values are not event probabilities.
- The current system does not establish a confirmed physical cause.

These boundaries are part of the product behavior and should be preserved in
future implementation work.

## Documentation

- [`docs/architecture/overview.md`](docs/architecture/overview.md) - system layers and repository layout
- [`docs/science/scientific-principles.md`](docs/science/scientific-principles.md) - scientific rules and limitations
- [`docs/evidence-engine/design-notes.md`](docs/evidence-engine/design-notes.md) - evidence-engine design notes
- [`docs/product/experience-structure.md`](docs/product/experience-structure.md) - product experience structure
- [`app/README.md`](app/README.md) - frontend setup and structure
- [`backend/README.md`](backend/README.md) - backend notes

## License

This project is distributed under the Apache License 2.0. See
[`LICENSE`](LICENSE).
