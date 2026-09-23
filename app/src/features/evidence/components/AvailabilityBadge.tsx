import { CheckCircle2, FlaskConical, CircleSlash } from 'lucide-react'
import type { EvidenceAvailability } from '@/features/evidence/types'
import { cn } from '@/lib/utils'

const CONFIG: Record<EvidenceAvailability, { label: string; icon: typeof CheckCircle2; className: string }> = {
  measured: {
    label: 'Measured',
    icon: CheckCircle2,
    className: 'bg-[var(--color-earth-green)]/15 text-[#2E7D53]',
  },
  demonstration: {
    label: 'Demonstration data',
    icon: FlaskConical,
    className: 'bg-[var(--color-aqua-soft)] text-[var(--color-navy)]',
  },
  unavailable: {
    label: 'Not yet available',
    icon: CircleSlash,
    className: 'bg-[var(--color-sky)] text-[var(--color-muted)]',
  },
}

export function AvailabilityBadge({ availability }: { availability: EvidenceAvailability }) {
  const { label, icon: Icon, className } = CONFIG[availability]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-wide',
        className,
      )}
    >
      <Icon size={12} aria-hidden="true" />
      {label}
    </span>
  )
}
