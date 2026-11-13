import { useEffect, useMemo, useState } from 'react'
import {
  AlertCircle, ArrowLeft, ArrowRight, Brain, CheckCircle2, ChevronDown,
  ExternalLink, FileText, Info, Layers3, MapPin, Maximize2, Waves, X,
} from 'lucide-react'
import { GherProofMap } from './GherProofMap'
import { DHARA_DATA_MODE, GHERPROOF_API, getGherProofJson } from './services/gherproofApi'
import type { EvidenceRecord, FisheriesReport, GherProofData, RasterLayer } from './services/gherproofApi'
import './gherproof-phase9.css'

type MapView = 'satellite' | 'context' | 'ai'
type Preview = { id: string; secondId?: string; thirdId?: string; title: string; date: string; caption: string; category?: string; rgb?: boolean }
type LayerMetadata = { crs?: string | null; width?: number; height?: number; count?: number; nodata?: number | null; bounds?: number[]; descriptions?: Array<string | null> }
const EMPTY_RECORDS: EvidenceRecord[] = []

const REQUIRED_PREVIEWS: Preview[] = [
  { id: 's2-true-colour-2026-01-10', title: 'Before the reported incident', date: 'January 10, 2026', caption: 'Sentinel-2 natural colour (B04/B03/B02), surface-reflectance composite with the registered clear-pixel mask.', category: 'Satellite observation · true colour', rgb: true },
  { id: 's2-true-colour-2026-01-20', title: 'After the reported incident', date: 'January 20, 2026', caption: 'Sentinel-2 natural colour (B04/B03/B02), surface-reflectance composite with the registered clear-pixel mask.', category: 'Satellite observation · true colour', rgb: true },
  { id: 'prediction-scratch-2026-01-12-probability', secondId: 'prediction-pretrained-2026-01-12-probability', title: 'AI screening comparison', date: 'January 12, 2026', caption: 'Scratch-trained and pretrained model outputs are shown separately; both are exploratory and lack local reference-label validation.', category: 'Model predictions · exploratory' },
  { id: 'optical-weakref-temporal-temporal_change', secondId: 'disagreement-disagreement_2026-01-12_2026-01-24_rel12_ascending-xor', title: 'Water changes and model disagreement', date: 'January 10–20, 2026 · optical comparison', caption: 'Optical change candidates are not confirmed water. The Sentinel-1 XOR layer shows model disagreement, not a measured error rate.', category: 'Derived optical candidates + model comparison' },
]

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

function getBounds(geo: Record<string, unknown> | null): string | null {
  if (!geo) return null
  const points: number[][] = []
  const walk = (value: unknown) => {
    if (Array.isArray(value) && typeof value[0] === 'number' && typeof value[1] === 'number') points.push(value as number[])
    else if (Array.isArray(value)) value.forEach(walk)
  }
  const features = Array.isArray(geo.features) ? geo.features.map(asObject) : []
  for (const feature of features) walk(asObject(feature.geometry).coordinates)
  if (features.length === 0) walk(asObject(geo.geometry).coordinates)
  if (points.length === 0) return null
  const xs = points.map((point) => point[0])
  const ys = points.map((point) => point[1])
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)].join(',')
}

function formatNumber(value: unknown): string {
  return typeof value === 'number' && Number.isFinite(value) ? new Intl.NumberFormat('en-US').format(value) : 'Unavailable'
}

function imageUrl(id: string, bounds: string | null, width: number, rgb = false, staticPreviews?: Record<string, string>): string {
  if (DHARA_DATA_MODE === 'demo') return staticPreviews?.[`${id}|1`] ?? ''
  if (!bounds) return ''
  const query = new URLSearchParams({ bbox: bounds, width: String(width) })
  if (rgb) query.set('rgb', 'true')
  return `${GHERPROOF_API}/layers/${encodeURIComponent(id)}/preview.png?${query}`
}

function findLayer(layers: RasterLayer[], records: EvidenceRecord[], id: string): RasterLayer | undefined {
  return layers.find((layer) => layer.evidence_id === id && records.some((record) => record.evidence_id === id))
}

export function GherProofWorkspace({ data, failures, onRetry, onBack }: { data: GherProofData; failures: string[]; onRetry: () => void; onBack: () => void }) {
  const screening = data.fisheriesScreening
  const report = data.report
  const records = data.evidence?.records ?? EMPTY_RECORDS
  const layers = useMemo(() => {
    const selected = new Map<string, RasterLayer>()
    for (const layer of data.layers?.layers ?? []) {
      if (layer.asset === 'derived' || !selected.has(layer.evidence_id)) selected.set(layer.evidence_id, layer)
    }
    return [...selected.values()]
  }, [data.layers])
  const geographicData = data.geography
  const bounds = useMemo(() => getBounds(geographicData), [geographicData])
  const [view, setView] = useState<MapView>('satellite')
  const [selectedLayerId, setSelectedLayerId] = useState('s2-true-colour-2026-01-10')
  const [opacity, setOpacity] = useState(0.82)
  const [nisarBand, setNisarBand] = useState<1 | 2>(1)
  const [metadataState, setMetadataState] = useState<{ id: string; value: LayerMetadata } | null>(null)
  const [layerInfoOpen, setLayerInfoOpen] = useState(false)
  const [technicalOpen, setTechnicalOpen] = useState(false)
  const [mapError, setMapError] = useState<string | null>(null)
  const [lightbox, setLightbox] = useState<Preview | null>(null)
  const [reportOpen, setReportOpen] = useState(false)

  const mapChoices = useMemo(() => {
    if (view === 'satellite') return layers.filter((layer) => layer.evidence_category === 'verified_satellite_observation' || layer.evidence_id.startsWith('nisar-gcov-change-') || /^s2-(true-colour-2026-01-(10|20)|2026-01-(10|20)-B08)$/.test(layer.evidence_id))
    if (view === 'context') return layers.filter((layer) => layer.evidence_category === 'historical_landcover_context')
    return layers.filter((layer) => ['model_prediction', 'model_comparison', 'uncertainty_layer', 'optical_weak_reference'].includes(layer.evidence_category) && (layer.evidence_id.includes('2026-01-12') || layer.evidence_id.includes('temporal_change') || layer.evidence_id.startsWith('disagreement-')))
  }, [layers, view])

  const preferredLayerId = view === 'satellite' ? 's2-true-colour-2026-01-10' : view === 'context' ? 'clark-2022-aquaculture-context' : 'optical-weakref-temporal-temporal_change'
  const activeLayerId = mapChoices.some((layer) => layer.evidence_id === selectedLayerId) ? selectedLayerId : (mapChoices.find((layer) => layer.evidence_id === preferredLayerId)?.evidence_id ?? mapChoices[0]?.evidence_id ?? '')
  const metadata = metadataState?.id === activeLayerId ? metadataState.value : null
  const demoMode = DHARA_DATA_MODE === 'demo'
  const staticPreviews = data.demo?.previews ?? {}
  const staticPreviewBounds = data.demo?.preview_bounds ?? {}

  useEffect(() => {
    if (!activeLayerId) return
    if (demoMode) {
      const value = data.demo?.layer_metadata[activeLayerId] as LayerMetadata | undefined
      setMetadataState(value ? { id: activeLayerId, value } : null)
      return
    }
    const controller = new AbortController()
    getGherProofJson<LayerMetadata>(`/layers/${encodeURIComponent(activeLayerId)}`, controller.signal)
      .then((value) => setMetadataState({ id: activeLayerId, value }))
      .catch(() => setMetadataState(null))
    return () => controller.abort()
  }, [activeLayerId, data.demo, demoMode])

  useEffect(() => {
    const onEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setLightbox(null); setReportOpen(false) }
    }
    window.addEventListener('keydown', onEscape)
    return () => window.removeEventListener('keydown', onEscape)
  }, [])

  const counts = screening?.optical_change_screening.candidate_counts_grid_cells ?? null
  const modelNames = [...new Set((screening?.model_evidence.per_acquisition_comparisons ?? []).map((row) => String(row.model ?? '')).filter(Boolean))]
  const comparedModels = modelNames.length || data.status?.model_outputs?.models?.length || 0
  const predictions = data.predictions?.models?.length ?? 0
  const clarkRecord = records.find((record) => record.evidence_id === 'clark-2022-aquaculture-context')
  const clarkMetadata = asObject(clarkRecord?.metadata)
  const clarkAreaKm2 = clarkMetadata.pond_aquaculture_area_km2_in_covered_footprint
  const clarkCoverageKm2 = asObject(clarkRecord?.spatial_coverage).valid_covered_aoi_area_km2
  const worldcoverRecord = records.find((record) => record.evidence_id === 'worldcover-2021-landcover-context')
  const worldcoverOverlap = asObject(worldcoverRecord?.metadata).new_water_candidate_overlap
  const croplandOverlap = asObject(asObject(worldcoverOverlap).overlap_by_class)['40']
  const waterOverlap = asObject(asObject(worldcoverOverlap).overlap_by_class)['80']
  const nisarPreviews: Preview[] = layers
    .filter((layer) => layer.evidence_id === 'nisar-gcov-2026-10-23-track170-ascending-validated' || layer.evidence_id === 'nisar-gcov-change-2026-10-23-to-2026-11-04-track170')
    .map((layer) => ({
      id: layer.evidence_id,
      title: layer.title,
      date: layer.acquisition_date ?? 'Oct 23 → Nov 4, 2026 comparison',
      category: layer.evidence_id.startsWith('nisar-gcov-change-') ? 'Derived backscatter comparison · exploratory' : 'NISAR L-band GCOV · validated product maturity',
      caption: layer.evidence_id.startsWith('nisar-gcov-change-')
        ? 'Signed change in gamma0 power, displayed in dB. This is a backscatter comparison, not a water-probability layer.'
        : 'October 23, 2026 regional observation · 10 m Frequency A · HH/HV gamma0 power.',
    }))
  const selectedRecord = records.find((record) => record.evidence_id === activeLayerId)
  const currentOverlayIds = useMemo(() => activeLayerId ? [activeLayerId] : [], [activeLayerId])
  const friendlyFailures: Record<string, string> = {
    evidence: 'evidence catalogue', layers: 'map layers', scenes: 'acquisition details', predictions: 'AI comparison details',
    weakReference: 'optical screening details', comparisons: 'model comparison details', coverage: 'coverage details', geography: 'provisional study-area map',
    fisheriesSummary: 'incident summary', fisheriesFindings: 'screening findings', fisheriesPriorities: 'inspection priorities', report: 'investigation report',
    'map evidence registry': 'map evidence',
  }
  const visibleFailures = failures.map((failure) => friendlyFailures[failure] ?? 'optional evidence').filter((value, index, values) => values.indexOf(value) === index)

  const switchView = (next: MapView) => setView(next)

  return <section className="gp9-results" aria-label="DHARA fisheries incident screening results">
    <div className="gp9-heading-row">
      <div className="gp9-heading-icon" aria-hidden="true"><Waves size={25}/></div>
      <div className="gp9-heading-copy">
        <div className="gp9-breadcrumb">EARTH WHISPER <span>/</span> DHARA <span>/</span> INVESTIGATION RESULTS</div>
        <h1>DHARA: Fisheries Incident Screening</h1>
        <p>Sujatpur Pallimangal Fisheries Enclosure <i>·</i> Manirampur, Jashore <i>·</i> Jan 14, 2026 (reported, inferred)</p>
      </div>
      <span className="gp9-status"><span/>EXPLORATORY REGIONAL SCREENING</span>
    </div>

    {demoMode && <div className="gp9-screening-scope"><strong>Prepared demonstration data</strong><span>Static snapshot from registered local evidence; no hosted analysis backend is connected. {data.demo?.generated_at_utc ? `Prepared ${new Date(data.demo.generated_at_utc).toLocaleDateString()}.` : ''}</span></div>}
    {visibleFailures.length > 0 && <div className="gp9-warning" role="status"><AlertCircle size={17}/><span>Some optional content is unavailable: {visibleFailures.join(', ')}.</span><button onClick={onRetry}>Retry</button></div>}

    <div className="gp9-metrics" aria-label="Investigation summary metrics">
      <Metric icon={<Waves/>} tone="cyan" value={formatNumber(counts?.possible_new_water_candidate)} title="Possible new-water signals" description="Optical candidates · Jan 10–20 · 20 m grid"/>
      <Metric icon={<Waves/>} tone="blue" value={formatNumber(counts?.possible_water_loss_candidate)} title="Possible water decrease" description="Optical candidates · Jan 10–20 · 20 m grid"/>
      <Metric icon={<Layers3/>} tone="green" value={typeof clarkAreaKm2 === 'number' ? `${clarkAreaKm2.toFixed(2)} km²` : 'Unavailable'} title="Historical pond-aquaculture class" description={typeof clarkCoverageKm2 === 'number' ? `Clark 2022 · ${clarkCoverageKm2.toFixed(1)} km² valid footprint` : 'Clark 2022 historical context'}/>
      <Metric icon={<Brain/>} tone="amber" value={predictions || comparedModels ? String(predictions || comparedModels) : 'Unavailable'} title="AI screening models" description="Scratch and pretrained predictions remain separate" />
    </div>
    <div className="gp9-screening-scope"><strong>Screening scope</strong><span>This case combines January 2026 satellite observations, historical land-cover context and exploratory AI across a provisional regional search area. It guides further fisheries investigation; it does not confirm damage to an individual enclosure.</span></div>

    <div className="gp9-main-grid">
      <section className="gp9-map-card" aria-label="Interactive evidence map">
        <div className="gp9-map-toolbar">
          <div className="gp9-tabs" role="tablist" aria-label="Map views">
            {([['satellite', 'Satellite View'], ['context', 'Historical Context'], ['ai', 'AI Screening']] as const).map(([key, label]) => <button key={key} type="button" role="tab" aria-selected={view === key} className={view === key ? 'is-active' : ''} onClick={() => switchView(key)}>{label}</button>)}
          </div>
          {activeLayerId.startsWith('nisar-gcov-') && <label className="gp9-nisar-band">Polarization <select value={nisarBand} onChange={(event) => setNisarBand(Number(event.target.value) as 1 | 2)} aria-label="Choose NISAR polarization layer"><option value={1}>HHHH</option><option value={2}>HVHV</option></select></label>}
          <label className="gp9-layer-select"><Layers3 size={15}/><span className="sr-only">Choose a map evidence layer</span><select value={activeLayerId} onChange={(event) => setSelectedLayerId(event.target.value)} disabled={mapChoices.length === 0}>
            {mapChoices.length === 0 && <option value="">No registered layers available</option>}
            {mapChoices.map((layer) => <option key={layer.evidence_id} value={layer.evidence_id}>{layer.acquisition_date ?? 'Undated'} · {layer.title}</option>)}
          </select><ChevronDown size={14}/></label>
        </div>
        <div className="gp9-map-frame">
          {geographicData ? <GherProofMap layers={layers} layerIds={currentOverlayIds} opacity={opacity} band={activeLayerId.startsWith('nisar-gcov-') ? nisarBand : 1} aoi={geographicData} onError={setMapError} demoMode={demoMode} staticPreviews={staticPreviews} staticPreviewBounds={staticPreviewBounds}/> : <div className="gp9-map-unavailable"><MapPin/><span>Study-area geography is unavailable.</span></div>}
          <div className="gp9-map-label"><MapPin size={15}/><span>Provisional regional study area<small>Not official village or enclosure boundaries</small></span></div>
          <MapLegend view={view} selectedLayerId={activeLayerId}/>
        </div>
        <div className="gp9-map-footer">
        <div className="gp9-map-layer-caption"><strong>{selectedRecord?.title ?? mapChoices[0]?.title ?? 'Prepared evidence'}</strong><span>{selectedRecord?.acquisition_date ?? mapChoices[0]?.acquisition_date ?? 'Date unavailable'}{selectedRecord?.crs ? ` · ${selectedRecord.crs}` : ''}{activeLayerId.startsWith('s2-true-colour-') ? ' · True colour RGB' : ''}</span>{activeLayerId.startsWith('nisar-gcov-change-') ? <span>Derived · Oct 23 → Nov 4, 2026 · {(nisarBand === 1 ? 'HHHH' : 'HVHV')} · dB ratio of gamma0 power · {activeLayerId.includes('frequencyB') ? '80 m' : '10 m'}</span> : activeLayerId.startsWith('nisar-gcov-') && <span>NASA/ISRO NISAR · VALIDATED · Ascending relative orbit 170 · {nisarBand === 1 ? 'HHHH' : 'HVHV'} · linear gamma0 power · {activeLayerId.includes('frequencyB') ? '80 m Frequency B' : '10 m Frequency A'}</span>}</div>
          {selectedRecord?.source_dataset?.includes('NISAR') && <p className="gp9-nisar-note"><strong>Radar observations:</strong> Sentinel-1 C-band and NISAR L-band are separate measurements. NISAR uses a different radar wavelength and can add complementary information about surface and vegetation conditions. These validated October–November 2026 scenes are later regional observations, not evidence for the January incident; no Sentinel-1 model uses NISAR values.</p>}
          <div className="gp9-map-actions">
            <label title="Adjust the selected evidence overlay opacity">Opacity <input type="range" min="15" max="100" value={Math.round(opacity * 100)} onChange={(event) => setOpacity(Number(event.target.value) / 100)} aria-label="Evidence layer opacity"/></label>
            <button type="button" onClick={() => setLayerInfoOpen((open) => !open)} aria-expanded={layerInfoOpen}><Info size={15}/> Layer info</button>
          </div>
        </div>
        {mapError && <div className="gp9-map-error" role="status">This map layer is unavailable: {mapError}</div>}
        {layerInfoOpen && <div className="gp9-layer-info"><strong>{activeLayerId || 'No layer selected'}</strong><span>{metadata?.crs ?? selectedRecord?.crs ?? 'CRS unavailable'} · {metadata?.width ?? '—'} × {metadata?.height ?? '—'} px · NoData {metadata?.nodata ?? 'not reported'}</span><p>{selectedRecord?.limitations?.join(' ') ?? 'Display stretch is for visualization only; interpretation follows the linked evidence record.'}</p></div>}
      </section>

      <aside className="gp9-insights" aria-label="Investigation interpretation and next steps">
        <Insight icon={<Brain/>} tone="blue" title="What satellite screening found">
          {screening?.optical_change_screening.status === 'available_automated_weak_reference'
            ? `Sentinel-2 comparisons from ${screening.optical_change_screening.pre_date} and ${screening.optical_change_screening.post_date} flagged ${formatNumber(counts?.possible_new_water_candidate)} possible new-water cells and ${formatNumber(counts?.possible_water_loss_candidate)} possible water-decrease cells across the regional grid. These are candidate signals, not confirmed flooding.`
            : 'Satellite screening counts are unavailable for this incident. Use the registered observations and map layers to review available evidence.'}
        </Insight>
        <Insight icon={<Layers3/>} tone="green" title="Historical fisheries context">
          {typeof clarkAreaKm2 === 'number'
            ? `Clark Labs mapped ${clarkAreaKm2.toFixed(2)} km² of pond-aquaculture class in 2022 within ${typeof clarkCoverageKm2 === 'number' ? `${clarkCoverageKm2.toFixed(2)} km² of valid raster coverage` : 'the available raster footprint'} inside the provisional study area. This is historical context, not a current farm inventory or enclosure boundary.`
            : 'Clark 2022 aquaculture class statistics are unavailable. ESA WorldCover 2021 remains available as general historical land-cover context.'}
          ESA WorldCover 2021 can also help orient review across the provisional regional study area. Its classes are historical context, not current ground truth or a verified fisheries asset map.
          {typeof asObject(croplandOverlap).candidate_cells === 'number' && <span className="gp9-insight-extra">Of the possible-new-water candidate cells, {formatNumber(asObject(croplandOverlap).candidate_cells)} overlap the 2021 cropland class and {formatNumber(asObject(waterOverlap).candidate_cells)} overlap its permanent-water class. These are context overlays only.</span>}
          <span className="gp9-insight-extra">Clark Labs / Clark University 2022 · CC BY 4.0; displayed for this non-commercial research demonstration under the source page's non-commercial-use terms. The source archive is not redistributed.</span>
        </Insight>
        <Insight icon={<CheckCircle2/>} tone="purple" title="Suggested Fisheries Officer review">
          <ul><li>Review the candidate locations and compare both Sentinel-2 dates.</li><li>Compare highlighted cells with historical aquaculture and land-cover context.</li><li>Check embankments and nearby drainage channels where the site is identified.</li><li>Record inside/outside water conditions and any directly observed fish escape or damage.</li></ul>
          <span className="gp9-insight-extra">These are suggested checks; no visit, inspection or fish loss is represented as completed.</span>
        </Insight>
      </aside>
    </div>

    <section className="gp9-evidence" aria-labelledby="gp9-evidence-title">
      <div className="gp9-evidence-heading"><div><span className="gp9-kicker">REGISTERED PROJECT OUTPUTS</span><h2 id="gp9-evidence-title">Key Evidence</h2></div><span>Open a preview for details and provenance</span></div>
      <div className="gp9-evidence-layout">
        <div className="gp9-preview-grid">{REQUIRED_PREVIEWS.map((preview) => <EvidenceCard key={preview.id} preview={preview} bounds={bounds} records={records} layers={layers} staticPreviews={staticPreviews} onOpen={setLightbox}/>)}</div>
        <button className="gp9-report-button" type="button" onClick={() => setReportOpen(true)} disabled={!report}><FileText size={18}/><span>View Investigation Report</span><ArrowRight size={17}/></button>
      </div>
      {!report && <div className="gp9-report-unavailable" role="status">The fisheries report service did not return a report. <button onClick={onRetry}>Retry report loading</button></div>}
    </section>

    {nisarPreviews.length > 0 && <section className="gp9-evidence" aria-labelledby="gp9-nisar-title">
      <div className="gp9-evidence-heading"><div><span className="gp9-kicker">SEPARATE SENSOR · LATER REGIONAL OBSERVATIONS</span><h2 id="gp9-nisar-title">Additional NISAR Regional Observations</h2></div><span>October 23 and November 4, 2026 · not evidence for the January incident</span></div>
      <p className="gp9-nisar-note">These are later regional NISAR observations, acquired after the reported January incident. They provide additional L-band radar context, not evidence of the January fisheries incident. NISAR gamma0 intensity and change are not water probability. Frequency B (80 m) layers remain available in the map selector.</p>
      <div className="gp9-preview-grid">{nisarPreviews.map((preview) => <EvidenceCard key={preview.id} preview={preview} bounds={bounds} records={records} layers={layers} staticPreviews={staticPreviews} onOpen={setLightbox}/>)}</div>
    </section>}

    <details className="gp9-limitations"><summary>Evidence limitations</summary><p>The exact Pallimangal enclosure boundary is not identified, so enclosure exposure cannot be calculated. The incident and date are reported/inferred and have not been independently confirmed. Candidate-cell counts are not measured flood area. The two models remain separate exploratory predictions with no local human-label validation. Historical Clark and WorldCover classes may differ from 2026 conditions. The evidence does not confirm fish escape, mortality, breach location or financial damage.</p><p>{(screening?.limitations ?? []).join(' ')}</p><button type="button" onClick={() => setTechnicalOpen((open) => !open)} aria-expanded={technicalOpen}>Technical details <ChevronDown size={13}/></button>{technicalOpen && <span>Sentinel-2 comparison: {screening?.optical_change_screening.pre_date ?? 'date unavailable'} → {screening?.optical_change_screening.post_date ?? 'date unavailable'} · {screening?.optical_change_screening.pixel_resolution_m ?? '—'} m grid. Registered satellite observations: {screening?.observations.length ?? 0}. AI comparison records: {screening?.model_evidence.per_acquisition_comparisons.length ?? 0}; model selection: none.</span>}</details>
    <div className="gp9-bottom-actions"><button type="button" className="gp9-back-link" onClick={onBack}><ArrowLeft size={15}/> Back to investigation</button><a href={demoMode ? (data.demo?.evidence_report_url ?? '/data/dhara-evidence-report.json') : `${GHERPROOF_API}/evidence-report`} target="_blank" rel="noreferrer"><ExternalLink size={14}/> Evidence registry report</a></div>

    {lightbox && <EvidenceLightbox preview={lightbox} bounds={bounds} records={records} staticPreviews={staticPreviews} onClose={() => setLightbox(null)}/>}
    {reportOpen && report && <ReportDialog report={report} layers={layers} aoi={geographicData} demoMode={demoMode} staticPreviews={staticPreviews} staticPreviewBounds={staticPreviewBounds} onClose={() => setReportOpen(false)}/>}
  </section>
}

function Metric({ icon, tone, value, title, description }: { icon: React.ReactNode; tone: string; value: string; title: string; description: string }) {
  return <article className={`gp9-metric gp9-${tone}`}><span className="gp9-metric-icon" aria-hidden="true">{icon}</span><div className="gp9-metric-content"><strong className="gp9-metric-value">{value}</strong><h2>{title}</h2><p>{description}</p></div></article>
}

function Insight({ icon, tone, title, children }: { icon: React.ReactNode; tone: string; title: string; children: React.ReactNode }) {
  return <section className={`gp9-insight gp9-${tone}`}><span className="gp9-insight-icon" aria-hidden="true">{icon}</span><div><h2>{title}</h2><div className="gp9-insight-copy">{children}</div></div></section>
}

function MapLegend({ view, selectedLayerId }: { view: MapView; selectedLayerId: string }) {
  const entries: string[][] = view === 'context'
    ? selectedLayerId.includes('worldcover')
      ? [['#f096ff', 'Cropland · 2021'], ['#0064c8', 'Permanent water · 2021'], ['#0096a0', 'Herbaceous wetland · 2021'], ['#006400', 'Tree cover · 2021'], ['#fa0000', 'Built-up · 2021']]
      : [['#19c5aa', 'Pond aquaculture · Clark 2022'], ['#2773be', 'Mapped water · 2022'], ['#5096aa', 'Coastal wetland · 2022'], ['#8a8f71', 'Other landcover · 2022']]
    : view === 'ai'
      ? selectedLayerId.includes('temporal_change')
        ? [['#69747e', 'Invalid / missing'], ['#1c5b7e', 'Persistent-water candidate'], ['#38c7e5', 'Possible increase in water indicators'], ['#e84cb0', 'Possible decrease in water indicators'], ['#74847c', 'Stable non-water indicator'], ['#979ea5', 'Uncertain change']]
        : selectedLayerId.includes('disagreement')
          ? [['#36bfe4', 'Model outputs differ'], ['#69747e', 'Agreement / unavailable']]
          : [['#36bfe4', 'Exploratory model prediction'], ['#69747e', 'No usable observations']]
      : selectedLayerId.startsWith('nisar-gcov-change-')
        ? [['#377eb8', 'Nov 4 lower than Oct 23'], ['#eeeeee', 'Near zero change'], ['#d73027', 'Nov 4 higher than Oct 23'], ['#6b7781', 'Gamma0 change only · not water probability']]
        : selectedLayerId.startsWith('nisar-gcov-')
          ? [['#72a7cb', 'NISAR L-band GCOV · linear gamma0 power'], ['#6b7781', 'Display stretch · not water probability']]
      : selectedLayerId.startsWith('s2-')
        ? [['#7bb77d', 'Sentinel-2 false-colour composite'], ['#4caef0', 'B08 / B04 / B03 display']]
        : [['#72a7cb', 'Sentinel-1 radar · display stretch'], ['#6b7781', 'Provisional regional search extent']]
  const attribution = view === 'context' ? selectedLayerId.includes('worldcover') ? '© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.' : '©2024 Clark Labs, Clark University · CC BY 4.0 · non-commercial use only.' : selectedLayerId.startsWith('nisar-gcov-') ? 'NASA/ISRO NISAR via ASF DAAC · visual display only' : 'Historical and automated evidence is not current ground truth or confirmed incident impact.'
  return <div className="gp9-legend"><strong>{view === 'context' ? 'Historical context' : view === 'ai' ? 'Screening key' : 'Map key'}</strong>{entries.map(([color, text]) => <span key={text}><i style={{ backgroundColor: color }}/>{text}</span>)}<small>{attribution}</small></div>
}

function EvidenceCard({ preview, bounds, records, layers, staticPreviews, onOpen }: { preview: Preview; bounds: string | null; records: EvidenceRecord[]; layers: RasterLayer[]; staticPreviews: Record<string, string>; onOpen: (preview: Preview) => void }) {
  const ids = [preview.id, preview.secondId, preview.thirdId].filter((id): id is string => Boolean(id))
  const availableIds = ids.filter((id) => Boolean(findLayer(layers, records, id)))
  const [failed, setFailed] = useState<Record<string, boolean>>({})
  const hasAvailablePreview = availableIds.some((id) => !failed[id])
  return <button type="button" className="gp9-preview-card" onClick={() => hasAvailablePreview && onOpen(preview)} disabled={!hasAvailablePreview} aria-label={`${preview.title}, ${preview.date}`}>
    <div className="gp9-preview-image">
      {availableIds.filter((id) => !failed[id]).map((id) => <img key={id} className={availableIds.length > 1 ? 'gp9-preview-secondary' : ''} style={availableIds.length > 1 ? { width: `${100 / availableIds.length}%` } : undefined} src={imageUrl(id, bounds, 480, Boolean(preview.rgb && id === preview.id), staticPreviews)} alt={`${preview.title}; ${id}`} onError={() => setFailed((previous) => ({ ...previous, [id]: true }))}/>)}
      {!hasAvailablePreview && <span className="gp9-preview-unavailable">Registered preview unavailable</span>}
      {preview.rgb && <span className="gp9-image-tag">{preview.id.startsWith('s2-true-colour-') ? 'NATURAL COLOUR' : 'FALSE COLOUR'}</span>}
      {preview.id.includes('prediction') && <span className="gp9-image-tag">EXPLORATORY</span>}
      <span className="gp9-preview-zoom"><Maximize2 size={13}/> Enlarge</span>
    </div>
    <span className="gp9-preview-date">{preview.date}</span><strong>{preview.title}</strong>{preview.category && <span className="gp9-preview-category">{preview.category}</span>}<small>{preview.caption}</small>
  </button>
}

function EvidenceLightbox({ preview, bounds, records, staticPreviews, onClose }: { preview: Preview; bounds: string | null; records: EvidenceRecord[]; staticPreviews: Record<string, string>; onClose: () => void }) {
  const [failed, setFailed] = useState<Record<string, boolean>>({})
  const ids = [preview.id, preview.secondId, preview.thirdId].filter((id): id is string => Boolean(id) && records.some((record) => record.evidence_id === id))
  const evidence = ids.map((id) => records.find((record) => record.evidence_id === id)).filter((record): record is EvidenceRecord => Boolean(record))
  return <div className="gp9-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><section className="gp9-lightbox" role="dialog" aria-modal="true" aria-labelledby="gp9-lightbox-title">
    <header><div><span>{preview.date}</span><h2 id="gp9-lightbox-title">{preview.title}</h2></div><button type="button" onClick={onClose} aria-label="Close preview"><X/></button></header>
    <div className={`gp9-lightbox-images ${ids.length > 1 ? 'has-two' : ''} ${ids.length > 2 ? 'has-many' : ''}`}>{ids.map((id) => <div key={id} className="gp9-lightbox-image">{findEvidence(evidence, id) && !failed[id] ? <img src={imageUrl(id, bounds, 1100, Boolean(preview.rgb && id === preview.id), staticPreviews)} alt={`${preview.title}; evidence ${id}`} onError={() => setFailed((previous) => ({ ...previous, [id]: true }))}/> : <span>Preview unavailable for {id}</span>}<small>{id}</small></div>)}</div>
    <p>{preview.caption} Display is a visualization of stored raster values, not an independently validated event finding.</p>
    <div className="gp9-provenance"><strong>Evidence provenance</strong>{evidence.map((item) => <span key={item.evidence_id}>{item.evidence_id} · {item.confidence_or_validation_status} · {item.source_dataset ?? item.evidence_category}{item.acquisition_date ? ` · ${item.acquisition_date}` : ''}</span>)}</div>
  </section></div>
}

function findEvidence(records: EvidenceRecord[], id: string): EvidenceRecord | undefined { return records.find((record) => record.evidence_id === id) }

function ignoreMapError(): void {}

function ReportDialog({ report, layers, aoi, onClose, demoMode = false, staticPreviews, staticPreviewBounds }: { report: FisheriesReport; layers: RasterLayer[]; aoi: Record<string, unknown> | null; onClose: () => void; demoMode?: boolean; staticPreviews?: Record<string, string>; staticPreviewBounds?: Record<string, string> }) {
  const screening = report.water_change_screening
  const counts = screening.candidate_counts_grid_cells ?? {}
  const models = report.ai_screening
  const context = asObject(report.fisheries_context)
  const clark = asObject(context.clark_2022)
  const worldcover = asObject(context.worldcover_2021)
  const landOverlap = asObject(worldcover.possible_new_water_candidate_overlap)
  const overlapClasses = asObject(landOverlap.overlap_by_class)
  const cropland = asObject(overlapClasses['40'])
  const historicWater = asObject(overlapClasses['80'])
  const fisheriesStats = asObject(context.department_of_fisheries)
  return <div className="gp9-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><article className="gp9-report-dialog" role="dialog" aria-modal="true" aria-labelledby="gp9-report-title">
    <header><div><span>DHARA · EXPLORATORY INVESTIGATION</span><h2 id="gp9-report-title">{report.title}</h2></div><button type="button" onClick={onClose} aria-label="Close investigation report"><X/></button></header>
    <div className="gp9-report-content">
      <section><h3>Reported incident</h3><p><strong>{report.incident.title}</strong></p><p>{report.incident.description}</p><p>{report.incident.administrative_location.site_description ?? 'Reported Sujatpur, Manirampur, Jashore; exact site boundary remains unresolved.'}</p><p>Incident date: {report.incident.incident_date ?? 'unavailable'} ({report.incident.incident_date_status}). This is source-reported information, not independent field confirmation.</p><ul>{report.evidence_sources.map((source, index) => <li key={`${source.source_name}-${index}`}>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.source_name}</a> : source.source_name}: {source.claim} ({source.claim_status})</li>)}</ul></section>
      <section><h3>Provisional regional study-area map</h3><div className="gp9-report-map">{aoi && <GherProofMap layers={layers} layerIds={[report.study_area_map.candidate_change_layer_id]} opacity={0.92} aoi={aoi} onError={ignoreMapError} demoMode={demoMode} staticPreviews={staticPreviews} staticPreviewBounds={staticPreviewBounds}/>}</div><p>Regional search extent only; it does not identify Pallimangal, a village boundary or an enclosure boundary.</p></section>
      <section><h3>Available satellite observations</h3>{report.satellite_observations.length ? <ul>{report.satellite_observations.map((item) => <li key={`${item.sensor}-${item.acquisition_date}`}>{item.sensor} · {item.acquisition_date ?? 'date unavailable'}{item.limitations.length ? ` — ${item.limitations.join(' ')}` : ''}</li>)}</ul> : <p>No satellite observations were returned.</p>}</section>
      <section><h3>Possible water-change screening</h3><p>{screening.interpretation ?? 'Optical comparison is unavailable.'}</p><p>{screening.pre_date ?? 'Earlier date unavailable'} → {screening.post_date ?? 'Later date unavailable'} · {screening.pixel_resolution_m ?? '—'} m grid. Possible increase: {formatNumber(counts.possible_new_water_candidate)} cells. Possible decrease: {formatNumber(counts.possible_water_loss_candidate)} cells. Grid counts are not area or confirmed flooding.</p></section>
      <section><h3>Historical aquaculture and land-cover context</h3><p>Clark Labs Bangladesh Land Cover and Change Maps 2022 v1 class 3 is <strong>Pond aquaculture</strong>. The AOI-masked raster contains {formatNumber(asObject(clark.pond_aquaculture_class_3_area_km2_in_covered_footprint))} km² of this historical class across {formatNumber(asObject(clark.valid_covered_aoi_area_km2))} km² of valid coverage. This partial footprint is not a 2026 farm inventory or enclosure boundary.</p><p>ESA WorldCover 2021 class overlap: {formatNumber(cropland.candidate_cells)} possible-new-water candidates on historical cropland and {formatNumber(historicWater.candidate_cells)} on its permanent-water class. These land classes are historical context, not water truth for January 2026.</p><p>Attribution: Clark Labs, Clark University, Bangladesh Land Cover and Change Maps 2022 v1 (©2024), CC BY 4.0; use limited to non-commercial purposes. ESA WorldCover attribution: {String(worldcover.attribution ?? 'ESA WorldCover 2021 attribution unavailable')}</p></section>
      <section><h3>AI findings and model differences</h3><p>{models.overall_interpretation}</p>{report.findings.length > 0 && <ul>{report.findings.map((finding) => <li key={finding.finding_id}><strong>{finding.category.replaceAll('_', ' ')}:</strong> {finding.explanation}</li>)}</ul>}</section>
      <section><h3>Fisheries inspection recommendations</h3><ul>{report.recommended_inspection_checks.map((check) => <li key={check}>{check}</li>)}</ul>{report.inspection_priorities.map((priority) => <p key={priority.priority}><strong>{priority.priority.replaceAll('_', ' ')}:</strong> {priority.recommended_action} {priority.not_an_emergency_instruction ? 'This is not an emergency instruction.' : ''}</p>)}</section>
      <section><h3>Regional fisheries statistics (optional context)</h3>{typeof fisheriesStats.aquaculture_production_lakh_metric_tonnes === 'number' ? <p>Bangladesh Department of Fisheries reports {fisheriesStats.aquaculture_production_lakh_metric_tonnes} lakh metric tonnes of national aquaculture production for {String(fisheriesStats.year)}. This national figure is not an estimate for Manirampur, Pallimangal or this incident. <a href={String(fisheriesStats.source_url)} target="_blank" rel="noreferrer">Source</a></p> : <p>No geographic fisheries statistic is included in this report.</p>}</section>
      <section><h3>Data sources and licenses</h3><ul><li><a href={String(clark.source_url ?? 'https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/')} target="_blank" rel="noreferrer">Clark Labs Bangladesh Land Cover and Change Maps 2022 v1</a> · CC BY 4.0, use limited to non-commercial purposes; the source archive is not redistributed.</li><li><a href={String(worldcover.source_url ?? 'https://esa-worldcover.org/en/data-access')} target="_blank" rel="noreferrer">ESA WorldCover 2021 v200</a> · CC BY 4.0; attribution shown above.</li><li><a href="https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory" target="_blank" rel="noreferrer">JRC Global Surface Water Monthly History</a> · documented through 2021; no JRC raster was acquired or used in these results.</li>{report.evidence_sources.map((source, index) => <li key={`${source.source_name}-${index}`}>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.source_name}</a> : source.source_name}: {source.claim} ({source.claim_status})</li>)}</ul></section>
      <section className="gp9-report-unknowns"><h3>Readiness and remaining uncertainties</h3><p>Model readiness: {report.readiness.model_readiness}; human reference labels: {report.readiness.human_reference_status}; impact quantification: {report.readiness.impact_quantification}; Pallimangal boundary: {report.readiness.pallimangal_geometry_status}.</p><p>Enclosure exposure: {report.asset_exposure[0]?.status ?? 'not_assessable'}. Fish escape, mortality, production and financial loss are unavailable.</p><ul>{report.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></section>
    </div>
    <footer><span>Generated {new Date(report.generated_at_utc).toLocaleString()}</span><button type="button" onClick={onClose}>Close report</button></footer>
  </article></div>
}
