import { forwardRef } from 'react'
import type { ComponentPropsWithoutRef, ReactNode } from 'react'

export interface InvestigationResultShellProps
  extends Omit<ComponentPropsWithoutRef<'section'>, 'children'> {
  children: ReactNode
}

/** Shared result frame; evidence and actions remain owned by each site. */
export const InvestigationResultShell = forwardRef<HTMLElement, InvestigationResultShellProps>(
  function InvestigationResultShell({ children, ...sectionProps }, ref) {
    return (
      <section ref={ref} {...sectionProps}>
        {children}
      </section>
    )
  },
)
