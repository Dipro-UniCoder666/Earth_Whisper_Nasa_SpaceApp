import { useEffect } from 'react'
import { createBrowserRouter, Navigate, Outlet, useLocation } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { LandingPage } from '@/pages/LandingPage'
import { InvestigationPage } from '@/pages/InvestigationPage'
import { CaseInvestigationPage } from '@/pages/CaseInvestigationPage'
import { AboutPage } from '@/pages/AboutPage'
import { WhisperLabPage } from '@/pages/WhisperLabPage'
import { ROUTES } from '@/lib/constants'

function DocumentTitleLayout() {
  const { pathname } = useLocation()

  useEffect(() => {
    if (pathname === '/') {
      document.title = 'Earth Whisper'
      return
    }

    const pageName = pathname.startsWith('/investigate/case/')
      ? 'Event Case File'
      : pathname.startsWith('/investigate')
        ? 'Investigate'
        : pathname.startsWith('/science')
          ? 'Whisper Lab'
          : pathname.startsWith('/about')
            ? 'About'
            : 'Earth Whisper'

    document.title = pageName === 'Earth Whisper' ? pageName : `Earth Whisper - ${pageName}`
  }, [pathname])

  return <Outlet />
}

export const router = createBrowserRouter([
  {
    element: <DocumentTitleLayout />,
    children: [
      // Landing page is standalone — no AppLayout (no GlobalNav, no Footer)
      { path: ROUTES.landing, element: <LandingPage /> },

      {
        // AppLayout wraps science and about pages
        element: <AppLayout />,
        children: [
          { path: ROUTES.science, element: <WhisperLabPage /> },
          { path: ROUTES.analysis, element: <Navigate to={ROUTES.science} replace /> },
          { path: ROUTES.about,   element: <AboutPage /> },
        ],
      },

      // Investigation pages manage their own navigation
      { path: ROUTES.investigate,                          element: <InvestigationPage /> },
      { path: `${ROUTES.investigate}/map`,                 element: <Navigate to={ROUTES.investigate} replace /> },
      { path: `${ROUTES.investigate}/case/:candidateId`,   element: <CaseInvestigationPage /> },
    ],
  },
])
