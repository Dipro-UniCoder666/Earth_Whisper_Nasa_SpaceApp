import type { CandidateDetail, CandidateListResponse, CandidateSummary } from '@/features/candidates/types'

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

async function fetchWithTimeout(url: string, timeoutMs = API_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fetch(url, { signal: controller.signal })
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
async function tryApi<T>(path: string): Promise<T | null> {
  if (!API_BASE_URL) return null
  if (apiAvailable === false) return null
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}${path}`)
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

/** API PDF route when the service is reachable, otherwise the static Step 11 PDF. */
export function getCaseFilePdfUrl(): string {
  return apiAvailable === true ? `${API_BASE_URL}/api/case-file/pdf` : STATIC_CASE_FILE_PDF_URL
}
