import { useEffect, useState } from 'react'
import { DHARA_CONTEXT_IMAGE, DHARA_DATA_MODE, GHERPROOF_API } from './services/gherproofApi'
import { CircleMarker, ImageOverlay, MapContainer, Polygon, TileLayer, useMapEvents } from 'react-leaflet'
import type { LatLngExpression, LatLngTuple } from 'leaflet'

type BoundaryStatus = 'not_delineated' | 'candidate' | 'under_review' | 'verified'
type Feature = { type: 'Feature'; geometry: { type: 'Polygon'; coordinates: number[][][] }; properties?: Record<string, unknown> }
type BoundaryResponse = { status: BoundaryStatus; feature: Feature | null; context_bounds_wgs84: [[number, number], [number, number]] | null }

const panel: React.CSSProperties = { border: '1px solid rgba(127,190,199,.2)', borderRadius: 14, background: 'rgba(5,23,34,.82)', padding: 22 }
const muted = 'rgba(184,204,216,.72)'

function AddVertex({ onAdd }: { onAdd: (point: LatLngTuple) => void }) {
  useMapEvents({ click: (event) => onAdd([event.latlng.lat, event.latlng.lng]) })
  return null
}

export function BoundaryReviewMap() {
  const [loaded, setLoaded] = useState<BoundaryResponse | null>(null)
  const [points, setPoints] = useState<LatLngTuple[]>([])
  const [status, setStatus] = useState<'candidate' | 'under_review' | 'verified'>('candidate')
  const [evidence, setEvidence] = useState('')
  const [reviewer, setReviewer] = useState('')
  const [reviewedAt, setReviewedAt] = useState('')
  const [confidence, setConfidence] = useState('low')
  const [message, setMessage] = useState('Loading boundary status…')
  const [busy, setBusy] = useState(false)

  async function load() {
    const response = await fetch(`${GHERPROOF_API}/boundary`)
    if (!response.ok) throw new Error(`Boundary API returned ${response.status}`)
    const body = await response.json() as BoundaryResponse
    setLoaded(body)
    if (body.feature?.geometry.type === 'Polygon') {
      const ring = body.feature.geometry.coordinates[0] ?? []
      setPoints(ring.slice(0, -1).map(([lng, lat]) => [lat, lng] as LatLngTuple))
      const saved = body.feature.properties?.status
      if (saved === 'candidate' || saved === 'under_review' || saved === 'verified') setStatus(saved)
    }
    setMessage(body.status === 'not_delineated' ? 'No enclosure geometry is stored. Click the map to begin a human-reviewed candidate trace.' : `Loaded ${body.status} boundary version.`)
  }

  useEffect(() => {
    if (DHARA_DATA_MODE === 'demo') {
      setLoaded({ status: 'not_delineated', feature: null, context_bounds_wgs84: null })
      setMessage('Static demonstration mode is read-only. No verified enclosure geometry is available.')
      return
    }
    load().catch((error: Error) => setMessage(error.message))
  }, [])

  function updatePoint(index: number, axis: 0 | 1, value: number) {
    setPoints((current) => current.map((point, i) => i === index ? (axis === 0 ? [value, point[1]] : [point[0], value]) : point))
  }

  async function save() {
    setBusy(true); setMessage('Saving boundary and provenance…')
    try {
      if (points.length < 3) throw new Error('Add at least three vertices to make a polygon.')
      const ring = points.map(([lat, lng]) => [lng, lat])
      ring.push(ring[0])
      const evidenceItems = evidence.split('\n').map((line) => line.trim()).filter(Boolean).map((description) => ({ description }))
      const body: Feature = { type: 'Feature', geometry: { type: 'Polygon', coordinates: [ring] }, properties: {
        status, evidence: evidenceItems, reviewer: reviewer.trim() || null,
        reviewed_at: reviewedAt ? new Date(reviewedAt).toISOString() : null, confidence,
      } }
      const response = await fetch(`${GHERPROOF_API}/boundary`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const result = await response.json()
      if (!response.ok) throw new Error(result.detail ?? `Save failed (${response.status})`)
      setLoaded(result); setMessage(`Saved version ${result.provenance.active_version} as ${result.status}.`)
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not save boundary.') }
    finally { setBusy(false) }
  }

  const polygon: LatLngExpression[] = points
  const stroke = status === 'verified' ? '#65d49e' : status === 'under_review' ? '#ffbf69' : '#ff8b67'
  return <section style={{ ...panel, marginBottom: 18 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
      <div><h2 style={{ marginTop: 0 }}>Pallimangal boundary review</h2><p style={{ color: muted, lineHeight: 1.55 }}>The orange frame is a broad locality context, not an enclosure. Trace only when you have a credible target reference; this map does not establish the farm location.</p></div>
      <strong style={{ color: stroke, textTransform: 'capitalize' }}>Boundary: {loaded?.status ?? 'loading'}</strong>
    </div>
    {DHARA_DATA_MODE === 'demo' ? <div role="status" style={{ padding: 24, border: '1px solid rgba(255,191,105,.35)', borderRadius: 10, color: muted }}>No Pallimangal enclosure boundary is included in the hosted demonstration. Boundary editing and saving require the local backend.</div> : <MapContainer center={[23.005, 89.225]} zoom={11} scrollWheelZoom style={{ height: 440, borderRadius: 10, margin: '14px 0' }}>
      <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {loaded?.context_bounds_wgs84 && <ImageOverlay url={DHARA_CONTEXT_IMAGE} bounds={loaded.context_bounds_wgs84} opacity={0.72} />}
      <AddVertex onAdd={(point) => setPoints((current) => [...current, point])} />
      {points.length >= 3 && <Polygon positions={polygon} pathOptions={{ color: stroke, fillColor: stroke, fillOpacity: status === 'verified' ? 0.18 : 0.1, dashArray: status === 'verified' ? undefined : '7 6' }} />}
      {points.map((point, index) => <CircleMarker key={`${index}-${point[0]}-${point[1]}`} center={point} radius={6} pathOptions={{ color: '#fff', fillColor: stroke, fillOpacity: 1 }} />)}
    </MapContainer>}
    <p style={{ color: muted, fontSize: 13 }}>Click to add vertices. Edit coordinates below; the current polygon outline is candidate/review geometry only.</p>
    {DHARA_DATA_MODE !== 'demo' && <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 8, maxHeight: 170, overflowY: 'auto' }}>
      {points.map(([lat, lng], index) => <div key={index} style={{ display: 'flex', gap: 5 }}>
        <label style={{ color: muted, fontSize: 11 }}>Lat <input aria-label={`Vertex ${index + 1} latitude`} type="number" step="0.000001" value={lat} onChange={(event) => updatePoint(index, 0, Number(event.target.value))} style={{ width: 104 }} /></label>
        <label style={{ color: muted, fontSize: 11 }}>Lon <input aria-label={`Vertex ${index + 1} longitude`} type="number" step="0.000001" value={lng} onChange={(event) => updatePoint(index, 1, Number(event.target.value))} style={{ width: 104 }} /></label>
        <button type="button" onClick={() => setPoints((current) => current.filter((_, i) => i !== index))} aria-label={`Remove vertex ${index + 1}`}>×</button>
      </div>)}
    </div>}
    {DHARA_DATA_MODE !== 'demo' && <>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 10, marginTop: 16 }}>
      <label>Review state<select value={status} onChange={(event) => setStatus(event.target.value as typeof status)}><option value="candidate">Candidate</option><option value="under_review">Under review</option><option value="verified">Verified</option></select></label>
      <label>Confidence<select value={confidence} onChange={(event) => setConfidence(event.target.value)}><option>low</option><option>medium</option><option>high</option></select></label>
      <label>Reviewer<input value={reviewer} onChange={(event) => setReviewer(event.target.value)} placeholder="Required for review/verification" /></label>
      <label>Review date/time<input type="datetime-local" value={reviewedAt} onChange={(event) => setReviewedAt(event.target.value)} /></label>
    </div>
    <label style={{ display: 'block', marginTop: 10 }}>Evidence supporting this trace<textarea value={evidence} onChange={(event) => setEvidence(event.target.value)} rows={3} placeholder="One source or field observation per line. Include dates and links/record IDs where available." style={{ display: 'block', width: '100%' }} /></label>
    <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 12 }}><button type="button" onClick={save} disabled={busy}>{busy ? 'Saving…' : 'Save boundary version'}</button><button type="button" onClick={() => setPoints([])}>Clear vertices</button><span role="status" style={{ color: muted }}>{message}</span></div>
    </>}
  </section>
}
