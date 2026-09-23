import { useRef, useState } from 'react'
import { MapPin } from 'lucide-react'
import { InvestigationMap } from '@/features/investigation/components/InvestigationMap'
import { InvestigationResults } from '@/features/investigation/components/InvestigationResults'
import { SecondaryPageLayout } from '@/components/layout/SecondaryPageLayout'
import { MONDA_INVESTIGATION } from '@/features/investigation/data/investigationSite'


const INVESTIGATION_BUTTONS = [
  { id: MONDA_INVESTIGATION.id, label: MONDA_INVESTIGATION.shortName },
  { id: 'investigation-2', label: 'Investigation 2' },
  { id: 'investigation-3', label: 'Investigation 3' },
  { id: 'investigation-4', label: 'Investigation 4' },
]

export function InvestigationPage() {
  const [selectedLocation, setSelectedLocation] = useState<{
    name: string
    latitude: string
    longitude: string
  } | null>(null)
  const [investigationStarted, setInvestigationStarted] = useState(false)
  const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number } | null>(null)
  const resultsRef = useRef<HTMLElement | null>(null)

  function selectMondaInvestigation() {
    setSelectedLocation({
      name: MONDA_INVESTIGATION.name,
      latitude: MONDA_INVESTIGATION.latitude,
      longitude: MONDA_INVESTIGATION.longitude,
    })
    setMapCenter({ ...MONDA_INVESTIGATION.coords })
  }

  function beginInvestigation() {
    if (!selectedLocation) return
    setInvestigationStarted(true)
    window.setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 80)
  }

  return (
    <SecondaryPageLayout>
      <div className="page-container py-6 md:py-7">
        <div className="mb-4">
          <p className="eyebrow" style={{ color: '#18B7C9' }}>
            EARTH EVENT INVESTIGATION
          </p>
          <h1 className="mt-2 text-3xl font-bold md:text-5xl">
            Investigate an <span style={{ color: '#18B7C9' }}>Earth Event</span>
          </h1>
          <p className="mt-2 max-w-xl text-[var(--color-text-muted)]">
            Choose a place and discover what Earth-observation data reveals.
          </p>
        </div>

        <section className="ew-panel" aria-labelledby="investigation-location">
          <div className="ew-panel-map">
            <InvestigationMap
              center={mapCenter}
              initialCenter={MONDA_INVESTIGATION.coords}
              initialZoom={7}
              candidates={[]}
              className="h-full w-full"
            />
            {selectedLocation && (
              <div className="ew-map-label" aria-hidden="true">
                <span className="ew-map-label-place">{MONDA_INVESTIGATION.name}</span>
                <span className="ew-map-label-coords">{MONDA_INVESTIGATION.coordLabel}</span>
              </div>
            )}
          </div>

          <div className="ew-location-selector" aria-labelledby="investigation-location">
            <p id="investigation-location" className="ew-panel-label">
              AVAILABLE INVESTIGATIONS
            </p>
            <div className="ew-location-options" aria-label="Available investigations">
              {INVESTIGATION_BUTTONS.map((investigation) => {
                const isActive = investigation.id === MONDA_INVESTIGATION.id

                const cardClass = isActive
                  ? selectedLocation
                    ? 'ew-location-card is-active is-selected'
                    : 'ew-location-card is-active'
                  : 'ew-location-card is-placeholder'

                return (
                  <button
                    key={investigation.id}
                    type="button"
                    className={cardClass}
                    aria-current={isActive && selectedLocation ? 'true' : undefined}
                    onClick={isActive ? selectMondaInvestigation : undefined}
                  >
                    <span className="ew-location-card-name">{investigation.label}</span>
                    {isActive && (
                      <span className="ew-location-card-sub">{MONDA_INVESTIGATION.coordLabel}</span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          <section className="ew-location-section" aria-labelledby="location-section-title">
            <div className="ew-location-section-head">
              <p id="location-section-title" className="ew-location-section-title">
                <MapPin size={13} aria-hidden="true" />
                LOCATION
              </p>
              <p className="ew-location-section-sub">Selected investigation location</p>
            </div>

            <div className="ew-location-selected">
              <p className="ew-location-selected-kicker">Selected Location</p>
              <p
                className={
                  selectedLocation
                    ? 'ew-location-selected-name'
                    : 'ew-location-selected-name is-empty'
                }
              >
                {selectedLocation?.name ?? 'No location selected'}
              </p>
              {selectedLocation && (
                <p className="ew-location-selected-coords">{MONDA_INVESTIGATION.coordLabel}</p>
              )}
            </div>

            <div className="ew-coord-display">
              <div>
                <span className="ew-coord-display-label">Latitude</span>
                <span
                  className={
                    selectedLocation ? 'ew-coord-display-value' : 'ew-coord-display-value is-empty'
                  }
                >
                  {selectedLocation?.latitude ?? '—'}
                </span>
              </div>
              <div>
                <span className="ew-coord-display-label">Longitude</span>
                <span
                  className={
                    selectedLocation ? 'ew-coord-display-value' : 'ew-coord-display-value is-empty'
                  }
                >
                  {selectedLocation?.longitude ?? '—'}
                </span>
              </div>
            </div>
          </section>

          <div className="ew-begin-row">
            <button
              type="button"
              className="ew-cta"
              onClick={beginInvestigation}
              disabled={!selectedLocation}
            >
              <span className="ew-cta-title">Begin Investigation</span>
            </button>
          </div>

        </section>

        {investigationStarted && (
          <div className="ew-results-region">
            <InvestigationResults ref={resultsRef} site={MONDA_INVESTIGATION} />
          </div>
        )}
      </div>
    </SecondaryPageLayout>
  )
}
