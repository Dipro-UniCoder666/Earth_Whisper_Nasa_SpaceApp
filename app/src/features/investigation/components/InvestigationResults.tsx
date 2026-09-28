import { forwardRef, useState } from 'react'
import type { InvestigationSite } from '@/features/investigation/data/investigationSite'
import { downloadCaseFile } from '@/features/investigation/caseFile/buildCaseFile'
import type { InvestigationLifecycleStatus } from '@/features/investigation/models/investigationModel'
import type { InvestigationSourceStatus } from '@/features/candidates/types'
import { InvestigationScan } from './InvestigationScan'
import { InvestigationResultShell } from './InvestigationResultShell'

export interface InvestigationResultsProps {
  site: InvestigationSite
  sourceStatus: InvestigationSourceStatus
  lifecycleStatus: Extract<InvestigationLifecycleStatus, 'scanning' | 'ready'>
  scanProgress: number
}

/**
 * Stage 2 of the investigation: the Earth Event Evidence result.
 *
 * A separate section below the location-selection panel, rendered only after
 * "Begin Investigation" is pressed. It reports what the data shows - NISAR
 * radar observation, terrain context, an evidence summary and the data and
 * technology actually used. It never classifies the event or claims a cause.
 *
 * Everything is derived from the InvestigationSite passed in, so the panel
 * (and the downloadable case file) follow whichever investigation is selected.
 */
export const InvestigationResults = forwardRef<HTMLElement, InvestigationResultsProps>(
  function InvestigationResults({ site, sourceStatus, lifecycleStatus, scanProgress }, ref) {
    const [caseFileState, setCaseFileState] = useState<'idle' | 'building' | 'ready'>('idle')

    const before = site.nisar.beforeCoherence.toFixed(4)
    const after = site.nisar.afterCoherence.toFixed(4)
    const meanChange = site.nisar.meanChange.toFixed(4)
    const medianChange = site.nisar.medianChange.toFixed(4)
    const validPixels = site.nisar.validPixels.toLocaleString('en-US')
    const elevation = site.terrain.elevationMeters.toLocaleString('en-US')
    const slope = site.terrain.localSlopeDegrees + '\u00b0'

    const handleCaseFile = async () => {
      setCaseFileState('building')
      try {
        await downloadCaseFile(site)
        setCaseFileState('ready')
      } catch {
        setCaseFileState('idle')
      }
    }

    if (lifecycleStatus === 'scanning') {
      return (
        <InvestigationResultShell ref={ref} className="ew-results-card ew-sandhya-results" aria-live="polite">
          <InvestigationScan locationName={site.shortName} progress={scanProgress} />
        </InvestigationResultShell>
      )
    }

    return (
      <InvestigationResultShell ref={ref} className="ew-results-card" aria-labelledby="results-title">
        {/* ---------- Header ---------- */}
        <div className="ew-results-head">
          <p className="ew-panel-label">EARTH EVENT EVIDENCE</p>
          <h2 id="results-title" className="ew-results-title">
            {site.name}
          </h2>
          <p className="ew-results-head-coords">{site.coordLabel}</p>
          <p className="ew-results-head-note">NISAR radar observation + terrain context · Metadata: {sourceStatus === 'LIVE' ? 'live NASA discovery' : sourceStatus === 'CACHED_LIVE' ? 'cached NASA discovery' : 'not available'} · Scientific result: verified precomputed evidence</p>
        </div>

        {/* ---------- 01 NISAR radar observation ---------- */}
        <section className="ew-results-section" aria-labelledby="ew-section-01">
          <div className="ew-section-head">
            <span className="ew-section-num">01</span>
            <h3 id="ew-section-01" className="ew-section-title">
              NISAR RADAR OBSERVATION
            </h3>
          </div>
          <p className="ew-section-note">Coherence change measured across the investigated region.</p>

          <div className="ew-evidence-grid" aria-label="NISAR coherence measurements">
            <article>
              <strong>{before}</strong>
              <span>Before coherence</span>
            </article>
            <article>
              <strong>{after}</strong>
              <span>After coherence</span>
            </article>
            <article>
              <strong>{meanChange}</strong>
              <span>Mean change</span>
            </article>
            <article>
              <strong>{medianChange}</strong>
              <span>Median change</span>
            </article>
            <article>
              <strong>{validPixels}</strong>
              <span>Valid pixels</span>
            </article>
          </div>

          <div className="ew-change" aria-label={'Coherence comparison from ' + before + ' to ' + after}>
            <div className="ew-change-end">
              <span className="ew-change-label">BEFORE</span>
              <span className="ew-change-value">{before}</span>
            </div>
            <span className="ew-change-track" aria-hidden="true" />
            <span className="ew-change-glyph" aria-hidden="true">
              →
            </span>
            <div className="ew-change-end is-after">
              <span className="ew-change-label">AFTER</span>
              <span className="ew-change-value">{after}</span>
            </div>
          </div>
          <p className="ew-change-note">
            Coherence decreased by {meanChange.replace('-', '')} across the investigated region.
          </p>
        </section>

        {/* ---------- 02 Terrain context ---------- */}
        <section className="ew-results-section" aria-labelledby="ew-section-02">
          <div className="ew-section-head">
            <span className="ew-section-num">02</span>
            <h3 id="ew-section-02" className="ew-section-title">
              TERRAIN CONTEXT
            </h3>
          </div>
          <p className="ew-section-note">Local elevation and slope derived from {site.terrain.dem}.</p>

          <div className="ew-metric-row">
            <div className="ew-metric-card">
              <strong>{elevation} m</strong>
              <span>Elevation</span>
            </div>
            <div className="ew-metric-card">
              <strong>{slope}</strong>
              <span>Local slope</span>
            </div>
            <div className="ew-metric-card is-context">
              <strong>{site.terrain.context}</strong>
              <span>Terrain context</span>
            </div>
          </div>

          <dl className="ew-fact-row">
            <div>
              <dt>LOCATION</dt>
              <dd>{site.name}</dd>
            </div>
            <div>
              <dt>ELEVATION</dt>
              <dd>{elevation} m</dd>
            </div>
            <div>
              <dt>LOCAL SLOPE</dt>
              <dd>{slope}</dd>
            </div>
            <div>
              <dt>DEM</dt>
              <dd>{site.terrain.dem}</dd>
            </div>
          </dl>
        </section>

        {/* ---------- 03 Observation summary ---------- */}
        <section className="ew-results-section" aria-labelledby="ew-section-03">
          <div className="ew-section-head">
            <span className="ew-section-num">03</span>
            <h3 id="ew-section-03" className="ew-section-title">
              OBSERVATION SUMMARY
            </h3>
          </div>

          <div className="ew-evidence-cards">
            <article className="ew-evidence-card">
              <h4>RADAR SIGNAL</h4>
              <p>{site.nisar.observationSummary}</p>
              <p className="ew-evidence-support">
                <span>Supporting measurement</span>
                <strong>
                  {before} → {after}
                </strong>
              </p>
            </article>

            <article className="ew-evidence-card">
              <h4>TERRAIN CONTEXT</h4>
              <p>{site.terrain.summary}</p>
              <p className="ew-evidence-support">
                <span>Supporting data</span>
                <strong>{site.terrain.dem}</strong>
              </p>
            </article>

            <article className="ew-evidence-card">
              <h4>EVIDENCE COVERAGE</h4>
              <p>{validPixels} valid NISAR pixels were used for the regional coherence comparison.</p>
              <p className="ew-evidence-support">
                <span>Supporting dataset</span>
                <strong>{site.nisar.product}</strong>
              </p>
            </article>
          </div>
        </section>

        {/* ---------- 04 Data & technology ---------- */}
        <section className="ew-results-section" aria-labelledby="ew-section-04">
          <div className="ew-section-head">
            <span className="ew-section-num">04</span>
            <h3 id="ew-section-04" className="ew-section-title">
              DATA &amp; TECHNOLOGY
            </h3>
          </div>

          <div className="ew-tech-grid">
            <article className="ew-tech-card">
              <h4>NISAR</h4>
              <p className="ew-tech-agency">NASA / JPL</p>
              <p className="ew-tech-type">Synthetic Aperture Radar</p>
              <p className="ew-tech-use">Used for regional coherence-change detection</p>
            </article>

            <article className="ew-tech-card">
              <h4>{site.terrain.dem}</h4>
              <p className="ew-tech-agency">NASA</p>
              <p className="ew-tech-type">Digital Elevation Model</p>
              <p className="ew-tech-use">Used for elevation and terrain/slope context</p>
            </article>

            <article className="ew-tech-card">
              <h4>LEAFLET + OPENSTREETMAP</h4>
              <p className="ew-tech-agency">Interactive geographic visualization</p>
              <p className="ew-tech-use">Used for investigation location mapping</p>
            </article>
          </div>
        </section>

        {/* ---------- What the data shows ---------- */}
        <section className="ew-results-section" aria-labelledby="ew-takeaway">
          <div className="ew-section-head">
            <h3 id="ew-takeaway" className="ew-section-title">
              WHAT THE DATA SHOWS
            </h3>
          </div>
          <ul className="ew-takeaway-list">
            <li>Radar coherence changed substantially between the compared observations.</li>
            <li>The investigated region has high local terrain slope at the selected point.</li>
            <li>The evidence combines regional NISAR measurements with local terrain context.</li>
          </ul>
        </section>

        {/* ---------- Actions ---------- */}
        <div className="ew-results-actions">
          <button type="button" className="ew-action-btn" onClick={handleCaseFile}>
            {caseFileState === 'building' ? 'Preparing case file…' : 'Event Case File'}
          </button>
          {/* Science Mode: intentionally renders no panel yet */}
          <button type="button" className="ew-action-btn">
            Science Mode
          </button>
        </div>
      </InvestigationResultShell>
    )
  },
)
