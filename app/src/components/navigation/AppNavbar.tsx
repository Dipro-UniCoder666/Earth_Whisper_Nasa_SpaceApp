import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FlaskConical, Menu, Info, Home } from 'lucide-react'
import { EarthWhisperLogo } from '@/components/branding/EarthWhisperLogo'
import { IconButton } from '@/components/common/IconButton'
import { MobileMenu } from '@/components/navigation/MobileMenu'
import { ROUTES } from '@/lib/constants'

const APP_NAV_LINKS = [
  { label: 'Science Mode', href: '#science-mode' },
  { label: 'About', href: '#about' },
  { label: 'Home', href: ROUTES.landing },
] as const

export function AppNavbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scienceMode, setScienceMode] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--color-sky)] bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-10">
        <Link to={ROUTES.landing} className="flex items-center gap-3" aria-label="Earth Whisper home">
          <EarthWhisperLogo />
          <span className="hidden rounded-full bg-[var(--color-sky)] px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-primary)] sm:inline-block">
            Investigation
          </span>
        </Link>

        <nav className="hidden items-center gap-2 md:flex" aria-label="Application">
          <button
            type="button"
            onClick={() => setScienceMode((v) => !v)}
            aria-pressed={scienceMode}
            title="Science Mode is a preview control — full functionality arrives in a future update."
            className="flex items-center gap-2 rounded-full border border-[var(--color-sky)] px-4 py-2 text-sm font-medium text-[var(--color-navy)] transition-colors hover:border-[var(--color-primary)]"
          >
            <FlaskConical size={16} className={scienceMode ? 'text-[var(--color-aqua)]' : 'text-[var(--color-muted)]'} />
            Science Mode
            <span
              className={`ml-1 inline-block h-2 w-2 rounded-full ${scienceMode ? 'bg-[var(--color-earth-green)]' : 'bg-[var(--color-sky)]'}`}
              aria-hidden="true"
            />
          </button>
          <a
            href="#about"
            className="flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium text-[var(--color-text)] transition-colors hover:bg-[var(--color-sky)]"
          >
            <Info size={16} />
            About
          </a>
          <Link
            to={ROUTES.landing}
            className="flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium text-[var(--color-text)] transition-colors hover:bg-[var(--color-sky)]"
          >
            <Home size={16} />
            Home
          </Link>
        </nav>

        <div className="md:hidden">
          <IconButton icon={<Menu size={22} />} label="Open menu" onClick={() => setMenuOpen(true)} />
        </div>
      </div>

      <MobileMenu open={menuOpen} onClose={() => setMenuOpen(false)} links={APP_NAV_LINKS} />
    </header>
  )
}
