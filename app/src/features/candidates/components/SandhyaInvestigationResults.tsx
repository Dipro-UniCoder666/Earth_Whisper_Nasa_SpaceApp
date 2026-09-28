import { forwardRef, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Activity, BadgeCheck, CheckCircle2, CircleAlert, CircleDashed, CloudRain, Eye, RadioTower, Sparkles } from 'lucide-react'
import type { InvestigationLocation } from '@/features/investigation/data/investigationSite'
import { InvestigationScan } from '@/features/investigation/components/InvestigationScan'
import { InvestigationResultShell } from '@/features/investigation/components/InvestigationResultShell'
import { getCaseFilePdfUrl, runSandhyaInvestigation } from '@/features/candidates/services/candidateService'
import type { CandidateDetail, InvestigationResponse } from '@/features/candidates/types'

interface SandhyaInvestigationResultsProps { location: InvestigationLocation }

const PAIRS: Record<string, { polarization: 'HH' | 'VV'; observation: string; dates: string; first: string; second: string; rainfallPrefix: string }> = {
  HH_023_to_029: { polarization: 'HH', observation: 'GUNW_023 to GUNW_029', dates: '20 Jun 2026 to 02 Jul 2026', first: 'GUNW_023_HH_median', second: 'GUNW_029_HH_median', rainfallPrefix: 'gunw_029' },
  VV_025_to_026: { polarization: 'VV', observation: 'GUNW_025 to GUNW_026', dates: '14 Jul 2026 to 31 Aug 2026', first: 'GUNW_025_VV_median', second: 'GUNW_026_VV_median', rainfallPrefix: 'gunw_026' },
}

const OBSERVATIONS = [
  ['20 Jun 2026 → 02 Jul 2026', 'HH', 'GUNW_023_HH_median', 'GUNW_029_HH_median'],
  ['14 Jul 2026 → 31 Aug 2026', 'VV', 'GUNW_025_VV_median', 'GUNW_026_VV_median'],
  ['26 Jul 2026 → 19 Aug 2026', 'VV', 'GUNW_026_VV_median', 'GUNW_025_VV_median'],
  ['31 Aug 2026 → 12 Sep 2026', 'HH', 'GUNW_029_HH_median', 'GUNW_023_HH_median'],
] as const

function numberText(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined || !Number.isFinite(value)) return 'Not available'
  return value.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function dbText(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return 'Not available'
  return `${value < 0 ? '−' : '+'}${Math.abs(value).toFixed(2)} dB`
}

function percentText(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return 'Not available'
  return `${value.toFixed(1)}%`
}

function recordNumber(candidate: CandidateDetail | null, key: string) {
  const raw = candidate?.source_records.step8c_evidence_matrix[key]
  const value = typeof raw === 'number' ? raw : raw ? Number(raw) : NaN
  return Number.isFinite(value) ? value : null
}

function humanize(value: string | null | undefined) {
  return value ? value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) : 'Not available'
}

function crossRadarText(value: string | null | undefined) {
  if (value === 'dual_radar_upper_quartile') return 'Dual-radar upper-quartile pattern'
  if (value === 's1_upper_quartile_nisar_not_upper_quartile') return 'Sentinel-1 upper-quartile pattern; NISAR is not upper-quartile'
  if (value === 'neither_upper_quartile') return 'Radar pattern not in the upper quartile'
  return humanize(value)
}

function opticalText(candidate: CandidateDetail) {
  if (candidate.optical_status === 'tested_but_inconclusive_no_valid_pixels') return 'TESTED — INCONCLUSIVE'
  if (candidate.optical_status === 'not_tested') return 'NOT TESTED'
  return humanize(candidate.optical_status)
}

function Finding({ label, headline, subtitle }: { label: string; headline: string; subtitle: string }) {
  return <article className="ew-sandhya-finding"><span>{label}</span><strong>{headline}</strong><p>{subtitle}</p></article>
}

function StatusRow({ label, value, tone }: { label: string; value: string; tone: 'ok' | 'warn' | 'muted' }) {
  const Icon = tone === 'ok' ? CheckCircle2 : tone === 'warn' ? CircleAlert : CircleDashed
  return <div className="ew-sandhya-status-row"><Icon size={15} aria-hidden="true" className={`is-${tone}`} /><span>{label}</span><strong>{value}</strong></div>
}

export const SandhyaInvestigationResults = forwardRef<HTMLElement, SandhyaInvestigationResultsProps>(function SandhyaInvestigationResults({ location }, ref) {
  const [payload, setPayload] = useState<InvestigationResponse | null>(null)
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState<'analysis' | 'result' | 'error'>('analysis')
  const [scanProgress, setScanProgress] = useState(0)
  const [apiReady, setApiReady] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [startedAt, setStartedAt] = useState(() => Date.now())

  useEffect(() => {
    let active = true
    setPhase('analysis')
    setScanProgress(0)
    setApiReady(false)
    setError(null)
    setPayload(null)
    setCandidate(null)
    setStartedAt(Date.now())

    runSandhyaInvestigation(location.id, location.coords.lat, location.coords.lng).then((result) => {
      if (!active) return
      setPayload(result)
      if (active) {
        setCandidate(result.result.candidate)
        setApiReady(true)
      }
    }).catch(() => {
      if (active) {
        setError('Earth Whisper could not load the verified investigation evidence.')
        setPhase('error')
      }
    })

    return () => {
      active = false
    }
  }, [attempt])

  useEffect(() => {
    if (apiReady) setScanProgress(1)
  }, [apiReady])

  useEffect(() => {
    if (!apiReady) return
    const remaining = Math.max(0, 4000 - (Date.now() - startedAt))
    const timer = window.setTimeout(() => {
      setPhase('result')
    }, remaining)
    return () => window.clearTimeout(timer)
  }, [apiReady, startedAt])

  const pair = candidate ? PAIRS[candidate.comparison] : undefined
  const before = pair ? recordNumber(candidate, pair.first) : null
  const after = pair ? recordNumber(candidate, pair.second) : null
  const rain = pair ? {
    three: recordNumber(candidate, `${pair.rainfallPrefix}_rainfall_3day_mm`),
    seven: recordNumber(candidate, `${pair.rainfallPrefix}_rainfall_7day_mm`),
    fourteen: recordNumber(candidate, `${pair.rainfallPrefix}_rainfall_14day_mm`),
    maximum: recordNumber(candidate, `${pair.rainfallPrefix}_max_daily_rainfall_14day_mm`),
    wetDays: recordNumber(candidate, `${pair.rainfallPrefix}_wet_days_gt5mm_14day`),
  } : { three: null, seven: null, fourteen: null, maximum: null, wetDays: null }
  const rainfallBars = [rain.three, rain.seven, rain.fourteen].filter((value): value is number => value !== null)
  const maxRainfall = Math.max(...rainfallBars, 1)
  const change = candidate?.nisar_change ?? null
  const plainFinding = change === null ? 'The selected candidate does not have a verified NISAR change value.' : change < 0 ? 'Radar coherence decreased across this candidate region.' : 'Radar coherence increased across this candidate region.'
  const radarSupportsSignal = candidate?.cross_radar_status === 'dual_radar_upper_quartile' || candidate?.cross_radar_status?.includes('s1_upper_quartile')
  const interpretationHeadline = radarSupportsSignal ? 'Independent radar supports the signal' : 'Another radar view is available'
  const interpretationSubtitle = radarSupportsSignal ? 'Sentinel-1 shows an unusual radar pattern at this location.' : 'Sentinel-1 provides additional evidence for the observed radar change.'
  const limitationSubtitle = candidate?.optical_status === 'not_tested'
    ? 'Optical verification was not performed for this candidate, so the radar signal still needs independent validation.'
    : 'Optical verification is inconclusive, so the radar signal still needs independent validation.'
  const temporalValues = OBSERVATIONS.map(([dates, polarization, beforeKey, afterKey]) => ({
    dates,
    polarization,
    before: recordNumber(candidate, beforeKey),
    after: recordNumber(candidate, afterKey),
  }))
  const temporalMax = Math.max(...temporalValues.flatMap(({ before: first, after: second }) => [first ?? 0, second ?? 0]), 0.75)

  if (phase === 'error') {
    return (
      <InvestigationResultShell ref={ref} className="ew-results-card ew-sandhya-results" aria-live="assertive">
        <div className="ew-sandhya-analysis is-error">
          <div className="ew-sandhya-analysis-icon"><CircleAlert size={25} aria-hidden="true" /></div>
          <p className="ew-panel-label">EARTH WHISPER</p>
          <h2 className="ew-results-title">INVESTIGATION UNAVAILABLE</h2>
          <p className="ew-sandhya-analysis-place">{error}</p>
          <button type="button" className="ew-action-btn" onClick={() => setAttempt((value) => value + 1)}>Retry Investigation</button>
        </div>
      </InvestigationResultShell>
    )
  }

  if (phase === 'analysis') {
    return (
      <InvestigationResultShell ref={ref} className="ew-results-card ew-sandhya-results" aria-live="polite">
        <InvestigationScan locationName={location.shortName} progress={scanProgress} />
      </InvestigationResultShell>
    )
  }

  return (
    <InvestigationResultShell ref={ref} className="ew-results-card ew-sandhya-results is-revealed" aria-labelledby="sandhya-results-title">
      <header className="ew-sandhya-header">
        <div>
          <p className="ew-panel-label">EARTH EVENT EVIDENCE</p>
          <h2 id="sandhya-results-title" className="ew-results-title">{location.name}</h2>
          <p className="ew-results-head-coords">{location.coordLabel} <span>· AOI CENTER</span></p>
          <p className="ew-results-head-note">Turning satellite signals into understandable environmental evidence.</p>
        </div>
        <div className="ew-sandhya-header-mark" aria-hidden="true"><RadioTower size={24} /></div>
      </header>

      {error && <p className="ew-sandhya-api-error" role="alert">{error}</p>}

      <div className="ew-sandhya-stat-grid" aria-label="Selected Sandhya candidate result">
        <article><strong>{numberText(change, 4)}</strong><span>NISAR Radar Change</span><small>Coherence change · {pair?.polarization ?? 'comparison loading'} polarization</small></article>
        <article><strong>{dbText(candidate?.s1_median_db)}</strong><span>Sentinel-1 Cross-Check</span><small>Median backscatter change</small></article>
        <article><strong>{candidate?.area_m2 === null || candidate?.area_m2 === undefined ? 'Not available' : `${numberText(candidate.area_m2, 0)} m²`}</strong><span>Investigated Region</span><small>Candidate region</small></article>
        <article className="is-warning"><strong>{candidate ? opticalText(candidate) : 'LOADING'}</strong><span>Verification</span><small>Optical evidence</small></article>
      </div>
      <p className="ew-sandhya-project-context">Sandhya investigation: {payload?.result.candidate_count ?? '—'} radar candidates · {payload?.result.investigated_candidate_count ?? '—'} investigated · Metadata: {payload?.source_status === 'LIVE' ? 'live NASA discovery' : payload?.source_status === 'CACHED_LIVE' ? 'cached NASA discovery' : 'not available'} · Scientific result: verified precomputed evidence</p>

      <section className="ew-sandhya-primary-result" aria-labelledby="sandhya-primary-result-title">
        <div className="ew-sandhya-primary-icon"><BadgeCheck size={21} aria-hidden="true" /></div>
        <div>
          <p className="ew-sandhya-kicker">EARTH WHISPER FINDING</p>
          <h3 id="sandhya-primary-result-title">RADAR CHANGE DETECTED</h3>
          <p>A measurable change in radar coherence was detected across this investigated candidate region.</p>
          <span>Requires independent validation</span>
        </div>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-change-title">
        <SectionTitle number="01" icon={<RadioTower size={16} />} id="sandhya-change-title">WHAT CHANGED?</SectionTitle>
        <p className="ew-sandhya-section-note">Radar observations reveal where the surface signal changed.</p>
        <div className="ew-sandhya-radar-grid">
          <div className="ew-sandhya-comparison-panel"><p className="ew-sandhya-kicker">MEASURED COHERENCE CHANGE</p><strong className="ew-sandhya-large-number">{numberText(change, 4)}</strong><span className="ew-sandhya-value-caption">NISAR radar observation · {pair?.polarization ?? '—'} polarization</span><div className="ew-sandhya-before-after"><Metric label="Observation A" value={numberText(before, 4)} /><span aria-hidden="true">↓</span><Metric label="Observation B" value={numberText(after, 4)} /></div><p className="ew-sandhya-footnote">{pair?.dates ?? 'Acquisition interval unavailable'} · separate interferometric observation pair</p></div>
          <div className="ew-sandhya-crosscheck-panel"><p className="ew-sandhya-kicker">CHANGE CONTEXT</p><div className="ew-sandhya-context-stat"><strong>{candidate?.area_m2 === null || candidate?.area_m2 === undefined ? '—' : `${numberText(candidate.area_m2, 0)} m²`}</strong><span>candidate area</span></div><div className="ew-sandhya-context-stat"><strong>{candidate?.nisar_signal_percentile === null || candidate?.nisar_signal_percentile === undefined ? '—' : percentText(candidate.nisar_signal_percentile * 100)}</strong><span>NISAR statistical isolation percentile</span></div><div className="ew-sandhya-context-stat"><strong>{candidate?.comparison_population_size ?? '—'}</strong><span>comparison population</span></div></div>
        </div>
        <p className="ew-sandhya-plain-finding">{plainFinding}</p>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-crosscheck-title">
        <SectionTitle number="02" icon={<Activity size={16} />} id="sandhya-crosscheck-title">RADAR CROSS-CHECK</SectionTitle>
        <p className="ew-sandhya-section-note">Does another radar observation show an unusual pattern?</p>
        <div className="ew-sandhya-crosscheck-metrics"><MiniStat value={dbText(candidate?.s1_median_db)} label="median change" /><MiniStat value={dbText(candidate?.s1_mean_db)} label="mean change" /><MiniStat value={percentText(candidate?.s1_pct_le_minus3db)} label="pixels ≤ −3 dB" /></div>
        <div className="ew-sandhya-status-callout"><strong>Cross-radar pattern</strong><span>{crossRadarText(candidate?.cross_radar_status)}</span><p>Sentinel-1 provides an independent radar cross-check of the NISAR-selected candidate.</p></div>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-temporal-title">
        <SectionTitle number="03" icon={<Activity size={16} />} id="sandhya-temporal-title">TEMPORAL FINGERPRINT</SectionTitle>
        <p className="ew-sandhya-section-note">Four NISAR observations across the investigation period.</p>
        <div className="ew-sandhya-temporal-graph" aria-label="Four separate NISAR interferometric observation pairs">
          <svg viewBox="0 0 800 245" role="img" aria-labelledby="temporal-graph-title temporal-graph-desc">
            <title id="temporal-graph-title">NISAR temporal fingerprint</title>
            <desc id="temporal-graph-desc">Four separate interferometric pairs with before and after coherence values, distinguished by HH and VV polarization.</desc>
            <defs><marker id="ew-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="currentColor" /></marker></defs>
            <line className="ew-graph-axis" x1="28" y1="190" x2="772" y2="190" />
            {temporalValues.map(({ dates, polarization, before: first, after: second }, index) => {
              const x = 34 + index * 188
              const firstY = first === null ? 190 : 180 - (first / temporalMax) * 120
              const secondY = second === null ? 190 : 180 - (second / temporalMax) * 120
              return <g key={dates} className={`ew-graph-pair is-${polarization.toLowerCase()}`}>
                <text className="ew-graph-pair-number" x={x} y="20">PAIR 0{index + 1}</text>
                <text className="ew-graph-polarization" x={x} y="39">{polarization} POLARIZATION</text>
                <line className="ew-graph-connector" x1={x + 30} y1={firstY} x2={x + 126} y2={secondY} />
                <circle className="ew-graph-point" cx={x + 30} cy={firstY} r="6" />
                <circle className="ew-graph-point" cx={x + 126} cy={secondY} r="6" />
                <text className="ew-graph-value" x={x + 30} y={firstY - 12} textAnchor="middle">{numberText(first, 4)}</text>
                <text className="ew-graph-value" x={x + 126} y={secondY - 12} textAnchor="middle">{numberText(second, 4)}</text>
                <text className="ew-graph-label" x={x + 30} y="211" textAnchor="middle">BEFORE</text>
                <text className="ew-graph-label" x={x + 126} y="211" textAnchor="middle">AFTER</text>
                <text className="ew-graph-date" x={x + 78} y="235" textAnchor="middle">{dates}</text>
              </g>
            })}
          </svg>
        </div>
        <p className="ew-sandhya-footnote">Different interferometric pairs and polarizations are shown separately.</p>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-environment-title">
        <SectionTitle number="04" icon={<CloudRain size={16} />} id="sandhya-environment-title">ENVIRONMENTAL CONTEXT</SectionTitle>
        <div className="ew-sandhya-environment-grid"><div className="ew-sandhya-rain-chart" aria-label="Candidate observation rainfall context">{rainfallBars.map((value, index) => <div className="ew-sandhya-rain-bar" key={`${value}-${index}`} style={{ height: `${Math.max((value / maxRainfall) * 100, 16)}%` }}><span>{['3d', '7d', '14d'][index]}</span></div>)}</div><div className="ew-sandhya-rain-metrics"><MiniStat value={rain.three === null ? '—' : `${numberText(rain.three)} mm`} label="3-day" /><MiniStat value={rain.seven === null ? '—' : `${numberText(rain.seven)} mm`} label="7-day" /><MiniStat value={rain.fourteen === null ? '—' : `${numberText(rain.fourteen)} mm`} label="14-day" /><MiniStat value={rain.maximum === null ? '—' : `${numberText(rain.maximum)} mm`} label="maximum daily" /><MiniStat value={rain.wetDays === null ? '—' : `${numberText(rain.wetDays, 0)} days`} label="wet days >5 mm" /></div></div>
        <p className="ew-sandhya-footnote">Regional rainfall context.{candidate?.rainfall_context_status?.includes('GUNW_023') ? ' GUNW_023 14-day context unavailable.' : ''}</p>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-optical-title">
        <SectionTitle number="05" icon={<Eye size={16} />} id="sandhya-optical-title">OPTICAL VERIFICATION</SectionTitle>
        <div className="ew-sandhya-optical-panel"><div><p className="ew-sandhya-kicker">STATUS</p><strong>{candidate ? opticalText(candidate) : 'LOADING'}</strong></div><div><span>{candidate?.optical.optical_observation_count ?? '—'} regions tested</span><span>{candidate?.optical.optical_max_valid_pixels ?? 0} valid optical pixels</span></div><div><span>26 Jun 2026</span><span>14 Sep 2026</span></div><p>{candidate?.optical_status === 'not_tested' ? 'Optical verification was not performed for this candidate.' : 'Optical verification was attempted, but QA conditions left no valid pixels for verification.'}</p></div>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-coverage-title">
        <SectionTitle number="06" icon={<CheckCircle2 size={16} />} id="sandhya-coverage-title">EVIDENCE COVERAGE</SectionTitle>
        <div className="ew-sandhya-status-grid"><StatusRow label="NISAR" value="Available" tone="ok" /><StatusRow label="Sentinel-1" value="Available" tone="ok" /><StatusRow label="Optical" value={candidate?.optical_status === 'not_tested' ? 'Not tested' : 'Inconclusive'} tone={candidate?.optical_status === 'not_tested' ? 'muted' : 'warn'} /><StatusRow label="Rainfall" value="Context available" tone="ok" /><StatusRow label="Ground truth" value="Not available" tone="muted" /></div>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-finding-title">
        <SectionTitle number="07" icon={<Sparkles size={16} />} id="sandhya-finding-title">EARTH WHISPER FINDING</SectionTitle><p className="ew-sandhya-section-note">Evidence synthesis</p>
        <div className="ew-sandhya-findings-grid"><Finding label="OBSERVATION" headline="Radar change detected" subtitle="NISAR shows a measurable coherence change across this candidate region." /><Finding label="INTERPRETATION" headline={interpretationHeadline} subtitle={interpretationSubtitle} /><Finding label="LIMITATION" headline="Physical cause remains unresolved" subtitle={limitationSubtitle} /></div>
      </section>

      <section className="ew-sandhya-section" aria-labelledby="sandhya-status-title">
        <SectionTitle number="08" icon={<CircleDashed size={16} />} id="sandhya-status-title">EVIDENCE STATUS</SectionTitle>
        <div className="ew-sandhya-uncertainty-grid"><div><strong>Analysis sensitivity</strong><span>{candidate?.anomaly_stability_band === 'low_k_sensitivity' ? 'Low sensitivity to analysis settings' : candidate?.anomaly_stability_band === 'high_k_sensitivity' ? 'High sensitivity to analysis settings' : 'Moderate sensitivity to analysis settings'}</span></div><div><strong>Comparison population</strong><span>{candidate?.comparison === 'HH_023_to_029' ? 'HH 195' : 'VV 16'}</span></div><div><strong>Optical</strong><span>{candidate?.optical_status === 'not_tested' ? 'Not tested' : 'Tested — Inconclusive'}</span></div><div><strong>Ground truth</strong><span>Not available</span></div></div>
        <p className="ew-sandhya-footnote">Radar anomaly values indicate statistical unusualness, not a physical-event probability.</p>
      </section>

      <div className="ew-results-actions ew-sandhya-actions"><button type="button" className="ew-action-btn" onClick={() => window.open(getCaseFilePdfUrl(), '_blank', 'noopener,noreferrer')}>Event Case File</button><button type="button" className="ew-action-btn" onClick={() => document.getElementById('sandhya-status-title')?.scrollIntoView({ behavior: 'smooth' })}>Science Mode</button></div>
    </InvestigationResultShell>
  )
})

function SectionTitle({ number, icon, id, children }: { number: string; icon?: ReactNode; id: string; children: ReactNode }) {
  return <div className="ew-section-head"><span className="ew-section-num">{number}</span>{icon}<h3 id={id} className="ew-section-title">{children}</h3></div>
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="ew-sandhya-metric"><span>{label}</span><strong>{value}</strong></div>
}

function MiniStat({ value, label }: { value: number | string | null | undefined; label: string }) {
  return <div className="ew-sandhya-mini-stat"><strong>{value ?? '—'}</strong><span>{label}</span></div>
}
