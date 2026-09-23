# Earth Whisper — Frontend

React + TypeScript + Vite application for Earth Whisper, AquaByte's NASA
Space Apps Challenge 2026 project.

## Getting started

```bash
npm install
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`).

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Start the Vite dev server with hot module reload |
| `npm run build` | Type-check (`tsc -b`) then build for production into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run oxlint |

## Routes

| Path | Page | Purpose |
|---|---|---|
| `/` | `src/pages/LandingPage.tsx` | Single-hero landing page |
| `/investigate` | `src/pages/InvestigationPage.tsx` | Investigation start — location search |
| `/investigate/map` | `src/pages/InvestigationMapPage.tsx` | Leaflet map, NISAR observation timeline, candidate panel |
| `/investigate/case/:candidateId` | `src/pages/CaseInvestigationPage.tsx` | Evidence board — Earth Event Fingerprint |

## Structure

```
src/
├── components/
│   ├── navigation/   LandingNavbar, AppNavbar, MobileMenu
│   ├── branding/     EarthWhisperLogo, AquaByteMark
│   ├── hero/         Hero, HeroEarth (custom SVG visual), HeroCTA
│   ├── app/          AppShell, InvestigationHeader, InvestigationWelcome
│   └── common/        Button, IconButton, GlassCard, LoadingScreen
├── pages/             LandingPage, InvestigationPage, InvestigationMapPage,
│                       CaseInvestigationPage
├── features/
│   ├── investigation/  Location search (locationService, useLocationSearch),
│   │                    NISAR observation model + demo catalog (nisarService,
│   │                    nisarDemoData), map/timeline/candidate-panel components
│   ├── evidence/        Six-clue evidence engine (radar/terrain/weather/
│   │                    optical/fire/water services), fingerprintService,
│   │                    EvidenceBoard + clue-card components
│   ├── casefile/        Types only — reserved for a future prompt
│   └── investigator/    Types only — reserved for a future prompt
├── data/              eventTypes.ts (shared types), demoEvent.ts (Candidate #1,
│                       real measured values only)
├── lib/               constants.ts, utils.ts
├── styles/            globals.css (design tokens, Tailwind v4 theme, Leaflet
│                       control restyle), animations.css
├── App.tsx, main.tsx, router.tsx
```

## Location search & maps

- **Geocoding:** `features/investigation/services/locationService.ts` wraps
  OpenStreetMap's Nominatim API behind a provider-agnostic interface
  (`searchLocations`, `validateCoordinates`, `coordinatesToResult`).
  Swapping providers later means editing only this file.
- **Map:** `features/investigation/components/InvestigationMap.tsx` uses
  Leaflet + React-Leaflet + OpenStreetMap tiles (no Google Maps), with
  custom SVG markers (no dependency on Leaflet's default marker image
  paths, which break under bundlers).

## NISAR data

`features/investigation/services/nisarService.ts` is the single interface
the rest of the app calls for NISAR observations and candidate anomalies.
It is currently backed entirely by
`features/investigation/services/nisarDemoData.ts` — a demonstration
catalog of the team's four known prototype products and the real
coherence values computed in `AquaByte_NISAR`. Every observation returned
carries `availability: 'demonstration'`, and the UI surfaces that label —
this is never presented as a live NASA query result.

## Evidence engine

`features/evidence/services/fingerprintService.ts` assembles an
`EarthEventFingerprint` by calling six independent per-source services
(`radarService`, `terrainService`, `weatherService`, `opticalService`,
`fireService`, `waterService`). Each clue is labeled `measured`,
`demonstration`, or `unavailable` — radar is measured (from
`AquaByte_NISAR`), optical is honestly `unavailable` (no fabricated
imagery), and the rest are clearly labeled demonstration placeholders. No
service compares clues against each other or determines a cause.

## Design system

Defined as CSS custom properties and a Tailwind v4 `@theme` block in
`src/styles/globals.css`:

- **Display type:** Fraunces (headlines, wordmark)
- **UI/body type:** Inter
- **Palette:** background `#F7FBFF`, navy `#073B66`, primary blue `#0B5EA8`,
  aqua `#18B7C9`, soft aqua `#DDF7FA`, sky `#EAF6FF`, earth green `#4FAF83`,
  text `#12304A`, muted `#6D8294`

## Accessibility

- Semantic landmarks (`header`, `main`, `nav`, `footer`)
- Visible focus states via `:focus-visible` on all interactive elements
- All icon-only buttons carry `aria-label`
- `prefers-reduced-motion` is respected globally (`globals.css`) and
  additionally disables looping ambient animations (`animations.css`)
- Responsive from mobile to desktop, no horizontal scroll

## Path alias

`@/*` resolves to `src/*` (configured in `vite.config.ts` and
`tsconfig.app.json`).
