import type { WaterClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Water / geographic context evidence (Clue 06) — DEMONSTRATION DATA.
 *
 * No real hydrography source is connected yet. This service returns a
 * clearly labeled placeholder so future flood-investigation support can
 * be added by swapping this implementation, not by restructuring callers.
 */
export async function getWaterClue(candidate: CandidateAnomaly): Promise<WaterClue> {
  const isKnownCandidate = candidate.id === 'candidate-001'

  if (!isKnownCandidate) {
    return {
      id: 'water',
      order: 6,
      title: 'Water — hydrographic context',
      availability: 'unavailable',
      source: { label: 'Surface water / hydrography dataset (not yet connected)' },
      summary: 'No hydrographic data source is connected for this location yet.',
      limitations: ['Water-context integration has not been implemented.'],
      inFloodplain: 'unknown',
    }
  }

  return {
    id: 'water',
    order: 6,
    title: 'Water — hydrographic context',
    availability: 'demonstration',
    source: { label: 'Surface water / hydrography dataset (demonstration placeholder — not a real query)' },
    summary: 'Illustrative proximity to the nearest mapped water feature, pending real hydrographic integration.',
    limitations: [
      'These are placeholder values, not values retrieved from an actual hydrography dataset.',
      'Proximity to water is context for flood investigation — it is not evidence of a flood having occurred.',
    ],
    distanceToNearestWaterKm: 1.8,
    nearestWaterFeature: 'Unnamed mountain stream (illustrative)',
    inFloodplain: false,
    elevationAboveNearestWaterMeters: 310,
  }
}
