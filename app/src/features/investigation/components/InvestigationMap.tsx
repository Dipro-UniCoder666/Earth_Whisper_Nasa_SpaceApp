import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Circle, useMap, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { CandidateAnomaly } from '@/features/investigation/types'

interface InvestigationMapProps {
  center: { lat: number; lng: number } | null
  initialCenter?: { lat: number; lng: number }
  initialZoom?: number
  fitBounds?: [[number, number], [number, number]]
  candidates: CandidateAnomaly[]
  selectedCandidateId?: string
  onMapClick?: (lat: number, lng: number) => void
  onCandidateSelect?: (candidateId: string) => void
  className?: string
}

const DEFAULT_CENTER: [number, number] = [20, 0]
const DEFAULT_ZOOM = 2
const SELECTED_ZOOM = 10

/** Small circular pin, custom-drawn so we never depend on Leaflet's default marker image paths. */
function buildLocationIcon(variant: 'selected' | 'candidate', isActive = false) {
  const color = variant === 'selected' || isActive ? '#18B7C9' : '#073B66'
  const size = variant === 'selected' ? 30 : 26
  return L.divIcon({
    className: 'ew-map-marker',
    html: `
      <svg width="${size}" height="${size}" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="15" cy="15" r="9" fill="${color}" stroke="#FFFFFF" stroke-width="2.5" />
        ${variant === 'selected' || isActive ? `<circle cx="15" cy="15" r="13" fill="${color}" fill-opacity="0.16" />` : ''}
      </svg>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function MapClickHandler({ onMapClick }: { onMapClick?: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onMapClick?.(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

/** Recenters/zooms the map imperatively when `center` changes, without remounting the map. */
function MapRecenter({
  center,
  bounds,
}: {
  center: { lat: number; lng: number } | null
  bounds?: [[number, number], [number, number]]
}) {
  const map = useMap()
  const hasCenteredRef = useRef(false)

  useEffect(() => {
    if (bounds) {
      map.flyToBounds(bounds, { duration: 1.1, padding: [24, 24] })
      hasCenteredRef.current = true
      return
    }
    if (!center) return
    map.flyTo([center.lat, center.lng], hasCenteredRef.current ? Math.max(map.getZoom(), SELECTED_ZOOM) : SELECTED_ZOOM, {
      duration: 1.1,
    })
    hasCenteredRef.current = true
  }, [bounds, center, map])

  return null
}

export function InvestigationMap({
  center,
  initialCenter,
  initialZoom,
  fitBounds,
  candidates,
  selectedCandidateId,
  onMapClick,
  onCandidateSelect,
  className,
}: InvestigationMapProps) {
  const selectedIcon = useMemo(() => buildLocationIcon('selected'), [])

  return (
    <div className={className}>
      <MapContainer
        center={initialCenter ? [initialCenter.lat, initialCenter.lng] : DEFAULT_CENTER}
        zoom={initialZoom ?? DEFAULT_ZOOM}
        scrollWheelZoom
        className="h-full w-full"
        style={{ background: '#EAF6FF' }}
        aria-label="Earth Whisper investigation map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onMapClick={onMapClick} />
        <MapRecenter center={center} bounds={fitBounds} />

        {center && <Marker position={[center.lat, center.lng]} icon={selectedIcon} />}

        {candidates.map((candidate) => {
          const isSelected = candidate.id === selectedCandidateId
          const icon = buildLocationIcon('candidate', isSelected)
          const radiusMeters = candidate.areaSqKm ? Math.sqrt((candidate.areaSqKm * 1_000_000) / Math.PI) : 3000

          return (
            <div key={candidate.id}>
              <Circle
                center={[candidate.latitude, candidate.longitude]}
                radius={radiusMeters}
                pathOptions={{
                  color: isSelected ? '#18B7C9' : '#0B5EA8',
                  weight: isSelected ? 2 : 1.4,
                  fillColor: '#18B7C9',
                  fillOpacity: isSelected ? 0.18 : 0.08,
                }}
                eventHandlers={{
                  click: () => onCandidateSelect?.(candidate.id),
                }}
              />
              <Marker
                position={[candidate.latitude, candidate.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onCandidateSelect?.(candidate.id),
                }}
              />
            </div>
          )
        })}
      </MapContainer>
    </div>
  )
}
