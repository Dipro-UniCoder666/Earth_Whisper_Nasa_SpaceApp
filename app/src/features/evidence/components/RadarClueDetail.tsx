import type { RadarClue } from '@/features/evidence/types'

export function RadarClueDetail({ clue }: { clue: RadarClue }) {
  if (clue.coherenceBefore === undefined && clue.coherenceAfter === undefined) return null

  return (
    <div className="grid grid-cols-3 gap-2 rounded-xl bg-[var(--color-bg)] p-3 text-center">
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Before</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.coherenceBefore?.toFixed(4) ?? '—'}
        </p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">After</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.coherenceAfter?.toFixed(4) ?? '—'}
        </p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Change</p>
        <p className="mt-0.5 font-display text-base text-[#B3432B]">
          {clue.meanCoherenceChange !== undefined ? clue.meanCoherenceChange.toFixed(4) : '—'}
        </p>
      </div>
    </div>
  )
}
