import { CheckCircle2, HelpCircle, XCircle } from 'lucide-react'
import type { FingerprintUncertainty } from '@/features/evidence/types'

interface UncertaintyPanelProps {
  uncertainty: FingerprintUncertainty
}

const SECTIONS: Array<{ key: keyof FingerprintUncertainty; label: string; icon: typeof CheckCircle2; className: string }> = [
  { key: 'known', label: 'What is known', icon: CheckCircle2, className: 'text-[#2E7D53]' },
  { key: 'uncertain', label: 'What is uncertain', icon: HelpCircle, className: 'text-[var(--color-primary)]' },
  { key: 'cannotConclude', label: 'What cannot be concluded', icon: XCircle, className: 'text-[#B3432B]' },
]

export function UncertaintyPanel({ uncertainty }: UncertaintyPanelProps) {
  return (
    <div className="rounded-2xl border border-[var(--color-sky)] bg-white p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-aqua)]">Uncertainty</p>
      <div className="mt-4 grid gap-5 sm:grid-cols-3">
        {SECTIONS.map(({ key, label, icon: Icon, className }) => (
          <div key={key}>
            <p className={`flex items-center gap-1.5 text-sm font-semibold ${className}`}>
              <Icon size={15} aria-hidden="true" />
              {label}
            </p>
            <ul className="mt-2 flex flex-col gap-1.5 text-xs leading-relaxed text-[var(--color-muted)]">
              {uncertainty[key].map((item, i) => (
                <li key={i}>• {item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
