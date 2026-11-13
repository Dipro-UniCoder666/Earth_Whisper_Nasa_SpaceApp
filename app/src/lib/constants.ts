export const APP_NAME = 'Earth Whisper'
export const APP_TAGLINE = "Where Earth's Changes Tell Their Story"
export const DHARA_NAME = 'DHARA'
export const DHARA_TAGLINE = 'Seeing Water Changes. Supporting Better Decisions.'
export const DHARA_DESCRIPTION = 'Satellite-powered environmental monitoring and decision support.'
export const TEAM_NAME = 'AquaByte'
export const CHALLENGE_NAME = 'Dancing with the SARs'
export const CHALLENGE_YEAR = 'NASA Space Apps Challenge 2026'

export const ROUTES = {
  landing:     '/',
  investigate: '/investigate',
  science:     '/science',
  analysis:    '/analysis',
  investigationAnalysis: '/investigate/analysis',
  dhara:       '/dhara',
  dharaPallimangal: '/dhara/pallimangal',
  // Legacy route retained for saved links and internal integrations.
  gherproof:   '/gherproof',
  about:       '/about',
} as const

export const NAV_LINKS = [
  { label: 'Home',        to: '/',            external: false },
  { label: DHARA_NAME,   to: '/dhara',       external: false },
  { label: 'About',       to: '/about',       external: false },
] as const

// Legacy alias kept for any preserved components that reference it
export const NAV_LINKS_LANDING = NAV_LINKS
