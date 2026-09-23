import type { OpticalClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Optical imagery evidence (Clue 04) — NOT YET AVAILABLE.
 *
 * No Sentinel-2/Landsat integration exists, and unlike terrain/weather we
 * do not fabricate a plausible-looking before/after image pair here —
 * inventing "visual" evidence is a materially different kind of
 * fabrication than a placeholder number, so this clue is honestly reported
 * as unavailable rather than demonstrated.
 */
export async function getOpticalClue(_candidate: CandidateAnomaly): Promise<OpticalClue> {
  return {
    id: 'optical',
    order: 4,
    title: 'Optical — before/after imagery',
    availability: 'unavailable',
    source: { label: 'Sentinel-2 / Landsat (not yet connected)' },
    summary: 'No optical imagery source is connected yet. No before/after comparison is available.',
    limitations: [
      'Optical integration has not been implemented — this is a missing-data state, not an indication that no visible change occurred.',
    ],
  }
}
