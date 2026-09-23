# Requirements Document — Earth Whisper Investigation Workspace (Prompt 2)

## Introduction

This document specifies formal requirements for the **Investigation Workspace** feature. The workspace transforms the `/investigate` route from a two-step welcome→map flow into a single, cohesive, full-height investigation experience built around real NISAR coherence data.

The workspace provides a unified interface for selecting a location on Earth, discovering NISAR candidate anomalies near that location, and examining the coherence evidence associated with each candidate — all before proceeding to a full case investigation. All scientific backend services, types, and preserved components remain unchanged.

---

## Glossary

- **Investigation_Workspace**: The unified page rendered at `/investigate`, combining location entry, map, and observation panel.
- **useInvestigationState**: The consolidated React hook that owns all investigation state, actions, and derived values.
- **InvestigationProgressBar**: The horizontal 5-step stepper rendered between the navbar and workspace content.
- **LocationSearchBox**: The preserved Nominatim-backed combobox search component.
- **InvestigationMap**: The preserved Leaflet map component used in the workspace.
- **ObservationPanel**: The new right-column panel that displays NISAR observations for a selected candidate.
- **CoherenceChangeIndicator**: The visual component displaying before/after coherence values and a gradient scale.
- **FingerprintPreview**: The preliminary Earth Event Fingerprint card sourced from `demoEvent`.
- **SampleEventCard**: The card that loads the prototype NISAR investigation directly.
- **NisarTimeline**: The preserved component displaying all four NISAR observations.
- **MapLayerControl**: The preserved overlay control for toggling map layers.
- **CandidateAnomaly**: A spatially identified location with measurable coherence loss (from `types.ts`).
- **NisarObservation**: A single NISAR interferometric product record (from `types.ts`).
- **NisarObservationPair**: A pair of observations used for coherence comparison (from `types.ts`).
- **loadingPhase**: The current async phase of `useInvestigationState` — one of `idle`, `searching-candidates`, `loading-observations`, or `ready`.
- **activeStep**: The derived 1–5 integer indicating the current investigation step.
- **scienceMode**: A boolean flag that switches all new components between simplified and detailed scientific text.
- **demoEvent**: The static `DemoEvent` object in `src/data/demoEvent.ts` representing `candidate-001`.
- **candidate-001**: The prototype NISAR anomaly at 31.1105° N, 77.9373° E in Himachal Pradesh, India.
- **pair-025-026**: The coherence comparison pair — obs-025-055 (before) vs obs-026-055 (after).

---

## Requirements

### Requirement 1: Route Consolidation

**User Story:** As a user, I want navigating to `/investigate` or `/investigate/map` to bring me to the same workspace, so that bookmarks and shared links always work regardless of which URL was saved.

#### Acceptance Criteria

1. WHEN a user navigates to `/investigate/map`, THE Router SHALL perform a client-side redirect to `/investigate` using `replace` history semantics and SHALL NOT add a `/investigate/map` entry to the browser history.
2. WHEN a user navigates to `/investigate/map` with any query parameters, THE Router SHALL redirect to `/investigate` and SHALL discard the query parameters.
3. WHEN a user navigates to `/investigate/case/:candidateId`, THE Router SHALL render the `CaseInvestigationPage` component and SHALL NOT redirect.
4. THE Router SHALL preserve `InvestigationMapPage.tsx` in the codebase without deletion, even though it is no longer routed to.

---

### Requirement 2: Investigation State Hook

**User Story:** As a developer, I want a single consolidated hook for investigation state, so that the workspace has one authoritative source of truth and avoids duplicated async logic.

#### Acceptance Criteria

1. THE `useInvestigationState` Hook SHALL expose the following state fields on its return value: `selectedLocation`, `manualLat`, `manualLng`, `manualError`, `candidates`, `selectedCandidateId`, `observations`, `selectedObservationId`, `loadingPhase`, `errorMessage`, and `scienceMode`.
2. WHEN `selectLocation` is called with a `LocationSearchResult`, THE `useInvestigationState` Hook SHALL set `loadingPhase` to `'searching-candidates'`, call `findCandidatesNear`, and on resolution set `candidates` and `loadingPhase` to `'ready'`.
3. WHEN `selectCandidate` is called with a candidate ID, THE `useInvestigationState` Hook SHALL set `selectedCandidateId`, set `loadingPhase` to `'loading-observations'`, call `getObservationsForCandidate`, and on resolution set `observations` and `loadingPhase` to `'ready'`.
4. WHEN `reset` is called, THE `useInvestigationState` Hook SHALL return all state fields to their initial values with `selectedLocation` set to `null`, `candidates` set to an empty array, and `loadingPhase` set to `'idle'`.
5. WHEN `selectLocation` is called a second time before the first call resolves, THE `useInvestigationState` Hook SHALL discard the first response and SHALL set `candidates` exclusively from the second call's result.
6. THE `useInvestigationState` Hook SHALL expose the derived values `selectedCandidate`, `mapCenter`, `hasActiveInvestigation`, `canContinue`, and `activeStep` as memoised properties on its return value.

---

### Requirement 3: Investigation Progress Bar

**User Story:** As a user, I want a clear visual indicator of where I am in the scientific process, so that I understand that location selection and candidate review are early steps in a larger workflow.

#### Acceptance Criteria

1. THE `InvestigationProgressBar` SHALL render exactly five steps with the labels `OBSERVE`, `COMPARE`, `COLLECT CLUES`, `INVESTIGATE`, and `UNDERSTAND` in that order.
2. WHEN `activeStep` equals a step's position, THE `InvestigationProgressBar` SHALL render that step with a navy text color and an aqua bottom-border accent, and SHALL render steps at a lower position as completed with a checkmark icon.
3. WHEN `activeStep` is `1`, `2`, or `3`, THE `InvestigationProgressBar` SHALL render steps `4` (`INVESTIGATE`) and `5` (`UNDERSTAND`) in a visually dimmed inactive state.
4. WHEN the viewport width is less than `768px`, THE `InvestigationProgressBar` SHALL display only the active step label in full and SHALL collapse all other steps to abbreviated indicators.
5. THE `InvestigationProgressBar` SHALL render a `<nav>` element with `aria-label="Investigation progress"` as its container.
6. THE `InvestigationProgressBar` SHALL render each step as a `<span>` element with `aria-current="step"` on the active step and no `aria-current` attribute on all other steps.

---

### Requirement 4: Empty State

**User Story:** As a user arriving at the investigation workspace with no prior location selected, I want to see a clear entry point for starting my investigation, so that I understand how to begin.

#### Acceptance Criteria

1. WHEN `selectedLocation` is `null`, THE `Investigation_Workspace` SHALL render the empty state layout containing the `LocationSearchBox`, manual latitude and longitude inputs, and the `SampleEventCard`.
2. WHEN `selectedLocation` is `null`, THE `Investigation_Workspace` SHALL render the `InvestigationMap` at zoom level 2 centered at coordinates `[20, 0]`.
3. WHEN `selectedLocation` is `null`, THE `Investigation_Workspace` SHALL NOT render the `ObservationPanel`.
4. WHEN `selectedLocation` transitions from `null` to a set value, THE `Investigation_Workspace` SHALL replace the empty state layout with the split-view workspace layout.

---

### Requirement 5: Location Entry

**User Story:** As a user, I want to find a location by name or by entering coordinates directly, so that I can start an investigation at any point on Earth.

#### Acceptance Criteria

1. WHEN a user types a place name into the `LocationSearchBox`, THE `LocationSearchBox` SHALL query the Nominatim geocoding service with a 400ms debounce and SHALL display a dropdown of matching `LocationSearchResult` entries.
2. WHEN a user submits manual latitude and longitude values, THE `useInvestigationState` Hook SHALL call `validateCoordinates` on those values before proceeding.
3. IF `validateCoordinates` returns an error string for the supplied coordinates, THEN THE `Investigation_Workspace` SHALL display that error string as inline text below the coordinate inputs and SHALL NOT call `selectLocation`.
4. IF `validateCoordinates` returns no error for the supplied coordinates, THEN THE `useInvestigationState` Hook SHALL call `selectLocation` with a `LocationSearchResult` constructed from the validated coordinate values.
5. WHEN a manual coordinate error is displayed and the user subsequently submits valid coordinates, THE `Investigation_Workspace` SHALL clear the error message.

---

### Requirement 6: Sample Investigation

**User Story:** As a first-time user, I want to load a pre-prepared investigation with a single click, so that I can explore the workspace immediately without needing to find a location myself.

#### Acceptance Criteria

1. WHEN a user clicks the `SampleEventCard` load button, THE `useInvestigationState` Hook SHALL call `loadSampleInvestigation`, which SHALL call `selectLocation` with the coordinates `{ latitude: 31.1105, longitude: 77.9373, label: 'Himachal Pradesh, India' }`.
2. WHEN `loadSampleInvestigation` resolves candidates, THE `useInvestigationState` Hook SHALL automatically call `selectCandidate('candidate-001')` without requiring further user interaction.
3. THE `SampleEventCard` SHALL display the coordinates `31.1105° N, 77.9373° E` and the label `Candidate #1` in its body copy.
4. THE `SampleEventCard` SHALL NOT claim the anomaly is a confirmed event and SHALL describe it as a prototype NISAR anomaly.
5. THE `SampleEventCard` load button SHALL have an `aria-label` of `"Load sample investigation: prototype NISAR anomaly, Himachal Pradesh"`.

---

### Requirement 7: Map Workspace

**User Story:** As a user with an active investigation, I want a responsive map showing candidate anomaly locations, so that I can spatially understand where coherence changes were detected.

#### Acceptance Criteria

1. WHEN `candidates` contains one or more `CandidateAnomaly` entries, THE `Investigation_Workspace` SHALL render each candidate as both a `Circle` and a `Marker` on the `InvestigationMap`.
2. WHEN a user clicks a candidate `Circle` or `Marker` on the `InvestigationMap`, THE `useInvestigationState` Hook SHALL set `selectedCandidateId` to that candidate's ID.
3. THE `Investigation_Workspace` SHALL render the `MapLayerControl` as an overlay on the `InvestigationMap`.
4. WHEN `selectedLocation` is set, THE `InvestigationMap` SHALL pan and zoom to center on that location.
5. THE `InvestigationMap` component, `CandidatePanel.tsx`, `LocationSearchBox.tsx`, `NisarTimeline.tsx`, `MapLayerControl.tsx`, and all files under `src/features/investigation/services/` and `src/features/evidence/` SHALL be preserved without any source modifications.

---

### Requirement 8: Observation Panel

**User Story:** As a user who has selected a candidate anomaly, I want a structured panel of NISAR evidence, so that I can understand what the satellite detected before deciding to proceed with a full case investigation.

#### Acceptance Criteria

1. WHEN `selectedCandidateId` is set, THE `ObservationPanel` SHALL render a location header displaying `candidate.regionLabel`, formatted coordinates, and the candidate polygon area in km².
2. WHEN `loadingPhase` is `'loading-observations'`, THE `ObservationPanel` SHALL render skeleton shimmer placeholders using the `animate-pulse` CSS class in place of the `CoherenceChangeIndicator`.
3. WHEN `loadingPhase` is `'ready'` and an observation pair is loaded, THE `ObservationPanel` SHALL render the `CoherenceChangeIndicator`, `FingerprintPreview`, and `NisarTimeline` components.
4. THE `ObservationPanel` SHALL render a sticky Continue Investigation action bar at the bottom of the panel containing the Continue button and the disclaimer text `"Surface change detected. Cause has not been determined."`.
5. THE `ObservationPanel` SHALL have `role="region"` and an `aria-labelledby` attribute pointing to the location header element.
6. WHEN `loadingPhase` is `'loading-observations'` or `'searching-candidates'`, THE `ObservationPanel` SHALL contain a `<div>` with `aria-live="polite"` and `aria-atomic="true"` that announces the current loading status to assistive technologies.

---

### Requirement 9: Coherence Change Indicator

**User Story:** As a user examining NISAR data, I want a clear visual display of coherence before, after, and the change, so that I can intuitively understand the magnitude of the detected surface change without needing to interpret raw numbers alone.

#### Acceptance Criteria

1. THE `CoherenceChangeIndicator` SHALL render three metric boxes displaying `coherenceBefore`, `coherenceAfter`, and `meanCoherenceChange` values sourced from the `NisarObservationPair` — not from inline numeric literals computed within the component.
2. THE `CoherenceChangeIndicator` SHALL render a gradient scale bar spanning from high coherence (left) to low coherence (right) with two triangular position markers placed at `(1 - coherenceBefore) × 100%` and `(1 - coherenceAfter) × 100%` of the bar width.
3. WHEN `meanCoherenceChange` is less than or equal to `−0.3`, THE `CoherenceChangeIndicator` SHALL render the magnitude label `"Substantial coherence loss"`.
4. WHEN `meanCoherenceChange` is greater than `−0.3` and less than or equal to `−0.1`, THE `CoherenceChangeIndicator` SHALL render the magnitude label `"Moderate coherence loss"`.
5. WHEN `meanCoherenceChange` is greater than `−0.1`, THE `CoherenceChangeIndicator` SHALL render the magnitude label `"Minor coherence change"`.
6. THE `CoherenceChangeIndicator` SHALL render a `role="img"` element with an `aria-label` containing the numeric `coherenceBefore`, `coherenceAfter`, and `meanCoherenceChange` values expressed in words, ensuring the information is not conveyed by color alone.

---

### Requirement 10: Earth Event Fingerprint Preview

**User Story:** As a user reviewing a candidate anomaly, I want a preliminary fingerprint card that honestly represents what is and is not yet known, so that I do not form incorrect conclusions before the full investigation is complete.

#### Acceptance Criteria

1. THE `FingerprintPreview` SHALL render the status label `"SURFACE CHANGE DETECTED"` and SHALL NOT render any cause label such as `"landslide detected"`, `"flood detected"`, or `"earthquake detected"`.
2. THE `FingerprintPreview` SHALL render the evidence slot `RADAR` as `"✓ Collected"` and SHALL render the evidence slots `TERRAIN`, `WEATHER`, `OPTICAL`, and `WATER` each as `"Not yet collected"`.
3. THE `FingerprintPreview` SHALL source all displayed coherence values, area, and coordinates from `demoEvent.evidence.nisar` and `candidate.*` respectively, and SHALL NOT render fake confidence scores, probability percentages, or fabricated measurements.
4. WHEN `scienceMode` is `false`, THE `FingerprintPreview` SHALL render only the `known` statements from `demoEvent.uncertainty`.
5. WHEN `scienceMode` is `true`, THE `FingerprintPreview` SHALL render the `known`, `uncertain`, and `cannotConclude` statement arrays from `demoEvent.uncertainty`, each labelled by its category.
6. THE `FingerprintPreview` SHALL render a `<section>` element with `aria-labelledby` pointing to the fingerprint heading element, and SHALL render the evidence slots as a `<dl>` list.

---

### Requirement 11: NISAR Timeline

**User Story:** As a user in the observation panel, I want to see all available NISAR observation products for the candidate region displayed in chronological order, so that I can understand the temporal context of the coherence change.

#### Acceptance Criteria

1. WHEN `observations` is populated from `nisarDemoData`, THE `NisarTimeline` SHALL display all four observations: `obs-022-055`, `obs-025-055`, `obs-026-055`, and `obs-029-055`.
2. WHEN a user selects an observation in the `NisarTimeline`, THE `NisarTimeline` SHALL invoke the `onSelect` callback with that observation's ID.
3. THE `NisarTimeline` SHALL display each observation's track number, frame number, start date, and end date.
4. THE `NisarTimeline` SHALL render each observation as a button element with `aria-pressed` indicating whether it is the currently selected observation.

---

### Requirement 12: Science Mode

**User Story:** As a scientist or advanced user, I want to toggle a Science Mode that reveals more detailed and cautious scientific language, so that I can distinguish between simplified summaries and technically precise statements.

#### Acceptance Criteria

1. THE `AppNavbar` SHALL accept two optional props, `scienceMode: boolean` and `onScienceModeChange: (v: boolean) => void`, and WHEN these props are absent THE `AppNavbar` SHALL manage `scienceMode` using its own internal `useState` (backward-compatible behavior).
2. WHEN `scienceMode` props are provided to `AppNavbar`, THE `AppNavbar` SHALL use the prop value as the controlled state and SHALL call `onScienceModeChange` when the toggle is activated, instead of updating internal state.
3. WHEN `scienceMode` is `true`, THE `ObservationPanel` SHALL display the detailed text variant: `"Mean coherence decreased from 0.6648 to 0.2188 across the candidate region (~41.57 km²). This is a coherence comparison, not an unwrapped-phase displacement measurement."`.
4. WHEN `scienceMode` is `false`, THE `ObservationPanel` SHALL display the simplified text variant: `"Significant radar coherence loss detected."`.
5. WHEN `scienceMode` changes, THE `ObservationPanel` and THE `FingerprintPreview` SHALL both update their displayed text variant simultaneously — a state where one component displays simple mode while the other displays science mode SHALL NOT occur.

---

### Requirement 13: Loading States

**User Story:** As a user waiting for NISAR coverage data to load, I want clear visual feedback that the system is working, so that I know the application has not frozen.

#### Acceptance Criteria

1. WHILE `loadingPhase` is `'searching-candidates'`, THE `Investigation_Workspace` SHALL display a spinning `Loader2` icon and the text `"Checking NISAR coverage…"` in the right column.
2. WHILE `loadingPhase` is `'loading-observations'`, THE `ObservationPanel` SHALL render skeleton shimmer elements using the `animate-pulse` CSS class in place of `CoherenceChangeIndicator`.
3. WHILE `loadingPhase` is `'searching-candidates'` or `'loading-observations'`, THE `Investigation_Workspace` SHALL update the `aria-live="polite"` region with a human-readable loading status string.

---

### Requirement 14: Error States

**User Story:** As a user encountering a problem, I want clear, actionable error messages rather than blank states, so that I understand what went wrong and how to recover.

#### Acceptance Criteria

1. WHEN `loadingPhase` is `'ready'` and `candidates` is empty after a location search, THE `Investigation_Workspace` SHALL render the `SampleEventCard` as a recovery option alongside the message `"No NISAR observations available for this location in our demonstration catalog."`.
2. WHEN `errorMessage` is set by `useInvestigationState` following a service failure, THE `Investigation_Workspace` SHALL render an `AlertCircle` icon and the `errorMessage` string in the right panel.
3. WHEN `manualError` is set by `useInvestigationState` following invalid coordinate input, THE `Investigation_Workspace` SHALL render the `manualError` string as inline text directly below the coordinate inputs.
4. IF a candidate's `observationPairId` cannot be resolved by the service, THEN THE `ObservationPanel` SHALL render the message `"No coherence comparison has been computed for this candidate yet."` in place of the `CoherenceChangeIndicator`.

---

### Requirement 15: Continue Investigation Action

**User Story:** As a user who has reviewed a candidate anomaly, I want a clearly gated action to proceed to the full case investigation, so that I cannot accidentally navigate to a case page without selecting a candidate first.

#### Acceptance Criteria

1. WHEN `selectedCandidateId` is `undefined`, THE `ObservationPanel` SHALL render the Continue Investigation button with `aria-disabled="true"`, a `cursor-not-allowed` style, and SHALL NOT invoke navigation on click.
2. WHEN `selectedCandidateId` is set, THE `ObservationPanel` SHALL render the Continue Investigation button in an enabled state, and WHEN clicked THE button SHALL navigate to `/investigate/case/{selectedCandidateId}`.
3. THE `ObservationPanel` SHALL always render the disclaimer text `"Surface change detected. Cause has not been determined."` above the Continue Investigation button, regardless of button enabled state.

---

### Requirement 16: Scientific Language Constraints

**User Story:** As a member of the science team, I want the UI to never assert a cause or confirmed status for the anomaly, so that the application maintains scientific integrity and does not mislead users or misrepresent early-stage prototype data.

#### Acceptance Criteria

1. THE `Investigation_Workspace`, `ObservationPanel`, `CoherenceChangeIndicator`, `FingerprintPreview`, and `SampleEventCard` SHALL NOT render the strings `"landslide"`, `"disaster"`, or `"confirmed"` in any visible text node or element attribute.
2. THE `FingerprintPreview` SHALL NOT render any fabricated confidence score, probability percentage, or severity rating for the anomaly.
3. THE `CoherenceChangeIndicator` magnitude labels SHALL be limited exclusively to the three defined strings: `"Substantial coherence loss"`, `"Moderate coherence loss"`, and `"Minor coherence change"`.

---

### Requirement 17: Responsive Layout

**User Story:** As a user on a mobile device or narrow viewport, I want the workspace to reflow into a readable single-column layout, so that I can use the investigation workspace on any screen size.

#### Acceptance Criteria

1. WHEN the viewport width is `1024px` or greater, THE `Investigation_Workspace` SHALL render a two-column grid with the map column occupying approximately 55% of the width and the observation panel occupying approximately 45%.
2. WHEN the viewport width is less than `768px`, THE `Investigation_Workspace` SHALL render a single-column stacked layout with the map at a fixed height of `300px`.
3. WHEN the viewport width is `1024px` or greater, THE `InvestigationMap` SHALL have a height of `calc(100vh - 160px)` with a minimum height of `420px`.
4. THE `Investigation_Workspace` SHALL render all interactive elements — including candidate selector buttons, `NisarTimeline` observation buttons, and the Continue Investigation button — at a minimum touch target size of `44×44px`.

---

### Requirement 18: Accessibility

**User Story:** As a user who relies on assistive technology, I want the investigation workspace to be navigable with a keyboard and screen reader, so that I have equal access to the scientific investigation tools.

#### Acceptance Criteria

1. WHEN `loadingPhase` changes to `'searching-candidates'` or `'loading-observations'`, THE `Investigation_Workspace` SHALL update an `aria-live="polite"` region with a descriptive status string so that screen readers announce the state change without interrupting the user.
2. WHEN `loadSampleInvestigation` completes and the `ObservationPanel` becomes visible, THE `Investigation_Workspace` SHALL programmatically move keyboard focus to the first focusable element inside the `ObservationPanel`.
3. THE `Investigation_Workspace` SHALL implement the following landmark structure: `<header>` for AppNavbar, `<nav>` for InvestigationProgressBar, `<main>` for the workspace content, and `<section aria-labelledby>` for the left map column and the ObservationPanel.
4. ALL interactive elements in the new components SHALL be reachable and activatable via keyboard navigation in document order, and SHALL render a visible focus ring when focused.

---

### Requirement 19: Preservation of Existing Code

**User Story:** As the development team, I want all previously built scientific backend code and preserved UI components to remain unmodified, so that Prompt 2 changes can be reviewed in isolation and do not risk regressions in data integrity or existing behavior.

#### Acceptance Criteria

1. THE following files SHALL have zero source-level modifications: `src/features/investigation/services/nisarService.ts`, `src/features/investigation/services/nisarDemoData.ts`, `src/features/investigation/services/locationService.ts`, `src/features/investigation/types.ts`, `src/features/investigation/hooks/useLocationSearch.ts`, `src/features/investigation/components/InvestigationMap.tsx`, `src/features/investigation/components/CandidatePanel.tsx`, `src/features/investigation/components/LocationSearchBox.tsx`, `src/features/investigation/components/NisarTimeline.tsx`, `src/features/investigation/components/MapLayerControl.tsx`, `src/features/evidence/` (all files), `src/data/demoEvent.ts`, and `src/data/eventTypes.ts`.
2. THE `AppNavbar` component SHALL gain only two optional props — `scienceMode?: boolean` and `onScienceModeChange?: (v: boolean) => void` — and all existing call sites that pass neither prop SHALL continue to function without modification.
3. THE `AppShell` component SHALL gain only two optional passthrough props — `scienceMode?: boolean` and `onScienceModeChange?: (v: boolean) => void` — and all existing call sites SHALL continue to function without modification.

---

### Requirement 20: Build Verification

**User Story:** As a developer merging this feature, I want the build and lint pipelines to pass with zero errors, so that no type errors or lint violations are introduced into the codebase.

#### Acceptance Criteria

1. WHEN the command `tsc -b` is run from the `app/` directory, THE TypeScript Compiler SHALL exit with code `0` and zero reported diagnostics.
2. WHEN the command `vite build` is run from the `app/` directory, THE Vite Build Tool SHALL exit with code `0` and zero errors.
3. WHEN the command `npx oxlint src/` is run from the `app/` directory, THE OXLint linter SHALL exit with code `0` and zero reported violations.
4. THE new files `useInvestigationState.ts`, `InvestigationProgressBar.tsx`, `ObservationPanel.tsx`, `CoherenceChangeIndicator.tsx`, `FingerprintPreview.tsx`, and `SampleEventCard.tsx` SHALL contain no `any` type annotations, no unused variable declarations, and no missing `key` props on list renders.
