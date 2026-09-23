import { Link } from 'react-router-dom'
import { ROUTES } from '@/lib/constants'

/**
 * WhisperNav - the single shared navbar for the whole application.
 *
 * Visually identical to the landing page's transparent floating pill:
 * transparent background, thin rounded border, white logo + wordmark on
 * the left, the four primary links on the right (white text).
 *
 * Variants:
 * - `overlay` - absolutely positioned over a hero image (landing page).
 * - `sticky`  - pinned to the top of a scrolling page; the page supplies
 *               the dark landing background behind it.
 */
const NAV_LINKS = [
  { label: 'Home', to: ROUTES.landing },
  { label: 'Investigate', to: ROUTES.investigate },
  { label: 'Science', to: ROUTES.science },
  { label: 'About', to: ROUTES.about },
]

interface WhisperNavProps {
  variant?: 'overlay' | 'sticky'
}

export function WhisperNav({ variant = 'overlay' }: WhisperNavProps) {
  const pill = (
    <nav
      aria-label="Primary"
      className="whisper-nav-pill"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'transparent',
        border: '1px solid rgba(255,255,255,0.28)',
        borderRadius: '999px',
        padding: '0 32px',
        height: '58px',
      }}
    >
      {/* LEFT: white logo + wordmark */}
      <Link
        to={ROUTES.landing}
        aria-label="Earth Whisper home"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none',
          flexShrink: 0,
        }}
      >
        <img
          src="/images/LOGO_EW.svg"
          alt="Earth Whisper logo"
          className="whisper-nav-logo"
          style={{
            height: '30px',
            width: 'auto',
            display: 'block',
            filter: 'brightness(0) invert(1)',
          }}
        />
        <span
          className="whisper-nav-wordmark"
          style={{
            fontSize: '0.95rem',
            fontWeight: 700,
            color: '#ffffff',
            letterSpacing: '0.05em',
            whiteSpace: 'nowrap',
          }}
        >
          EARTH WHISPER
        </span>
      </Link>

      {/* RIGHT: nav links - white text */}
      <div className="whisper-nav-links" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        {NAV_LINKS.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="whisper-nav-link"
            style={{
              padding: '6px 16px',
              fontSize: '0.9rem',
              fontWeight: 500,
              color: '#ffffff',
              textDecoration: 'none',
              whiteSpace: 'nowrap',
              borderRadius: '999px',
              transition: 'background-color 0.15s',
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )

  if (variant === 'sticky') {
    return (
      <div
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 40,
          width: '100%',
          paddingTop: '20px',
          paddingBottom: '4px',
        }}
      >
        <div style={{ width: 'calc(100% - 80px)', maxWidth: '1200px', margin: '0 auto' }}>{pill}</div>
      </div>
    )
  }

  return (
    <div
      style={{
        position: 'absolute',
        top: '28px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 30,
        width: 'calc(100% - 80px)',
        maxWidth: '1200px',
      }}
    >
      {pill}
    </div>
  )
}