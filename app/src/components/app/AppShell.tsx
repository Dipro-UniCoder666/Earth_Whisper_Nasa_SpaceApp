import type { ReactNode } from 'react'
import { SecondaryPageLayout } from '@/components/layout/SecondaryPageLayout'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  return (
    <SecondaryPageLayout>
      {children}
    </SecondaryPageLayout>
  )
}
