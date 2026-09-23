import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { MapPin, Compass, Info } from 'lucide-react'
import { AppShell } from '@/components/app/AppShell'
import { LocationSearchBox } from '@/features/investigation/components/LocationSearchBox'
import { InvestigationMap } from '@/features/investigation/components/InvestigationMap'
import { MapLayerControl, type MapLayerState } from '@/features/investigation/components/MapLayerControl'
import { NisarTimeline } from '@/features/investigation/components/NisarTimeline'
import { CandidatePanel } from '@/features/investigation/components/CandidatePanel'
import type { CandidateAnomaly, LocationSearchResult, NisarObservation } from '@/features/investigation/types'
import { findCandidatesNear, getObservationsForCandidate } from '@/features/investigation/services/nisarService'
import { coordinatesToResult, validateCoordinates } from '@/features/investigation/services/locationService'
import { formatCoordinate } from '@/lib/utils'
import { ROUTES } from '@/lib/constants'

const DEFAULT_LAYERS: MapLayerState = { candidateAnomalies: true }

export function InvestigationMapPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [selectedLocation, setSelectedLocation] = useState<LocationSearchResult | null>(null)
  const [candidates, setCandidates] = useState<CandidateAnomaly[]>([])
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | undefined>()
  const [observations, setObservations] = useState<NisarObservation[]>([])
  const [selectedObservationId, setSelectedObservationId] = useState<string | undefined>()
  const [layers, setLayers] = useState<MapLayerState>(DEFAULT_LAYERS)
  const [loadingCandidates, setLoadingCandidates] = useState(false)

  // Pick up ?lat=&lng=&label= if the welcome screen passed a location.
  useEffect(() => {
    const lat = searchParams.get('lat')
    const lng = searchParams.get('lng')
    if (lat && lng) {
      const parsedLat = Number(lat)
      const parsedLng = Number(lng)
      if (!Number.isNaN(parsedLat) && !Number.isNaN(parsedLng)) {
        setSelectedLocation({
          id: `param-${lat}-${lng}`,
          label: searchParams.get('label') ?? `${parsedLat.toFixed(4)}, ${parsedLng.toFixed(4)}`,
          latitude: parsedLat,
          longitude: parsedLng,
        })
      }
    }
  }, [])

  // Whenever a location is chosen, look for nearby candidates and load their observations.
  useEffect(() => {
    if (!selectedLocation) return

    let cancelled = false
    setLoadingCandidates(true)
    setSelectedCandidateId(undefined)
    setObservations([])
    setSelectedObservationId(undefined)

    findCandidatesNear(selectedLocation.latitude, selectedLocation.longitude).then((found) => {
      if (cancelled) return
      setCandidates(found)
      setLoadingCandidates(false)
    })

    return () => {
      cancelled = true
    }
  }, [selectedLocation])

  // When a candidate is selected, load its NISAR observations for the timeline.
  useEffect(() => {
    const candidate = candidates.find((c) => c.id === selectedCandidateId)
    if (!candidate) {
      setObservations([])
      return
    }
    let cancelled = false
    getObservationsForCandidate(candidate).then((obs) => {
      if (!cancelled) setObservations(obs)
    })
    return () => {
      cancelled = true
    }
  }, [selectedCandidateId, candidates])

  const [manualLat, setManualLat] = useState('')
  const [manualLng, setManualLng] = useState('')
  const [manualError, setManualError] = useState<string | null>(null)

  function handleManualSubmit() {
    const error = validateCoordinates(manualLat, manualLng)
    if (error) {
      setManualError(error)
      return
    }
    setManualError(null)
    setSelectedLocation(coordinatesToResult(Number(manualLat), Number(manualLng)))
  }

  const selectedCandidate = useMemo(
    () => candidates.find((c) => c.id === selectedCandidateId),
    [candidates, selectedCandidateId],
  )

  function handleInvestigate(candidateId: string) {
    navigate(`${ROUTES.investigate}/case/${candidateId}`)
  }

  const mapCenter = selectedLocation ? { lat: selectedLocation.latitude, lng: selectedLocation.longitude } : null

  return (
    <AppShell>
      <div className="mx-auto max-w-7xl px-4 py-8 lg:px-8">
        {/* Location controls */}
        <div className="grid gap-4 lg:grid-cols-[1fr_auto_auto] lg:items-end">
          <div>
            <label className="mb-2 block text-sm font-medium text-[var(--color-navy)]">Search a location</label>
            <LocationSearchBox
              onSelect={(result) => {
                setSelectedLocation(result)
                setManualLat('')
                setManualLng('')
                setManualError(null)
              }}
            />
          </div>
          <div className="flex gap-3">
            <div>
              <label htmlFor="manual-lat" className="mb-2 flex items-center gap-1.5 text-sm font-medium text-[var(--color-navy)]">
                <MapPin size={14} aria-hidden="true" /> Latitude
              </label>
              <input
                id="manual-lat"
                type="text"
                inputMode="decimal"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                placeholder="31.1105"
                className="w-32 rounded-xl border border-[var(--color-sky)] bg-[var(--color-bg)] px-3 py-3 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:border-[var(--color-primary)] focus:bg-white focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="manual-lng" className="mb-2 flex items-center gap-1.5 text-sm font-medium text-[var(--color-navy)]">
                <Compass size={14} aria-hidden="true" /> Longitude
              </label>
              <input
                id="manual-lng"
                type="text"
                inputMode="decimal"
                value={manualLng}
                onChange={(e) => setManualLng(e.target.value)}
                placeholder="77.9373"
                className="w-32 rounded-xl border border-[var(--color-sky)] bg-[var(--color-bg)] px-3 py-3 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:border-[var(--color-primary)] focus:bg-white focus:outline-none"
              />
            </div>
          </div>
          <button
            type="button"
            onClick={handleManualSubmit}
            className="h-[50px] rounded-xl bg-[var(--color-navy)] px-5 text-sm font-medium text-white transition-colors hover:bg-[#052945]"
          >
            Go
          </button>
        </div>
        {manualError && (
          <p className="mt-2 flex items-center gap-1.5 text-sm text-[#B3432B]">
            <Info size={14} aria-hidden="true" /> {manualError}
          </p>
        )}

        {/* Main layout: map + side panel */}
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="relative h-[420px] overflow-hidden rounded-2xl border border-[var(--color-sky)] shadow-[0_20px_50px_-30px_rgba(7,59,102,0.35)] lg:h-[560px]">
            <InvestigationMap
              center={mapCenter}
              candidates={layers.candidateAnomalies ? candidates : []}
              selectedCandidateId={selectedCandidateId}
              onMapClick={(lat, lng) => setSelectedLocation(coordinatesToResult(lat, lng))}
              onCandidateSelect={(id) => setSelectedCandidateId(id)}
              className="h-full w-full"
            />
            <div className="absolute right-3 top-3 z-[400]">
              <MapLayerControl layers={layers} onChange={setLayers} />
            </div>
          </div>

          <div className="flex flex-col gap-6">
            {!selectedLocation && (
              <div className="rounded-2xl border border-dashed border-[var(--color-sky)] bg-white/60 p-6 text-center">
                <p className="text-sm text-[var(--color-muted)]">
                  Search for a place, enter coordinates, or click anywhere on the map to begin.
                </p>
              </div>
            )}

            {selectedLocation && (
              <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-aqua)]">Location</p>
                <h2 className="mt-1 font-display text-xl font-medium text-[var(--color-navy)]">
                  {selectedLocation.label}
                </h2>
                {selectedLocation.context && (
                  <p className="text-sm text-[var(--color-muted)]">{selectedLocation.context}</p>
                )}
                <p className="mt-2 text-sm text-[var(--color-text)]">
                  {formatCoordinate(selectedLocation.latitude, 'lat')}, {formatCoordinate(selectedLocation.longitude, 'lng')}
                </p>
              </div>
            )}

            {selectedLocation && loadingCandidates && (
              <p className="text-sm text-[var(--color-muted)]">Checking for NISAR coverage…</p>
            )}

            {selectedLocation && !loadingCandidates && candidates.length === 0 && (
              <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
                <p className="text-sm text-[var(--color-muted)]">
                  No NISAR observations are available yet for this location in our demonstration catalog. Try the
                  prototype candidate location near 31.1105° N, 77.9373° E.
                </p>
              </div>
            )}

            {candidates.length > 0 && (
              <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-aqua)]">NISAR coverage</p>
                <p className="mt-1 text-sm text-[var(--color-muted)]">
                  {candidates.length} candidate {candidates.length === 1 ? 'anomaly' : 'anomalies'} found nearby.
                  Select one to see its observation timeline.
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {candidates.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelectedCandidateId(c.id)}
                      className={
                        c.id === selectedCandidateId
                          ? 'rounded-full bg-[var(--color-navy)] px-3 py-1.5 text-xs font-medium text-white'
                          : 'rounded-full border border-[var(--color-sky)] px-3 py-1.5 text-xs font-medium text-[var(--color-navy)] hover:border-[var(--color-primary)]'
                      }
                    >
                      {c.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {selectedCandidate && observations.length > 0 && (
              <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
                <p className="mb-4 text-xs font-semibold uppercase tracking-wide text-[var(--color-aqua)]">
                  Observation timeline
                </p>
                <NisarTimeline
                  observations={observations}
                  selectedObservationId={selectedObservationId}
                  onSelect={setSelectedObservationId}
                />
              </div>
            )}

            {selectedCandidate && <CandidatePanel candidate={selectedCandidate} onInvestigate={handleInvestigate} />}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
