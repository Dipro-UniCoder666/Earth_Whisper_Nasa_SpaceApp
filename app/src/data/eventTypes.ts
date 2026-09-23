/**
 * Earth Whisper — Event data model
 *
 * This file defines the shape of an "Earth Event" investigation.
 * It intentionally allows most evidence fields to be absent (`undefined`)
 * because, per Earth Whisper's scientific principle, we do not fabricate
 * evidence that has not actually been collected or measured.
 *
 * Populated only in Prompt 2+ as real evidence pipelines are connected.
 */

export type EventHypothesisType =
  | 'landslide'
  | 'flood'
  | 'vegetation-disturbance'
  | 'wildfire'
  | 'human-disturbance'
  | 'subsidence'
  | 'seismic-deformation'
  | 'undetermined'

export interface GeoLocation {
  latitude: number
  longitude: number
  label?: string
}

export interface NisarObservation {
  /** ISO date string of the acquisition, if known. */
  date?: string
  /** Mean coherence value for the region of interest, 0–1. */
  coherence?: number
  /** Free-text note on what this observation represents. */
  note?: string
}

export interface NisarEvidence {
  observations?: NisarObservation[]
  coherenceBefore?: number
  coherenceAfter?: number
  meanCoherenceChange?: number
  areaSqKm?: number
  productType?: string
}

export interface TerrainEvidence {
  elevationMeters?: number
  slopeDegrees?: number
  source?: string
}

export interface WeatherEvidence {
  precipitationEvidence?: string
  source?: string
}

export interface OpticalEvidence {
  summary?: string
  source?: string
}

export interface FireEvidence {
  detected?: boolean
  source?: string
}

export interface WaterEvidence {
  summary?: string
  source?: string
}

export interface EvidenceBundle {
  nisar?: NisarEvidence
  terrain?: TerrainEvidence
  weather?: WeatherEvidence
  optical?: OpticalEvidence
  fire?: FireEvidence
  water?: WaterEvidence
}

export interface Hypothesis {
  type: EventHypothesisType
  /** Human-readable label for display. */
  label: string
  /** Whether current evidence is sufficient to assess this hypothesis at all. */
  status: 'not-yet-assessed' | 'consistent' | 'inconsistent' | 'insufficient-evidence'
}

export interface Uncertainty {
  known: string[]
  uncertain: string[]
  cannotConclude: string[]
}

export interface SourceReference {
  label: string
  url?: string
}

export interface DemoEvent {
  id: string
  title: string
  status: 'prototype-anomaly' | 'under-investigation' | 'case-file-complete'
  location: GeoLocation
  area?: {
    valueSqKm: number
    description?: string
  }
  observationDates?: string[]
  evidence: EvidenceBundle
  hypotheses: Hypothesis[]
  uncertainty: Uncertainty
  sources: SourceReference[]
}
