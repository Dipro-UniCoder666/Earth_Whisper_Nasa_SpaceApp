import type { TerrainClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Terrain evidence (Clue 02) — DEMONSTRATION DATA.
 *
 * No real DEM (e.g. NASADEM/SRTM) integration exists yet. This service
 * returns a clearly labeled placeholder so the evidence UI and the future
 * real integration share one call site — swapping this implementation for
 * a real elevation API call is the only change needed later.
 *
 * The placeholder values below are illustrative of what real terrain
 * evidence would look like for mountainous terrain at the Monda site,
 * India (Candidate #1's region) — they are NOT measured from an actual
 * DEM and must never be treated as such.
 */
export async function getTerrainClue(candidate: CandidateAnomaly): Promise<TerrainClue> {
  const isKnownCandidate = candidate.id === 'candidate-001'

  if (!isKnownCandidate) {
    return {
      id: 'terrain',
      order: 2,
      title: 'Terrain — elevation & slope',
      availability: 'unavailable',
      source: { label: 'NASADEM / SRTM (not yet connected)' },
      summary: 'No terrain data source is connected for this location yet.',
      limitations: ['DEM integration has not been implemented.'],
    }
  }

  return {
    id: 'terrain',
    order: 2,
    title: 'Terrain — elevation & slope',
    availability: 'demonstration',
    source: { label: 'NASADEM / SRTM (demonstration placeholder — not a real query)' },
    summary: 'Illustrative terrain characteristics for this mountainous region, pending real DEM integration.',
    limitations: [
      'These are placeholder values representative of the region, not values extracted from an actual elevation model.',
      'Steep terrain is context, not a conclusion — it does not by itself indicate what caused the observed change.',
    ],
    elevationMeters: 2140,
    slopeDegrees: 34,
    aspectDegrees: 205,
    aspectDirection: 'SSW',
    terrainClass: 'steep',
  }
}
