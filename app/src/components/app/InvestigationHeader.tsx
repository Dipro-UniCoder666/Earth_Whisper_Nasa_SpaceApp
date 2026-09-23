interface InvestigationHeaderProps {
  eyebrow?: string
  title: string
  subtitle: string
}

export function InvestigationHeader({ eyebrow, title, subtitle }: InvestigationHeaderProps) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      {eyebrow && (
        <p className="ew-anim-rise text-xs font-semibold uppercase tracking-[0.14em] text-[var(--color-aqua)]">
          {eyebrow}
        </p>
      )}
      <h1
        className="ew-anim-rise mt-3 font-display text-4xl font-medium leading-tight text-[var(--color-navy)] sm:text-[2.75rem]"
        style={{ animationDelay: '0.08s' }}
      >
        {title}
      </h1>
      <p className="ew-anim-rise mt-4 text-base leading-relaxed text-[var(--color-muted)]" style={{ animationDelay: '0.16s' }}>
        {subtitle}
      </p>
    </div>
  )
}
