import type { WeatherClue } from '@/features/evidence/types'

export function WeatherClueDetail({ clue }: { clue: WeatherClue }) {
  if (clue.windows.length === 0) return null

  return (
    <div>
      <div className="grid grid-cols-4 gap-2 rounded-xl bg-[var(--color-bg)] p-3 text-center">
        {clue.windows.map((w) => (
          <div key={w.label}>
            <p className="text-[0.6rem] uppercase tracking-wide text-[var(--color-muted)]">{w.label}</p>
            <p className="mt-0.5 font-display text-base text-[var(--color-navy)]">
              {w.millimeters !== undefined ? `${w.millimeters}mm` : '—'}
            </p>
          </div>
        ))}
      </div>
      {clue.anomalyMillimeters !== undefined && (
        <p className="mt-2 text-xs text-[var(--color-muted)]">
          ~{clue.anomalyMillimeters}mm above baseline. {clue.baselineDescription}
        </p>
      )}
    </div>
  )
}
