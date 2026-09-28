import { useRef, useState } from 'react'
import { MapPin } from 'lucide-react'
import { InvestigationMap } from '@/features/investigation/components/InvestigationMap'
import { InvestigationResults } from '@/features/investigation/components/InvestigationResults'
import { SandhyaInvestigationResults } from '@/features/candidates/components/SandhyaInvestigationResults'
import { SecondaryPageLayout } from '@/components/layout/SecondaryPageLayout'
import { mondaInvestigationAdapter } from '@/features/investigation/adapters/mondaInvestigationAdapter'
import { useInvestigationLifecycle } from '@/features/investigation/hooks/useInvestigationLifecycle'
import {
  MONDA_INVESTIGATION,
  SANDHYA_INVESTIGATION,
  type InvestigationLocation,
} from '@/features/investigation/data/investigationSite'


const INVESTIGATION_BUTTONS = [
  { ...SANDHYA_INVESTIGATION, number: '01' },
  {
    id: MONDA_INVESTIGATION.id,
    shortName: MONDA_INVESTIGATION.shortName,
    subtitle: MONDA_INVESTIGATION.name,
    name: MONDA_INVESTIGATION.name,
    coords: MONDA_INVESTIGATION.coords,
    latitude: MONDA_INVESTIGATION.latitude,
    longitude: MONDA_INVESTIGATION.longitude,
    coordLabel: MONDA_INVESTIGATION.coordLabel,
    number: '02',
  },
  { id: 'investigation-3', shortName: 'Investigation 3', subtitle: 'Reserved investigation', number: '03' },
  { id: 'investigation-4', shortName: 'Investigation 4', subtitle: 'Reserved investigation', number: '04' },
]

export function InvestigationPage() {
  const [selectedLocation, setSelectedLocation] = useState<InvestigationLocation | null>(null)
  const [investigationStarted, setInvestigationStarted] = useState(false)
  const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number } | null>(null)
  const resultsRef = useRef<HTMLElement | null>(null)
  const mondaLifecycle = useInvestigationLifecycle(mondaInvestigationAdapter)

  function selectInvestigation(investigation: InvestigationLocation) {
    setSelectedLocation(investigation)
    setMapCenter({ ...investigation.coords })
    setInvestigationStarted(false)
    mondaLifecycle.reset()
  }

  function beginInvestigation() {
    if (!selectedLocation) return
    setInvestigationStarted(true)
    if (selectedLocation.id === MONDA_INVESTIGATION.id) mondaLifecycle.start()
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
              initialCenter={SANDHYA_INVESTIGATION.coords}
              initialZoom={7}
              fitBounds={selectedLocation?.aoiBounds}
              candidates={[]}
              className="h-full w-full"
            />
            {selectedLocation && (
              <div className="ew-map-label" aria-hidden="true">
                <span className="ew-map-label-place">{selectedLocation.name}</span>
                <span className="ew-map-label-coords">
                  {selectedLocation.id === SANDHYA_INVESTIGATION.id ? 'AOI center ' : ''}
                  {selectedLocation.coordLabel}
                </span>
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
                const isSandhya = investigation.id === SANDHYA_INVESTIGATION.id
                const isSelected = investigation.id === selectedLocation?.id
                const isAvailable = isSandhya || isActive

                const cardClass = isAvailable
                  ? isSelected
                    ? 'ew-location-card is-active is-selected'
                    : 'ew-location-card is-active'
                  : 'ew-location-card is-placeholder'
                const cardName = isSandhya
                  ? SANDHYA_INVESTIGATION.shortName
                  : isActive
                    ? MONDA_INVESTIGATION.shortName
                    : investigation.shortName

                return (
                  <button
                    key={investigation.id}
                    type="button"
                    className={cardClass}
                    aria-current={isSelected ? 'true' : undefined}
                    onClick={isAvailable ? () => selectInvestigation(investigation as InvestigationLocation) : undefined}
                  >
                    <span className="ew-location-card-name">{cardName}</span>
                    {isAvailable && 'coordLabel' in investigation && (
                      <span className="ew-location-card-sub">{investigation.coordLabel}</span>
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
                <p className="ew-location-selected-coords">
                  {selectedLocation.id === SANDHYA_INVESTIGATION.id ? 'AOI center ' : ''}
                  {selectedLocation.coordLabel}
                </p>
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
              disabled={!selectedLocation || (selectedLocation.id === SANDHYA_INVESTIGATION.id && investigationStarted)}
            >
              <span className="ew-cta-title">Begin Investigation</span>
            </button>
          </div>

        </section>

        {investigationStarted && (
          <div className="ew-results-region">
            {selectedLocation?.id === SANDHYA_INVESTIGATION.id ? (
              <SandhyaInvestigationResults ref={resultsRef} location={selectedLocation} />
            ) : mondaLifecycle.lifecycle.data &&
              (mondaLifecycle.lifecycle.status === 'scanning' || mondaLifecycle.lifecycle.status === 'ready') ? (
              <InvestigationResults
                ref={resultsRef}
                site={mondaLifecycle.lifecycle.data.site}
                lifecycleStatus={mondaLifecycle.lifecycle.status}
                scanProgress={mondaLifecycle.progress}
              />
            ) : null}
          </div>
        )}
      </div>
    </SecondaryPageLayout>
  )
}
