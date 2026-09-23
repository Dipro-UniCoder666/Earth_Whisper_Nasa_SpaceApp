import { HeroEarth } from '@/components/hero/HeroEarth'
import { HeroCTA } from '@/components/hero/HeroCTA'

export function Hero() {
  return (
    <section className="relative overflow-hidden px-6 pb-16 pt-6 lg:px-10 lg:pb-24">
      <div className="mx-auto grid max-w-7xl items-center gap-16 lg:grid-cols-[1.05fr_1fr] lg:gap-8">
        {/* Left: content */}
        <div className="relative z-10 max-w-xl">
          <p
            className="ew-anim-rise flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--color-primary)]"
            style={{ animationDelay: '0.05s' }}
          >
            <span>NASA Space Apps 2026</span>
            <span aria-hidden="true" className="text-[var(--color-muted)]">
              ×
            </span>
            <span>NISAR Earth Observation</span>
          </p>

          <h1
            className="ew-anim-rise mt-5 font-display text-[3.4rem] font-medium leading-[0.95] tracking-tight text-[var(--color-navy)] sm:text-[4.4rem]"
            style={{ animationDelay: '0.15s' }}
          >
            Earth
            <br />
            Whisper
          </h1>

          <p
            className="ew-anim-rise mt-6 font-display text-xl italic text-[var(--color-primary)] sm:text-2xl"
            style={{ animationDelay: '0.28s' }}
          >
            Where Earth&rsquo;s changes tell their story
          </p>

          <p
            className="ew-anim-rise mt-6 text-lg leading-relaxed text-[var(--color-muted)]"
            style={{ animationDelay: '0.4s' }}
          >
            Earth is constantly changing. Earth Whisper uses NASA NISAR radar observations to help
            uncover subtle changes across our planet — then turns those signals into an investigation.
          </p>

          <div className="ew-anim-rise mt-10" style={{ animationDelay: '0.55s' }}>
            <HeroCTA />
          </div>
        </div>

        {/* Right: visual */}
        <div className="ew-anim-scale relative z-10" style={{ animationDelay: '0.3s' }}>
          <HeroEarth />
        </div>
      </div>

      {/* Ambient background contour lines, very subtle */}
      <svg
        className="pointer-events-none absolute inset-x-0 bottom-0 -z-0 h-72 w-full opacity-[0.35]"
        viewBox="0 0 1200 300"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <path d="M0 260 C 300 200, 900 320, 1200 240" stroke="#0B5EA8" strokeOpacity="0.15" fill="none" />
        <path d="M0 220 C 300 160, 900 280, 1200 200" stroke="#18B7C9" strokeOpacity="0.12" fill="none" />
      </svg>
    </section>
  )
}
