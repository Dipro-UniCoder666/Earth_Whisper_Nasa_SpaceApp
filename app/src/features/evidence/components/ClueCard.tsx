import type { ReactNode } from 'react'
import { Info } from 'lucide-react'
import type { ClueBase } from '@/features/evidence/types'
import { AvailabilityBadge } from '@/features/evidence/components/AvailabilityBadge'

interface ClueCardProps {
  clue: ClueBase
  clueNumber: number
  children?: ReactNode
}

function formatDate(iso?: string): string | null {
  if (!iso) return null
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

export function ClueCard({ clue, clueNumber, children }: ClueCardProps) {
  const dateLabel = formatDate(clue.observedAt)

  return (
    <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-aqua)]">
          Clue {String(clueNumber).padStart(2, '0')}
        </p>
        <AvailabilityBadge availability={clue.availability} />
      </div>

      <h3 className="mt-1.5 font-display text-lg font-medium text-[var(--color-navy)]">{clue.title}</h3>

      <p className="mt-2 text-sm leading-relaxed text-[var(--color-text)]">{clue.summary}</p>

      {children && <div className="mt-4">{children}</div>}

      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-[var(--color-sky)] pt-3 text-xs text-[var(--color-muted)]">
        <span>
          Source: <span className="text-[var(--color-text)]">{clue.source.label}</span>
        </span>
        {dateLabel && <span>{dateLabel}</span>}
      </div>

      {clue.limitations.length > 0 && (
        <div className="mt-3 rounded-xl bg-[var(--color-bg)] p-3">
          <p className="flex items-center gap-1.5 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
            <Info size={12} aria-hidden="true" />
            Limitations
          </p>
          <ul className="mt-1.5 flex flex-col gap-1 text-xs leading-relaxed text-[var(--color-muted)]">
            {clue.limitations.map((limitation, i) => (
              <li key={i}>• {limitation}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
