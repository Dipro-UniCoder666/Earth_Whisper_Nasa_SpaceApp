import type { FireClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Fire evidence (Clue 05) — DEMONSTRATION DATA.
 *
 * No real NASA FIRMS integration exists yet. Per the project's scientific
 * rule, an absence of detections must always be reported as "no
 * corresponding fire signal detected" — never as "no fire occurred,"
 * since satellite fire detection has real gaps (cloud cover, timing,
 * sensor resolution).
 */
export async function getFireClue(candidate: CandidateAnomaly): Promise<FireClue> {
  const isKnownCandidate = candidate.id === 'candidate-001'

  if (!isKnownCandidate) {
    return {
      id: 'fire',
      order: 5,
      title: 'Fire — active-fire detections',
      availability: 'unavailable',
      source: { label: 'NASA FIRMS (not yet connected)' },
      summary: 'No fire detection source is connected for this location yet.',
      limitations: ['FIRMS integration has not been implemented.'],
      detectionsWithinCandidate: 0,
      detectionsNearby: 0,
    }
  }

  return {
    id: 'fire',
    order: 5,
    title: 'Fire — active-fire detections',
    availability: 'demonstration',
    source: { label: 'NASA FIRMS (demonstration placeholder — not a real query)' },
    observedAt: '2026-07-24',
    summary: 'No corresponding fire signal detected within or near the candidate during the relevant window.',
    limitations: [
      'This is a placeholder result standing in for a real FIRMS query.',
      'Absence of a detected fire signal does not confirm that no fire occurred — satellite fire detection has coverage gaps from cloud cover, revisit timing, and sensor resolution.',
    ],
    detectionsWithinCandidate: 0,
    detectionsNearby: 0,
    searchRadiusKm: 10,
    windowDescription: 'Illustrative ±14-day window around the "after" acquisition.',
  }
}
