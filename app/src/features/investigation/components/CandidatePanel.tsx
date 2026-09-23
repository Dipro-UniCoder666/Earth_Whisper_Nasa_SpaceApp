import { useEffect, useState } from 'react'
import { AlertTriangle, ArrowRight, Radar } from 'lucide-react'
import type { CandidateAnomaly, NisarObservationPair } from '@/features/investigation/types'
import { getObservationPair } from '@/features/investigation/services/nisarService'
import { Button } from '@/components/common/Button'
import { formatCoordinate } from '@/lib/utils'

interface CandidatePanelProps {
  candidate: CandidateAnomaly
  onInvestigate: (candidateId: string) => void
}

const STATUS_LABEL: Record<CandidateAnomaly['status'], string> = {
  'prototype-anomaly': 'Prototype NISAR anomaly',
  'under-investigation': 'Under investigation',
  'case-file-complete': 'Case file complete',
}

export function CandidatePanel({ candidate, onInvestigate }: CandidatePanelProps) {
  const [pair, setPair] = useState<NisarObservationPair | undefined>()
  const [loading, setLoading] = useState(Boolean(candidate.observationPairId))

  useEffect(() => {
    let cancelled = false
    if (!candidate.observationPairId) {
      setPair(undefined)
      setLoading(false)
      return
    }
    setLoading(true)
    getObservationPair(candidate.observationPairId).then((result) => {
      if (!cancelled) {
        setPair(result)
        setLoading(false)
      }
    })
    return () => {
      cancelled = true
    }
  }, [candidate.observationPairId])

  return (
    <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--color-aqua-soft)] px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-navy)]">
            <AlertTriangle size={12} aria-hidden="true" />
            {STATUS_LABEL[candidate.status]}
          </span>
          <h3 className="mt-2 font-display text-lg font-medium text-[var(--color-navy)]">{candidate.title}</h3>
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <dt className="text-[var(--color-muted)]">Location</dt>
        <dd className="text-right text-[var(--color-text)]">
          {formatCoordinate(candidate.latitude, 'lat')}, {formatCoordinate(candidate.longitude, 'lng')}
        </dd>
        {candidate.regionLabel && (
          <>
            <dt className="text-[var(--color-muted)]">Region</dt>
            <dd className="text-right text-[var(--color-text)]">{candidate.regionLabel}</dd>
          </>
        )}
        {candidate.areaSqKm !== undefined && (
          <>
            <dt className="text-[var(--color-muted)]">Candidate area</dt>
            <dd className="text-right text-[var(--color-text)]">~{candidate.areaSqKm.toFixed(2)} km²</dd>
          </>
        )}
      </dl>

      <div className="mt-4 rounded-xl bg-[var(--color-bg)] p-4">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[var(--color-primary)]">
          <Radar size={14} aria-hidden="true" />
          NISAR coherence comparison
        </p>

        {loading && <p className="mt-2 text-sm text-[var(--color-muted)]">Loading measurement…</p>}

        {!loading && pair && (
          <>
            <div className="mt-2 grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-[0.65rem] uppercase tracking-wide text-[var(--color-muted)]">Before</p>
                <p className="mt-0.5 font-display text-lg text-[var(--color-navy)]">
                  {pair.coherenceBefore?.toFixed(4) ?? '—'}
                </p>
              </div>
              <div>
                <p className="text-[0.65rem] uppercase tracking-wide text-[var(--color-muted)]">After</p>
                <p className="mt-0.5 font-display text-lg text-[var(--color-navy)]">
                  {pair.coherenceAfter?.toFixed(4) ?? '—'}
                </p>
              </div>
              <div>
                <p className="text-[0.65rem] uppercase tracking-wide text-[var(--color-muted)]">Change</p>
                <p className="mt-0.5 font-display text-lg text-[#B3432B]">
                  {pair.meanCoherenceChange !== undefined ? pair.meanCoherenceChange.toFixed(4) : '—'}
                </p>
              </div>
            </div>
            {pair.note && <p className="mt-3 text-xs leading-relaxed text-[var(--color-muted)]">{pair.note}</p>}
          </>
        )}

        {!loading && !pair && (
          <p className="mt-2 text-sm text-[var(--color-muted)]">
            No coherence comparison has been computed for this candidate yet.
          </p>
        )}
      </div>

      <p className="mt-4 text-xs leading-relaxed text-[var(--color-muted)]">
        This is a measured coherence change, not a confirmed cause. No claim of landslide, disaster, or hazard can be
        made from this observation alone.
      </p>

      <Button
        size="lg"
        icon={<ArrowRight size={18} />}
        onClick={() => onInvestigate(candidate.id)}
        className="mt-5 w-full"
      >
        Investigate This Change
      </Button>
    </div>
  )
}
