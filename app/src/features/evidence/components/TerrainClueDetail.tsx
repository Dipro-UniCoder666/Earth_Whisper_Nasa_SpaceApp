import type { TerrainClue } from '@/features/evidence/types'

export function TerrainClueDetail({ clue }: { clue: TerrainClue }) {
  if (clue.elevationMeters === undefined && clue.slopeDegrees === undefined) return null

  return (
    <div className="grid grid-cols-2 gap-2 rounded-xl bg-[var(--color-bg)] p-3 text-center sm:grid-cols-4">
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Elevation</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.elevationMeters !== undefined ? `${clue.elevationMeters} m` : '—'}
        </p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Slope</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
          {clue.slopeDegrees !== undefined ? `${clue.slopeDegrees}°` : '—'}
        </p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Aspect</p>
        <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">{clue.aspectDirection ?? '—'}</p>
      </div>
      <div>
        <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">Class</p>
        <p className="mt-0.5 font-display text-base capitalize text-[var(--color-navy)]">
          {clue.terrainClass?.replace('-', ' ') ?? '—'}
        </p>
      </div>
    </div>
  )
}
