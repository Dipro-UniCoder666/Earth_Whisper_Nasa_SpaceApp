import type { EarthEventFingerprint, Clue, ProvenanceEntry } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'
import { getRadarClue } from '@/features/evidence/services/radarService'
import { getTerrainClue } from '@/features/evidence/services/terrainService'
import { getWeatherClue } from '@/features/evidence/services/weatherService'
import { getOpticalClue } from '@/features/evidence/services/opticalService'
import { getFireClue } from '@/features/evidence/services/fireService'
import { getWaterClue } from '@/features/evidence/services/waterService'

/**
 * Assembles the Earth Event Fingerprint for a candidate anomaly by calling
 * each evidence service independently and combining the results. This
 * function does NOT interpret the evidence, compare hypotheses, or decide
 * a cause — it only collects and records what each source reported, with
 * provenance. Candidate-cause analysis is a later prompt.
 */
export async function buildEarthEventFingerprint(candidate: CandidateAnomaly): Promise<EarthEventFingerprint> {
  const [radar, terrain, weather, optical, fire, water] = await Promise.all([
    getRadarClue(candidate),
    getTerrainClue(candidate),
    getWeatherClue(candidate),
    getOpticalClue(candidate),
    getFireClue(candidate),
    getWaterClue(candidate),
  ])

  const clues: Clue[] = [radar, terrain, weather, optical, fire, water]

  const provenance: ProvenanceEntry[] = clues.map((clue) => ({
    clueId: clue.id,
    source: clue.source,
    availability: clue.availability,
  }))

  const demonstrationCount = clues.filter((c) => c.availability === 'demonstration').length
  const unavailableCount = clues.filter((c) => c.availability === 'unavailable').length

  return {
    candidateId: candidate.id,
    location: {
      latitude: candidate.latitude,
      longitude: candidate.longitude,
      label: candidate.regionLabel,
      areaSqKm: candidate.areaSqKm,
    },
    clues,
    temporal: {
      afterWindowStart: radar.observedAt,
    },
    spatial: {
      areaSqKm: candidate.areaSqKm,
    },
    provenance,
    uncertainty: {
      known: [
        radar.availability === 'measured'
          ? `A measured NISAR coherence change of ${radar.meanCoherenceChange?.toFixed(4) ?? 'an unknown amount'} was recorded across the candidate polygon.`
          : 'No measured radar evidence is available for this candidate.',
      ],
      uncertain: [
        `${demonstrationCount} of 6 evidence clues are demonstration placeholders standing in for data sources not yet connected.`,
        'No candidate-cause comparison has been performed — this fingerprint records observations only.',
      ],
      cannotConclude: [
        'No cause can be attributed to this anomaly from the current evidence.',
        `${unavailableCount} of 6 evidence sources produced no data at all (missing, not "negative").`,
      ],
    },
    compiledAt: new Date().toISOString(),
  }
}

export function summarizeFingerprintCompleteness(fingerprint: EarthEventFingerprint) {
  const total = fingerprint.clues.length
  const measured = fingerprint.clues.filter((c) => c.availability === 'measured').length
  const demonstration = fingerprint.clues.filter((c) => c.availability === 'demonstration').length
  const unavailable = fingerprint.clues.filter((c) => c.availability === 'unavailable').length
  return { total, measured, demonstration, unavailable }
}
