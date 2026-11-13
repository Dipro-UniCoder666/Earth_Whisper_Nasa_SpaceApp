import { useEffect } from 'react'
import { createBrowserRouter, Navigate, Outlet, useLocation } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { LandingPage } from '@/pages/LandingPage'
import { InvestigationPage } from '@/pages/InvestigationPage'
import { CaseInvestigationPage } from '@/pages/CaseInvestigationPage'
import { AboutPage } from '@/pages/AboutPage'
import { WhisperLabPage } from '@/pages/WhisperLabPage'
import { GherProofPage } from '@/features/gherproof/GherProofPage'
import { DHARA_DESCRIPTION, DHARA_NAME, DHARA_TAGLINE, ROUTES } from '@/lib/constants'

function DocumentTitleLayout() {
  const { pathname } = useLocation()

  useEffect(() => {
    const description = document.querySelector<HTMLMetaElement>('meta[name="description"]')
    if (pathname === '/') {
      document.title = 'Earth Whisper'
      if (description) description.content = "Earth Whisper — an interactive Earth-observation investigation experience by AquaByte."
      return
    }

    const pageName = pathname.startsWith('/investigate/case/')
      ? 'Event Case File'
      : pathname === ROUTES.investigationAnalysis
        ? 'Analysis Workbench'
        : pathname.startsWith('/dhara') || pathname.startsWith('/gherproof')
          ? DHARA_NAME
          : pathname.startsWith('/investigate')
        ? 'Investigate'
        : pathname.startsWith('/science')
          ? 'Analysis Workbench'
          : pathname.startsWith('/about')
            ? 'About'
            : 'Earth Whisper'

    document.title = pageName === 'Earth Whisper' ? pageName : `Earth Whisper - ${pageName}`
    if (description && (pathname.startsWith('/dhara') || pathname.startsWith('/gherproof'))) {
      description.content = `${DHARA_NAME} — ${DHARA_DESCRIPTION} ${DHARA_TAGLINE}`
    } else if (description) {
      description.content = "Earth Whisper — an interactive Earth-observation investigation experience by AquaByte."
    }
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
          { path: ROUTES.science, element: <Navigate to={ROUTES.investigationAnalysis} replace /> },
          { path: ROUTES.analysis, element: <Navigate to={ROUTES.investigationAnalysis} replace /> },
          { path: ROUTES.investigationAnalysis, element: <WhisperLabPage /> },
          { path: ROUTES.about,   element: <AboutPage /> },
          { path: ROUTES.gherproof, element: <GherProofPage /> },
          { path: ROUTES.dhara, element: <GherProofPage /> },
          { path: ROUTES.dharaPallimangal, element: <GherProofPage /> },
        ],
      },

      // Investigation pages manage their own navigation
      { path: ROUTES.investigate,                          element: <InvestigationPage /> },
      { path: `${ROUTES.investigate}/map`,                 element: <Navigate to={ROUTES.investigate} replace /> },
      { path: `${ROUTES.investigate}/case/:candidateId`,   element: <CaseInvestigationPage /> },
    ],
  },
])
