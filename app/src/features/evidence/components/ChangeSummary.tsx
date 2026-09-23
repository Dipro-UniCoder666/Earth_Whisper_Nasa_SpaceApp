import { Radio } from 'lucide-react'
import type { RadarClue } from '@/features/evidence/types'
import type { CandidateAnomaly } from '@/features/investigation/types'
import { formatCoordinate } from '@/lib/utils'

interface ChangeSummaryProps {
  candidate: CandidateAnomaly
  radar: RadarClue
}

/** The "CHANGE" header: what NISAR detected, before any clues are shown. */
export function ChangeSummary({ candidate, radar }: ChangeSummaryProps) {
  return (
    <div className="rounded-2xl border border-[var(--color-sky)] bg-gradient-to-br from-white to-[var(--color-sky)] p-6">
      <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--color-primary)]">
        <Radio size={14} aria-hidden="true" />
        Change detected
      </p>
      <h2 className="mt-2 font-display text-2xl font-medium text-[var(--color-navy)]">{candidate.title}</h2>
      <p className="mt-1 text-sm text-[var(--color-muted)]">
        {formatCoordinate(candidate.latitude, 'lat')}, {formatCoordinate(candidate.longitude, 'lng')}
        {candidate.areaSqKm !== undefined && <> · ~{candidate.areaSqKm.toFixed(2)} km²</>}
      </p>
      <p className="mt-4 text-sm leading-relaxed text-[var(--color-text)]">{radar.summary}</p>
      <p className="mt-3 text-xs leading-relaxed text-[var(--color-muted)]">
        The clues below gather independent evidence around this change. None of them determine a cause — that
        comparison happens in a later stage of the investigation.
      </p>
    </div>
  )
}
