import { Outlet } from 'react-router-dom'
import { SecondaryPageLayout } from '@/components/layout/SecondaryPageLayout'

export function AppLayout() {
  return (
    <SecondaryPageLayout>
      <Outlet />
    </SecondaryPageLayout>
  )
}
