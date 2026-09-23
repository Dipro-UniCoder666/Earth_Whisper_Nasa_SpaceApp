import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Compass, ArrowRight, Info } from 'lucide-react'
import { GlassCard } from '@/components/common/GlassCard'
import { Button } from '@/components/common/Button'
import { InvestigationHeader } from '@/components/app/InvestigationHeader'
import { LocationSearchBox } from '@/features/investigation/components/LocationSearchBox'
import type { LocationSearchResult } from '@/features/investigation/types'
import { validateCoordinates, coordinatesToResult } from '@/features/investigation/services/locationService'
import { formatCoordinate } from '@/lib/utils'
import { ROUTES } from '@/lib/constants'
import { DEMO_CANDIDATE_ANOMALIES } from '@/features/investigation/services/nisarDemoData'

const prototypeCandidate = DEMO_CANDIDATE_ANOMALIES[0]

/**
 * The first screen a user sees inside the application. Lets them search a
 * place, type coordinates, or jump straight to the prototype candidate —
 * then routes to /investigate/map, where the real Leaflet map, NISAR
 * timeline, and candidate panel live.
 */
export function InvestigationWelcome() {
  const navigate = useNavigate()
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [error, setError] = useState<string | null>(null)

  function goToLocation(result: LocationSearchResult) {
    const params = new URLSearchParams({
      lat: String(result.latitude),
      lng: String(result.longitude),
      label: result.label,
    })
    navigate(`${ROUTES.investigate}/map?${params.toString()}`)
  }

  function handleBeginInvestigation() {
    const validationError = validateCoordinates(lat, lng)
    if (validationError) {
      setError(validationError)
      return
    }
    setError(null)
    goToLocation(coordinatesToResult(Number(lat), Number(lng)))
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-16 lg:py-24">
      <InvestigationHeader
        eyebrow="Start here"
        title="Where do you want to investigate?"
        subtitle="Choose a place on Earth and explore the changes observed from space."
      />

      <GlassCard padding="lg" className="ew-anim-rise mt-12" style={{ animationDelay: '0.24s' }}>
        <label className="mb-2 block text-sm font-medium text-[var(--color-navy)]">Search a location</label>
        <LocationSearchBox onSelect={goToLocation} />

        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="lat-input" className="mb-2 flex items-center gap-1.5 text-sm font-medium text-[var(--color-navy)]">
              <MapPin size={14} aria-hidden="true" /> Latitude
            </label>
            <input
              id="lat-input"
              type="text"
              inputMode="decimal"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder="e.g. 31.1105"
              className="w-full rounded-xl border border-[var(--color-sky)] bg-[var(--color-bg)] px-4 py-3 text-[var(--color-text)] placeholder:text-[var(--color-muted)] transition-colors focus:border-[var(--color-primary)] focus:bg-white focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="lng-input" className="mb-2 flex items-center gap-1.5 text-sm font-medium text-[var(--color-navy)]">
              <Compass size={14} aria-hidden="true" /> Longitude
            </label>
            <input
              id="lng-input"
              type="text"
              inputMode="decimal"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              placeholder="e.g. 77.9373"
              className="w-full rounded-xl border border-[var(--color-sky)] bg-[var(--color-bg)] px-4 py-3 text-[var(--color-text)] placeholder:text-[var(--color-muted)] transition-colors focus:border-[var(--color-primary)] focus:bg-white focus:outline-none"
            />
          </div>
        </div>

        {error && (
          <p className="mt-3 flex items-center gap-1.5 text-sm text-[#B3432B]">
            <Info size={14} aria-hidden="true" /> {error}
          </p>
        )}

        <div className="mt-7 flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
          <button
            type="button"
            onClick={() => {
              setLat(String(prototypeCandidate.latitude))
              setLng(String(prototypeCandidate.longitude))
              setError(null)
            }}
            className="text-left text-sm font-medium text-[var(--color-primary)] underline-offset-4 hover:underline"
          >
            Use the prototype candidate location
          </button>
          <Button size="lg" icon={<ArrowRight size={18} />} className="w-full sm:w-auto" onClick={handleBeginInvestigation}>
            Begin Investigation
          </Button>
        </div>
      </GlassCard>

      <p className="ew-anim-rise mt-6 text-center text-sm text-[var(--color-muted)]" style={{ animationDelay: '0.32s' }}>
        NISAR coverage shown after you choose a location is demonstration data from our AquaByte QGIS workspace. Today
        you can preview the candidate anomaly at{' '}
        {formatCoordinate(prototypeCandidate.latitude, 'lat')}, {formatCoordinate(prototypeCandidate.longitude, 'lng')}.
      </p>
    </div>
  )
}
