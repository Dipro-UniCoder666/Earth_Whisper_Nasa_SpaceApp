import { Outlet, useLocation } from 'react-router-dom'
import { SecondaryPageLayout } from '@/components/layout/SecondaryPageLayout'

export function AppLayout() {
  const { pathname } = useLocation()
  return (
    <SecondaryPageLayout quiet={pathname.startsWith('/dhara') || pathname.startsWith('/gherproof')}>
      <Outlet />
    </SecondaryPageLayout>
  )
}
