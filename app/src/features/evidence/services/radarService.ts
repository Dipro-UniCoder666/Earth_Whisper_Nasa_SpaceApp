import type { RadarClue } from '@/features/evidence/types'
import { getObservationPair, getObservation } from '@/features/investigation/services/nisarService'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Radar evidence (Clue 01) is Earth Whisper's one genuinely *measured*
 * clue — it comes directly from the team's QGIS coherence analysis in
 * AquaByte_NISAR, not a placeholder. Everything else in the evidence
 * engine is demonstration data until real integrations are built.
 */
export async function getRadarClue(candidate: CandidateAnomaly): Promise<RadarClue> {
  if (!candidate.observationPairId) {
    return {
      id: 'radar',
      order: 1,
      title: 'Radar — NISAR coherence',
      availability: 'unavailable',
      source: { label: 'AquaByte NISAR/QGIS workspace' },
      summary: 'No coherence comparison has been computed for this candidate.',
      limitations: ['No NISAR observation pair is associated with this candidate yet.'],
    }
  }

  const pair = await getObservationPair(candidate.observationPairId)
  if (!pair) {
    return {
      id: 'radar',
      order: 1,
      title: 'Radar — NISAR coherence',
      availability: 'unavailable',
      source: { label: 'AquaByte NISAR/QGIS workspace' },
      summary: 'The referenced NISAR observation pair could not be found.',
      limitations: ['Data lookup failed — this is a missing-data state, not a scientific finding.'],
    }
  }

  const [before, after] = await Promise.all([
    getObservation(pair.beforeObservationId),
    getObservation(pair.afterObservationId),
  ])

  return {
    id: 'radar',
    order: 1,
    title: 'Radar — NISAR coherence',
    availability: 'measured',
    source: { label: 'AquaByte NISAR/QGIS workspace' },
    observedAt: after?.startDate,
    summary: `Mean coherence across the candidate polygon changed by ${pair.meanCoherenceChange?.toFixed(4) ?? 'an unknown amount'} between the two acquisitions.`,
    limitations: [
      'Coherence loss indicates surface change occurred — it does not by itself identify what caused the change.',
      '025 and 026 are different interferometric pairs; their unwrapped phase cannot be directly subtracted as a displacement measurement.',
    ],
    coherenceBefore: pair.coherenceBefore,
    coherenceAfter: pair.coherenceAfter,
    meanCoherenceChange: pair.meanCoherenceChange,
    areaSqKm: candidate.areaSqKm,
    beforeProductId: before?.productId,
    afterProductId: after?.productId,
  }
}
