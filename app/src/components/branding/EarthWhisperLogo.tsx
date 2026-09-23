import { cn } from '@/lib/utils'

interface EarthWhisperLogoProps {
  className?: string
  markOnly?: boolean
}

/**
 * The Earth Whisper mark: a simple radar-arc-over-sphere glyph, followed by
 * the wordmark. Kept intentionally quiet — this is a science instrument's
 * insignia, not a startup logo.
 */
export function EarthWhisperLogo({ className, markOnly = false }: EarthWhisperLogoProps) {
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true" className="shrink-0">
        <circle cx="14" cy="14" r="8" fill="var(--color-navy)" />
        <path
          d="M14 3.5c-2.8 3-4.3 6.7-4.3 10.5s1.5 7.5 4.3 10.5"
          stroke="var(--color-aqua)"
          strokeWidth="1.4"
          fill="none"
          opacity="0.85"
        />
        <path
          d="M4 10.5c4-2 16-2 20 0"
          stroke="var(--color-primary)"
          strokeWidth="1.4"
          fill="none"
          opacity="0.7"
        />
      </svg>
      {!markOnly && (
        <span className="font-display text-[1.35rem] font-medium tracking-tight text-[var(--color-navy)]">
          Earth Whisper
        </span>
      )}
    </div>
  )
}
