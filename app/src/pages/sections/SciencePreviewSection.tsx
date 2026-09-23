import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2, Circle } from 'lucide-react'
import { ROUTES } from '@/lib/constants'

const EVIDENCE_SLOTS = [
  { label: 'RADAR', collected: true },
  { label: 'TERRAIN', collected: false },
  { label: 'WEATHER', collected: false },
  { label: 'OPTICAL', collected: false },
  { label: 'WATER', collected: false },
]

export function SciencePreviewSection() {
  return (
    <section className="bg-[var(--color-bg)] py-20 md:py-28">
      <div className="mx-auto max-w-[var(--max-width-content)] px-[var(--page-gutter-mobile)] md:px-[var(--page-gutter-desktop)]">
        <div className="mx-auto max-w-[var(--max-width-narrow)] text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--color-aqua)]">
            Investigation Preview
          </p>
          <h2 className="mt-3 font-display text-3xl font-medium leading-tight text-[var(--color-navy)] md:text-4xl">
            The Earth Event Fingerprint
          </h2>
          <p className="mt-4 text-base leading-relaxed text-[var(--color-text-muted)]">
            Every investigation builds a structured evidence record. Each data source is assessed
            independently, then combined into a transparent Earth Event Fingerprint.
          </p>
        </div>

        {/* Sample fingerprint card */}
        <div className="mx-auto mt-12 max-w-2xl">
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[0_20px_50px_-20px_rgba(7,59,102,0.15)]">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] px-6 py-4">
              <div>
                <p className="text-[0.65rem] font-bold uppercase tracking-widest text-[var(--color-aqua)]">
                  Earth Event Fingerprint
                </p>
                <p className="mt-0.5 font-display text-lg font-medium text-[var(--color-navy)]">
                  Sample investigation structure
                </p>
              </div>
              <span className="rounded-full bg-[var(--color-aqua-soft)] px-3 py-1 text-xs font-semibold text-[var(--color-aqua)]">
                ILLUSTRATIVE
              </span>
            </div>

            {/* Status */}
            <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-subtle)] px-6 py-3">
              <span className="h-2 w-2 rounded-full bg-[var(--color-scientific-positive)]" aria-hidden="true" />
              <p className="text-sm font-semibold text-[var(--color-navy)]">SURFACE CHANGE DETECTED</p>
            </div>

            {/* Measurements */}
            <div className="grid grid-cols-2 gap-4 p-6 md:grid-cols-4">
              {[
                { label: 'Location', value: '31.1105° N, 77.9373° E' },
                { label: 'Observed area', value: '~41.57 km²' },
                { label: 'Radar coherence', value: '0.6648 → 0.2188' },
                { label: 'Change', value: '−0.4460' },
              ].map((item) => (
                <div key={item.label}>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-text-muted)]">
                    {item.label}
                  </p>
                  <p className="mt-1 text-sm font-medium text-[var(--color-navy)]">{item.value}</p>
                </div>
              ))}
            </div>

            {/* Evidence slots */}
            <div className="border-t border-[var(--color-border-subtle)] px-6 py-4">
              <p className="mb-3 text-[0.65rem] font-bold uppercase tracking-widest text-[var(--color-text-muted)]">
                Evidence Status
              </p>
              <div className="flex flex-wrap gap-2">
                {EVIDENCE_SLOTS.map((slot) => (
                  <div
                    key={slot.label}
                    className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium ${
                      slot.collected
                        ? 'border-[var(--color-scientific-positive)] bg-[#f0faf5] text-[var(--color-scientific-positive)]'
                        : 'border-[var(--color-border-subtle)] bg-[var(--color-surface-subtle)] text-[var(--color-text-muted)] opacity-60'
                    }`}
                  >
                    {slot.collected ? (
                      <CheckCircle2 size={12} aria-hidden="true" />
                    ) : (
                      <Circle size={12} aria-hidden="true" />
                    )}
                    {slot.label}
                  </div>
                ))}
              </div>
            </div>

            {/* Disclaimer + CTA */}
            <div className="border-t border-[var(--color-border-subtle)] px-6 py-5">
              <p className="mb-4 text-xs text-[var(--color-text-muted)]">
                This is an illustrative preview using prototype data. Cause has not been determined.
              </p>
              <Link
                to={ROUTES.investigate}
                className="inline-flex items-center gap-2 rounded-full bg-[var(--color-navy)] px-6 py-3 text-sm font-semibold text-white shadow-[0_10px_30px_-12px_rgba(7,59,102,0.5)] transition-all hover:bg-[#052945]"
              >
                Begin Your Investigation
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
