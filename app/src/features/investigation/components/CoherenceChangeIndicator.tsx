interface CoherenceChangeIndicatorProps {
  coherenceBefore: number
  coherenceAfter: number
  meanCoherenceChange: number
}

function getMagnitudeLabel(change: number): string {
  if (change <= -0.3) return 'Substantial coherence loss'
  if (change <= -0.1) return 'Moderate coherence loss'
  return 'Minor coherence change'
}

export function CoherenceChangeIndicator({
  coherenceBefore,
  coherenceAfter,
  meanCoherenceChange,
}: CoherenceChangeIndicatorProps) {
  // Positions on bar: coherence 1.0 = left (0%), 0.0 = right (100%)
  const beforePct = (1 - coherenceBefore) * 100
  const afterPct = (1 - coherenceAfter) * 100
  const label = getMagnitudeLabel(meanCoherenceChange)

  return (
    <div className="space-y-4">
      {/* Three metric boxes */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'BEFORE', value: coherenceBefore.toFixed(4), color: 'text-[var(--color-navy)]' },
          { label: 'AFTER', value: coherenceAfter.toFixed(4), color: 'text-[var(--color-navy)]' },
          { label: 'CHANGE', value: meanCoherenceChange.toFixed(4), color: 'text-[#B3432B]' },
        ].map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-subtle)] p-3 text-center"
          >
            <p className="text-[0.6rem] font-bold uppercase tracking-widest text-[var(--color-text-muted)]">
              {m.label}
            </p>
            <p className={`mt-1 font-display text-xl font-medium ${m.color}`}>{m.value}</p>
            <p className="text-[0.6rem] text-[var(--color-text-muted)]">coherence</p>
          </div>
        ))}
      </div>

      {/* Gradient scale bar */}
      <div
        role="img"
        aria-label={`Coherence change scale: before ${coherenceBefore.toFixed(4)}, after ${coherenceAfter.toFixed(4)}, change ${meanCoherenceChange.toFixed(4)}`}
      >
        <div className="relative mt-2">
          <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-gradient-to-r from-[#4FAF83] via-[#18B7C9] to-[#DC2626]">
            {/* Highlight region between before/after */}
            <div
              className="absolute inset-y-0 bg-[var(--color-navy)]/20"
              style={{
                left: `${beforePct}%`,
                width: `${Math.abs(afterPct - beforePct)}%`,
              }}
              aria-hidden="true"
            />
          </div>
          {/* Markers */}
          {[
            { pct: beforePct, label: 'Before', color: '#073B66' },
            { pct: afterPct, label: 'After', color: '#B3432B' },
          ].map((m) => (
            <div
              key={m.label}
              className="absolute top-3 -translate-x-1/2"
              style={{ left: `${m.pct}%` }}
              aria-hidden="true"
            >
              <svg width="8" height="6" viewBox="0 0 8 6">
                <path d="M4 0 L8 6 L0 6 Z" fill={m.color} />
              </svg>
              <p className="mt-0.5 whitespace-nowrap text-[0.55rem] font-semibold" style={{ color: m.color }}>
                {m.label}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-8 flex justify-between text-[0.6rem] text-[var(--color-text-muted)]">
          <span>High coherence (1.0)</span>
          <span>Low coherence (0.0)</span>
        </div>
      </div>

      {/* Label */}
      <div className="flex items-center gap-2">
        <span className="h-1.5 w-1.5 rounded-full bg-[#B3432B]" aria-hidden="true" />
        <p className="text-xs font-medium text-[var(--color-text-muted)]">{label}</p>
      </div>
    </div>
  )
}
