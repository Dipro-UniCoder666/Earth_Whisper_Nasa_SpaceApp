# Earth Whisper — Evidence Engine

**Status: evidence collection implemented (Prompt 3). Candidate-cause
comparison not yet implemented.** This document describes what exists
today and what remains, so implementation of the comparison layer in a
future prompt has a clear starting point.

## Purpose

Given a NISAR-detected anomaly, gather the *minimum useful* set of
independent evidence needed to eventually distinguish between candidate
explanations — not the maximum possible number of datasets. The engine
collects and records evidence; it does not yet interpret it.

## Implementation (as of Prompt 3)

Location: `app/src/features/evidence/`

- `types.ts` — the `EarthEventFingerprint`, `Clue` (discriminated union of
  six clue types), `EvidenceAvailability` ('measured' | 'demonstration' |
  'unavailable'), and `FingerprintUncertainty` types.
- `services/radarService.ts` — **measured.** Reads the team's actual
  coherence comparison from `AquaByte_NISAR` via
  `features/investigation/services/nisarService.ts`.
- `services/terrainService.ts` — demonstration placeholder (NASADEM/SRTM
  not yet connected).
- `services/weatherService.ts` — demonstration placeholder (GPM/IMERG not
  yet connected).
- `services/opticalService.ts` — **honestly unavailable.** Unlike the
  other placeholders, no plausible-looking image pair is fabricated;
  inventing "visual" evidence was judged a materially different kind of
  fabrication than a placeholder number.
- `services/fireService.ts` — demonstration placeholder (FIRMS not yet
  connected). Absence of a detection is always worded as "no
  corresponding fire signal detected," never "no fire occurred."
- `services/waterService.ts` — demonstration placeholder (hydrography
  dataset not yet connected).
- `services/fingerprintService.ts` — `buildEarthEventFingerprint()` calls
  all six services in parallel and assembles the fingerprint, including
  provenance and an uncertainty summary. It does **not** compare clues
  against each other or infer a cause.

UI: `components/EvidenceBoard.tsx` renders one card per clue via
`ClueCard.tsx` + per-type detail components (`RadarClueDetail.tsx`, etc.),
each showing an `AvailabilityBadge`, source, date, and limitations.
`UncertaintyPanel.tsx` renders known / uncertain / cannot-conclude. Both
are used on `app/src/pages/CaseInvestigationPage.tsx`
(`/investigate/case/:candidateId`).

## Candidate-cause analysis flow (not yet implemented)

```
Observed deformation / coherence change
        ↓
 Possible causes: landslide, flood, vegetation disturbance,
 wildfire, human disturbance, subsidence, seismic deformation, undetermined
        ↓
 For each hypothesis: is available evidence consistent, inconsistent,
 or insufficient?
        ↓
 Evidence-supported interpretation + explicit uncertainty
```

This comparison layer would consume `EarthEventFingerprint.clues` and
produce something matching the existing `Hypothesis[]` type in
`app/src/data/eventTypes.ts`, so the case-file UI can render it without a
data-shape migration.

## Non-goals

- Do not integrate every possible NASA dataset. NISAR + precipitation +
  terrain + fire + water is the current set; expand only if a specific
  case needs more.
- Do not build a trained ML classifier before a simpler statistical/
  feature-based anomaly detector has been validated on real cases.
- Do not let the comparison layer output a single confident label — it
  must represent multiple hypotheses with explicit consistency/
  inconsistency/insufficient-evidence status, per
  `docs/science/scientific-principles.md`.
