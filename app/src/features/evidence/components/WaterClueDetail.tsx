import type { WaterClue } from '@/features/evidence/types'

export function WaterClueDetail({ clue }: { clue: WaterClue }) {
  if (clue.distanceToNearestWaterKm === undefined) return null

  return (
    <div className="grid grid-cols-2 gap-2 rounded-xl bg-[var(--color-bg)] p-3 text-center sm:grid-cols-3">
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Nearest water</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.distanceToNearestWaterKm.toFixed(1)} km
        </p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Floodplain</p>
        <p className="mt-0.5 font-display text-base capitalize text-[var(--color-navy)]">
          {clue.inFloodplain === 'unknown' ? 'Unknown' : clue.inFloodplain ? 'Yes' : 'No'}
        </p>
      </div>
      <div className="col-span-2 sm:col-span-1">
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Elev. above water</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.elevationAboveNearestWaterMeters !== undefined ? `${clue.elevationAboveNearestWaterMeters} m` : '—'}
        </p>
      </div>
    </div>
  )
}
