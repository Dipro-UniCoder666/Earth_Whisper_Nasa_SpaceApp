import { cn } from '@/lib/utils'

interface InvestigationProgressBarProps {
  activeStep: 1 | 2 | 3 | 4 | 5
}

const STEPS = [
  { num: '01', label: 'Observe' },
  { num: '02', label: 'Compare' },
  { num: '03', label: 'Collect clues' },
  { num: '04', label: 'Investigate' },
  { num: '05', label: 'Understand' },
]

export function InvestigationProgressBar({ activeStep }: InvestigationProgressBarProps) {
  return (
    <nav
      aria-label="Investigation progress"
      className="border-b border-[var(--color-border-subtle)] bg-white"
    >
      <div className="page-container">
        {/* Desktop: full stepper */}
        <div className="hidden items-center py-2.5 md:flex">
          {STEPS.map((step, i) => {
            const stepNum = (i + 1) as 1 | 2 | 3 | 4 | 5
            const isActive = stepNum === activeStep
            const isComplete = stepNum < activeStep
            const isLocked = stepNum > activeStep

            return (
              <div key={step.num} className="flex items-center">
                <div
                  aria-current={isActive ? 'step' : undefined}
                  className={cn(
                    'flex items-center gap-1.5 text-xs',
                    isActive && 'font-semibold text-[var(--color-primary)]',
                    isComplete && 'font-medium text-[var(--color-primary)]/70',
                    isLocked && 'font-medium text-[var(--color-text-muted)]/50',
                  )}
                >
                  <span
                    className={cn(
                      'flex h-5 w-5 items-center justify-center rounded-full text-[0.6rem] font-bold',
                      isActive && 'bg-[var(--color-primary)] text-white',
                      isComplete && 'bg-[var(--color-primary)]/15 text-[var(--color-primary)]',
                      isLocked && 'bg-[var(--color-surface-subtle)] text-[var(--color-text-muted)]/50',
                    )}
                    aria-hidden="true"
                  >
                    {step.num}
                  </span>
                  {step.label}
                </div>
                {i < STEPS.length - 1 && (
                  <span
                    className="mx-3 text-[var(--color-border)] text-xs"
                    aria-hidden="true"
                  >
                    ───
                  </span>
                )}
              </div>
            )
          })}
        </div>

        {/* Mobile: show only active step */}
        <div className="flex items-center gap-2 py-2.5 md:hidden">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-primary)] text-[0.6rem] font-bold text-white" aria-hidden="true">
            {STEPS[activeStep - 1].num}
          </span>
          <span className="text-xs font-semibold text-[var(--color-primary)]">
            {STEPS[activeStep - 1].label}
          </span>
          <span className="text-xs text-[var(--color-text-muted)]">
            · Step {activeStep} of {STEPS.length}
          </span>
        </div>
      </div>
    </nav>
  )
}
