const configuredApiBase = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/+$/, '')
export const GHERPROOF_API = `${configuredApiBase}/api/gherproof`
export const DHARA_CONTEXT_IMAGE = '/images/dhara-sentinel2-context-2026-01-13.png'
export const PALLIMANGAL_INCIDENT_ID = 'incident-pallimangal-2026-01-14'
export const PALLIMANGAL_ASSET_ID = 'asset-pallimangal-reported'

export interface EvidenceRecord {
  evidence_id: string
  title: string
  evidence_category: string
  confidence_or_validation_status: string
  acquisition_date?: string | null
  source_dataset?: string
  source?: string
  crs?: string | null
  spatial_coverage?: Record<string, unknown> | null
  limitations?: string[]
  metadata?: Record<string, unknown>
}

export interface RasterLayer {
  evidence_id: string
  title: string
  status: string
  evidence_category: string
  url: string
  acquisition_date?: string | null
  crs?: string | null
  asset?: string
  sha256?: string
}

export interface RegionalStatus {
  model_readiness: string
  local_validation_status: string
  impact_quantification: string
  human_labels_completed?: number
  human_label_slots?: number
  satellite_acquisitions?: Record<string, unknown>
  model_outputs?: { models?: string[]; [key: string]: unknown }
  limitations?: string[]
}

export interface FisheriesScreening {
  incident_id: string
  case_status: string
  model_readiness: string
  human_reference_status: string
  impact_quantification: string
  observations: Array<{ observation_id: string; sensor: string; acquisition_date: string | null; limitations: string[] }>
  optical_change_screening: {
    status: string
    pre_date?: string | null
    post_date?: string | null
    candidate_counts_grid_cells: Record<string, number | null> | null
    pixel_resolution_m?: number | null
    units?: string | null
    interpretation?: string
    evidence_ids?: string[]
    limitations?: string[]
  }
  model_evidence: {
    status: string
    model_selection: string
    per_acquisition_comparisons: Array<Record<string, unknown>>
    model_candidate_evidence_ids: Record<string, string[]>
    model_disagreement_evidence_ids: string[]
    overall_interpretation: string
    uncertainty_reasons: string[]
  }
  asset_exposure: Array<{
    asset_id: string | null
    status: string
    geometry_status: string | null
    candidate_pixel_overlap_count: number | null
    explanation: string
  }>
  limitations: string[]
}

export interface FisheriesSummary {
  incident_id: string
  case_status: string
  what_happened: string
  satellite_screening: string
  inspection_needed: string
  recommended_checks: string[]
  unknowns: string[]
  evidence_ids: string[]
}

export interface FisheriesFinding {
  finding_id: string
  category: string
  explanation: string
  evidence_ids: string[]
  limitations: string[]
  recommended_verification_action: string
}

export interface FisheriesPriority {
  priority: string
  recommended_action: string
  rationale: string
  missing_information: string[]
  fisheries_officer_checks: string[]
  not_an_emergency_instruction: boolean
}

export interface FisheriesReport {
  title: 'DHARA — Pallimangal Fisheries Incident Screening Case Study'
  report_type: string
  generated_at_utc: string
  incident: {
    incident_id: string
    title: string
    incident_date: string | null
    incident_date_status: string
    description: string
    administrative_location: Record<string, string | null>
    affected_localities_reported: string[]
    reporting_sources: Array<{ source_name: string; claim: string; url?: string | null; published_date?: string | null; claim_status: string }>
  }
  study_area_map: { evidence_id: string; status: string; not_an_enclosure_boundary: boolean; candidate_change_layer_id: string }
  fisheries_context: Record<string, unknown>
  fisheries_assets: Array<{ asset_id: string; asset_name: string; geometry_status: string; geometry_reference: string | null }>
  satellite_observations: FisheriesScreening['observations']
  water_change_screening: FisheriesScreening['optical_change_screening']
  ai_screening: FisheriesScreening['model_evidence']
  findings: FisheriesFinding[]
  asset_exposure: FisheriesScreening['asset_exposure']
  inspection_priorities: FisheriesPriority[]
  recommended_inspection_checks: string[]
  evidence_sources: FisheriesReport['incident']['reporting_sources']
  field_inspection_records: Array<Record<string, unknown>>
  unavailable_measurements: Record<string, unknown>
  readiness: Record<string, string>
  limitations: string[]
}

export interface GherProofData {
  status: RegionalStatus | null
  evidence: { records: EvidenceRecord[] } | null
  layers: { layers: RasterLayer[] } | null
  scenes: Record<string, unknown> | null
  predictions: { models?: string[]; prediction_layers?: EvidenceRecord[]; disagreement_layers?: EvidenceRecord[]; [key: string]: unknown } | null
  weakReference: { scenes?: Array<Record<string, unknown>>; temporal_change?: Record<string, unknown>; [key: string]: unknown } | null
  comparisons: Record<string, unknown> | null
  coverage: Record<string, unknown> | null
  geography: Record<string, unknown> | null
  fisheriesScreening: FisheriesScreening | null
  fisheriesSummary: FisheriesSummary | null
  fisheriesFindings: { incident_id: string; findings: FisheriesFinding[] } | null
  fisheriesPriorities: { incident_id: string; priorities: FisheriesPriority[] } | null
  report: FisheriesReport | null
}

export class GherProofApiError extends Error {
  readonly status: number
  readonly path: string

  constructor(status: number, path: string) {
    super(`Request failed (${status}) for ${path}`)
    this.name = 'GherProofApiError'
    this.status = status
    this.path = path
  }
}

export async function getGherProofJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${GHERPROOF_API}${path}`, { signal, headers: { Accept: 'application/json' } })
  if (!response.ok) throw new GherProofApiError(response.status, path)
  return response.json() as Promise<T>
}

export async function loadGherProofData(signal?: AbortSignal): Promise<{ data: GherProofData; failures: string[] }> {
  const requests = [
    ['status', '/screening/status'],
    ['evidence', '/evidence?limit=500'],
    ['layers', '/layers'],
    ['scenes', '/scenes'],
    ['predictions', '/predictions'],
    ['weakReference', '/weak-reference'],
    ['comparisons', '/comparisons'],
    ['coverage', '/coverage'],
    ['geography', '/geography/geography-provisional-regional-aoi'],
    ['fisheriesScreening', `/fisheries/incidents/${PALLIMANGAL_INCIDENT_ID}/screening`],
    ['fisheriesSummary', `/fisheries/incidents/${PALLIMANGAL_INCIDENT_ID}/summary`],
    ['fisheriesFindings', `/fisheries/incidents/${PALLIMANGAL_INCIDENT_ID}/findings`],
    ['fisheriesPriorities', `/fisheries/incidents/${PALLIMANGAL_INCIDENT_ID}/priorities`],
    ['report', `/fisheries/incidents/${PALLIMANGAL_INCIDENT_ID}/report`],
  ] as const

  const results = await Promise.allSettled(requests.map(([, path]) => getGherProofJson<unknown>(path, signal)))
  const partial: Partial<GherProofData> = {}
  const failures: string[] = []
  let screeningFailure: unknown
  results.forEach((result, index) => {
    const key = requests[index][0] as keyof GherProofData
    if (result.status === 'fulfilled') Object.assign(partial, { [key]: result.value })
    else if (!signal?.aborted) {
      if (key === 'fisheriesScreening') screeningFailure = result.reason
      if (key !== 'status') failures.push(requests[index][0])
    }
  })
  if (!partial.fisheriesScreening) {
    const reason = screeningFailure instanceof GherProofApiError
      ? `HTTP ${screeningFailure.status}`
      : 'a network or CORS failure'
    throw new Error(`The Pallimangal screening service could not be reached (${reason}). Check VITE_API_BASE_URL or same-origin /api routing, then confirm backend availability and CORS.`)
  }
  if ((!partial.evidence || !partial.layers) && !failures.includes('evidence') && !failures.includes('layers')) {
    failures.push('map evidence registry')
  }
  return { data: partial as GherProofData, failures }
}
