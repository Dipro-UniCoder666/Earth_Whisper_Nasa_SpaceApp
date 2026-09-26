export interface CandidateSummary {
  candidate_key: string
  comparison: string
  region_id: number
  lon: number | null
  lat: number | null
  area_m2: number | null
  investigated: boolean
}

export interface CandidateDetail extends CandidateSummary {
  nisar_change: number | null
  nisar_change_strength: number | null
  nisar_signal_percentile: number | null
  nisar_signal_band: string | null
  s1_mean_db: number | null
  s1_median_db: number | null
  s1_pct_le_minus3db: number | null
  s1_anomaly_percentile: number | null
  s1_anomaly_stability: string | null
  cross_radar_status: string | null
  optical_status: string | null
  rainfall_context_status: string | null
  comparison_population_size: number | null
  anomaly_stability_band: string | null
  evidence_limitation: string | null
  nisar: {
    nisar_change: number | null
    nisar_change_strength: number | null
    nisar_signal_percentile: number | null
    nisar_signal_band: string | null
  }
  sentinel1: {
    s1_mean_db: number | null
    s1_median_db: number | null
    s1_pct_le_minus3db: number | null
    s1_anomaly_percentile: number | null
    s1_anomaly_stability: string | null
  }
  cross_radar: {
    cross_radar_status: string | null
    nisar_signal_band: string | null
    s1_anomaly_band: string | null
  }
  optical: {
    optical_status: string | null
    optical_tested: string | null
    optical_observation_count: number | null
    optical_valid_observation_count: number | null
    optical_max_valid_pixels: number | null
  }
  environmental: {
    rainfall_context_status: string | null
    rainfall_role: string | null
    gunw_023_rainfall_14day_mm: number | null
    gunw_025_rainfall_14day_mm: number | null
    gunw_026_rainfall_14day_mm: number | null
    gunw_029_rainfall_14day_mm: number | null
  }
  uncertainty: {
    comparison_population_size: number | null
    anomaly_stability_band: string | null
    evidence_limitation: string | null
  }
  observations: {
    observation_summary: string | null
    inference_summary: string | null
    limitation_summary: string | null
  }
  source_records: {
    step8c_evidence_matrix: Record<string, string | number | null>
  }
}

export interface NisarComparisonSummary {
  comparison: string
  observation_pairs: string[]
  polarization: 'HH' | 'VV'
  mean_change: number
  median_change: number
}

export interface DashboardSummary {
  exact_aoi_valid_pixels: number
  nisar_comparisons: NisarComparisonSummary[]
  sentinel1_threshold_counts: Record<string, number>
  dual_radar_stable_patterns: number
  stability_bands: Record<string, number>
  optical_tested_regions: number
  optical_inconclusive_regions: number
  optical_not_tested_regions: number
  rainfall_context: {
    event_day_mm: number
    three_day_mm: number
    seven_day_mm: number
    fourteen_day_mm: number
    maximum_daily_mm: number
    wet_days_gt_5mm: number
  }
}

export interface CandidateListResponse {
  project: string
  aoi: { name: string; wkt: string }
  candidate_count: number
  investigated_candidate_count: number
  dashboard_summary: DashboardSummary
  candidates: CandidateSummary[]
}
