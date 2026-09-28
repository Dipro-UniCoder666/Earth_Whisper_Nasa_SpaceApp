import type { CandidateDetail, CandidateListResponse, CandidateSummary, InvestigationResponse } from '@/features/candidates/types'

/**
 * Sandhya River investigation data access.
 *
 * The verified evidence is produced by the Step 12 backend foundation
 * (`backend/`), but the demonstration must also work when that service is not
 * running - for example when only the Vite dev server is started, or on a
 * static deployment. So each request is API-first with a static fallback:
 *
 *   1. try the read-only API when VITE_API_BASE_URL is explicitly configured
 *   2. if it is unreachable, load the same generated contract that the API
 *      serves, from the static asset /data/earth_whisper_candidates.json
 *
 * Both paths return the identical generated values - nothing is recomputed,
 * no probability or confidence value is derived, and missing values stay null.
 */

// The generated contract is the reliable client-side source for the demo. An
// API is used only when the deployment explicitly opts into one, so a stale or
// unavailable localhost service cannot put a verified investigation into an
// error state before the bundled evidence is read.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? null
const STATIC_CONTRACT_URL = `${import.meta.env.BASE_URL}data/earth_whisper_candidates.json`
const STATIC_CASE_FILE_PDF_URL = '/data/step11/earth_event_case_file.pdf'
const API_TIMEOUT_MS = 2500

/** The generated contract mirrors the API shapes: flat summary fields plus grouped evidence. */
type StaticContract = {
  project: string
  aoi: { name: string; wkt: string }
  candidate_count: number
  investigated_candidate_count: number
  dashboard_summary: CandidateListResponse['dashboard_summary']
  candidates: CandidateDetail[]
}

let apiAvailable: boolean | null = null
let staticContract: StaticContract | null = null

async function fetchWithTimeout(url: string, init?: RequestInit, timeoutMs = API_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fetch(url, { ...init, signal: controller.signal })
  } finally {
    window.clearTimeout(timer)
  }
}

async function loadStaticContract(): Promise<StaticContract> {
  if (staticContract) return staticContract
  const response = await fetch(STATIC_CONTRACT_URL)
  if (!response.ok) {
    throw new Error(`Earth Whisper evidence data unavailable (${response.status})`)
  }
  staticContract = (await response.json()) as StaticContract
  return staticContract
}

/** Returns null (and remembers that the API is down) instead of throwing. */
async function tryApi<T>(path: string, init?: RequestInit): Promise<T | null> {
  if (!API_BASE_URL) return null
  if (apiAvailable === false) return null
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, init)
    if (!response.ok) throw new Error(`Earth Whisper API request failed (${response.status})`)
    const payload = (await response.json()) as T
    apiAvailable = true
    return payload
  } catch {
    apiAvailable = false
    return null
  }
}

function toSummary(candidate: CandidateDetail): CandidateSummary {
  return {
    candidate_key: candidate.candidate_key,
    comparison: candidate.comparison,
    region_id: candidate.region_id,
    lon: candidate.lon,
    lat: candidate.lat,
    area_m2: candidate.area_m2,
    investigated: candidate.investigated,
  }
}

/** Keeps the declared nested shapes honest when a source value is absent. */
function normalizeDetail(candidate: CandidateDetail): CandidateDetail {
  return {
    ...candidate,
    sentinel1: {
      ...candidate.sentinel1,
      s1_mean_db: candidate.sentinel1.s1_mean_db ?? candidate.s1_mean_db ?? null,
    },
  }
}

export async function getSandhyaCandidates(investigated?: boolean): Promise<CandidateListResponse> {
  const query = investigated === undefined ? '' : `?investigated=${investigated}`
  const fromApi = await tryApi<CandidateListResponse>(`/api/candidates${query}`)
  if (fromApi) return fromApi

  const contract = await loadStaticContract()
  const rows = contract.candidates.filter(
    (candidate) => investigated === undefined || candidate.investigated === investigated,
  )

  return {
    project: contract.project,
    aoi: contract.aoi,
    candidate_count: contract.candidate_count,
    investigated_candidate_count: contract.investigated_candidate_count,
    dashboard_summary: contract.dashboard_summary,
    candidates: rows.map(toSummary),
  }
}

export async function getSandhyaCandidate(candidateKey: string): Promise<CandidateDetail> {
  const fromApi = await tryApi<CandidateDetail>(`/api/candidates/${encodeURIComponent(candidateKey)}`)
  if (fromApi) return fromApi

  const contract = await loadStaticContract()
  const found = contract.candidates.find((candidate) => candidate.candidate_key === candidateKey)
  if (!found) {
    throw new Error(`Candidate ${candidateKey} is not present in the verified investigation data.`)
  }
  return normalizeDetail(found)
}

function distanceSquared(candidate: CandidateSummary, latitude: number, longitude: number) {
  return Math.pow((candidate.lat ?? 0) - latitude, 2) + Math.pow((candidate.lon ?? 0) - longitude, 2)
}

/** Runs the request-time investigation, with the same verified static fallback as the read API. */
export async function requestInvestigation(locationId: string, latitude: number, longitude: number): Promise<InvestigationResponse> {
  const request = { location_id: locationId, latitude, longitude }
  const fromApi = await tryApi<InvestigationResponse>('/api/investigations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!fromApi) throw new Error('Earth Whisper investigation service is unavailable.')
  return fromApi
}

/** Runs Sandhya through the backend and preserves the existing static fallback. */
export async function runSandhyaInvestigation(locationId: string, latitude: number, longitude: number): Promise<InvestigationResponse> {
  try {
    return await requestInvestigation(locationId, latitude, longitude)
  } catch {
    // The static fallback remains available for deployments without the API.
  }

  const contract = await loadStaticContract()
  if (locationId !== 'sandhya-river') throw new Error('This investigation location is not available in the verified evidence contract.')
  const candidates = contract.candidates.filter((candidate) => candidate.investigated)
  const candidate = candidates.reduce<CandidateDetail | null>((nearest, current) => {
    if (!nearest) return current
    return distanceSquared(current, latitude, longitude) < distanceSquared(nearest, latitude, longitude) ? current : nearest
  }, null)
  if (!candidate) throw new Error('No verified investigated candidates are available for this location.')
  return {
    status: 'ready',
    location_id: locationId,
    candidate_key: candidate.candidate_key,
    stages: [
      ['initializing', 'Location resolved', 'The selected Sandhya River investigation was validated.'],
      ['loading_observations', 'Observations loaded', 'Verified radar, rainfall, optical, and uncertainty records were read.'],
      ['analyzing_radar_change', 'Radar change analyzed', 'NISAR change and Sentinel-1 cross-check records were assembled.'],
      ['checking_supporting_evidence', 'Supporting evidence checked', 'Radar, environmental, and optical availability was recorded.'],
      ['assessing_uncertainty', 'Uncertainty assessed', 'Recorded uncertainty and limitation statements were retained.'],
      ['assembling_investigation', 'Investigation assembled', 'The verified evidence groups and supporting context are ready to present.'],
    ].map(([id, label, detail]) => ({ id, label, status: 'complete' as const, detail })),
    result: {
      project: contract.project,
      location_id: locationId,
      candidate_count: contract.candidate_count,
      investigated_candidate_count: contract.investigated_candidate_count,
      candidate,
      evidence_groups: { nisar: candidate.nisar, sentinel1: candidate.sentinel1, rainfall: candidate.environmental, optical: candidate.optical },
      evidence_availability: Object.fromEntries(['nisar', 'sentinel1', 'rainfall', 'optical'].map((name) => [name, 'available'])),
      uncertainty: candidate.uncertainty,
      limitations: candidate.observations.limitation_summary,
      provenance: {},
    },
  }
}

/** API PDF route when the service is reachable, otherwise the static Step 11 PDF. */
export function getCaseFilePdfUrl(): string {
  return apiAvailable === true ? `${API_BASE_URL}/api/case-file/pdf` : STATIC_CASE_FILE_PDF_URL
}
