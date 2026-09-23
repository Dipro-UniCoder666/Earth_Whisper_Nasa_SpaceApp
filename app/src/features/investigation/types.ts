/**
 * Earth Whisper — Investigation feature types
 *
 * Covers location search state and the NISAR observation model. Fields
 * follow what NISAR L2 GUNW-style products actually carry; optional
 * fields stay `undefined` when unknown — never a guessed value.
 *
 * Source of truth for populated demo values: the team's AquaByte_NISAR
 * QGIS workspace. See features/investigation/services/nisarService.ts.
 */

export interface InvestigationQuery {
  label?: string
  latitude: number
  longitude: number
}

export type InvestigationStatus = 'idle' | 'searching' | 'observing' | 'complete'

// ---------------------------------------------------------------------------
// Location search
// ---------------------------------------------------------------------------

export interface LocationSearchResult {
  id: string
  label: string
  /** Secondary descriptive line (region, country) for disambiguation. */
  context?: string
  latitude: number
  longitude: number
  /** Approximate bounding box for zoom-to-fit, [south, west, north, east]. */
  bbox?: [number, number, number, number]
}

export type LocationSearchState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; results: LocationSearchResult[] }
  | { status: 'no-results' }
  | { status: 'error'; message: string }

// ---------------------------------------------------------------------------
// NISAR observation model
// ---------------------------------------------------------------------------

export type NisarObservationType = 'GUNW' | 'GSLC' | 'GCOV' | 'RSLC' | 'unknown'

export type NisarPolarization = 'HH' | 'HV' | 'VH' | 'VV' | 'unknown'

export type NisarProcessingLevel = 'L1' | 'L2' | 'unknown'

export interface OrbitInfo {
  track?: number
  frame?: number
  direction?: 'ascending' | 'descending'
}

export interface GeographicCoverage {
  /** Approximate bounding box, [south, west, north, east] in decimal degrees. */
  bbox?: [number, number, number, number]
  /** Human-readable description of the covered region. */
  description?: string
}

export interface NisarObservation {
  id: string
  /** Full product identifier, e.g. NISAR_L2_PR_GUNW_026_055 */
  productId: string
  observationType: NisarObservationType
  processingLevel: NisarProcessingLevel
  polarization: NisarPolarization
  /** Acquisition window start (ISO date). */
  startDate: string
  /** Acquisition window end (ISO date). */
  endDate: string
  orbit?: OrbitInfo
  coverage?: GeographicCoverage
  /** Link to the source product or documentation, if available. */
  sourceUrl?: string
  /** Whether this is real catalog data or a labeled demonstration product. */
  availability: 'demonstration' | 'live'
  /** Free-text notes — measured values, caveats, or provenance. */
  metadata?: Record<string, string | number>
}

/**
 * A pairing of two NISAR observations used for coherence/interferometric
 * comparison. We deliberately do NOT expose an "unwrapped phase
 * difference" here — combining unwrapped phase across different
 * interferometric pairs is not a valid physical displacement measurement,
 * per Earth Whisper's scientific principle.
 */
export interface NisarObservationPair {
  id: string
  beforeObservationId: string
  afterObservationId: string
  /** Mean coherence of the earlier acquisition, 0–1. */
  coherenceBefore?: number
  /** Mean coherence of the later acquisition, 0–1. */
  coherenceAfter?: number
  /** coherenceAfter - coherenceBefore, when both are known. */
  meanCoherenceChange?: number
  note?: string
}

// ---------------------------------------------------------------------------
// Candidate anomaly
// ---------------------------------------------------------------------------

export interface CandidateAnomaly {
  id: string
  title: string
  status: 'prototype-anomaly' | 'under-investigation' | 'case-file-complete'
  latitude: number
  longitude: number
  areaSqKm?: number
  /** IDs into the NISAR observation catalog relevant to this candidate. */
  observationIds: string[]
  /** ID of the observation pair used for the coherence comparison, if any. */
  observationPairId?: string
  regionLabel?: string
}
