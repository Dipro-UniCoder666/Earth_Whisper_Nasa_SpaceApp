import type { FireClue } from '@/features/evidence/types'

export function FireClueDetail({ clue }: { clue: FireClue }) {
  return (
    <div className="grid grid-cols-2 gap-2 rounded-xl bg-[var(--color-bg)] p-3 text-center">
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Within candidate</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">{clue.detectionsWithinCandidate}</p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">
          Nearby{clue.searchRadiusKm ? ` (${clue.searchRadiusKm}km)` : ''}
        </p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">{clue.detectionsNearby}</p>
      </div>
    </div>
  )
}
