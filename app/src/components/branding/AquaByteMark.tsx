import { cn } from '@/lib/utils'

interface AquaByteMarkProps {
  className?: string
}

/** Small "by AquaByte" attribution mark used beneath the Earth Whisper wordmark. */
export function AquaByteMark({ className }: AquaByteMarkProps) {
  return (
    <span className={cn('text-xs font-medium text-[var(--color-muted)]', className)}>
      by <span className="text-[var(--color-aqua)]">AquaByte</span>
    </span>
  )
}
