import { Eye, GitCompare, Archive, Search, BookOpen } from 'lucide-react'

const PHASES = [
  {
    num: '01',
    icon: Eye,
    label: 'OBSERVE',
    description:
      'NISAR radar scans the same patch of ground repeatedly, building a precise record of how it looks from space.',
  },
  {
    num: '02',
    icon: GitCompare,
    label: 'COMPARE',
    description:
      'We compare the before and after: how much did the surface change? In which direction? How quickly?',
  },
  {
    num: '03',
    icon: Archive,
    label: 'COLLECT CLUES',
    description:
      'Independent data streams — terrain shape, weather history, water levels, optical imagery, fire records — are each assessed separately.',
  },
  {
    num: '04',
    icon: Search,
    label: 'INVESTIGATE',
    description:
      'The evidence is laid out without a predetermined conclusion. We ask: what could plausibly explain what we see?',
  },
  {
    num: '05',
    icon: BookOpen,
    label: 'UNDERSTAND',
    description: 'A scientific assessment, with explicit uncertainty. Not a label — an inquiry.',
  },
]

export function StorySection() {
  return (
    <section id="story-section" className="bg-[var(--color-bg)] py-20 md:py-28">
      <div className="mx-auto max-w-[var(--max-width-content)] px-[var(--page-gutter-mobile)] md:px-[var(--page-gutter-desktop)]">
        {/* Heading */}
        <div className="mx-auto max-w-[var(--max-width-narrow)] text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--color-aqua)]">
            From Signal to Story
          </p>
          <h2 className="mt-3 font-display text-3xl font-medium leading-tight text-[var(--color-navy)] md:text-4xl">
            How an Earth Whisper Investigation Works
          </h2>
        </div>

        {/* Steps */}
        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {PHASES.map((phase, i) => {
            const Icon = phase.icon
            return (
              <div
                key={phase.num}
                className="relative flex flex-col gap-4 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-6 shadow-[0_4px_20px_-8px_rgba(7,59,102,0.1)]"
              >
                {/* Connector line (desktop) */}
                {i < PHASES.length - 1 && (
                  <span
                    className="absolute -right-3 top-10 hidden h-px w-6 bg-[var(--color-border)] lg:block"
                    aria-hidden="true"
                  />
                )}
                <div className="flex items-center gap-3">
                  <span className="text-[0.65rem] font-bold tracking-widest text-[var(--color-text-muted)]">
                    {phase.num}
                  </span>
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--color-aqua-soft)]">
                    <Icon size={16} className="text-[var(--color-primary)]" aria-hidden="true" />
                  </div>
                </div>
                <p className="text-xs font-bold uppercase tracking-widest text-[var(--color-navy)]">
                  {phase.label}
                </p>
                <p className="text-sm leading-relaxed text-[var(--color-text-muted)]">{phase.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
