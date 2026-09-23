import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, AlertCircle } from 'lucide-react'
import type { CandidateAnomaly, NisarObservation, NisarObservationPair } from '@/features/investigation/types'
import { getObservationPair } from '@/features/investigation/services/nisarService'
import { NisarTimeline } from '@/features/investigation/components/NisarTimeline'
import { FingerprintPreview } from '@/features/investigation/components/FingerprintPreview'
import { formatCoordinate } from '@/lib/utils'
import { ROUTES } from '@/lib/constants'

interface ObservationPanelProps {
  candidate: CandidateAnomaly
  observations: NisarObservation[]
  selectedObservationId: string | undefined
  onSelectObservation: (id: string) => void
  scienceMode: boolean
}

export function ObservationPanel({
  candidate,
  observations,
  selectedObservationId,
  onSelectObservation,
  scienceMode,
}: ObservationPanelProps) {
  const [pair, setPair] = useState<NisarObservationPair | undefined>()
  const [pairLoading, setPairLoading] = useState(false)

  useEffect(() => {
    if (!candidate.observationPairId) return
    let cancelled = false
    setPairLoading(true)
    getObservationPair(candidate.observationPairId).then((result) => {
      if (cancelled) return
      setPair(result)
      setPairLoading(false)
    })
    return () => { cancelled = true }
  }, [candidate.observationPairId])

  const continueUrl = `${ROUTES.investigate}/case/${candidate.id}`

  return (
    <div
      className="flex flex-col"
      role="region"
      aria-labelledby="obs-panel-heading"
    >
      {/* ── Location header ─────────────────────────── */}
      <div className="border-b border-[var(--color-border-subtle)] px-5 py-4">
        <p className="eyebrow">Selected region</p>
        <h2
          id="obs-panel-heading"
          className="mt-1 text-base font-semibold text-[var(--color-navy)]"
        >
          {candidate.regionLabel ?? 'Unknown region'}
        </h2>
        <p className="mt-0.5 text-xs text-[var(--color-text-muted)]">
          {formatCoordinate(candidate.latitude, 'lat')},{' '}
          {formatCoordinate(candidate.longitude, 'lng')}
          {candidate.areaSqKm !== undefined && ` · ~${candidate.areaSqKm.toFixed(2)} km²`}
        </p>
      </div>

      {/* ── NISAR Observation ────────────────────────── */}
      <div className="border-b border-[var(--color-border-subtle)] px-5 py-5">
        <p className="eyebrow mb-3">NISAR observation</p>

        {pairLoading && (
          <div className="space-y-2" aria-live="polite">
            <div className="h-16 animate-pulse rounded bg-[var(--color-surface-subtle)]" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-[var(--color-surface-subtle)]" />
          </div>
        )}

        {!pairLoading && !pair && (
          <div className="flex items-start gap-2 text-sm text-[var(--color-text-muted)]">
            <AlertCircle size={14} className="mt-0.5 shrink-0 text-[var(--color-scientific-warning)]" aria-hidden="true" />
            No coherence comparison available for this candidate.
          </div>
        )}

        {!pairLoading && pair && (
          <>
            {/* Status line */}
            <div className="mb-4 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[var(--color-primary)]" aria-hidden="true" />
              <p className="text-xs font-semibold text-[var(--color-primary)]">
                SURFACE CHANGE DETECTED
              </p>
            </div>

            {/* Description */}
            <p className="mb-4 text-sm text-[var(--color-text-muted)]">
              {scienceMode
                ? `Mean coherence decreased from ${pair.coherenceBefore?.toFixed(4)} to ${pair.coherenceAfter?.toFixed(4)} across the candidate region (~${candidate.areaSqKm?.toFixed(2)} km²). This is a coherence comparison, not an unwrapped-phase displacement measurement.`
                : 'A substantial change in radar coherence was observed across the selected region.'}
            </p>

            {/* Before / After / Change — inline report layout */}
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4">
              {/* Column headers */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                    Before
                  </p>
                  <p className="mt-2 text-2xl font-bold tabular-nums text-[var(--color-navy)]">
                    {pair.coherenceBefore?.toFixed(4) ?? '—'}
                  </p>
                  <p className="mt-0.5 text-[0.65rem] text-[var(--color-text-muted)]">Pair 025 · Jul 2026</p>
                </div>
                <div>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                    After
                  </p>
                  <p className="mt-2 text-2xl font-bold tabular-nums text-[var(--color-navy)]">
                    {pair.coherenceAfter?.toFixed(4) ?? '—'}
                  </p>
                  <p className="mt-0.5 text-[0.65rem] text-[var(--color-text-muted)]">Pair 026 · Aug 2026</p>
                </div>
                <div>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                    Change
                  </p>
                  <p className="mt-2 text-2xl font-bold tabular-nums text-[var(--color-scientific-anomaly)]">
                    {pair.meanCoherenceChange !== undefined
                      ? pair.meanCoherenceChange.toFixed(4)
                      : '—'}
                  </p>
                  <p className="mt-0.5 text-[0.65rem] text-[var(--color-text-muted)]">Mean coherence change</p>
                </div>
              </div>

              {/* Visual scale bar */}
              <div className="mt-4 border-t border-[var(--color-border-subtle)] pt-3">
                <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-gradient-to-r from-[#1479C9] via-[#8EC5D4] to-[#B3432B]">
                  {pair.coherenceBefore !== undefined && pair.coherenceAfter !== undefined && (
                    <div
                      className="absolute inset-y-0 bg-[var(--color-navy)]/15"
                      style={{
                        left: `${(1 - pair.coherenceBefore) * 100}%`,
                        width: `${Math.abs((pair.coherenceAfter - pair.coherenceBefore)) * 100}%`,
                      }}
                      aria-hidden="true"
                    />
                  )}
                </div>
                <div className="mt-1.5 flex justify-between text-[0.6rem] text-[var(--color-text-muted)]">
                  <span>High coherence</span>
                  <span>Substantial loss</span>
                </div>
              </div>
            </div>

            {/* Observed area + data source */}
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                  Observed area
                </p>
                <p className="mt-0.5 text-sm font-medium text-[var(--color-navy)]">
                  ~{candidate.areaSqKm?.toFixed(2)} km²
                </p>
              </div>
              <div>
                <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                  Cause
                </p>
                <p className="mt-0.5 text-sm font-medium text-[var(--color-text-muted)]">
                  Not yet determined
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                  Data source
                </p>
                <p className="mt-0.5 text-xs text-[var(--color-text-muted)]">
                  NASA-ISRO NISAR · GUNW demonstration data
                </p>
              </div>
            </div>

            {scienceMode && pair.note && (
              <blockquote className="mt-4 border-l-2 border-[var(--color-border)] pl-3 text-xs italic text-[var(--color-text-muted)]">
                {pair.note}
              </blockquote>
            )}
          </>
        )}
      </div>

      {/* ── Earth Event Fingerprint ───────────────────── */}
      <div className="border-b border-[var(--color-border-subtle)] px-5 py-5">
        <FingerprintPreview candidate={candidate} scienceMode={scienceMode} />
      </div>

      {/* ── NISAR Timeline ───────────────────────────── */}
      {observations.length > 0 && (
        <div className="border-b border-[var(--color-border-subtle)] px-5 py-5">
          <p className="eyebrow mb-3">Observation timeline</p>
          <NisarTimeline
            observations={observations}
            selectedObservationId={selectedObservationId}
            onSelect={onSelectObservation}
          />
        </div>
      )}

      {/* ── Continue action ───────────────────────────── */}
      <div className="px-5 py-4">
        <p className="mb-3 text-xs text-[var(--color-text-muted)]">
          Surface change detected. Cause has not been determined.
        </p>
        <Link
          to={continueUrl}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-[var(--color-primary)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#0d66b0]"
        >
          Continue Investigation
          <ArrowRight size={15} aria-hidden="true" />
        </Link>
      </div>
    </div>
  )
}
