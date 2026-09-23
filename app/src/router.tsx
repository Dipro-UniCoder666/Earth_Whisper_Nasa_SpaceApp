import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { LandingPage } from '@/pages/LandingPage'
import { InvestigationPage } from '@/pages/InvestigationPage'
import { CaseInvestigationPage } from '@/pages/CaseInvestigationPage'
import { AboutPage } from '@/pages/AboutPage'
import { SciencePage } from '@/pages/SciencePage'
import { ROUTES } from '@/lib/constants'

export const router = createBrowserRouter([
  // Landing page is standalone — no AppLayout (no GlobalNav, no Footer)
  { path: ROUTES.landing, element: <LandingPage /> },

  {
    // AppLayout wraps science and about pages
    element: <AppLayout />,
    children: [
      { path: ROUTES.science, element: <SciencePage /> },
      { path: ROUTES.about,   element: <AboutPage /> },
    ],
  },

  // Investigation pages manage their own navigation
  { path: ROUTES.investigate,                          element: <InvestigationPage /> },
  { path: `${ROUTES.investigate}/map`,                 element: <Navigate to={ROUTES.investigate} replace /> },
  { path: `${ROUTES.investigate}/case/:candidateId`,   element: <CaseInvestigationPage /> },
])
