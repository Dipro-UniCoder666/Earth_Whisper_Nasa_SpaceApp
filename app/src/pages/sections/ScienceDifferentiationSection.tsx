import { Shield, SplitSquareHorizontal, Eye } from 'lucide-react'

const PRINCIPLES = [
  {
    icon: SplitSquareHorizontal,
    title: 'Evidence Independence',
    body: 'Each data source is assessed separately. Radar, terrain, weather, optical imagery, fire, and water clues are never blended into a single score before their individual signals are understood.',
  },
  {
    icon: Shield,
    title: 'Honest Uncertainty',
    body: 'We state explicitly what we know, what we are uncertain about, and what the current data cannot tell us. A conclusion without stated confidence is not a scientific finding.',
  },
  {
    icon: Eye,
    title: 'Observation Over Prediction',
    body: 'Earth Whisper does not predict events. It documents changes that have already been observed by NISAR and asks what the evidence supports — not what an algorithm guesses.',
  },
]

export function ScienceDifferentiationSection() {
  return (
    <section className="relative overflow-hidden bg-[var(--color-surface-subtle)] py-20 md:py-28">
      {/* Decorative contour lines */}
      <svg
        className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.06]"
        viewBox="0 0 1200 500"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
        <path d="M0 400 C 300 320, 600 450, 900 350 S 1100 200, 1200 300" stroke="#0B5EA8" strokeWidth="1.5" fill="none" />
        <path d="M0 300 C 300 220, 600 350, 900 250 S 1100 100, 1200 200" stroke="#18B7C9" strokeWidth="1" fill="none" />
        <path d="M0 200 C 300 140, 600 250, 900 150 S 1100 50, 1200 120" stroke="#0B5EA8" strokeWidth="0.8" fill="none" />
      </svg>

      <div className="relative mx-auto max-w-[var(--max-width-content)] px-[var(--page-gutter-mobile)] md:px-[var(--page-gutter-desktop)]">
        <div className="mx-auto max-w-[var(--max-width-narrow)] text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--color-aqua)]">
            Scientific Method
          </p>
          <h2 className="mt-3 font-display text-3xl font-medium leading-tight text-[var(--color-navy)] md:text-4xl">
            Not a Disaster Dashboard
          </h2>
          <p className="mt-4 text-base leading-relaxed text-[var(--color-text-muted)]">
            A radar signal changes. That does not automatically mean &ldquo;landslide.&rdquo; It could be slope
            disturbance, flooding, vegetation change, wildfire, human activity, deformation, or something
            entirely unknown. Earth Whisper investigates the evidence before presenting an explanation.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {PRINCIPLES.map((p) => {
            const Icon = p.icon
            return (
              <div
                key={p.title}
                className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-8 shadow-[0_4px_24px_-8px_rgba(7,59,102,0.1)]"
              >
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--color-aqua-soft)]">
                  <Icon size={20} className="text-[var(--color-primary)]" aria-hidden="true" />
                </div>
                <h3 className="font-display text-xl font-medium text-[var(--color-navy)]">{p.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[var(--color-text-muted)]">{p.body}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
