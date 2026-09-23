import type { CandidateAnomaly } from '@/features/investigation/types'
import { demoEvent } from '@/data/demoEvent'
import { formatCoordinate } from '@/lib/utils'

interface FingerprintPreviewProps {
  candidate: CandidateAnomaly
  scienceMode: boolean
}

const EVIDENCE_SLOTS = [
  { key: 'radar', label: 'Radar', collected: true },
  { key: 'terrain', label: 'Terrain', collected: false },
  { key: 'weather', label: 'Weather', collected: false },
  { key: 'optical', label: 'Optical', collected: false },
  { key: 'water', label: 'Water', collected: false },
]

export function FingerprintPreview({ candidate, scienceMode }: FingerprintPreviewProps) {
  const nisar = demoEvent.evidence.nisar
  const uncertainty = demoEvent.uncertainty

  return (
    <section aria-labelledby="fp-heading">
      <div className="mb-3 flex items-center justify-between">
        <p className="eyebrow" id="fp-heading">Earth Event Fingerprint</p>
        <span className="rounded border border-[var(--color-border)] px-2 py-0.5 text-[0.6rem] font-medium text-[var(--color-text-muted)]">
          PRELIMINARY
        </span>
      </div>

      {/* Status */}
      <div className="mb-4 flex items-center gap-2 rounded-md bg-[#EBF5FB] px-3 py-2">
        <span className="h-2 w-2 rounded-full bg-[var(--color-primary)]" aria-hidden="true" />
        <p className="text-xs font-semibold text-[var(--color-primary)]">SURFACE CHANGE DETECTED</p>
      </div>

      {/* Measurements — two-column clean layout, no individual cards */}
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
        <div>
          <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
            Location
          </dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--color-navy)]">
            {formatCoordinate(candidate.latitude, 'lat')},<br />
            {formatCoordinate(candidate.longitude, 'lng')}
          </dd>
        </div>

        {candidate.areaSqKm !== undefined && (
          <div>
            <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
              Observed area
            </dt>
            <dd className="mt-0.5 text-sm font-medium text-[var(--color-navy)]">
              ~{candidate.areaSqKm.toFixed(2)} km²
            </dd>
          </div>
        )}

        {nisar && (
          <>
            <div>
              <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                Radar coherence
              </dt>
              <dd className="mt-0.5 text-sm font-medium text-[var(--color-navy)]">
                {nisar.coherenceBefore?.toFixed(4)} → {nisar.coherenceAfter?.toFixed(4)}
              </dd>
            </div>

            <div>
              <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                Change
              </dt>
              <dd className="mt-0.5 text-sm font-bold text-[var(--color-scientific-anomaly)]">
                {nisar.meanCoherenceChange !== undefined
                  ? nisar.meanCoherenceChange.toFixed(4)
                  : '—'}
              </dd>
            </div>
          </>
        )}

        <div>
          <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
            Observation period
          </dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--color-navy)]">
            Jul 12 → Aug 17, 2026
          </dd>
        </div>

        <div>
          <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
            Cause
          </dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--color-text-muted)]">
            Not yet determined
          </dd>
        </div>

        <div className="col-span-2">
          <dt className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
            Source
          </dt>
          <dd className="mt-0.5 text-xs text-[var(--color-text-muted)]">
            NASA-ISRO NISAR (GUNW demonstration data)
          </dd>
        </div>
      </dl>

      {/* Evidence status */}
      <div className="mt-4 border-t border-[var(--color-border-subtle)] pt-4">
        <p className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
          Evidence collected
        </p>
        <div className="flex flex-wrap gap-2">
          {EVIDENCE_SLOTS.map((slot) => (
            <span
              key={slot.key}
              className={
                slot.collected
                  ? 'rounded border border-[var(--color-primary)]/30 bg-[#EBF5FB] px-2.5 py-1 text-[0.65rem] font-medium text-[var(--color-primary)]'
                  : 'rounded border border-[var(--color-border-subtle)] px-2.5 py-1 text-[0.65rem] font-medium text-[var(--color-text-muted)] opacity-50'
              }
            >
              {slot.collected ? '✓ ' : ''}{slot.label}
            </span>
          ))}
        </div>
      </div>

      {/* Uncertainty */}
      <div className="mt-4 border-t border-[var(--color-border-subtle)] pt-4">
        <p className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
          What we know
        </p>
        <ul className="space-y-1.5">
          {uncertainty.known.map((s, i) => (
            <li key={i} className="flex gap-2 text-xs leading-relaxed text-[var(--color-text-muted)]">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--color-primary)]" aria-hidden="true" />
              {s}
            </li>
          ))}
        </ul>

        {scienceMode && (
          <>
            <p className="mb-2 mt-4 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
              Still uncertain
            </p>
            <ul className="space-y-1.5">
              {uncertainty.uncertain.map((s, i) => (
                <li key={i} className="flex gap-2 text-xs leading-relaxed text-[var(--color-text-muted)]">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--color-scientific-warning)]" aria-hidden="true" />
                  {s}
                </li>
              ))}
            </ul>

            <p className="mb-2 mt-4 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
              Cannot yet conclude
            </p>
            <ul className="space-y-1.5">
              {uncertainty.cannotConclude.map((s, i) => (
                <li key={i} className="flex gap-2 text-xs leading-relaxed text-[var(--color-text-muted)]">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--color-scientific-anomaly)]" aria-hidden="true" />
                  {s}
                </li>
              ))}
            </ul>
          </>
        )}

        {!scienceMode && (
          <p className="mt-3 text-[0.65rem] italic text-[var(--color-text-muted)]">
            Enable Science Mode for full uncertainty detail.
          </p>
        )}
      </div>
    </section>
  )
}
