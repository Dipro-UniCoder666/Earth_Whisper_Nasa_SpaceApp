import type { NisarObservation, NisarObservationPair, CandidateAnomaly } from '@/features/investigation/types'
import {
  DEMO_NISAR_OBSERVATIONS,
  DEMO_NISAR_OBSERVATION_PAIRS,
  DEMO_CANDIDATE_ANOMALIES,
} from '@/features/investigation/services/nisarDemoData'

/**
 * Earth Whisper — NISAR service
 *
 * Abstracts "where NISAR observation data comes from" behind a stable
 * interface. Today it is backed entirely by the local demonstration
 * catalog in nisarDemoData.ts. When live ASF/NASA NISAR catalog access is
 * implemented, this file is the only place that should need to change —
 * callers (components, hooks) should never talk to a data source
 * directly.
 *
 * IMPORTANT: every observation and pair returned here carries
 * `availability: 'demonstration'` or the pair's note explains its
 * provenance. Consuming UI must surface that label; it must never present
 * this as a live NASA query result.
 */

const ARTIFICIAL_LATENCY_MS = 350

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ARTIFICIAL_LATENCY_MS))
}

export async function listObservations(): Promise<NisarObservation[]> {
  return delay(DEMO_NISAR_OBSERVATIONS)
}

export async function getObservation(id: string): Promise<NisarObservation | undefined> {
  const all = await listObservations()
  return all.find((obs) => obs.id === id)
}

export async function listObservationPairs(): Promise<NisarObservationPair[]> {
  return delay(DEMO_NISAR_OBSERVATION_PAIRS)
}

export async function getObservationPair(id: string): Promise<NisarObservationPair | undefined> {
  const all = await listObservationPairs()
  return all.find((pair) => pair.id === id)
}

/**
 * Returns candidate anomalies near a given location. Today this simply
 * returns the full demonstration catalog regardless of distance — a real
 * implementation would filter/query spatially. The (lat, lng) parameters
 * are accepted now so calling code doesn't need to change later.
 */
export async function findCandidatesNear(_latitude: number, _longitude: number): Promise<CandidateAnomaly[]> {
  return delay(DEMO_CANDIDATE_ANOMALIES)
}

export async function getCandidate(id: string): Promise<CandidateAnomaly | undefined> {
  const all = await delay(DEMO_CANDIDATE_ANOMALIES)
  return all.find((c) => c.id === id)
}

export async function getObservationsForCandidate(candidate: CandidateAnomaly): Promise<NisarObservation[]> {
  const all = await listObservations()
  return all.filter((obs) => candidate.observationIds.includes(obs.id))
}
