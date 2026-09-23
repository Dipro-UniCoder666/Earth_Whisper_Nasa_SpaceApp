interface SampleEventCardProps {
  onLoad: () => void
}

export function SampleEventCard({ onLoad }: SampleEventCardProps) {
  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-subtle)] p-4">
      <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
        Sample investigation
      </p>
      <p className="mt-1 text-sm font-semibold text-[var(--color-navy)]">
        Prototype NISAR Anomaly · Himachal Pradesh, India
      </p>
      <p className="mt-1 text-xs leading-relaxed text-[var(--color-text-muted)]">
        Load a pre-prepared investigation using real NISAR coherence data from Candidate #1 —
        31.1105° N, 77.9373° E.
      </p>
      <button
        type="button"
        onClick={onLoad}
        aria-label="Load sample investigation: prototype NISAR anomaly, Monda"
        className="mt-3 rounded-md border border-[var(--color-border)] bg-white px-4 py-2 text-xs font-semibold text-[var(--color-navy)] transition-colors hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]"
      >
        Load sample investigation →
      </button>
    </div>
  )
}
