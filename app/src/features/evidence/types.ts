/**
 * Earth Whisper — Evidence Engine types
 *
 * Models the "Earth Event Fingerprint": a structured collection of
 * independent evidence ("clues") gathered around a NISAR-detected
 * candidate anomaly. This layer NEVER decides a cause — it only records
 * what was observed, where it came from, and how confident/limited that
 * observation is. Candidate-cause comparison is Prompt 4.
 *
 * Every clue is one of three availability states:
 * - 'measured'        real data, actually computed/retrieved
 * - 'demonstration'   realistic placeholder standing in for a data source
 *                      not yet connected, clearly labeled as such
 * - 'unavailable'      the source was checked (or would be checked) but
 *                      produced nothing usable — an honest negative/absence,
 *                      never presented as "zero" or "none occurred"
 */

export type EvidenceAvailability = 'measured' | 'demonstration' | 'unavailable'

export type ClueId = 'radar' | 'terrain' | 'weather' | 'optical' | 'fire' | 'water'

export interface ClueSource {
  label: string
  url?: string
}

/** Shared shape every clue card renders, regardless of evidence type. */
export interface ClueBase {
  id: ClueId
  order: number
  title: string
  availability: EvidenceAvailability
  source: ClueSource
  /** ISO date the underlying observation/measurement corresponds to, if known. */
  observedAt?: string
  /** One-line statement of what was actually observed. */
  summary: string
  /** Explicit caveats — what this evidence does NOT tell us. */
  limitations: string[]
}

// ---------------------------------------------------------------------------
// Clue 01 — Radar (NISAR)
// ---------------------------------------------------------------------------

export interface RadarClue extends ClueBase {
  id: 'radar'
  coherenceBefore?: number
  coherenceAfter?: number
  meanCoherenceChange?: number
  areaSqKm?: number
  beforeProductId?: string
  afterProductId?: string
}

// ---------------------------------------------------------------------------
// Clue 02 — Terrain / DEM
// ---------------------------------------------------------------------------

export interface TerrainClue extends ClueBase {
  id: 'terrain'
  elevationMeters?: number
  slopeDegrees?: number
  aspectDegrees?: number
  aspectDirection?: string
  terrainClass?: 'flat' | 'gentle' | 'moderate' | 'steep' | 'very-steep'
}

// ---------------------------------------------------------------------------
// Clue 03 — Weather / Rainfall
// ---------------------------------------------------------------------------

export interface RainfallWindow {
  label: '24h' | '3d' | '7d' | '14d'
  millimeters?: number
}

export interface WeatherClue extends ClueBase {
  id: 'weather'
  windows: RainfallWindow[]
  /** Deviation from the local historical baseline for the same period, in mm, if available. */
  anomalyMillimeters?: number
  baselineDescription?: string
}

// ---------------------------------------------------------------------------
// Clue 04 — Optical imagery
// ---------------------------------------------------------------------------

export interface OpticalClue extends ClueBase {
  id: 'optical'
  beforeImageDate?: string
  afterImageDate?: string
  beforeImageUrl?: string
  afterImageUrl?: string
  vegetationChangeNote?: string
  waterChangeNote?: string
  surfaceChangeNote?: string
}

// ---------------------------------------------------------------------------
// Clue 05 — Fire (FIRMS)
// ---------------------------------------------------------------------------

export interface FireClue extends ClueBase {
  id: 'fire'
  detectionsWithinCandidate: number
  detectionsNearby: number
  searchRadiusKm?: number
  windowDescription?: string
}

// ---------------------------------------------------------------------------
// Clue 06 — Water / geographic context
// ---------------------------------------------------------------------------

export interface WaterClue extends ClueBase {
  id: 'water'
  distanceToNearestWaterKm?: number
  nearestWaterFeature?: string
  inFloodplain?: boolean | 'unknown'
  elevationAboveNearestWaterMeters?: number
}

export type Clue = RadarClue | TerrainClue | WeatherClue | OpticalClue | FireClue | WaterClue

// ---------------------------------------------------------------------------
// Earth Event Fingerprint
// ---------------------------------------------------------------------------

export interface FingerprintLocation {
  latitude: number
  longitude: number
  label?: string
  areaSqKm?: number
}

export interface TemporalFeatures {
  /** ISO date the anomaly's "before" observation window starts. */
  beforeWindowStart?: string
  beforeWindowEnd?: string
  afterWindowStart?: string
  afterWindowEnd?: string
}

export interface SpatialFeatures {
  areaSqKm?: number
  /** Rough shape descriptor from the source polygon, if known. */
  shapeDescription?: string
}

export interface ProvenanceEntry {
  clueId: ClueId
  source: ClueSource
  availability: EvidenceAvailability
}

export interface FingerprintUncertainty {
  known: string[]
  uncertain: string[]
  cannotConclude: string[]
}

export interface EarthEventFingerprint {
  candidateId: string
  location: FingerprintLocation
  clues: Clue[]
  temporal: TemporalFeatures
  spatial: SpatialFeatures
  provenance: ProvenanceEntry[]
  uncertainty: FingerprintUncertainty
  /** ISO timestamp this fingerprint was assembled — not a scientific measurement, just bookkeeping. */
  compiledAt: string
}
