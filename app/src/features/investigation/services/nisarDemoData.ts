import type { NisarObservation, NisarObservationPair, CandidateAnomaly } from '@/features/investigation/types'

/**
 * DEMONSTRATION DATASET.
 *
 * These four products are the team's actual known prototype NISAR
 * acquisitions from the AquaByte_NISAR QGIS workspace. They are real
 * product identifiers and real acquisition windows as provided by the
 * team — but they are served here as a static, local demonstration
 * catalog, not a live query against ASF/NASA's NISAR archive. That live
 * integration does not exist yet (see nisarService.ts).
 *
 * Do not add products, dates, or metadata beyond what the team has
 * actually provided.
 */
export const DEMO_NISAR_OBSERVATIONS: NisarObservation[] = [
  {
    id: 'obs-022-055',
    productId: 'NISAR_L2_PR_GUNW_022_055',
    observationType: 'GUNW',
    processingLevel: 'L2',
    polarization: 'unknown',
    startDate: '2026-06-06',
    endDate: '2026-06-18',
    orbit: { track: 22, frame: 55 },
    coverage: { description: 'Candidate region, Monda, Uttarakhand, India' },
    availability: 'demonstration',
    metadata: {
      note: 'Prototype product analyzed in AquaByte QGIS workspace (coherence_022_055.tif).',
    },
  },
  {
    id: 'obs-025-055',
    productId: 'NISAR_L2_PR_GUNW_025_055',
    observationType: 'GUNW',
    processingLevel: 'L2',
    polarization: 'unknown',
    startDate: '2026-07-12',
    endDate: '2026-07-24',
    orbit: { track: 25, frame: 55 },
    coverage: { description: 'Candidate region, Monda, Uttarakhand, India' },
    availability: 'demonstration',
    metadata: {
      note: 'Prototype product analyzed in AquaByte QGIS workspace (coherence_025_055.tif).',
    },
  },
  {
    id: 'obs-026-055',
    productId: 'NISAR_L2_PR_GUNW_026_055',
    observationType: 'GUNW',
    processingLevel: 'L2',
    polarization: 'unknown',
    startDate: '2026-07-24',
    endDate: '2026-08-17',
    orbit: { track: 26, frame: 55 },
    coverage: { description: 'Candidate region, Monda, Uttarakhand, India' },
    availability: 'demonstration',
    metadata: {
      note: 'Prototype product analyzed in AquaByte QGIS workspace (coherence_026_055.tif). Used in the 025→026 coherence-loss comparison for Candidate #1.',
    },
  },
  {
    id: 'obs-029-055',
    productId: 'NISAR_L2_PR_GUNW_029_055',
    observationType: 'GUNW',
    processingLevel: 'L2',
    polarization: 'unknown',
    startDate: '2026-08-29',
    endDate: '2026-09-10',
    orbit: { track: 29, frame: 55 },
    coverage: { description: 'Candidate region, Monda, Uttarakhand, India' },
    availability: 'demonstration',
    metadata: {
      note: 'Prototype product identified in AquaByte QGIS workspace. Not yet analyzed for coherence change.',
    },
  },
]

/**
 * The one scientifically valid coherence comparison the team has actually
 * computed: 025 → 026. 025 and 026 are different interferometric pairs;
 * we compare their mean coherence, not their unwrapped phase, and we do
 * not treat this as a displacement measurement.
 */
export const DEMO_NISAR_OBSERVATION_PAIRS: NisarObservationPair[] = [
  {
    id: 'pair-025-026',
    beforeObservationId: 'obs-025-055',
    afterObservationId: 'obs-026-055',
    coherenceBefore: 0.6648,
    coherenceAfter: 0.2188,
    meanCoherenceChange: -0.446,
    note: 'Mean coherence comparison across the Candidate #1 polygon, computed in QGIS. This is a coherence comparison, not an unwrapped-phase displacement measurement — 025 and 026 are different interferometric pairs and cannot be directly subtracted in phase.',
  },
]

export const DEMO_CANDIDATE_ANOMALIES: CandidateAnomaly[] = [
  {
    id: 'candidate-001',
    title: 'Prototype NISAR anomaly — Candidate #1',
    status: 'prototype-anomaly',
    latitude: 31.1105,
    longitude: 77.9373,
    areaSqKm: 41.57,
    observationIds: ['obs-025-055', 'obs-026-055'],
    observationPairId: 'pair-025-026',
    regionLabel: 'Monda, Uttarakhand, India',
  },
]
