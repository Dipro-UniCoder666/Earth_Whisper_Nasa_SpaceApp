# Design Document — Earth Whisper Investigation Workspace (Prompt 2)

## Overview

This document specifies the technical design for **Prompt 2: Investigation Workspace** — a transformation of the `/investigate` route from a two-step welcome→map flow into a single, cohesive, full-height investigation experience.

The core shift is **route consolidation**: `InvestigationPage` at `/investigate` becomes the complete workspace, replacing the scattered state in `InvestigationMapPage` with a clean `useInvestigationState` hook. The `/investigate/map` route becomes a redirect. All scientific backend code — services, types, demo data — is preserved without modification.

The visual language is light, premium, and scientific: `--color-bg` `#f7fbff` base, `--font-display` Fraunces for headings, `--font-sans` Inter for all data and labels. This is not a GIS dashboard. It is a structured scientific inquiry interface.

### What Changes vs. Prompt 1

Prompt 1 established the shell: design system, landing page, AppNavbar, AppShell, and the placeholder InvestigationPage. Prompt 2 **activates** the investigation workspace: real map, real NISAR data, real candidate selection, and a structured observation panel — all wired together through a unified state hook with Science Mode piped through from AppNavbar.

### Key Constraints

- **Zero changes** to any file under `src/features/investigation/services/`, `src/features/evidence/`, `src/features/investigation/types.ts`, or any preserved component listed below.
- **Zero new dependencies** — React 19, react-router-dom 7, Tailwind CSS v4, react-leaflet, lucide-react only.
- **Build gate** — `tsc -b && vite build` and `npx oxlint src/` must exit zero.

---

## Repository Audit Summary

### Fully Built — Preserve, Reuse, May Restyle

| File | Purpose | Prompt 2 treatment |
|------|---------|-------------------|
| `src/features/investigation/types.ts` | All investigation types | **PRESERVE** — no changes |
| `src/features/investigation/services/nisarService.ts` | listObservations, findCandidatesNear, etc. | **PRESERVE** — no changes |
| `src/features/investigation/services/nisarDemoData.ts` | 4 observations, 1 pair, 1 candidate | **PRESERVE** — no changes |
| `src/features/investigation/services/locationService.ts` | searchLocations, validateCoordinates | **PRESERVE** — no changes |
| `src/features/investigation/hooks/useLocationSearch.ts` | Debounced 400ms search hook | **PRESERVE** — no changes |
| `src/features/investigation/components/InvestigationMap.tsx` | Leaflet map container | **PRESERVE** — no changes |
| `src/features/investigation/components/CandidatePanel.tsx` | Coherence before/after/change | **PRESERVE** — not used directly in new layout, superseded by ObservationPanel but kept |
| `src/features/investigation/components/LocationSearchBox.tsx` | Combobox search | **PRESERVE** — reused as-is |
| `src/features/investigation/components/NisarTimeline.tsx` | 4-observation timeline | **PRESERVE** — reused inside ObservationPanel |
| `src/features/investigation/components/MapLayerControl.tsx` | Layer toggles | **PRESERVE** — reused on map |
| `src/components/app/AppShell.tsx` | Layout wrapper with AppNavbar | **PRESERVE** — still used by CaseInvestigationPage |
| `src/components/app/AppNavbar.tsx` | Navbar with scienceMode button | **PRESERVE** — wired to useInvestigationState |
| `src/components/app/InvestigationWelcome.tsx` | Old welcome form | **PRESERVE** — no longer routed to, kept in codebase |
| `src/data/demoEvent.ts` | DemoEvent for candidate-001 | **PRESERVE** — read by FingerprintPreview |
| `src/data/eventTypes.ts` | Full type system | **PRESERVE** — no changes |

### Modified Files

| File | Change |
|------|--------|
| `src/pages/InvestigationPage.tsx` | Replace AppShell+InvestigationWelcome with the new unified workspace |
| `src/router.tsx` | Add redirect from `/investigate/map` → `/investigate`; keep `/investigate/case/:candidateId` |
| `src/lib/constants.ts` | Add `investigateCase` route key |

### New Files

| File | Purpose |
|------|---------|
| `src/features/investigation/hooks/useInvestigationState.ts` | Consolidated investigation state + actions |
| `src/features/investigation/components/InvestigationProgressBar.tsx` | 5-step scientific stepper |
| `src/features/investigation/components/ObservationPanel.tsx` | Right-side structured data panel |
| `src/features/investigation/components/CoherenceChangeIndicator.tsx` | Visual coherence-loss bar |
| `src/features/investigation/components/FingerprintPreview.tsx` | Preliminary Earth Event fingerprint card |
| `src/features/investigation/components/SampleEventCard.tsx` | "Explore a Sample Investigation" entry card |

---

## Route Consolidation Decision

### Decision: Option (b) — Merge into `/investigate`

The two-step flow (welcome at `/investigate` → map at `/investigate/map`) creates unnecessary friction. The welcome form is essentially a location picker, which belongs inline in the workspace itself as the empty state.

**Implementation:**
- `/investigate` — renders the new unified `InvestigationWorkspace`
- `/investigate/map` — renders `<Navigate to="/investigate" replace />` for backward compatibility
- `/investigate/case/:candidateId` — unchanged, still renders `CaseInvestigationPage`

The existing `InvestigationMapPage.tsx` is **preserved** (not deleted) — the redirect means it is simply no longer routed to. This avoids any cascading import issues.

**router.tsx after change:**

```tsx
import { Navigate } from 'react-router-dom'
// ...
{ path: `${ROUTES.investigate}/map`, element: <Navigate to={ROUTES.investigate} replace /> },
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  router.tsx                                                              │
│    / → LandingPage (AppLayout)                                          │
│    /investigate → InvestigationPage (AppShell) ← MODIFIED              │
│    /investigate/map → <Navigate to="/investigate" replace />            │
│    /investigate/case/:candidateId → CaseInvestigationPage (AppShell)   │
└─────────────────────────────────────────────────────────────────────────┘

InvestigationPage
└── AppShell                         (preserved — grid backdrop + AppNavbar)
    └── InvestigationWorkspace        (new, lives inside InvestigationPage)
        ├── InvestigationProgressBar  (new — 5-step stepper)
        ├── [empty state view]        (when no location selected)
        │   ├── LocationSearchBox     (preserved)
        │   ├── manual lat/lng inputs
        │   └── SampleEventCard      (new — loads candidate-001 directly)
        └── [active investigation view] (when location/candidate selected)
            ├── [left column — ~55%]
            │   ├── LocationSearchBox (preserved)
            │   ├── manual lat/lng inputs
            │   ├── InvestigationMap  (preserved)
            │   └── MapLayerControl   (preserved, overlaid on map)
            └── [right column — ~45%]
                └── ObservationPanel (new)
                    ├── location header
                    ├── candidate selector buttons
                    ├── NISAR observation section
                    ├── CoherenceChangeIndicator (new)
                    ├── FingerprintPreview (new)
                    ├── NisarTimeline (preserved)
                    └── "Continue Investigation" action bar

State glue: useInvestigationState (new)
Science Mode: flows from AppNavbar down via prop/context
```

### State Flow

```
AppNavbar (scienceMode toggle)
    ↓ prop passed into InvestigationPage
InvestigationWorkspace
    ↓ consumed by useInvestigationState
ObservationPanel / FingerprintPreview
    ↓ renders simple vs. detailed text
```

AppNavbar's local `scienceMode` state is **lifted** to `InvestigationPage` so it can be threaded down into `useInvestigationState`. AppNavbar receives `scienceMode` and `onScienceModeChange` as props.

> **Note on AppNavbar modification:** The audit lists AppNavbar as PRESERVE. The narrowest change is to add two optional props: `scienceMode?: boolean` and `onScienceModeChange?: (v: boolean) => void`. When these props are absent, AppNavbar uses its own internal state (backward compatible). When present, it becomes controlled — exactly what `InvestigationPage` needs. This is a **backwards-compatible additive change**, not a restructuring.

---

## File Structure (Complete)

```
app/src/
├── router.tsx                                          [MODIFIED]
├── lib/
│   └── constants.ts                                   [MODIFIED]
├── components/
│   ├── navigation/
│   │   └── AppNavbar.tsx                              [MODIFIED — additive props only]
│   └── app/
│       ├── AppShell.tsx                               [PRESERVE]
│       ├── InvestigationWelcome.tsx                   [PRESERVE — no longer routed]
│       └── InvestigationHeader.tsx                    [PRESERVE]
├── pages/
│   ├── InvestigationPage.tsx                          [MODIFIED]
│   ├── InvestigationMapPage.tsx                       [PRESERVE — no longer routed]
│   └── CaseInvestigationPage.tsx                      [PRESERVE]
└── features/
    └── investigation/
        ├── types.ts                                   [PRESERVE]
        ├── services/
        │   ├── nisarService.ts                        [PRESERVE]
        │   ├── nisarDemoData.ts                       [PRESERVE]
        │   └── locationService.ts                     [PRESERVE]
        ├── hooks/
        │   ├── useLocationSearch.ts                   [PRESERVE]
        │   └── useInvestigationState.ts               [NEW]
        └── components/
            ├── InvestigationMap.tsx                   [PRESERVE]
            ├── CandidatePanel.tsx                     [PRESERVE]
            ├── LocationSearchBox.tsx                  [PRESERVE]
            ├── NisarTimeline.tsx                      [PRESERVE]
            ├── MapLayerControl.tsx                    [PRESERVE]
            ├── InvestigationProgressBar.tsx           [NEW]
            ├── ObservationPanel.tsx                   [NEW]
            ├── CoherenceChangeIndicator.tsx           [NEW]
            ├── FingerprintPreview.tsx                 [NEW]
            └── SampleEventCard.tsx                    [NEW]
```

---

## `useInvestigationState` Hook Specification

**File:** `src/features/investigation/hooks/useInvestigationState.ts`

### State Shape

```typescript
interface InvestigationState {
  // Location
  selectedLocation: LocationSearchResult | null
  manualLat: string
  manualLng: string
  manualError: string | null

  // Candidates
  candidates: CandidateAnomaly[]
  selectedCandidateId: string | undefined

  // Observations
  observations: NisarObservation[]
  selectedObservationId: string | undefined

  // Loading / error
  loadingPhase: 'idle' | 'searching-candidates' | 'loading-observations' | 'ready'
  errorMessage: string | null

  // Science mode
  scienceMode: boolean
}
```

### Actions

```typescript
interface InvestigationActions {
  selectLocation: (result: LocationSearchResult) => void
  setManualLat: (v: string) => void
  setManualLng: (v: string) => void
  submitManualCoordinates: () => void    // validates + calls selectLocation
  selectCandidate: (id: string) => void
  selectObservation: (id: string) => void
  loadSampleInvestigation: () => void    // sets candidate-001 location directly
  setScienceMode: (v: boolean) => void
  reset: () => void
}
```

### Derived values (memoised)

```typescript
interface InvestigationDerived {
  selectedCandidate: CandidateAnomaly | undefined
  mapCenter: { lat: number; lng: number } | null
  hasActiveInvestigation: boolean        // selectedCandidateId !== undefined
  canContinue: boolean                   // selectedCandidateId !== undefined
  activeStep: 1 | 2 | 3 | 4 | 5        // drives InvestigationProgressBar
}
```

### Behavior

- Calling `selectLocation` sets `selectedLocation`, clears candidates/observations, sets `loadingPhase: 'searching-candidates'`, and fires `findCandidatesNear`. On resolution, sets `candidates` and `loadingPhase: 'ready'`.
- Calling `selectCandidate` sets `selectedCandidateId`, sets `loadingPhase: 'loading-observations'`, fires `getObservationsForCandidate`. On resolution, sets `observations` and `loadingPhase: 'ready'`.
- Calling `loadSampleInvestigation` calls `selectLocation` with `{ id: 'candidate-001', label: 'Himachal Pradesh, India', latitude: 31.1105, longitude: 77.9373 }` then auto-selects `candidate-001` after candidates load.
- `submitManualCoordinates` calls `validateCoordinates(manualLat, manualLng)`. On error, sets `manualError`. On success, calls `selectLocation(coordinatesToResult(...))`.
- All async calls use a cancellation ref pattern (identical to `InvestigationMapPage`) to discard stale responses.
- `activeStep` derivation:
  - No location → `1` (OBSERVE)
  - Location, no candidate → `2` (COMPARE)
  - Candidate selected → `3` (COLLECT CLUES)
  - (Steps 4 and 5 are reached from CaseInvestigationPage, so the workspace always tops out at 3)

### Return type

```typescript
export function useInvestigationState(initialScienceMode?: boolean): InvestigationState & InvestigationActions & InvestigationDerived
```

---

## Components and Interfaces

### `InvestigationProgressBar`

**File:** `src/features/investigation/components/InvestigationProgressBar.tsx`

**Props:**
```typescript
interface InvestigationProgressBarProps {
  activeStep: 1 | 2 | 3 | 4 | 5
}
```

**Visual design:**
- Horizontal strip, `48px` tall on desktop, `40px` on mobile
- Five labeled steps in a flex row:
  ```
  ① OBSERVE  —  ② COMPARE  —  ③ COLLECT CLUES  —  ④ INVESTIGATE  —  ⑤ UNDERSTAND
  ```
- Each step: zero-padded number (`01`, `02`…) as a small eyebrow + label text
- Active step: `--color-navy` text, `--color-aqua` underline accent (`border-b-2 border-[var(--color-aqua)]`)
- Completed step (< activeStep): `--color-primary` text, checkmark icon replacing the number
- Inactive step (> activeStep): `--color-muted` text, dimmer
- Connector between steps: `1px` horizontal line, `--color-border-subtle`, shrinks on mobile
- Steps 4 and 5 are always dimmed in Prompt 2 (workspace only covers steps 1–3)

**Mobile behavior:**
- Below `md` (768px): only the active step label and its number are shown in full; others collapse to dots or abbreviated numbers
- `aria-label="Investigation progress"` on the `<nav>` container
- Each step is a `<span>` with `aria-current={step === activeStep ? 'step' : undefined}`

**Styling:**
```
bg-white border-b border-[var(--color-sky)] px-6 py-2
```
Sits between `AppNavbar` (sticky) and the workspace content area.

---

### `ObservationPanel`

**File:** `src/features/investigation/components/ObservationPanel.tsx`

**Props:**
```typescript
interface ObservationPanelProps {
  candidate: CandidateAnomaly
  observations: NisarObservation[]
  selectedObservationId: string | undefined
  onSelectObservation: (id: string) => void
  onContinue: (candidateId: string) => void
  scienceMode: boolean
}
```

**Sections (rendered top to bottom, scroll within panel):**

#### 1. Location header
- Eyebrow: `"CANDIDATE ANOMALY"` — aqua label pill
- Region label: `candidate.regionLabel` — `font-display` medium
- Coordinates: formatted with `formatCoordinate()`
- Area: `~{candidate.areaSqKm.toFixed(2)} km²`

#### 2. NISAR observation section — "What did NISAR see?"
- Loads `pair-025-026` via `getObservationPair(candidate.observationPairId!)` (mirrors CandidatePanel pattern)
- While loading: skeleton loaders (3 shimmer bars, `animate-pulse`)
- Loaded: renders `CoherenceChangeIndicator` with before/after/change values
- Science Mode toggle text:
  - **Simple:** `"Significant radar coherence loss detected."`
  - **Science:** `"Mean coherence decreased from 0.6648 to 0.2188 across the candidate region (~41.57 km²). This is a coherence comparison, not an unwrapped-phase displacement measurement."`
- Pair note rendered as a `<blockquote>` in science mode only

#### 3. Before/After comparison — "NISAR Observation A vs B"
- Two cards side by side (or stacked on mobile):
  - **Observation A** (obs-025-055): `"Jul 12 → Jul 24, 2026"`, `"Coherence: 0.6648"`, track badge `"T025·F055"`, `"Demo data"` pill
  - **Observation B** (obs-026-055): `"Jul 24 → Aug 17, 2026"`, `"Coherence: 0.2188"`, track badge `"T026·F055"`, `"Demo data"` pill
- A visual arrow or delta connector between them indicating direction of change
- Product source line: `"NASA-ISRO NISAR (GUNW demonstration data)"`

#### 4. Earth Event Fingerprint preview
- Renders `<FingerprintPreview>` (see below)

#### 5. NISAR Timeline
- Renders `<NisarTimeline observations={observations} selectedObservationId={selectedObservationId} onSelect={onSelectObservation} />`
- Section heading: `"Observation timeline"` — small uppercase aqua label

#### 6. Continue Investigation action bar (sticky bottom of panel on desktop)
```tsx
<Button size="lg" disabled={!onContinue} onClick={() => onContinue(candidate.id)}>
  Continue Investigation →
</Button>
```
- Renders `"Continue Investigation →"` when candidate selected
- `disabled` state: greyed, `cursor-not-allowed`, no hover change, `aria-disabled="true"`
- Legal/scientific disclaimer: `"Surface change detected. Cause has not been determined."` in muted small text above button

**Panel scroll:** The panel is `overflow-y-auto` with a `max-h` tied to the viewport minus the navbar + progress bar height (`calc(100vh - 48px - 48px)`). The action bar is `sticky bottom-0 bg-white border-t border-[var(--color-sky)] px-5 py-4`.

**Accessibility:**
- `role="region"` with `aria-labelledby` pointing to the location header
- Loading states announced via `aria-live="polite"` region
- All buttons have visible focus rings

---

### `CoherenceChangeIndicator`

**File:** `src/features/investigation/components/CoherenceChangeIndicator.tsx`

**Props:**
```typescript
interface CoherenceChangeIndicatorProps {
  coherenceBefore: number     // 0.6648
  coherenceAfter: number      // 0.2188
  meanCoherenceChange: number // -0.446
}
```

**Visual design:**

A horizontal measurement display with three tiers:

**Tier 1 — Three metric boxes (side by side):**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   BEFORE    │  │    AFTER    │  │   CHANGE    │
│   0.6648    │  │   0.2188    │  │   −0.4460   │
│  coherence  │  │  coherence  │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```
- Before/After: `--color-navy` value text
- Change: `#B3432B` (existing color already used in CandidatePanel for negative change)
- Values use `font-display` at `text-2xl` weight 500

**Tier 2 — Gradient scale bar:**
```
High coherence ←────────────────────────────→ Low coherence
1.0           0.8    0.6648  0.2188 0.0
                       ▲        ▲
                    Before    After
```
- Segmented gradient: `from-[var(--color-earth-green)] via-[var(--color-aqua)] to-[#DC2626]`
- Width: full panel width, `height: 8px`, `border-radius: 4px`
- Two triangle markers positioned at `(1 - coherenceBefore) * 100%` and `(1 - coherenceAfter) * 100%`
- Markers: small `▼` SVG triangles, 8px wide, in `--color-navy`
- Change region highlighted with a semi-transparent overlay between the two markers

**Tier 3 — Label:**
- Text: `"Substantial coherence loss"` (not "landslide", not a percentage, not "disaster")
- Derivation rule: `meanCoherenceChange <= -0.3` → `"Substantial coherence loss"`, `-0.3 < change <= -0.1` → `"Moderate coherence loss"`, else `"Minor coherence change"`. These labels are descriptive magnitude labels only.
- `text-xs text-[var(--color-muted)]` weight, with an `aria-label` that includes the numeric value for screen readers

**Accessibility:**
- `role="img"` on the scale bar container
- `aria-label={`Coherence change scale: before ${coherenceBefore.toFixed(4)}, after ${coherenceAfter.toFixed(4)}, change ${meanCoherenceChange.toFixed(4)}`}`
- Numeric values also present in the metric boxes (not color-only)

---

### `FingerprintPreview`

**File:** `src/features/investigation/components/FingerprintPreview.tsx`

**Props:**
```typescript
interface FingerprintPreviewProps {
  candidate: CandidateAnomaly
  scienceMode: boolean
}
```

**Data source:** Imports `demoEvent` from `src/data/demoEvent.ts` directly (no service call needed — it is static). Only uses `demoEvent.uncertainty` and `demoEvent.evidence.nisar`.

**Visual design — card structure:**

```
┌──────────────────────────────────────────────────────┐
│ EARTH EVENT FINGERPRINT                [PRELIMINARY] │
├──────────────────────────────────────────────────────┤
│ ● SURFACE CHANGE DETECTED                            │
│                                                      │
│ Location    31.1105° N, 77.9373° E                  │
│ Region      Himachal Pradesh, India                  │
│ Area        ~41.57 km²                               │
│ Period      Jul 12 → Aug 17, 2026                   │
│ Radar       0.6648 → 0.2188 (Δ −0.4460)            │
│ Source      NASA-ISRO NISAR (GUNW demonstration)     │
│                                                      │
├──────────────────────────────────────────────────────┤
│ EVIDENCE STATUS                                      │
│ ■ RADAR     ✓ Collected                              │
│ □ TERRAIN   Not yet collected                        │
│ □ WEATHER   Not yet collected                        │
│ □ OPTICAL   Not yet collected                        │
│ □ WATER     Not yet collected                        │
├──────────────────────────────────────────────────────┤
│ WHAT WE KNOW                                         │
│ • A substantial coherence loss (~-0.446) was        │
│   measured across the candidate polygon.             │
│ • The candidate area is approximately 41.57 km².    │
│                                                      │
│ CANNOT YET CONCLUDE                                  │
│ • This anomaly cannot yet be attributed to any      │
│   specific event type.                               │
└──────────────────────────────────────────────────────┘
```

**Heading:** `"Earth Event Fingerprint"` — `font-display text-lg` in `--color-navy`
**Preliminary badge:** `"PRELIMINARY"` — rounded-full `bg-[var(--color-aqua-soft)] text-[var(--color-aqua)]` label

**Status indicator:** Green dot (`bg-[var(--color-earth-green)]`) + `"SURFACE CHANGE DETECTED"` — never says "landslide detected" or "disaster"

**Measurement section:** All values pulled from `demoEvent.evidence.nisar` and `candidate.*`. Period dates calculated from obs-025-055 startDate to obs-026-055 endDate (hardcoded for Prompt 2 since the fingerprint is specifically for candidate-001).

**Evidence slots:**
- RADAR: shown as `"✓ Collected"` with `--color-earth-green` text
- TERRAIN / WEATHER / OPTICAL / WATER: `"Not yet collected"` in `--color-muted`, greyed border, `opacity-60`
- Science mode only: adds a note `"Prompt 3 will populate terrain, weather, optical, and water evidence."` in muted italic

**Uncertainty section:**
- In simple mode: shows only the `known` statements from `demoEvent.uncertainty`
- In science mode: shows `known`, `uncertain`, and `cannotConclude` all labelled separately

**Accessibility:**
- `<section aria-labelledby="fingerprint-heading">`
- The `[PRELIMINARY]` badge has `aria-label="Preliminary data — investigation not complete"`
- Evidence slots rendered as a `<dl>` list

---

### `SampleEventCard`

**File:** `src/features/investigation/components/SampleEventCard.tsx`

**Props:**
```typescript
interface SampleEventCardProps {
  onLoad: () => void   // calls useInvestigationState.loadSampleInvestigation
}
```

**Visual design:**

```
┌──────────────────────────────────────────────────────┐
│ [Satellite icon]  Explore a Sample Investigation     │
│                                                      │
│ We've prepared a prototype NISAR anomaly in         │
│ Himachal Pradesh, India. Jump straight in to see    │
│ what the investigation workspace looks like with    │
│ real data loaded.                                   │
│                                                     │
│ 31.1105° N, 77.9373° E · Candidate #1              │
│                                                     │
│              [Load Sample Investigation →]           │
└──────────────────────────────────────────────────────┘
```

- Card background: `bg-[var(--color-aqua-soft)] border border-[var(--color-aqua)]/30`
- Satellite icon: `Satellite` from lucide-react, `--color-aqua`
- Button: `bg-[var(--color-navy)] text-white` standard Button component
- The card must not claim the anomaly is a confirmed event

**Accessibility:**
- Button has a descriptive label: `"Load sample investigation: prototype NISAR anomaly, Himachal Pradesh"`

---

## Page Layout Specification

### `InvestigationPage` (modified)

**File:** `src/pages/InvestigationPage.tsx`

```tsx
export function InvestigationPage() {
  const [scienceMode, setScienceMode] = useState(false)
  return (
    <AppShell scienceMode={scienceMode} onScienceModeChange={setScienceMode}>
      <InvestigationProgressBar activeStep={...} />
      <InvestigationWorkspace scienceMode={scienceMode} />
    </AppShell>
  )
}
```

> **AppShell change:** AppShell currently passes no props to AppNavbar beyond rendering it. The narrowest modification is to thread `scienceMode` / `onScienceModeChange` through AppShell's props to AppNavbar. AppShell gets two optional new props; AppNavbar gets two optional new props. Both remain backward compatible.

### Desktop Layout (≥ 1024px)

```
┌────────────────────────────────────────────────────────┐
│  AppNavbar (sticky, 64px)                              │
├────────────────────────────────────────────────────────┤
│  InvestigationProgressBar (48px)                       │
├──────────────────────────────────┬─────────────────────┤
│  LEFT COLUMN (~55%)              │  RIGHT COLUMN (~45%) │
│                                  │                      │
│  Location search bar             │  ObservationPanel    │
│  ─────────────────────────────   │  (scrollable)        │
│  InvestigationMap                │                      │
│  (height: calc(100vh - 160px),   │  [empty state or     │
│   min-height: 420px)             │   candidate data]    │
│                                  │                      │
│  [MapLayerControl overlay]       │  [sticky action bar] │
└──────────────────────────────────┴─────────────────────┘
```

Grid: `grid lg:grid-cols-[55fr_45fr]`, `gap-0` (no gap — columns touch), outer padding `px-4 lg:px-6`.

The map column has `overflow-hidden`. The observation panel column has `overflow-y-auto` with `height: calc(100vh - 48px - 64px)` (viewport minus progress bar minus navbar).

### Tablet Layout (768px – 1023px)

Same two-column grid but at `md:grid-cols-[1.2fr_1fr]` — slightly narrower panel. Map height reduced to `360px` fixed. Panel scrolls independently.

### Mobile Layout (< 768px)

Stacked single column:
1. Location search bar + coordinate inputs
2. (If no location) SampleEventCard
3. InvestigationMap (fixed `300px` height)
4. (If location selected) ObservationPanel sections expand below the map in document flow

`InvestigationProgressBar` collapses to show only the active step number and name, with total step count `"Step 1 of 5"`.

The "Continue Investigation" button is full-width, always visible at the bottom of the ObservationPanel content (not sticky on mobile to avoid overlapping the map).

---

## Empty State Design

**Shown when:** `selectedLocation === null`

**Layout:** Centered column, `max-w-2xl mx-auto`, `pt-12 pb-16`

**Content:**
```
"Where should we look?"                  (font-display text-3xl)
"Choose a location on Earth to begin     (text-muted text-lg)
 observing surface changes."

[LocationSearchBox]

  — or —

Latitude [___________]  Longitude [___________]  [Go]

[SampleEventCard]
```

**Map behavior in empty state:** Map is rendered at zoom 2, center `[20, 0]` (world view). It remains interactive — clicking anywhere calls `selectLocation`.

**Transition to active state:** When `selectedLocation` is set, the empty-state copy fades out and the split-view layout animates in with `ew-anim-rise`.

---

## Loading and Error States

### Candidate search loading (`loadingPhase: 'searching-candidates'`)

In the right panel (ObservationPanel or its placeholder):
```
┌──────────────────────────────┐
│  [spinner]  Checking NISAR   │
│             coverage…         │
└──────────────────────────────┘
```
- `Loader2` icon from lucide-react, `animate-spin`, `--color-primary`
- Text: `"Checking NISAR coverage…"` — `text-sm text-[var(--color-muted)]`

### Observation pair loading (inside ObservationPanel)

Skeleton shimmer pattern in place of CoherenceChangeIndicator:
```tsx
<div className="animate-pulse space-y-3">
  <div className="h-12 rounded-xl bg-[var(--color-sky)]" />
  <div className="h-8 rounded-xl bg-[var(--color-sky)] w-3/4" />
</div>
```

### No candidates found

```
┌──────────────────────────────────────────────────────┐
│  No NISAR observations available for this location   │
│  in our demonstration catalog.                       │
│                                                      │
│  Try the prototype candidate near:                   │
│  31.1105° N, 77.9373° E                             │
│                                                      │
│  [Load Sample Investigation →]                       │
└──────────────────────────────────────────────────────┘
```

`SampleEventCard` is re-surfaced here as the escape hatch.

### Error state (network / service failure)

```
┌──────────────────────────────────────────────────────┐
│  [AlertCircle]  Could not load observation data.     │
│  Check your connection and try again.                │
└──────────────────────────────────────────────────────┘
```
- `AlertCircle` icon, `#B3432B` color (matches existing error color in codebase)
- `errorMessage` string from `useInvestigationState`
- Retry is implicit: selecting a new location resets state

---

## Science Mode Specification

### Wiring

1. `AppNavbar` gains two optional props:
   ```typescript
   scienceMode?: boolean
   onScienceModeChange?: (v: boolean) => void
   ```
   When these are provided, the `FlaskConical` button becomes controlled. When absent, it falls back to its existing internal `useState` (backward compatible for `CaseInvestigationPage` which uses `AppShell` without these props).

2. `AppShell` gains two optional passthrough props (same names) that it forwards to `AppNavbar`.

3. `InvestigationPage` owns the state: `const [scienceMode, setScienceMode] = useState(false)`. Passes it to `AppShell` and down to `useInvestigationState(scienceMode)`.

4. `useInvestigationState` stores `scienceMode` and exposes it. Components that need it receive it via prop from `ObservationPanel`.

### Text variants

| Location | Simple mode | Science mode |
|----------|-------------|--------------|
| ObservationPanel intro text | `"Significant radar coherence loss detected."` | `"Mean coherence decreased from 0.6648 to 0.2188 across the candidate region (~41.57 km²). This is a coherence comparison, not an unwrapped-phase displacement measurement."` |
| CoherenceChangeIndicator label | `"Substantial coherence loss"` | `"Substantial coherence loss (Δ −0.4460 mean)"` + pair note `<blockquote>` |
| FingerprintPreview uncertainty | Shows `known` statements only | Shows `known` + `uncertain` + `cannotConclude` all labelled |
| FingerprintPreview Prompt note | Hidden | `"Terrain, weather, optical, and water evidence will be populated in future updates."` |

### Visual indicator

The `FlaskConical` icon in AppNavbar:
- Science mode ON: `text-[var(--color-aqua)]`, indicator dot `bg-[var(--color-earth-green)]`
- Science mode OFF: `text-[var(--color-muted)]`, indicator dot `bg-[var(--color-sky)]`

This existing behavior is already implemented in AppNavbar — no change required to the visual indicator, only the state management source changes.

---

## Investigation Progress Bar — Step Derivation

| `activeStep` | Condition |
|---|---|
| `1` (OBSERVE) | No location selected |
| `2` (COMPARE) | Location selected, no candidate |
| `3` (COLLECT CLUES) | Candidate selected |
| `4` (INVESTIGATE) | Not reached from `/investigate` — shown dimmed |
| `5` (UNDERSTAND) | Not reached from `/investigate` — shown dimmed |

Steps 4 and 5 become active when the user proceeds to `/investigate/case/:candidateId` (Prompt 3 scope). They are rendered in the progress bar now for visual continuity, but always appear in the inactive/dimmed state.

---

## Responsive Design Specification

### Breakpoint grid

| Viewport | Grid | Map height | Panel | Progress bar |
|----------|------|-----------|-------|-------------|
| ≥ 1440px (2xl) | `grid-cols-[55fr_45fr]` | `calc(100vh - 160px)` | Scrollable, sticky action bar | Full 5 steps |
| 1024–1439px (lg/xl) | `grid-cols-[55fr_45fr]` | `calc(100vh - 160px)` | Scrollable, sticky action bar | Full 5 steps |
| 768–1023px (md) | `grid-cols-[1.2fr_1fr]` | `360px` fixed | Scrollable, sticky action bar | Full 5 steps |
| 390–767px (mobile) | Single column | `300px` fixed | Inline below map | Active step + `"Step N of 5"` |

### Touch targets

All interactive elements meet 44×44px minimum:
- LocationSearchBox input: `py-3.5` = ~54px height
- Candidate selector buttons: `px-3 py-1.5` may be too small — use `py-2` minimum
- NisarTimeline buttons: existing `mb-4 px-4 py-3` passes minimum
- Continue Investigation button: `size="lg"` Button component = ~56px height

### Overflow management

- Horizontal overflow: `overflow-x-hidden` on the workspace container root
- Map container: `overflow-hidden rounded-2xl`
- Panel: `overflow-y-auto` with `-webkit-overflow-scrolling: touch` for iOS momentum scroll

---

## Accessibility Specification

### Landmark structure

```html
<header>            ← AppNavbar (sticky, role="banner")
<nav aria-label>    ← InvestigationProgressBar progress steps  
<main id="main-content">
  <section aria-labelledby="workspace-location-heading">  ← left column
  <section aria-labelledby="observation-panel-heading">   ← ObservationPanel
    <section aria-labelledby="fingerprint-heading">       ← FingerprintPreview
```

### ARIA live regions

- `<div aria-live="polite" aria-atomic="true">` wrapping loading status text in ObservationPanel — announces "Checking NISAR coverage…" and "1 candidate anomaly found" to screen readers
- `<div aria-live="polite">` in `useInvestigationState` rendered output — announces phase transitions

### Focus management

- When `loadSampleInvestigation` fires, focus moves to the first element of ObservationPanel after data loads (implemented via `useEffect` + `ref.focus()`)
- When location is selected via search, the LocationSearchBox dropdown closes and focus returns to the input (existing behavior in `LocationSearchBox` via `onBlur` + `setFocused(false)`)
- When "Continue Investigation" is activated, `react-router-dom navigate()` fires — focus is handled by the router's scroll restoration

### Keyboard navigation

- All map interactions (InvestigationMap) are supplemental to the search/coordinate inputs — the map does not need to be keyboard-navigable for primary task completion
- Candidate selector buttons in ObservationPanel: standard button keyboard activation
- NisarTimeline: existing `aria-pressed` buttons, keyboard-accessible

### Color contrast

All text follows existing token usage:
- `--color-text` (`#12304a`) on `--color-bg` (`#f7fbff`): passes WCAG AA ✓
- `--color-muted` (`#6d8294`) on `--color-bg`: passes AA at normal text size ✓
- Coherence change value `#B3432B` on white: ratio ~4.6:1 ✓ (matches existing CandidatePanel usage)

Non-color indicators:
- Active step in progress bar: underline + weight change, not color alone
- Candidate selected state: border weight + background fill change
- Evidence collected: checkmark icon + text, not color alone

---

## Data Models

### InvestigationState

```typescript
interface InvestigationState {
  selectedLocation: LocationSearchResult | null   // from investigation/types.ts
  manualLat: string
  manualLng: string
  manualError: string | null
  candidates: CandidateAnomaly[]                  // from investigation/types.ts
  selectedCandidateId: string | undefined
  observations: NisarObservation[]                // from investigation/types.ts
  selectedObservationId: string | undefined
  loadingPhase: 'idle' | 'searching-candidates' | 'loading-observations' | 'ready'
  errorMessage: string | null
  scienceMode: boolean
}
```

### InvestigationDerived (memoised from InvestigationState)

```typescript
interface InvestigationDerived {
  selectedCandidate: CandidateAnomaly | undefined
  mapCenter: { lat: number; lng: number } | null
  hasActiveInvestigation: boolean
  canContinue: boolean
  activeStep: 1 | 2 | 3 | 4 | 5
}
```

`activeStep` is derived purely from `selectedLocation` and `selectedCandidateId`:

| `selectedLocation` | `selectedCandidateId` | `activeStep` |
|---|---|---|
| null | undefined | 1 |
| set | undefined | 2 |
| set | set | 3 |

Steps 4 and 5 are never set from within the Investigation Workspace (they are reached in CaseInvestigationPage, Prompt 3).

### Component Props Interfaces

All component interfaces are defined in their respective component files. Key prop interfaces:

```typescript
// InvestigationProgressBar
interface InvestigationProgressBarProps {
  activeStep: 1 | 2 | 3 | 4 | 5
}

// ObservationPanel
interface ObservationPanelProps {
  candidate: CandidateAnomaly
  observations: NisarObservation[]
  selectedObservationId: string | undefined
  onSelectObservation: (id: string) => void
  onContinue: (candidateId: string) => void
  scienceMode: boolean
}

// CoherenceChangeIndicator
interface CoherenceChangeIndicatorProps {
  coherenceBefore: number
  coherenceAfter: number
  meanCoherenceChange: number
}

// FingerprintPreview
interface FingerprintPreviewProps {
  candidate: CandidateAnomaly
  scienceMode: boolean
}

// SampleEventCard
interface SampleEventCardProps {
  onLoad: () => void
}
```

### AppNavbar / AppShell Additive Props (backward-compatible)

```typescript
// New optional props added to AppNavbar
interface AppNavbarProps {
  scienceMode?: boolean
  onScienceModeChange?: (v: boolean) => void
}

// New optional props added to AppShell
interface AppShellProps {
  children: ReactNode
  scienceMode?: boolean
  onScienceModeChange?: (v: boolean) => void
}
```

When `scienceMode` / `onScienceModeChange` are absent (as in all existing callers), AppNavbar uses its own internal `useState`. This is a strictly additive, non-breaking change.

---

## Error Handling

### Location search failure (Nominatim network error)

**Condition:** `searchLocations()` throws a `LocationServiceError` with `cause: 'network'`

**Response:** `useLocationSearch` (preserved hook) already handles this — the `LocationSearchBox` dropdown shows the error message. No additional handling needed in `useInvestigationState`.

**Recovery:** User edits the search query. State resets automatically on next keystroke.

### Candidate fetch failure (`findCandidatesNear` rejects)

**Condition:** The nisarService's simulated async resolves successfully in demo mode, but if a network-backed implementation throws, `useInvestigationState.selectLocation()` catches the error.

**Response:** Sets `errorMessage` to a user-readable string. Sets `loadingPhase: 'ready'`. The ObservationPanel right column renders the error state card with `AlertCircle` icon.

**Recovery:** Selecting a new location calls `reset()` on error state and retries.

### Observation pair loading failure (`getObservationPair` returns undefined)

**Condition:** `candidate.observationPairId` resolves to `undefined` from the service (or the pair ID is not found in the demo catalog).

**Response:** `ObservationPanel` renders `"No coherence comparison has been computed for this candidate yet."` — this message is identical to the existing `CandidatePanel` behavior for parity.

**Recovery:** No action needed — this is expected for candidates without a pair.

### Stale request race condition

**Condition:** User selects location A, then location B before A's candidate fetch resolves.

**Response:** Each `selectLocation` call increments a `requestIdRef`. The stale response from A is discarded. State reflects B's candidates only.

**Recovery:** Automatic — by design.

### Manual coordinate validation failure

**Condition:** User enters non-numeric or out-of-range lat/lng and clicks Go.

**Response:** `validateCoordinates()` (preserved from locationService) returns an error string. `useInvestigationState.manualError` is set. Error displays inline below the coordinate inputs with `AlertCircle` icon.

**Recovery:** User corrects the inputs. Error clears on next successful `submitManualCoordinates()`.

---

## Testing Strategy

### Unit Testing Approach

Test `useInvestigationState` in isolation via React Testing Library's `renderHook`:

- Initial state: `loadingPhase === 'idle'`, `selectedLocation === null`, `activeStep === 1`
- `selectLocation()`: transitions `loadingPhase` to `'searching-candidates'` then `'ready'`
- `selectCandidate()`: transitions `loadingPhase` to `'loading-observations'` then `'ready'`
- `loadSampleInvestigation()`: auto-selects `candidate-001`
- `reset()`: returns all state to initial values
- Stale request: concurrent calls to `selectLocation` — final state reflects last call only
- `activeStep` derivation: covers all three transition cases

### Property-Based Testing Approach

**Property Test Library:** fast-check

Property tests for `CoherenceChangeIndicator`:

```typescript
// Property 1: marker position is always within [0%, 100%]
fc.property(
  fc.float({ min: 0, max: 1 }),
  fc.float({ min: 0, max: 1 }),
  (before, after) => {
    const beforePct = (1 - before) * 100
    const afterPct = (1 - after) * 100
    return beforePct >= 0 && beforePct <= 100 && afterPct >= 0 && afterPct <= 100
  }
)

// Property 2: label is always one of the three defined magnitude strings
fc.property(
  fc.float({ min: -1, max: 0 }),
  (change) => {
    const label = getCoherenceLabel(change)
    return ['Substantial coherence loss', 'Moderate coherence loss', 'Minor coherence change'].includes(label)
  }
)
```

Property tests for `useInvestigationState.activeStep`:
```typescript
// Property 3: activeStep is always 1, 2, or 3 within the workspace
fc.property(
  fc.boolean(),  // hasLocation
  fc.boolean(),  // hasCandidate
  (hasLocation, hasCandidate) => {
    const step = deriveActiveStep(hasLocation, hasCandidate && hasLocation)
    return step >= 1 && step <= 3
  }
)
```

### Integration Testing Approach

Manual smoke test checklist (defined in Build Verification Plan section above) covers the critical user journeys. Automated integration tests are out of scope for Prompt 2 but the checklist items map 1:1 to future Playwright test cases.

Key journeys to cover:
1. Empty state → search → candidate select → Continue
2. Empty state → SampleEventCard → candidate auto-selected → Continue
3. Science Mode toggle → text variants change
4. `/investigate/map` redirect → lands on `/investigate`

---

## Correctness Properties

### Property 1: Empty state invariant
**For all** states where `selectedLocation === null`, the workspace MUST render the empty-state layout (location search + SampleEventCard) and MUST NOT render `ObservationPanel`.

### Property 2: Candidate load follows location selection
**For all** calls to `selectLocation(loc)`, `loadingPhase` MUST transition through `'searching-candidates'` before settling at `'ready'` or setting `errorMessage`. It MUST NOT remain `'idle'`.

### Property 3: Observation panel gated on candidate selection
**For all** states where `selectedCandidateId === undefined`, `ObservationPanel`, `CoherenceChangeIndicator`, and `FingerprintPreview` MUST NOT be rendered.

### Property 4: Continue button enablement
**For all** states, the Continue Investigation button MUST have `aria-disabled="true"` and MUST NOT trigger navigation when `selectedCandidateId === undefined`. When `selectedCandidateId !== undefined`, the button MUST be enabled and navigate to `/investigate/case/{candidateId}`.

### Property 5: Science mode text consistency
**For all** states where `scienceMode === true`, `ObservationPanel` and `FingerprintPreview` MUST simultaneously display science-mode text variants. **For all** states where `scienceMode === false`, both MUST display simple-mode variants. A mixed state (one simple, one science) MUST NOT occur.

### Property 6: Demo data scientific honesty
**For all** rendered states, `FingerprintPreview` MUST display `"SURFACE CHANGE DETECTED"` as the status — never a cause label such as "landslide", "flood", or "earthquake". The `cannotConclude` statements from `demoEvent.uncertainty` MUST be rendered as disclaimers, not conclusions.

### Property 7: Stale response rejection
**For all** sequences where `selectLocation` is called twice before the first resolves, the final `candidates` array MUST reflect only the second call's result. No candidates from the first call MUST appear in state.

### Property 8: Progress bar step monotonicity
**For all** state transitions within a session, `activeStep` MUST satisfy: `1` when no location, `>= 2` when location set, `>= 3` when candidate selected. `activeStep` MUST NOT decrease without an explicit `reset()` call.

### Property 9: Route redirect correctness
**For all** navigations to `/investigate/map` (with or without query parameters), the rendered route MUST be `/investigate`. The `/map` path segment MUST NOT appear in the final URL.

### Property 10: No hardcoded scientific calculations in components
**For all** numeric values rendered (coherence values, area, coordinates), the value MUST be sourced from `candidate.*`, `pair.*`, or `demoEvent.*` — not from inline numeric literals computed within component render logic. Threshold comparisons in `CoherenceChangeIndicator` for magnitude labels (`<= -0.3`) are presentational and permitted.


---

## Build Verification Plan

### TypeScript compilation

```bash
cd app && tsc -b
```

Expected: zero errors.

Critical type boundaries to verify:
- `AppShell` new optional props (`scienceMode?: boolean`, `onScienceModeChange?: (v: boolean) => void`) — existing callers pass neither → no breakage
- `AppNavbar` new optional props — same pattern
- `useInvestigationState` return type — union of `InvestigationState & InvestigationActions & InvestigationDerived` must satisfy all consumer prop types
- `FingerprintPreview` importing `demoEvent` — confirm `demoEvent.evidence.nisar` fields match what is rendered (no undefined access on required display fields)
- `Navigate` import from `react-router-dom` in router.tsx

### Vite build

```bash
cd app && vite build
```

Expected: zero errors, no warnings about unresolved imports.

Watch for:
- `leaflet/dist/leaflet.css` import in `InvestigationMap.tsx` — already working, must not be broken
- `@/` alias resolution for all new files
- Tree-shaking: `InvestigationWelcome` and `InvestigationMapPage` are no longer actively routed but remain importable — no unused import warnings from oxlint if they remain in router.tsx as preserved imports

### OXLint

```bash
cd app && npx oxlint src/
```

Expected: zero errors.

Rules to satisfy:
- No `any` types in new hooks or components
- No unused variables (careful with `_latitude`, `_longitude` pattern already used in nisarService)
- `aria-*` attribute correctness on new components
- No missing `key` props in map renders

### Smoke test checklist (manual)

| Step | Expected |
|------|---------|
| Navigate to `/investigate` | Empty state shown, world map, SampleEventCard visible |
| Navigate to `/investigate/map` | Redirects to `/investigate` |
| Click "Load Sample Investigation" | Map flies to Himachal Pradesh, ObservationPanel appears |
| Click candidate on map | Candidate selected, CoherenceChangeIndicator shows, Continue enabled |
| Click "Continue Investigation" | Navigates to `/investigate/case/candidate-001` |
| Toggle Science Mode in navbar | ObservationPanel and FingerprintPreview text updates |
| Resize to 390px | Stacked layout, map 300px, progress bar shows "Step N of 5" |
| Type "Himachal Pradesh" in search | Nominatim results appear, select → map flies to location |
| Enter `31.1105` / `77.9373` manually + Go | Same result as search selection |
| Navigate back to `/` | LandingPage renders, no investigation state leak |

---

## Dependencies

No new packages. All functionality is implemented with existing installed libraries:

| Library | Usage in Prompt 2 |
|---------|-----------------|
| `react` 19 | `useState`, `useEffect`, `useRef`, `useMemo`, `useCallback` |
| `react-router-dom` 7 | `useNavigate`, `Navigate` (redirect), `useLocation` |
| `react-leaflet` 5 | `InvestigationMap` — preserved, no new usage |
| `leaflet` 1.9 | Same |
| `lucide-react` 1.47 | `Satellite`, `Loader2`, `AlertCircle`, `CheckCircle2`, `ArrowRight`, `FlaskConical` (existing) |
| `tailwindcss` 4 | All styling via Tailwind utilities + existing CSS tokens |

All design tokens (`--color-*`, `--font-*`) are already defined in `globals.css` and available to all new components.
