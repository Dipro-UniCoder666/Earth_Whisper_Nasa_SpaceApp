import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Search } from 'lucide-react'
import { NAV_LINKS, ROUTES } from '@/lib/constants'
import { cn } from '@/lib/utils'

interface GlobalNavProps {
  scienceMode?: boolean
  onScienceModeChange?: (v: boolean) => void
}

export const NAV_HEIGHT = 60 // px — exported so LandingPage uses same value

export function GlobalNav({ scienceMode: _sm, onScienceModeChange: _oc }: GlobalNavProps) {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const triggerRef = useRef<HTMLButtonElement>(null)

  useEffect(() => { setMenuOpen(false) }, [location.pathname])
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && menuOpen) { setMenuOpen(false); triggerRef.current?.focus() }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [menuOpen])

  return (
    <>
      {/* ── Navbar ─────────────────────────────────────────── */}
      <header
        role="banner"
        className="sticky top-0 z-40 border-b border-[#D7E1EA] bg-white"
        style={{ height: `${NAV_HEIGHT}px` }}
      >
        <div className="page-container flex h-full items-center justify-between">

          {/* LEFT: logo */}
          <Link
            to={ROUTES.landing}
            aria-label="Earth Whisper home"
            className="flex shrink-0 items-center gap-2.5"
          >
            {/* Globe mark — exact size from reference ~36px */}
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" aria-hidden="true">
              <circle cx="18" cy="18" r="15" fill="#0B2A4A" />
              {/* land mass shapes */}
              <path d="M11 14 Q13 11 16 12 Q19 10 21 13 Q23 15 21 18 Q19 21 16 20 Q13 21 11 18 Z"
                fill="#1769B0" opacity="0.9" />
              <path d="M20 18 Q22 17 23 19 Q22 21 20 20 Z" fill="#1769B0" opacity="0.7" />
              {/* wave lines */}
              <path d="M5 15 Q8 13 11 15 Q14 17 17 15 Q20 13 23 15 Q26 17 29 15"
                stroke="#1D8C86" strokeWidth="1" fill="none" opacity="0.55" />
              <path d="M5 19 Q8 17 11 19 Q14 21 17 19 Q20 17 23 19 Q26 21 29 19"
                stroke="#1D8C86" strokeWidth="1" fill="none" opacity="0.45" />
              {/* circle border */}
              <circle cx="18" cy="18" r="15" stroke="#2E82C4" strokeWidth="1" fill="none" opacity="0.5" />
            </svg>
            <div className="flex flex-col leading-none">
              <span className="text-[0.95rem] font-bold tracking-tight text-[#0B2A4A]">
                EARTH WHISPER
              </span>
              <span className="mt-0.5 text-[0.65rem] font-normal text-[#52677D]">
                Where Earth&rsquo;s Changes Tell Their Story
              </span>
            </div>
          </Link>

          {/* CENTER: nav links */}
          <nav className="hidden items-center md:flex" aria-label="Primary">
            {NAV_LINKS.map((link) => {
              const isActive = location.pathname === link.to
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  aria-current={isActive ? 'page' : undefined}
                  className={cn(
                    'relative mx-1 px-3.5 py-1.5 text-[0.875rem] font-medium transition-colors',
                    isActive ? 'text-[#1769C2]' : 'text-[#0B2A4A] hover:text-[#1769C2]',
                  )}
                >
                  {link.label}
                  {isActive && (
                    <span
                      className="absolute bottom-[-1px] left-0 right-0 h-[2px] rounded-full bg-[#1769C2]"
                      aria-hidden="true"
                    />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* RIGHT: search + divider + CTA */}
          <div className="hidden items-center gap-2.5 md:flex">
            <button
              type="button"
              aria-label="Search"
              className="flex h-8 w-8 items-center justify-center text-[#52677D] hover:text-[#0B2A4A]"
            >
              <Search size={16} />
            </button>
            <span className="h-4 w-px bg-[#D7E1EA]" aria-hidden="true" />
            <Link
              to={ROUTES.investigate}
              className="inline-flex items-center gap-1.5 rounded-[8px] bg-[#1769C2] px-4 py-2 text-[0.82rem] font-semibold text-white hover:bg-[#1258A8]"
            >
              Begin Investigation
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
                <path d="M2 6.5h9M7 2.5l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          </div>

          {/* Mobile trigger */}
          <button
            ref={triggerRef}
            type="button"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            onClick={() => setMenuOpen((v) => !v)}
            className="flex h-8 w-8 items-center justify-center rounded border border-[#D7E1EA] text-[#0B2A4A] md:hidden"
          >
            {menuOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>
      </header>

      {/* Mobile menu */}
      {menuOpen && (
        <div
          id="mobile-nav"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation menu"
          className="fixed inset-0 z-50 flex flex-col bg-white md:hidden"
        >
          <div className="flex h-[60px] items-center justify-between border-b border-[#D7E1EA] px-5">
            <span className="text-[0.95rem] font-bold text-[#0B2A4A]">EARTH WHISPER</span>
            <button
              type="button"
              aria-label="Close menu"
              onClick={() => { setMenuOpen(false); triggerRef.current?.focus() }}
              className="flex h-8 w-8 items-center justify-center rounded border border-[#D7E1EA] text-[#0B2A4A]"
            >
              <X size={16} />
            </button>
          </div>
          <nav className="flex flex-col px-5" aria-label="Primary mobile">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMenuOpen(false)}
                className={cn(
                  'border-b border-[#EBF1F4] py-4 text-base font-medium',
                  location.pathname === link.to ? 'font-semibold text-[#1769C2]' : 'text-[#0B2A4A]',
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="mt-auto p-5">
            <Link
              to={ROUTES.investigate}
              onClick={() => setMenuOpen(false)}
              className="block w-full rounded-[8px] bg-[#1769C2] py-3 text-center text-sm font-semibold text-white"
            >
              Begin Investigation →
            </Link>
          </div>
        </div>
      )}
    </>
  )
}
