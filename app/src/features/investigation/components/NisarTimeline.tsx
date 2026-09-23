import { Satellite } from 'lucide-react'
import type { NisarObservation } from '@/features/investigation/types'
import { cn } from '@/lib/utils'

interface NisarTimelineProps {
  observations: NisarObservation[]
  selectedObservationId?: string
  onSelect?: (observationId: string) => void
}

function formatMonth(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short' }).toUpperCase()
}

function formatDateRange(startDate: string, endDate: string): string {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' }
  return `${start.toLocaleDateString(undefined, opts)} → ${end.toLocaleDateString(undefined, opts)}`
}

export function NisarTimeline({ observations, selectedObservationId, onSelect }: NisarTimelineProps) {
  const sorted = [...observations].sort((a, b) => a.startDate.localeCompare(b.startDate))

  if (sorted.length === 0) {
    return <p className="text-sm text-[var(--color-muted)]">No NISAR observations available for this location yet.</p>
  }

  return (
    <ol className="relative flex flex-col gap-1" aria-label="NISAR observation timeline">
      {sorted.map((obs, index) => {
        const isSelected = obs.id === selectedObservationId
        const isLast = index === sorted.length - 1

        return (
          <li key={obs.id} className="relative flex gap-4">
            <div className="flex flex-col items-center">
              <span
                className={cn(
                  'flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 text-[0.65rem] font-bold tracking-wide',
                  isSelected
                    ? 'border-[var(--color-aqua)] bg-[var(--color-aqua-soft)] text-[var(--color-navy)]'
                    : 'border-[var(--color-sky)] bg-white text-[var(--color-muted)]',
                )}
                aria-hidden="true"
              >
                {formatMonth(obs.startDate)}
              </span>
              {!isLast && <span className="my-0.5 h-full w-px flex-1 bg-[var(--color-sky)]" aria-hidden="true" />}
            </div>

            <button
              type="button"
              onClick={() => onSelect?.(obs.id)}
              aria-pressed={isSelected}
              className={cn(
                'mb-4 flex-1 rounded-xl border px-4 py-3 text-left transition-colors',
                isSelected
                  ? 'border-[var(--color-aqua)] bg-[var(--color-aqua-soft)]/60'
                  : 'border-[var(--color-sky)] bg-white hover:border-[var(--color-primary)]',
              )}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="flex items-center gap-2 text-sm font-semibold text-[var(--color-navy)]">
                  <Satellite size={14} className="text-[var(--color-primary)]" aria-hidden="true" />
                  {obs.productId}
                </span>
                <span className="shrink-0 rounded-full bg-[var(--color-sky)] px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-primary)]">
                  {obs.availability === 'demonstration' ? 'Demo data' : 'Live'}
                </span>
              </div>
              <p className="mt-1 text-xs text-[var(--color-muted)]">{formatDateRange(obs.startDate, obs.endDate)}</p>
              {obs.orbit?.track !== undefined && (
                <p className="mt-1 text-xs text-[var(--color-muted)]">
                  Track {obs.orbit.track} · Frame {obs.orbit.frame}
                </p>
              )}
            </button>
          </li>
        )
      })}
    </ol>
  )
}
