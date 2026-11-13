import { useEffect, useMemo, useState } from 'react'
import { GeoJSON, ImageOverlay, MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet'
import type { LatLngBoundsExpression, LatLngExpression } from 'leaflet'
import { Maximize2, Minus, Plus, RotateCcw } from 'lucide-react'
import { GHERPROOF_API } from './services/gherproofApi'
import type { RasterLayer } from './services/gherproofApi'
import './gherproof.css'

type Overlay = { evidenceId: string; url: string; bounds: LatLngBoundsExpression }

function MapControls({ bounds }: { bounds: LatLngBoundsExpression | null }) {
  const map = useMap()
  return <div className="gp-map-controls" aria-label="Map controls">
    <button type="button" aria-label="Zoom in" onClick={() => map.zoomIn()}><Plus size={17}/></button>
    <button type="button" aria-label="Zoom out" onClick={() => map.zoomOut()}><Minus size={17}/></button>
    <button type="button" aria-label="Reset map extent" onClick={() => bounds && map.fitBounds(bounds, { padding: [36, 36] })}><RotateCcw size={15}/></button>
    <button type="button" aria-label="Toggle map fullscreen" onClick={() => { const container = map.getContainer(); if (document.fullscreenElement === container) void document.exitFullscreen(); else void container.requestFullscreen?.() }}><Maximize2 size={15}/></button>
  </div>
}

function FitStudyExtent({ bounds }: { bounds: LatLngBoundsExpression | null }) {
  const map = useMap()
  useEffect(() => { if (bounds) map.fitBounds(bounds, { padding: [36, 36] }) }, [bounds, map])
  return null
}

function ExtentEvents({ onChange }: { onChange: (bounds: string) => void }) {
  const map = useMapEvents({
    moveend: () => { const b = map.getBounds(); onChange([b.getWest(), b.getSouth(), b.getEast(), b.getNorth()].map((x) => x.toFixed(6)).join(',')) },
    zoomend: () => { const b = map.getBounds(); onChange([b.getWest(), b.getSouth(), b.getEast(), b.getNorth()].map((x) => x.toFixed(6)).join(',')) },
  })
  return null
}

function geographyBounds(geo: Record<string, unknown> | null): LatLngBoundsExpression | null {
  if (!geo) return null
  const points: number[][] = []
  const walk = (value: unknown) => {
    if (Array.isArray(value) && typeof value[0] === 'number' && typeof value[1] === 'number') points.push(value as number[])
    else if (Array.isArray(value)) value.forEach(walk)
  }
  const features = Array.isArray(geo.features) ? geo.features as Array<Record<string, unknown>> : []
  for (const feature of features) walk((feature.geometry as Record<string, unknown> | undefined)?.coordinates)
  if (!features.length) walk((geo.geometry as Record<string, unknown> | undefined)?.coordinates)
  if (!points.length) return null
  const xs = points.map((point) => point[0])
  const ys = points.map((point) => point[1])
  return [[Math.min(...ys), Math.min(...xs)], [Math.max(...ys), Math.max(...xs)]]
}

function boundsToExtent(bounds: LatLngBoundsExpression | null): string {
  if (!bounds) return ''
  const [[south, west], [north, east]] = bounds as [[number, number], [number, number]]
  return [west, south, east, north].map((coordinate) => coordinate.toFixed(6)).join(',')
}

export function GherProofMap({ layers, layerIds, opacity, band = 1, aoi, onError }: { layers: RasterLayer[]; layerIds: string[]; opacity: number; band?: 1 | 2; aoi: Record<string, unknown> | null; onError: (message: string | null) => void }) {
  const studyBounds = useMemo(() => geographyBounds(aoi), [aoi])
  const [extent, setExtent] = useState(() => boundsToExtent(studyBounds))
  const [overlays, setOverlays] = useState<Overlay[]>([])

  useEffect(() => {
    if (!layerIds.length || !extent) return
    const controller = new AbortController()
    const objectUrls: string[] = []
    const selectedLayers = layerIds.map((id) => layers.find((layer) => layer.evidence_id === id)).filter((layer): layer is RasterLayer => Boolean(layer))
    if (selectedLayers.length === 0) return
    const load = async () => {
      try {
        const next = await Promise.all(selectedLayers.map(async (layer) => {
          const query = new URLSearchParams({ bbox: extent, width: '1000' })
          if (layer.evidence_id.startsWith('nisar-gcov-')) query.set('band', String(band))
          if (layer.evidence_id.startsWith('s2-true-colour-') || layer.evidence_id === 's2-2026-01-10-B08' || layer.evidence_id === 's2-2026-01-20-B08') query.set('rgb', 'true')
          const response = await fetch(`${GHERPROOF_API}/layers/${encodeURIComponent(layer.evidence_id)}/preview.png?${query}`, { signal: controller.signal })
          if (!response.ok) throw new Error(`${layer.evidence_id} (HTTP ${response.status})`)
          const rawBounds = (response.headers.get('X-Preview-Bounds-WGS84') ?? '').split(',').map(Number)
          if (rawBounds.length !== 4 || rawBounds.some(Number.isNaN)) throw new Error(`${layer.evidence_id} returned no map bounds`)
          const url = URL.createObjectURL(await response.blob())
          objectUrls.push(url)
          return { evidenceId: layer.evidence_id, url, bounds: [[rawBounds[1], rawBounds[0]], [rawBounds[3], rawBounds[2]]] as LatLngBoundsExpression }
        }))
        if (!controller.signal.aborted) { setOverlays(next); onError(null) }
      } catch (error) {
        if (!controller.signal.aborted) { setOverlays([]); onError(error instanceof Error ? error.message : 'Raster preview failed') }
      }
    }
    void load()
    return () => { controller.abort(); objectUrls.forEach(URL.revokeObjectURL) }
  }, [band, extent, layerIds, layers, onError])

  return <MapContainer center={[23.0, 89.4] as LatLngExpression} zoom={9} zoomControl={false} className="gp-leaflet-map" preferCanvas>
    <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
    {overlays.filter((overlay) => layerIds.includes(overlay.evidenceId)).map((overlay) => <ImageOverlay key={overlay.evidenceId} url={overlay.url} bounds={overlay.bounds} opacity={opacity} className={overlay.evidenceId.includes('temporal_change') ? 'gp-temporal-overlay' : ''}/>)}
    {aoi && <GeoJSON data={aoi as never} style={{ color: '#86a7b6', weight: 1.5, dashArray: '7 6', fillColor: '#526b78', fillOpacity: 0.025 }}/>}
    <FitStudyExtent bounds={studyBounds}/><ExtentEvents onChange={setExtent}/><MapControls bounds={studyBounds}/>
  </MapContainer>
}
