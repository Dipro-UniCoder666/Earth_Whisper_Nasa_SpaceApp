import type { WeatherClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'

/**
 * Weather / rainfall evidence (Clue 03) — DEMONSTRATION DATA.
 *
 * No real precipitation source (e.g. NASA GPM/IMERG) is connected yet.
 * This service returns clearly labeled placeholder rainfall windows so
 * the UI and future integration share one call site.
 */
export async function getWeatherClue(candidate: CandidateAnomaly): Promise<WeatherClue> {
  const isKnownCandidate = candidate.id === 'candidate-001'

  if (!isKnownCandidate) {
    return {
      id: 'weather',
      order: 3,
      title: 'Weather — precipitation',
      availability: 'unavailable',
      source: { label: 'NASA GPM / IMERG (not yet connected)' },
      summary: 'No precipitation data source is connected for this location yet.',
      limitations: ['Rainfall integration has not been implemented.'],
      windows: [],
    }
  }

  return {
    id: 'weather',
    order: 3,
    title: 'Weather — precipitation',
    availability: 'demonstration',
    source: { label: 'NASA GPM / IMERG (demonstration placeholder — not a real query)' },
    observedAt: '2026-07-24',
    summary: 'Illustrative rainfall accumulation ahead of the "after" acquisition, pending real GPM/IMERG integration.',
    limitations: [
      'These are placeholder values, not values retrieved from an actual precipitation product.',
      'Elevated rainfall is context, not proof — it does not automatically establish rainfall as the cause of the observed change.',
    ],
    windows: [
      { label: '24h', millimeters: 38 },
      { label: '3d', millimeters: 96 },
      { label: '7d', millimeters: 164 },
      { label: '14d', millimeters: 221 },
    ],
    anomalyMillimeters: 58,
    baselineDescription: 'Illustrative comparison to the regional historical average for the same 14-day period.',
  }
}
